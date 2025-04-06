#!/bin/bash

# Define backup directory
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup data directory
if [ -d "./data" ] && [ "$(ls -A ./data)" ]; then
  echo "Backing up data directory..."
  cp -r ./data/* "$BACKUP_DIR/"
fi

# Backup .env file
if [ -f ".env" ]; then
  echo "Backing up .env file..."
  cp .env "$BACKUP_DIR/"
fi

echo "Backup created at $BACKUP_DIR"
