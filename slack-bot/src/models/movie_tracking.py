import os
import json

class MovieTracker:
    """
    Tracks which users have added which movies.
    """
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.tracking_file = os.path.join(data_dir, 'movie_users.json')
        self.movie_users = self._load_tracking_data()
    
    def _load_tracking_data(self):
        """Load tracking data from JSON file."""
        os.makedirs(self.data_dir, exist_ok=True)
        if os.path.exists(self.tracking_file):
            try:
                with open(self.tracking_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading movie tracking data: {e}")
        return {}  # Default empty dict if file doesn't exist or can't be read
    
    def _save_tracking_data(self):
        """Save tracking data to JSON file."""
        try:
            with open(self.tracking_file, 'w', encoding='utf-8') as f:
                json.dump(self.movie_users, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving movie tracking data: {e}")
    
    def add_user_to_movie(self, movie_id, user_id):
        """Track that a user has added a movie."""
        movie_id = str(movie_id)  # Ensure movie_id is a string for JSON compatibility
        
        if movie_id not in self.movie_users:
            self.movie_users[movie_id] = []
        
        if user_id not in self.movie_users[movie_id]:
            self.movie_users[movie_id].append(user_id)
            self._save_tracking_data()
    
    def get_movie_users(self, movie_id):
        """Get all users who have added a movie."""
        movie_id = str(movie_id)  # Ensure movie_id is a string for JSON compatibility
        return self.movie_users.get(movie_id, [])
    
    def get_all_data(self):
        """Get all movie-user tracking data."""
        return self.movie_users
