from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# TMDB API Configuration
TMDB_API_KEY = os.getenv("TMDB_API_KEY")  # Load API key from .env file

# Application Configuration
DEBUG = True
