import os
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from src.config import SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SLACK_CHANNEL_ID
from src.tmdb_api import extract_movie_id_from_url, get_movie_details, save_to_json

# Initialize Slack Bolt app
app = App(token=SLACK_BOT_TOKEN)

# Set to keep track of processed URLs to avoid duplicates
processed_urls = set()

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
        # Check if it's a TMDB URL and hasn't been processed yet
        if is_tmdb_url(url) and url not in processed_urls:
            movie_data = process_tmdb_url(url)
            
            if movie_data:
                # Add to processed set and save to file
                processed_urls.add(url)
                save_processed_url(url)
                
                # Add a reaction to the message instead of replying
                try:
                    client.reactions_add(
                        channel=channel_id,
                        timestamp=event.get("ts"),
                        name="movie_camera"  # Movie camera emoji
                    )
                except Exception as e:
                    print(f"Error adding reaction: {e}")

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
