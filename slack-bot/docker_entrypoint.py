#!/usr/bin/env python3
"""
Docker entrypoint script for the Slack bot.
This script ensures the bot stays running and handles termination signals properly.
"""

import os
import signal
import sys
import time
from src.slack_bot import start_slack_bot

# Handle termination signals properly
def signal_handler(sig, frame):
    print("Received signal to terminate, shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    print("Starting Slack bot in Docker container...")
    
    try:
        # Run the Slack bot (this should be a blocking call)
        start_slack_bot()
        
        # If the bot function returns (non-blocking), keep the container alive
        print("Warning: Slack bot function returned. Keeping container alive...")
        while True:
            time.sleep(60)
    except Exception as e:
        print(f"Error running Slack bot: {e}")
        sys.exit(1)
