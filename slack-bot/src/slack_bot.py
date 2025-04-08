import os
import re
import json
import random
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from src.config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SLACK_CHANNEL_ID
from src.tmdb_api import extract_movie_id_from_url, get_movie_details, save_to_json
from src.models.movie import Movie
from src.models.movie_tracking import MovieTracker

# Initialize Slack Bolt app
app = App(token=SLACK_BOT_TOKEN)

# Set to keep track of processed URLs to avoid duplicates
processed_urls = set()

# Initialize movie tracker
movie_tracker = MovieTracker()

# Function to get user names from IDs
def get_user_names(client, user_ids):
    """Convert user IDs to display names."""
    user_names = []
    for user_id in user_ids:
        try:
            user_info = client.users_info(user=user_id)
            display_name = user_info["user"].get("profile", {}).get("display_name")
            if not display_name:
                display_name = user_info["user"].get("real_name")
            if not display_name:
                display_name = user_info["user"].get("name")  # Fallback to username
            user_names.append(display_name)
        except Exception as e:
            print(f"Error getting user info: {e}")
            user_names.append(f"User {user_id}")  # Fallback if we can't get user info
    
    return user_names

# Function to get all movie data files
def get_all_movies():
    """Get all movies from the data directory."""
    movies = []
    data_dir = 'data'
    
    if not os.path.exists(data_dir):
        return []
    
    for filename in os.listdir(data_dir):
        if filename.endswith('.json') and filename != 'popular_movies.json' and filename != 'movie_users.json':
            try:
                # Skip processing URLs file
                if filename == 'processed_urls.txt':
                    continue
                    
                with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
                    movie_data = json.load(f)
                    # Skip non-movie data files
                    if 'title' in movie_data and 'id' in movie_data:
                        movies.append(Movie(movie_data))
            except Exception as e:
                print(f"Error loading movie data from {filename}: {e}")
    
    return movies

def format_movie_list(movies, client=None):
    """Format movie list for slack display."""
    if not movies:
        return "No movies found in the database."
    
    movies.sort(key=lambda x: x.title)
    movie_lines = []
    
    for i, movie in enumerate(movies, 1):
        year = movie.release_date[:4] if movie.release_date else "N/A"
        rating = f"{movie.vote_average}/10" if movie.vote_average else "N/A"
        line = f"{i}. *{movie.title}* ({year}) - {rating}"
        
        # Get the users who added this movie if client is provided
        if client:
            user_ids = movie_tracker.get_movie_users(movie.id)
            if user_ids:
                user_names = get_user_names(client, user_ids)
                line += f" - Added by: {', '.join(user_names)}"
        
        movie_lines.append(line)
    
    return "\n".join(movie_lines)

def get_random_movie():
    """Get a random movie from the data directory."""
    movies = get_all_movies()
    if not movies:
        return None
    
    return random.choice(movies)

def format_movie_detail(movie, client=None):
    """Format a single movie for detailed slack display."""
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": movie.title,
                "emoji": True
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Year:* {movie.release_date[:4] if movie.release_date else 'N/A'}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Rating:* {movie.vote_average}/10 ({movie.vote_count} votes)"
                }
            ]
        }
    ]
    
    # Add genres if available
    if movie.genres:
        blocks.append({
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Genres:* {', '.join(movie.genres)}"
                }
            ]
        })
    
    # Add users who added this movie if client is provided
    if client:
        user_ids = movie_tracker.get_movie_users(movie.id)
        if user_ids:
            user_names = get_user_names(client, user_ids)
            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Added by:* {', '.join(user_names)}"
                    }
                ]
            })
    
    # Add overview if available
    if movie.overview:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Overview:*\n{movie.overview[:300]}{'...' if len(movie.overview) > 300 else ''}"
            }
        })
    
    # Add poster if available
    if movie.get_poster_url():
        blocks.append({
            "type": "image",
            "image_url": movie.get_poster_url(),
            "alt_text": movie.title
        })
    
    # Add TMDB link
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"<https://www.themoviedb.org/movie/{movie.id}|View on TMDB>"
            }
        ]
    })
    
    return blocks

# Add command handlers
@app.command("/movies")
def list_movies(ack, respond, command):
    """Handle /movies command to list all movies."""
    # Acknowledge command request
    ack()
    
    movies = get_all_movies()
    movie_list = format_movie_list(movies, app.client)
    
    respond({
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Movie List ({len(movies)} movies)*"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": movie_list
                }
            }
        ]
    })

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
    respond({
        "blocks": blocks
    })

def is_tmdb_url(url):
    """Check if a URL is from themoviedb.org."""
    return 'themoviedb.org/movie' in url

def load_processed_urls():
    """Load previously processed URLs from file."""
    try:
        if os.path.exists('data/processed_urls.txt'):
            with open('data/processed_urls.txt', 'r') as f:
                return set(line.strip() for line in f)
        return set()
    except Exception as e:
        print(f"Error loading processed URLs: {e}")
        return set()

def save_processed_url(url):
    """Save a processed URL to file."""
    try:
        os.makedirs('data', exist_ok=True)
        with open('data/processed_urls.txt', 'a') as f:
            f.write(f"{url}\n")
    except Exception as e:
        print(f"Error saving processed URL: {e}")

def process_tmdb_url(url, user_id=None):
    """Process a TMDB URL to fetch and save movie data."""
    movie_id = extract_movie_id_from_url(url)
    if not movie_id:
        return None
    
    movie_data = get_movie_details(movie_id)
    if not movie_data:
        return None
    
    # Save to JSON using just the movie ID as filename
    filename = f"{movie_id}.json"
    save_to_json(movie_data, filename)
    
    # Track the user who added this movie if user_id is provided
    if user_id:
        movie_tracker.add_user_to_movie(movie_id, user_id)
    
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
    urls = re.findall(r'https?://[^\s]+', text)
    
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
                            name="movie_camera"  # Movie camera emoji
                        )
                    except Exception as e:
                        print(f"Error adding movie reaction: {e}")
        else:
            # Not a TMDB URL, add middle finger reaction
            try:
                client.reactions_add(
                    channel=channel_id,
                    timestamp=event.get("ts"),
                    name="middle_finger"  # Middle finger emoji
                )
            except Exception as e:
                print(f"Error adding middle finger reaction: {e}")

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
    print(f"Already processed {len(processed_urls)} URLs")
    print("Press Ctrl+C to stop the bot")
    
    # Start the Socket Mode handler
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
