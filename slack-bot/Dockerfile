FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files
COPY slack-bot/pyproject.toml .
COPY slack-bot/uv.lock .

RUN uv sync

# Copy source code
COPY slack-bot/src/ src/
COPY slack-bot/main.py .

# Set environment variable for Python to run unbuffered
ENV PYTHONUNBUFFERED=1

# Run the bot using the start_slack_bot function
CMD ["uv", "run", "from src.slack_bot import start_slack_bot; start_slack_bot()"]
