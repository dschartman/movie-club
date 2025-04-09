FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Create data directory explicitly before any volume mounting happens
RUN mkdir -p /app/data

# Copy dependency file and install with uv
COPY pyproject.toml .
RUN uv pip install --system

# Copy source code
COPY main.py .
COPY app/ app/

# Set environment variable for Python to run unbuffered
ENV PYTHONUNBUFFERED=1

# Expose the port
EXPOSE 8000

# Run the API server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
