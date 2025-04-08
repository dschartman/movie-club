import os
import re
import json
import random
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from src.config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SLACK_CHANNEL_ID
from src.tmdb_api import extract_movie_id_from_url, get_movie_details, save_to_json
from src.models.movie import Movie

# Initialize Slack Bolt app
app = App(token=SLACK_BOT_TOKEN)

# Set to keep track of processed URLs to avoid duplicates
processed_urls = set()

# Function to get all movie data files
def get_all_movies():
    """Get all movies from the data directory."""
    movies = []
    data_dir = 'data'
    
    if not os.path.exists(data_dir):
        return []
    
    for filename in os.listdir(data_dir):
        if filename.endswith('.json') and filename != 'popular_movies.json':
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

def format_movie_list(movies):
    """Format movie list for slack display."""
    if not movies:
        return "No movies found in the database."
    
    movies.sort(key=lambda x: x.title)
    movie_lines = []
    
    for i, movie in enumerate(movies, 1):
        year = movie.release_date[:4] if movie.release_date else "N/A"
        rating = f"{movie.vote_average}/10" if movie.vote_average else "N/A"
        movie_lines.append(f"{i}. *{movie.title}* ({year}) - {rating}")
    
    return "\n".join(movie_lines)

def get_random_movie():
    """Get a random movie from the data directory."""
    movies = get_all_movies()
    if not movies:
        return None
    
    return random.choice(movies)

def format_movie_detail(movie):
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
def list_movies(ack, respond):
    """Handle /movies command to list all movies."""
    # Acknowledge command request
    ack()
    
    movies = get_all_movies()
    movie_list = format_movie_list(movies)
    
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
def random_movie(ack, respond):
    """Handle /random command to pick a random movie."""
    # Acknowledge command request
    ack()
    
    movie = get_random_movie()
    
    if not movie:
        respond("No movies found in the database.")
        return
    
    blocks = format_movie_detail(movie)
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

def process_tmdb_url(url):
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
    
    return movie_data

@app.event("message")
def handle_message_events(event, client):
    """Handle message events in the specified channel."""
    channel_id = event.get("channel")
    text = event.get("text", "")
    
    # Only process messages from the designated channel
    if channel_id != SLACK_CHANNEL_ID:
        return
    
    # Extract URLs from the message
    urls = re.findall(r'https?://[^\s]+', text)
    
    for url in urls:
        if is_tmdb_url(url):
            # Check if it hasn't been processed yet
            if url not in processed_urls:
                movie_data = process_tmdb_url(url)
                
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
