FROM python:3.11-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Create data directory explicitly before any volume mounting happens
RUN mkdir -p /app/data

# Copy dependency files
COPY slack-bot/pyproject.toml .
COPY slack-bot/uv.lock .

RUN uv sync

# Copy source code
COPY slack-bot/src/ src/
COPY slack-bot/main.py .

# Set environment variable for Python to run unbuffered
ENV PYTHONUNBUFFERED=1

# Run the bot using the proper module syntax
CMD ["python", "-m", "src.slack_bot"]
