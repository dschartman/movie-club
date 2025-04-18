import os
import re
import json
import random
import time
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from src.config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SLACK_CHANNEL_ID
from src.tmdb_api import extract_movie_id_from_url, get_movie_details
from src.models.movie import Movie
from src.api_client import ApiClient

# Initialize Slack Bolt app
app = App(token=SLACK_BOT_TOKEN)

# Set to keep track of processed URLs to avoid duplicates
processed_urls = set()

# Initialize API client
api_client = ApiClient()

# Cache for user information to reduce API calls
user_cache = {}
# Cache expiration time in seconds (24 hours)
USER_CACHE_EXPIRY = 86400


# Function to get user names from IDs
def get_user_names(client, user_ids):
    """Convert user IDs to display names with caching."""
    global user_cache
    current_time = time.time()
    user_names = []
    
    for user_id in user_ids:
        # Check if user is in the cache and not expired
        if user_id in user_cache and (current_time - user_cache[user_id]['timestamp'] < USER_CACHE_EXPIRY):
            user_names.append(user_cache[user_id]['display_name'])
            continue
            
        try:
            # Not in cache or expired, get user information from Slack
            if os.getenv("DEBUG_SLACK_API"):
                print(f"Cache miss for user {user_id}, fetching from Slack API")
                
            user_info = client.users_info(user=user_id)

            # Debug the response if needed
            if os.getenv("DEBUG_SLACK_API"):
                print(f"User info for {user_id}: {user_info.data}")

            # Try different fields in order of preference
            user_data = user_info.get("user", {})
            profile = user_data.get("profile", {})

            # Try several name options in order of preference
            display_name = profile.get("display_name_normalized") or profile.get(
                "display_name"
            )
            if not display_name or display_name == "":
                display_name = user_data.get("real_name") or profile.get("real_name")
            if not display_name or display_name == "":
                display_name = user_data.get("name")  # Fallback to username

            # If still nothing, use a better formatted fallback
            if not display_name or display_name == "":
                display_name = f"@{user_id.replace('U', '')}"

            # Store in cache
            user_cache[user_id] = {
                'display_name': display_name,
                'timestamp': current_time
            }
            
            user_names.append(display_name)

        except Exception as e:
            print(f"Error getting user info for {user_id}: {str(e)}")
            # Use a more friendly fallback
            user_names.append("@unknown-user")

    return user_names


# Cache for movie data
movie_cache = {
    'data': None,
    'timestamp': 0
}
# Movie cache expiration time in seconds (2 minutes)
MOVIE_CACHE_EXPIRY = 120

# Function to get all movies from API with caching
def get_all_movies():
    """Get all movies from the API with caching."""
    current_time = time.time()
    
    # Return cached data if available and not expired
    if movie_cache['data'] is not None and (current_time - movie_cache['timestamp'] < MOVIE_CACHE_EXPIRY):
        return movie_cache['data']
    
    # Cache miss or expired, fetch fresh data
    movies_dict = api_client.get_all_movies()
    movie_list = list(movies_dict.values())
    
    # Update cache
    movie_cache['data'] = movie_list
    movie_cache['timestamp'] = current_time
    
    return movie_list


def format_movie_list(movies, client=None, page=1, page_size=25):
    """Format movie list for slack display with pagination."""
    if not movies:
        return "No movies found in the database."

    # Sort movies alphabetically
    movies.sort(key=lambda x: x.title)
    
    # Calculate total pages
    total_pages = (len(movies) + page_size - 1) // page_size
    
    # Get movies for current page
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, len(movies))
    page_movies = movies[start_idx:end_idx]
    
    movie_lines = []
    
    # Add page info header
    movie_lines.append(f"*Page {page}/{total_pages} (Showing movies {start_idx+1}-{end_idx} of {len(movies)})*")
    movie_lines.append("")  # Empty line for spacing
    
    for i, movie in enumerate(page_movies, start_idx + 1):
        year = movie.release_date[:4] if movie.release_date else "N/A"
        rating = f"{movie.vote_average}/10" if movie.vote_average else "N/A"
        line = f"{i}. *{movie.title}* ({year}) - {rating}"

        # Get the users who added this movie if client is provided
        if client and movie.id:
            user_ids = api_client.get_movie_users(movie.id)
            if user_ids:
                user_names = get_user_names(client, user_ids)
                line += f" - Added by: {', '.join(user_names)}"

        movie_lines.append(line)

    return "\n".join(movie_lines)


def get_random_movie():
    """Get a random movie from the API."""
    return api_client.get_random_movie()


def format_movie_detail(movie, client=None):
    """Format a single movie for detailed slack display."""
    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": movie.title, "emoji": True},
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Year:* {movie.release_date[:4] if movie.release_date else 'N/A'}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Rating:* {movie.vote_average}/10 ({movie.vote_count} votes)",
                },
            ],
        },
    ]

    # Add genres if available
    if movie.genres:
        blocks.append(
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Genres:* {', '.join(movie.genres)}"}
                ],
            }
        )

    # Add users who added this movie if client is provided
    if client and movie.id:
        user_ids = api_client.get_movie_users(movie.id)
        if user_ids:
            user_names = get_user_names(client, user_ids)
            blocks.append(
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Added by:* {', '.join(user_names)}",
                        }
                    ],
                }
            )

    # Add overview if available
    if movie.overview:
        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Overview:*\n{movie.overview[:300]}{'...' if len(movie.overview) > 300 else ''}",
                },
            }
        )

    # Add poster if available
    if movie.get_poster_url():
        blocks.append(
            {
                "type": "image",
                "image_url": movie.get_poster_url(),
                "alt_text": movie.title,
            }
        )

    # Add TMDB link
    blocks.append(
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"<https://www.themoviedb.org/movie/{movie.id}|View on TMDB>",
                }
            ],
        }
    )

    return blocks


# Add command handlers
@app.command("/movies")
def list_movies(ack, respond, command):
    """Handle /movies command to list all movies."""
    # Acknowledge command request
    ack()

    # Parse command text for page number
    command_text = command.get("text", "").strip()
    try:
        page = int(command_text) if command_text else 1
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    movies = get_all_movies()
    
    # Calculate pagination info
    page_size = 25  # Number of movies per page
    total_pages = (len(movies) + page_size - 1) // page_size
    
    # Ensure page is within valid range
    if page > total_pages and total_pages > 0:
        page = total_pages
    
    # Use the common pagination handler
    handle_pagination(page, respond)


@app.command("/random")
def random_movie(ack, respond, command):
    """Handle /random command to pick a random movie."""
    # Acknowledge command request
    ack()

    movie = get_random_movie()

    if not movie:
        respond("No movies found in the database.")
        return

    blocks = format_movie_detail(movie, app.client)
    respond({"blocks": blocks})


def is_tmdb_url(url):
    """Check if a URL is from themoviedb.org."""
    return "themoviedb.org/movie" in url


def load_processed_urls():
    """Load previously processed URLs from file."""
    try:
        if os.path.exists("data/processed_urls.txt"):
            with open("data/processed_urls.txt", "r") as f:
                return set(line.strip() for line in f)
        return set()
    except Exception as e:
        print(f"Error loading processed URLs: {e}")
        return set()


def save_processed_url(url):
    """Save a processed URL to file."""
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/processed_urls.txt", "a") as f:
            f.write(f"{url}\n")
    except Exception as e:
        print(f"Error saving processed URL: {e}")


def process_tmdb_url(url, user_id=None):
    """Process a TMDB URL to fetch and add movie data via API."""
    movie_id = extract_movie_id_from_url(url)
    if not movie_id:
        return None

    movie_data = get_movie_details(movie_id)
    if not movie_data:
        return None

    # Add the movie to the API
    movie_obj = api_client.add_movie(movie_data)
    
    # Track the user who added this movie if user_id is provided
    if user_id and movie_obj and movie_obj.id:
        api_client.add_user_to_movie(movie_obj.id, user_id)

    return movie_data


@app.event("message")
def handle_message_events(event, client):
    """Handle message events in the specified channel."""
    channel_id = event.get("channel")
    text = event.get("text", "")
    user_id = event.get("user")  # Get the user who posted the message

    # Only process messages from the designated channel
    if channel_id != SLACK_CHANNEL_ID:
        return

    # Extract URLs from the message
    urls = re.findall(r"https?://[^\s]+", text)

    for url in urls:
        if is_tmdb_url(url):
            # Check if it hasn't been processed yet
            if url not in processed_urls:
                movie_data = process_tmdb_url(url, user_id)  # Pass the user_id

                if movie_data:
                    # Add to processed set and save to file
                    processed_urls.add(url)
                    save_processed_url(url)

                    # Add a movie camera reaction
                    try:
                        client.reactions_add(
                            channel=channel_id,
                            timestamp=event.get("ts"),
                            name="movie_camera",  # Movie camera emoji
                        )
                    except Exception as e:
                        print(f"Error adding movie reaction: {e}")
        else:
            # Not a TMDB URL, add middle finger reaction
            try:
                client.reactions_add(
                    channel=channel_id,
                    timestamp=event.get("ts"),
                    name="middle_finger",  # Middle finger emoji
                )
            except Exception as e:
                print(f"Error adding middle finger reaction: {e}")


# Helper function to handle pagination
def handle_pagination(page, respond):
    """Common handler for pagination."""
    start_time = time.time()
    movies = get_all_movies()
    page_size = 25
    
    # Format the movie list
    movie_list = format_movie_list(movies, app.client, page, page_size)
    
    total_pages = (len(movies) + page_size - 1) // page_size
    
    # Create page navigation buttons
    actions = []
    if page > 1:
        actions.append({
            "type": "button",
            "text": {"type": "plain_text", "text": "◀️ Previous", "emoji": True},
            "value": f"{page-1}",
            "action_id": "movie_prev_page"
        })
    
    if page < total_pages:
        actions.append({
            "type": "button",
            "text": {"type": "plain_text", "text": "Next ▶️", "emoji": True},
            "value": f"{page+1}",
            "action_id": "movie_next_page"
        })
    
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Movie List ({len(movies)} movies)*",
            },
        },
        {"type": "section", "text": {"type": "mrkdwn", "text": movie_list}}
    ]
    
    if actions:
        blocks.append({"type": "actions", "elements": actions})
    
    # Update the original message
    respond({"blocks": blocks, "replace_original": True})
    
    # Log performance
    end_time = time.time()
    print(f"Page {page} took {end_time - start_time:.2f} seconds to generate")

# Add button action handlers for pagination
@app.action("movie_next_page")
def handle_next_page(ack, body, respond):
    """Handle pagination next page button."""
    ack()
    page = int(body["actions"][0]["value"])
    handle_pagination(page, respond)

@app.action("movie_prev_page")
def handle_prev_page(ack, body, respond):
    """Handle pagination previous page button."""
    ack()
    page = int(body["actions"][0]["value"])
    handle_pagination(page, respond)

def start_slack_bot():
    """Start the Slack bot in Socket Mode."""
    global processed_urls

    # Check if required env variables are set
    if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN or not SLACK_CHANNEL_ID:
        print("Error: Missing required Slack configuration in .env file.")
        print("Please set SLACK_BOT_TOKEN, SLACK_APP_TOKEN, and SLACK_CHANNEL_ID.")
        return

    # Load previously processed URLs
    processed_urls = load_processed_urls()

    print(f"Starting Slack bot, monitoring channel ID: {SLACK_CHANNEL_ID}")
    print(f"Connected to Movie API at: {api_client.base_url}")
    print(f"Already processed {len(processed_urls)} URLs")
    print("Press Ctrl+C to stop the bot")

    # Start the Socket Mode handler
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
