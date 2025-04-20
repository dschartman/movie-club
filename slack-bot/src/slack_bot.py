import os
import importlib
import inspect
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from src.config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SLACK_CHANNEL_ID, BOT_ENVIRONMENT, ENV_PREFIX
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
            
            # Wrap the respond function to add environment prefix
            original_respond = respond
            def prefixed_respond(text_or_blocks, **kwargs):
                if isinstance(text_or_blocks, str):
                    # Add prefix to string responses
                    text_or_blocks = f"{ENV_PREFIX}{text_or_blocks}"
                elif isinstance(text_or_blocks, dict) and "text" in text_or_blocks:
                    # Add prefix to block text
                    text_or_blocks["text"] = f"{ENV_PREFIX}{text_or_blocks['text']}"
                return original_respond(text_or_blocks, **kwargs)
            
            # Execute the command asynchronously using a thread-safe approach
            import asyncio
            
            def run_async_command():
                # Create a new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    # Run the command in the new loop with prefixed respond
                    loop.run_until_complete(
                        cmd.execute(
                            ack=lambda: None,  # We already acked
                            respond=prefixed_respond,
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

# Add action handler for movie poll votes
@app.action(re.compile("^vote_movie_"))
def handle_movie_vote(ack, body, client):
    """Handle movie poll votes."""
    ack()
    
    # Check if action was triggered in the configured channel
    action_channel = body.get("channel", {}).get("id")
    if action_channel != SLACK_CHANNEL_ID:
        client.chat_postEphemeral(
            channel=action_channel,
            user=body["user"]["id"],
            text="⚠️ This action is only available in the designated movie channel."
        )
        return
    
    # Extract movie ID from action
    action_id = body["actions"][0]["action_id"]
    movie_id = action_id.replace("vote_movie_", "")
    
    # Get user info
    user_id = body["user"]["id"]
    
    try:
        # Get user name
        user_info = client.users_info(user=user_id)
        user_name = user_info["user"]["real_name"] or user_info["user"]["name"]
    except:
        user_name = f"<@{user_id}>"
    
    # Update the message to show vote
    blocks = body["message"]["blocks"]
    
    # Find the actions block and update it
    for block in blocks:
        if block.get("block_id") == "movie_poll_votes":
            for button in block.get("elements", []):
                if button.get("action_id") == action_id:
                    # Update the button text to show votes
                    current_text = button["text"]["text"]
                    
                    # Check if already voted - if so, REMOVE the vote
                    if "(" in current_text and user_name in current_text:
                        # User already voted, so remove their vote
                        vote_text = current_text.split("(")[0].strip()
                        voters_text = current_text.split("(")[1].replace(")", "")
                        
                        # Split the voters by comma and handle both single and multiple voter cases
                        voters = [v.strip() for v in voters_text.split(",")]
                        
                        # Remove this user from voters
                        if user_name in voters:
                            voters.remove(user_name)
                        
                        # If there are still voters, update the text
                        if voters:
                            voters_text = ", ".join(voters)
                            button["text"]["text"] = f"{vote_text} ({voters_text})"
                        else:
                            # No voters left, remove the parenthesis part
                            button["text"]["text"] = vote_text
                            
                        # Post ephemeral confirmation message just to the user
                        client.chat_postEphemeral(
                            channel=action_channel,
                            user=user_id,
                            text=f"You removed your vote from option {vote_text}"
                        )
                    elif "(" in current_text:
                        # Add user to existing votes
                        vote_text = current_text.split("(")[0].strip()
                        voters = current_text.split("(")[1].replace(")", "")
                        button["text"]["text"] = f"{vote_text} ({voters}, {user_name})"
                        
                        # Post ephemeral confirmation message just to the user
                        client.chat_postEphemeral(
                            channel=action_channel,
                            user=user_id,
                            text=f"You voted for {vote_text}"
                        )
                    else:
                        # First vote
                        button["text"]["text"] = f"{current_text} ({user_name})"
                        
                        # Post ephemeral confirmation message just to the user
                        client.chat_postEphemeral(
                            channel=action_channel,
                            user=user_id,
                            text=f"You voted for {current_text}"
                        )
    
    # Update the message
    try:
        client.chat_update(
            channel=action_channel,
            ts=body["message"]["ts"],
            blocks=blocks,
            text="Vote for the next movie to watch!"
        )
    except Exception as e:
        print(f"Error updating poll vote: {e}")

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
    print(f"Bot running in {BOT_ENVIRONMENT.upper()} environment")
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

    print(f"Starting Slack bot in {BOT_ENVIRONMENT.upper()} environment")
    print(f"Monitoring channel: #{channel_name} (ID: {SLACK_CHANNEL_ID})")
    print(f"Commands and actions will ONLY work in this channel")
    print(f"Connected to Movie API at: {api_client.base_url}")
    print("Press Ctrl+C to stop the bot")

    # Start the Socket Mode handler
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
