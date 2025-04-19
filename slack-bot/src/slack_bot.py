import os
import importlib
import inspect
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from src.config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SLACK_CHANNEL_ID
from src.api_client import ApiClient
from src.models.movie import Movie
from src.handlers.message_handlers import handle_message_event, initialize as init_message_handlers
from src.handlers.cache_management import get_cached_movies, get_all_movie_users
from src.handlers.pagination import handle_pagination
from src.commands.command_base import SlackCommand, registry
from src.handlers.command_handlers import handle_next_page, handle_prev_page

# Import all command modules to register commands
from src.commands import movie_commands

# Initialize Slack Bolt app
app = App(token=SLACK_BOT_TOKEN)

# Initialize API client
api_client = ApiClient()

# Register all commands with Slack
for command_name, command_obj in registry.get_all_commands().items():
    # Define a non-async handler that will be called by Slack Bolt
    def create_command_handler(cmd):
        def command_handler(ack, respond, command, logger):
            # Immediately acknowledge the command
            ack()
            
            # Check if command was issued in the configured channel
            command_channel = command.get("channel_id")
            if command_channel != SLACK_CHANNEL_ID:
                # Command was used in the wrong channel
                try:
                    channel_info = app.client.conversations_info(channel=SLACK_CHANNEL_ID)
                    channel_name = channel_info["channel"]["name"]
                    respond(f"⚠️ This command can only be used in <#{SLACK_CHANNEL_ID}|{channel_name}>")
                except Exception as e:
                    respond(f"⚠️ This command can only be used in the configured channel")
                    logger.error(f"Error getting channel info: {e}")
                logger.info(f"Command /{cmd.name} rejected - wrong channel: {command_channel}")
                return
                
            logger.info(f"Executing command: {cmd.name} in channel: {command_channel}")
            
            # Execute the command asynchronously using a thread-safe approach
            import asyncio
            
            def run_async_command():
                # Create a new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    # Run the command in the new loop
                    loop.run_until_complete(
                        cmd.execute(
                            ack=lambda: None,  # We already acked
                            respond=respond,
                            command=command,
                            app_client=app.client
                        )
                    )
                finally:
                    loop.close()
            
            # Run in a separate thread to avoid blocking
            import threading
            thread = threading.Thread(target=run_async_command)
            thread.start()
        
        return command_handler
    
    # Register with a dedicated function for each command
    handler = create_command_handler(command_obj)
    app.command(f"/{command_name}")(handler)
    print(f"Registered handler for /{command_name}")

@app.event("message")
def handle_message_events(event, client):
    """Handle message events in the specified channel."""
    handle_message_event(event, client, api_client, SLACK_CHANNEL_ID)

# Add button action handlers for pagination
@app.action("movie_next_page")
def next_page(ack, body, respond):
    """Handle pagination next page button."""
    ack()
    
    # Check if action was triggered in the configured channel
    action_channel = body.get("channel", {}).get("id")
    if action_channel != SLACK_CHANNEL_ID:
        respond({"text": "⚠️ This action is only available in the designated movie channel.", "replace_original": False})
        return
        
    page = int(body["actions"][0]["value"])
    
    # Handle pagination
    movies = get_cached_movies(api_client)
    users_by_movie = get_all_movie_users(movies, app.client, api_client)
    
    handle_pagination(
        page,
        respond,
        app.client,
        lambda: movies,
        lambda m, client: users_by_movie
    )

@app.action("movie_prev_page")
def prev_page(ack, body, respond):
    """Handle pagination previous page button."""
    ack()
    
    # Check if action was triggered in the configured channel
    action_channel = body.get("channel", {}).get("id")
    if action_channel != SLACK_CHANNEL_ID:
        respond({"text": "⚠️ This action is only available in the designated movie channel.", "replace_original": False})
        return
    
    page = int(body["actions"][0]["value"])
    
    # Handle pagination
    movies = get_cached_movies(api_client)
    users_by_movie = get_all_movie_users(movies, app.client, api_client)
    
    handle_pagination(
        page,
        respond,
        app.client,
        lambda: movies,
        lambda m, client: users_by_movie
    )

def start_slack_bot():
    """Start the Slack bot in Socket Mode."""
    # Check if required env variables are set
    if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN or not SLACK_CHANNEL_ID:
        print("Error: Missing required Slack configuration in .env file.")
        print("Please set SLACK_BOT_TOKEN, SLACK_APP_TOKEN, and SLACK_CHANNEL_ID.")
        return

    # Initialize message handlers (loads processed URLs)
    init_message_handlers()

    # Log available commands
    print("Registered commands:")
    for name, cmd in registry.get_all_commands().items():
        print(f"  /{name}: {cmd.description}")

    # Try to get channel name for more informative logging
    channel_name = "unknown"
    try:
        channel_info = app.client.conversations_info(channel=SLACK_CHANNEL_ID)
        channel_name = channel_info["channel"]["name"]
    except Exception as e:
        print(f"Warning: Could not fetch channel name: {e}")

    print(f"Starting Slack bot, monitoring channel: #{channel_name} (ID: {SLACK_CHANNEL_ID})")
    print(f"Commands and actions will ONLY work in this channel")
    print(f"Connected to Movie API at: {api_client.base_url}")
    print("Press Ctrl+C to stop the bot")

    # Start the Socket Mode handler
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
