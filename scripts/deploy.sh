#!/bin/bash

# Set script to exit on any error
set -e

# Define backup function
backup_data() {
  echo "Backing up data directory..."
  backup_dir="./backups/$(date +%Y%m%d_%H%M%S)"
  mkdir -p "$backup_dir"
  
  if [ -d "./data" ] && [ "$(ls -A ./data)" ]; then
    cp -r ./data/* "$backup_dir/"
    echo "Backup created at $backup_dir"
  else
    echo "No data to backup or data directory is empty"
  fi
}

# Create backup directory if it doesn't exist
mkdir -p ./backups

# Backup current data
backup_data

# Pull latest changes
echo "Pulling latest changes from repository..."
git pull

# Copy example env file if .env doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Please edit .env file with your credentials"
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p data

# Build and start Docker containers
echo "Building and starting Docker containers..."
docker-compose build
docker-compose up -d

# Show the status
echo "Deployment complete! Container status:"
docker-compose ps
