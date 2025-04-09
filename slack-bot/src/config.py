from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# TMDB API Configuration
TMDB_API_KEY = os.getenv("TMDB_API_KEY")  # Load API key from .env file

# Slack Configuration
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")  # xoxb- token
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")  # xapp- token for Socket Mode
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")  # Channel to monitor

# API Configuration
# In Docker Compose environment, use the service name as the host
API_BASE_URL = os.getenv("API_BASE_URL", "http://movie-api:8000")

# Application Configuration
DEBUG = True
DEBUG_SLACK_API = os.getenv("DEBUG_SLACK_API", "").lower() in ("true", "1", "t", "yes")
