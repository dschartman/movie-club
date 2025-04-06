FROM python:3.11-slim

WORKDIR /app

# Create data directory explicitly before any volume mounting happens
RUN mkdir -p /app/data

# Copy dependency files
COPY slack-bot/pyproject.toml .

# Install dependencies directly with pip
RUN pip install --no-cache-dir pytest python-dotenv requests slack-bolt

# Copy source code
COPY slack-bot/src/ src/
COPY slack-bot/main.py .

# Set environment variable for Python to run unbuffered
ENV PYTHONUNBUFFERED=1

# Run the bot using the proper module syntax
CMD ["python", "-m", "src.slack_bot"]
