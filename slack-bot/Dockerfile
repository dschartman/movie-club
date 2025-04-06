FROM python:3.13-slim

WORKDIR /app

# Copy dependency files
COPY slack-bot/pyproject.toml .
COPY slack-bot/uv.lock .

# Install dependencies
RUN pip install uv && \
    uv pip install -e .

# Copy source code
COPY slack-bot/src/ src/
COPY slack-bot/main.py .

# Create data directory
RUN mkdir -p /app/data

# Set environment variable for Python to run unbuffered
ENV PYTHONUNBUFFERED=1

# Run the bot using the start_slack_bot function
CMD ["python", "-c", "from src.slack_bot import start_slack_bot; start_slack_bot()"]
