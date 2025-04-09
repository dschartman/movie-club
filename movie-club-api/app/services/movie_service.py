import os
import json
import random
import re
from typing import Dict, List, Optional, Tuple, Union

from app.schemas.movie import Movie

class MovieService:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.tracking_file = os.path.join(data_dir, 'movie_users.json')
        os.makedirs(data_dir, exist_ok=True)
    
    def get_all_movies(self) -> Dict[str, Movie]:
        """Get all movies from the data directory."""
        movies = {}
        
        if not os.path.exists(self.data_dir):
            return {}
            
        for filename in os.listdir(self.data_dir):
            if (filename.endswith(".json") and 
                filename != "popular_movies.json" and 
                filename != "movie_users.json"):
                try:
                    with open(os.path.join(self.data_dir, filename), "r", encoding="utf-8") as f:
                        movie_data = json.load(f)
                        # Skip non-movie data files
                        if "title" in movie_data and "id" in movie_data:
                            movie_id = str(movie_data["id"])
                            movies[movie_id] = Movie(**movie_data)
                except Exception as e:
                    print(f"Error loading movie data from {filename}: {e}")
                    
        return movies
    
    def get_movie(self, movie_id: int) -> Optional[Movie]:
        """Get a specific movie by ID."""
        movie_file = os.path.join(self.data_dir, f"{movie_id}.json")
        
        if os.path.exists(movie_file):
            try:
                with open(movie_file, "r", encoding="utf-8") as f:
                    movie_data = json.load(f)
                    return Movie(**movie_data)
            except Exception as e:
                print(f"Error loading movie {movie_id}: {e}")
                
        return None
    
    def get_random_movie(self) -> Optional[Movie]:
        """Get a random movie."""
        movies = self.get_all_movies()
        if not movies:
            return None
            
        movie_id = random.choice(list(movies.keys()))
        return movies[movie_id]
    
    def get_movie_users(self, movie_id: int) -> List[str]:
        """Get users who added a movie."""
        movie_id = str(movie_id)
        
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, "r", encoding="utf-8") as f:
                    tracking_data = json.load(f)
                    return tracking_data.get(movie_id, [])
            except Exception as e:
                print(f"Error loading movie tracking data: {e}")
                
        return []
    
    def add_user_to_movie(self, movie_id: int, user_id: str) -> bool:
        """Add a user to a movie."""
        movie_id = str(movie_id)
        
        # Load existing tracking data
        tracking_data = {}
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, "r", encoding="utf-8") as f:
                    tracking_data = json.load(f)
            except Exception as e:
                print(f"Error loading tracking data: {e}")
        
        # Add the user to the movie
        if movie_id not in tracking_data:
            tracking_data[movie_id] = []
            
        if user_id not in tracking_data[movie_id]:
            tracking_data[movie_id].append(user_id)
            
            # Save the updated tracking data
            try:
                with open(self.tracking_file, "w", encoding="utf-8") as f:
                    json.dump(tracking_data, f, indent=4, ensure_ascii=False)
                return True
            except Exception as e:
                print(f"Error saving tracking data: {e}")
                
        return False
        
    def get_all_genres(self) -> List[Dict[str, Union[int, str, int]]]:
        """Get all available genres with counts."""
        movies = self.get_all_movies().values()
        genre_counts = {}
        
        for movie in movies:
            for genre in movie.genres:
                genre_id = genre.get("id")
                genre_name = genre.get("name")
                
                if genre_id and genre_name:
                    if genre_id not in genre_counts:
                        genre_counts[genre_id] = {"id": genre_id, "name": genre_name, "count": 0}
                    
                    genre_counts[genre_id]["count"] += 1
        
        return list(genre_counts.values())
    
    def get_movies_by_genre(self, genre_id: int) -> List[Movie]:
        """Get movies filtered by genre."""
        movies = self.get_all_movies().values()
        return [m for m in movies if any(g.get("id") == genre_id for g in m.genres)]
        
    def add_movie(self, movie_data: Dict) -> Optional[Movie]:
        """Add a new movie to the data directory."""
        if not movie_data or "id" not in movie_data:
            return None
            
        movie_id = movie_data["id"]
        movie_file = os.path.join(self.data_dir, f"{movie_id}.json")
        
        # Check if movie already exists
        if os.path.exists(movie_file):
            return self.get_movie(movie_id)
            
        try:
            # Ensure the movie data is valid by parsing it through the Movie model
            movie = Movie(**movie_data)
            
            # Save the movie data to a file
            with open(movie_file, "w", encoding="utf-8") as f:
                json.dump(movie_data, f, indent=4, ensure_ascii=False)
            
            return movie
        except Exception as e:
            print(f"Error adding movie {movie_id}: {e}")
            return None
