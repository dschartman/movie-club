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

# Application Configuration
DEBUG = True
