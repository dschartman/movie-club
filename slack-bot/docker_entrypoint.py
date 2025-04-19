#!/usr/bin/env python3
"""
Movie Club Bot entrypoint script.
This script serves as the single entry point for the Slack bot,
handling proper signal management, logging, and error handling.
"""

import os
import signal
import sys
import time
import logging
import argparse
from src.slack_bot import start_slack_bot

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('movie-club-bot')

# Handle termination signals properly
def signal_handler(sig, frame):
    logger.info("Received signal to terminate, shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def run_cli():
    """Run the CLI utility"""
    from src.cli_functions import main as cli_main
    logger.info("Starting Movie Club CLI...")
    cli_main()

def main():
    """Main entrypoint function"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Movie Club Bot')
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode')
    args = parser.parse_args()
    
    if args.cli:
        run_cli()
        return
    
    # Default: run as Slack bot
    logger.info("Starting Slack bot...")
    
    # Log environment settings (without sensitive info)
    logger.info(f"API Base URL: {os.getenv('API_BASE_URL', 'Not set - using default')}")
    logger.info(f"Debug mode: {os.getenv('DEBUG', 'False')}")
    
    try:
        # Run the Slack bot (this should be a blocking call)
        start_slack_bot()
        
        # If the bot function returns (non-blocking), keep the container alive
        logger.warning("Slack bot function returned. Keeping container alive...")
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Shutting down...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running Slack bot: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
