import requests
from typing import Dict, List, Optional, Any
import json
from src.config import API_BASE_URL
from src.models.movie import Movie

class ApiClient:
    """Client for communicating with the Movie Club API"""
    
    def __init__(self, base_url=None):
        self.base_url = base_url or API_BASE_URL
    
    def get_all_movies(self) -> Dict[str, Movie]:
        """Fetch all movies from the API"""
        try:
            response = requests.get(f"{self.base_url}/api/movies")
            response.raise_for_status()
            movies_dict = response.json()
            
            # Convert API response to Movie objects
            result = {}
            for movie_id, movie_data in movies_dict.items():
                result[movie_id] = Movie(movie_data)
            
            return result
        except Exception as e:
            print(f"Error fetching movies from API: {e}")
            return {}
    
    def get_movie(self, movie_id: int) -> Optional[Movie]:
        """Fetch a specific movie by ID"""
        try:
            response = requests.get(f"{self.base_url}/api/movies/{movie_id}")
            response.raise_for_status()
            movie_data = response.json()
            return Movie(movie_data)
        except Exception as e:
            print(f"Error fetching movie {movie_id} from API: {e}")
            return None
    
    def add_movie(self, movie_data: Dict[str, Any]) -> Optional[Movie]:
        """Add a new movie to the API"""
        try:
            response = requests.post(
                f"{self.base_url}/api/movies", 
                json=movie_data
            )
            
            if response.status_code in (200, 201):
                return Movie(response.json())
            else:
                print(f"Failed to add movie. Status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"Error adding movie to API: {e}")
            return None
    
    def get_random_movie(self) -> Optional[Movie]:
        """Get a random movie from the API"""
        try:
            response = requests.get(f"{self.base_url}/api/random")
            response.raise_for_status()
            return Movie(response.json())
        except Exception as e:
            print(f"Error fetching random movie from API: {e}")
            return None
    
    def get_movie_users(self, movie_id: int) -> List[str]:
        """Get users who have added a movie"""
        try:
            response = requests.get(f"{self.base_url}/api/movies/{movie_id}/users")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching users for movie {movie_id}: {e}")
            return []
    
    def add_user_to_movie(self, movie_id: int, user_id: str) -> bool:
        """Add a user to a movie's user list"""
        try:
            response = requests.post(
                f"{self.base_url}/api/movies/{movie_id}/users?user_id={user_id}"
            )
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error adding user {user_id} to movie {movie_id}: {e}")
            return False
