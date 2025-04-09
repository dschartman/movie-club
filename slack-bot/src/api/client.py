import requests
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class MovieApiClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def _make_request(self, method, endpoint, **kwargs):
        """Make an HTTP request to the API."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            if response.status_code != 204:  # No content
                return response.json()
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API request error for {url}: {e}")
            return None
    
    def get_all_movies(self) -> List[Dict[str, Any]]:
        """Get all movies from the API."""
        return self._make_request("GET", "/movies") or []
    
    def get_movie(self, movie_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific movie by ID."""
        return self._make_request("GET", f"/movies/{movie_id}")
    
    def get_random_movie(self) -> Optional[Dict[str, Any]]:
        """Get a random movie."""
        return self._make_request("GET", "/random")
    
    def add_user_to_movie(self, movie_id: int, user_id: str) -> bool:
        """Add a user to a movie."""
        response = self._make_request(
            "POST", 
            f"/movies/{movie_id}/users", 
            json={"user_id": user_id}
        )
        return response is not None
    
    def get_movie_users(self, movie_id: int) -> List[str]:
        """Get all users who have added a movie."""
        return self._make_request("GET", f"/movies/{movie_id}/users") or []
    
    def process_url(self, url: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Process a TMDB URL to fetch and save movie data."""
        params = {"url": url}
        if user_id:
            params["user_id"] = user_id
        return self._make_request("POST", "/process-url", params=params)
    
    def get_processed_urls(self) -> List[str]:
        """Get all processed URLs."""
        return self._make_request("GET", "/urls/processed") or []
    
    def add_processed_url(self, url: str) -> bool:
        """Add a URL to the list of processed URLs."""
        response = self._make_request("POST", "/urls/processed", params={"url": url})
        return response is not None
