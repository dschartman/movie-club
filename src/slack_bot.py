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
        print(f"Could not extract movie ID from URL: {url}")
        return None
    
    movie_data = get_movie_details(movie_id)
    if not movie_data:
        print(f"Could not retrieve movie with ID {movie_id}")
        return None
    
    # Save to JSON using just the movie ID as filename
    filename = f"{movie_id}.json"
    save_to_json(movie_data, filename)
    
    return movie_data

@app.event("message")
def handle_message_events(event, say):
    """Handle message events in the specified channel."""
    print(f"Received message event: {event}")
    channel_id = event.get("channel")
    text = event.get("text", "")
    
    print(f"Channel ID from event: {channel_id}")
    print(f"Expected channel ID: {SLACK_CHANNEL_ID}")
    print(f"Message text: {text}")
    
    # Only process messages from the designated channel
    if channel_id != SLACK_CHANNEL_ID:
        print("Channel ID doesn't match, ignoring message")
        return
    
    # Extract URLs from the message
    urls = re.findall(r'https?://[^\s]+', text)
    print(f"Found URLs: {urls}")
    
    for url in urls:
        # Check if it's a TMDB URL and hasn't been processed yet
        if is_tmdb_url(url):
            print(f"Found TMDB URL: {url}")
            if url in processed_urls:
                print(f"URL already processed: {url}")
                continue
                
            print(f"Processing TMDB URL: {url}")
            movie_data = process_tmdb_url(url)
            
            if movie_data:
                # Add to processed set and save to file
                processed_urls.add(url)
                save_processed_url(url)
                
                # Acknowledge in the channel that we've added the movie
                say(f"Added movie: {movie_data.get('title')} (ID: {movie_data.get('id')})")
            else:
                print(f"Failed to process movie data for URL: {url}")

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
