import requests
import json
import os
import re
from src.config import TMDB_API_KEY

BASE_URL = "https://api.themoviedb.org/3"

def save_to_json(data, filename="sample_movie_data.json"):
    """Save API response data to a JSON file with pretty formatting."""
    # Create 'data' directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Clean the filename to remove any characters that might cause issues
    if filename:
        filename = re.sub(r'[\\/*?:"<>|]', "", filename)
    
    filepath = os.path.join("data", filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Data saved to {filepath}")
    return filepath

def extract_movie_id_from_url(url):
    """Extract the movie ID from a TMDB URL.
    
    Example URL formats:
    - https://www.themoviedb.org/movie/550-fight-club
    - https://www.themoviedb.org/movie/550
    """
    # Extract the ID from the URL using regex
    # Looking for a number after /movie/
    match = re.search(r'/movie/(\d+)', url)
    if match:
        return match.group(1)
    return None

def get_movie_details(movie_id):
    """Fetch detailed information about a specific movie."""
    endpoint = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US"
    }
    
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_movie_by_url(url):
    """Get movie details from a TMDB URL and save to a JSON file."""
    movie_id = extract_movie_id_from_url(url)
    if not movie_id:
        return None, "Invalid URL format. Could not extract movie ID."
    
    movie_data = get_movie_details(movie_id)
    if not movie_data:
        return None, f"Could not retrieve movie with ID {movie_id}."
    
    # Save to JSON using the movie ID as filename
    title = movie_data.get('title', 'movie')
    filename = f"movie_{movie_id}_{title}.json"
    save_to_json(movie_data, filename)
    
    return movie_data, None

def search_movies(query, page=1):
    """Search for movies based on a keyword or phrase."""
    endpoint = f"{BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "query": query,
        "page": page,
        "include_adult": False
    }
    
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def get_popular_movies(page=1):
    """Get a list of currently popular movies."""
    endpoint = f"{BASE_URL}/movie/popular"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "page": page
    }
    
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None
