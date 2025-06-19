#!/bin/bash

# Check if webserver mode is requested
if [ "$1" == "webserver" ]; then
    COMPOSE_FILE="docker-compose-webserver.yml"
else
    COMPOSE_FILE="docker-compose.yml"
fi

# Pull latest images
docker compose -f ${COMPOSE_FILE} pull

# Start FreqTrade
docker compose -f ${COMPOSE_FILE} up -d