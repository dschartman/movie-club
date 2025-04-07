#!/bin/bash

# Script to start development environment with error handling

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running. Please start Docker and try again."
  exit 1
fi

# Ensure data directory exists with proper permissions
echo "Creating data directory if it doesn't exist..."
mkdir -p data
chmod 777 data

# Verify essential React app files exist
echo "Verifying essential React files..."
if [ ! -f "movie-club-web/src/App.tsx" ] || [ ! -f "movie-club-web/src/index.tsx" ] || [ ! -f "movie-club-web/src/reportWebVitals.ts" ]; then
  echo "WARNING: Some essential React files are missing. This may cause build errors."
fi

# Explicitly pull required images to avoid credential issues
echo "Pulling required Docker images..."
docker pull node:lts-alpine
docker pull python:3.11-slim
docker pull nginx:stable-alpine

echo "Starting development environment..."
docker-compose -f docker-compose.dev.yml up --build
