import requests
import json
import os
from src.config import TMDB_API_KEY

BASE_URL = "https://api.themoviedb.org/3"

def save_to_json(data, filename="sample_movie_data.json"):
    """Save API response data to a JSON file with pretty formatting."""
    # Create 'data' directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    filepath = os.path.join("data", filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Data saved to {filepath}")
    return filepath

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
