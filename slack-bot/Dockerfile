FROM python:3.13-slim

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
COPY slack-bot/docker_entrypoint.py .

# Set environment variable for Python to run unbuffered
ENV PYTHONUNBUFFERED=1

# Make the entrypoint script executable
RUN chmod +x docker_entrypoint.py

# Run the bot using our custom entrypoint script
CMD ["python", "docker_entrypoint.py"]
