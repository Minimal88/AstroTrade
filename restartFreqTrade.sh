#!/bin/bash

# Stop and remove the existing FreqTrade container
docker stop freqtrade
docker rm freqtrade

# Check if webserver mode is requested
if [ "$1" == "webserver" ]; then
    COMPOSE_FILE="freqTrade/docker-compose-webserver.yml"
else
    COMPOSE_FILE="freqTrade/docker-compose.yml"
fi

# Build the custom image
docker compose -f ${COMPOSE_FILE} build

# Pull latest images
# docker compose -f ${COMPOSE_FILE} pull

# Start FreqTrade
docker compose -f ${COMPOSE_FILE} up -d  --remove-orphans

# See the logs
docker logs -f freqtrade