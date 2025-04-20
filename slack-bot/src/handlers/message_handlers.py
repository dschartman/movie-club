import re
import os
from slack_sdk.errors import SlackApiError
from src.tmdb_api import extract_movie_id_from_url, get_movie_details

# Set to keep track of processed URLs to avoid duplicates
processed_urls = set()

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

def process_tmdb_url(url, user_id, api_client):
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

def handle_message_event(event, client, api_client, slack_channel_id):
    """Handle message events in the specified channel."""
    global processed_urls
    
    channel_id = event.get("channel")
    text = event.get("text", "")
    user_id = event.get("user")  # Get the user who posted the message

    # Only process messages from the designated channel
    if channel_id != slack_channel_id:
        return

    # Extract URLs from the message
    urls = re.findall(r"https?://[^\s]+", text)

    for url in urls:
        if is_tmdb_url(url):
            # Check if it hasn't been processed yet
            if url not in processed_urls:
                # First check if this URL already has a movie_camera reaction (another instance might have processed it)
                try:
                    reactions_response = client.reactions_get(
                        channel=channel_id,
                        timestamp=event.get("ts")
                    )
                    
                    existing_reactions = []
                    if 'message' in reactions_response and 'reactions' in reactions_response['message']:
                        existing_reactions = [r['name'] for r in reactions_response['message']['reactions']]
                    
                    # If already processed by another instance, skip processing
                    if 'movie_camera' in existing_reactions:
                        processed_urls.add(url)
                        save_processed_url(url)
                        continue
                except Exception as e:
                    print(f"Error checking reactions: {e}")
                
                movie_data = process_tmdb_url(url, user_id, api_client)

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
                    except SlackApiError as e:
                        if "already_reacted" in str(e):
                            # Already reacted, ignore this error
                            pass
                        else:
                            print(f"Error adding movie reaction: {e}")
        else:
            # Not a TMDB URL, add middle finger reaction - but check first
            try:
                # Check if the reaction is already there
                reactions_response = client.reactions_get(
                    channel=channel_id,
                    timestamp=event.get("ts")
                )
                
                existing_reactions = []
                if 'message' in reactions_response and 'reactions' in reactions_response['message']:
                    existing_reactions = [r['name'] for r in reactions_response['message']['reactions']]
                
                # Only add if not already there
                if 'middle_finger' not in existing_reactions:
                    client.reactions_add(
                        channel=channel_id,
                        timestamp=event.get("ts"),
                        name="middle_finger",  # Middle finger emoji
                    )
            except SlackApiError as e:
                if "already_reacted" in str(e):
                    # Already reacted, ignore this error
                    pass
                else:
                    print(f"Error adding reaction: {e}")

def initialize():
    """Initialize the message handlers module."""
    global processed_urls
    processed_urls = load_processed_urls()
    print(f"Message handler initialized, loaded {len(processed_urls)} processed URLs")
