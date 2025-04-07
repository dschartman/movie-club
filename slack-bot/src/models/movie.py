class Movie:
    """
    Movie model class representing a movie from TMDB.
    This model captures the essential information about a movie.
    """
    
    def __init__(self, tmdb_data=None):
        """Initialize a movie object from TMDB API data."""
        if tmdb_data:
            self.id = tmdb_data.get('id')
            self.title = tmdb_data.get('title')
            self.original_title = tmdb_data.get('original_title')
            self.overview = tmdb_data.get('overview')
            self.release_date = tmdb_data.get('release_date')
            self.poster_path = tmdb_data.get('poster_path')
            self.backdrop_path = tmdb_data.get('backdrop_path')
            self.popularity = tmdb_data.get('popularity')
            self.vote_average = tmdb_data.get('vote_average')
            self.vote_count = tmdb_data.get('vote_count')
            self.genres = [genre.get('name') for genre in tmdb_data.get('genres', [])]
            self.runtime = tmdb_data.get('runtime')
        else:
            self.id = None
            self.title = ""
            self.original_title = ""
            self.overview = ""
            self.release_date = ""
            self.poster_path = None
            self.backdrop_path = None
            self.popularity = 0.0
            self.vote_average = 0.0
            self.vote_count = 0
            self.genres = []
            self.runtime = None
    
    def get_poster_url(self, size="w500"):
        """Generate the full URL for the movie poster."""
        if self.poster_path:
            return f"https://image.tmdb.org/t/p/{size}{self.poster_path}"
        return None
    
    def get_backdrop_url(self, size="original"):
        """Generate the full URL for the movie backdrop."""
        if self.backdrop_path:
            return f"https://image.tmdb.org/t/p/{size}{self.backdrop_path}"
        return None
    
    def __str__(self):
        return f"{self.title} ({self.release_date[:4] if self.release_date else 'N/A'})"
    
    def __repr__(self):
        return f"Movie(id={self.id}, title='{self.title}')"
