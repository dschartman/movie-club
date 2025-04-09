FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Create data directory explicitly before any volume mounting happens
RUN mkdir -p /app/data

# Copy dependency files
COPY slack-bot/pyproject.toml .

# Install dependencies with uv
RUN uv sync

# Copy source code
COPY slack-bot/src/ src/
COPY slack-bot/main.py .
COPY slack-bot/docker_entrypoint.py .

# Set environment variable for Python to run unbuffered
ENV PYTHONUNBUFFERED=1

# Make the entrypoint script executable
RUN chmod +x docker_entrypoint.py

# Run the bot using our custom entrypoint script
CMD ["uv", "run", "python", "docker_entrypoint.py"]
