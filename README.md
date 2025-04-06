# Movie Club

A full-stack application for managing and discussing movies with your friends.

## Project Components

- **Web App**: React application for browsing and viewing movie details
- **API Server**: Node.js server providing movie data to the web app
- **Slack Bot**: Python-based bot for monitoring Slack channels for movie links

## Development Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in required API keys
3. Run `scripts/dev.sh` to start the development environment

## Docker Configuration

The project uses Docker for both development and production:

- **Development**: Uses hot-reloading for all components
- **Production**: Uses optimized builds with proper caching

### Docker Image Versions

- Web & API: Node.js LTS Alpine
- Slack Bot: Python 3.11 (downgraded from 3.13 for better compatibility)
- Web Server: Nginx stable-alpine

## Troubleshooting

If you encounter Docker credential issues, try these steps:
1. Use `docker login` to refresh your credentials
2. Add the Docker credential configuration to your `.env` file
