#!/bin/bash

# Script to start development environment with error handling

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running. Please start Docker and try again."
  exit 1
fi

# Explicitly pull required images to avoid credential issues
echo "Pulling required Docker images..."
docker pull node:lts-alpine
docker pull python:3.11-slim
docker pull nginx:stable-alpine

echo "Starting development environment..."
docker-compose -f docker-compose.dev.yml up
