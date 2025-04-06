#!/bin/bash

# Check if containers are running
echo "Checking container status..."
docker-compose ps

# Show logs for the last hour
echo -e "\nRecent logs:"
docker-compose logs --tail=50

# Check disk space
echo -e "\nDisk space:"
df -h | grep "/dev/"

# Check CPU and memory usage
echo -e "\nResource usage:"
top -b -n 1 | head -n 20
