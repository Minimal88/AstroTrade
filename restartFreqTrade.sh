#!/bin/bash

# Stop and remove the existing FreqTrade container
./stopFreqTrade.sh

STRATEGIES_DIRECTORY="freqtrade/user_data/strategies"
CONFIGS_DIRECTORY="freqtrade/user_data/configs"
# Parse arguments and print usage if needed
MODE="default"
STRATEGY_ARG=""

usage() {
    echo "Usage: $0 [mode] [opts]"
    echo "  mode: default | webserver"
    echo "  opts: --strategy strategyName"
    exit 1
}

# Check mode argument
if [[ "$1" == "webserver" ]]; then
    COMPOSE_FILE="freqtrade/docker-compose-webserver.yml"
    MODE="webserver"    
    shift
elif [[ "$1" == "default" ]]; then
    COMPOSE_FILE="freqtrade/docker-compose.yml"
    MODE="default"
    shift
elif [[ -n "$1" ]]; then
    usage
else
    COMPOSE_FILE="freqtrade/docker-compose.yml"
    MODE="default"
    echo "No mode specified, using default mode."
fi

# Parse options
while [[ $# -gt 0 ]]; do
    case "$1" in
        --strategy)
            if [[ -n "$2" ]]; then
                STRATEGY_ARG="$2"
                shift 2
            else
                usage
            fi
            ;;
        *)
            usage
            ;;
    esac
done

# If strategy is provided as an argument, then checks if it exists
if [[ -n "$STRATEGY_ARG" ]]; then    
    STRATEGY_PATH="$STRATEGIES_DIRECTORY/$STRATEGY_ARG.py"
    if [[ -f "$STRATEGY_PATH" ]]; then
        echo "Using provided strategy: $STRATEGY_ARG"
        export SELECTED_STRATEGY="$STRATEGY_ARG"
    else
        echo "Error: Strategy '$STRATEGY_ARG' does not exist in '$STRATEGIES_DIRECTORY'."
        exit 1
    fi
else
    echo "No strategy provided. Please select a strategy from '$STRATEGIES_DIRECTORY'."
    # Obtain the available strategies from the strategies directory
    if [ ! -d "$STRATEGIES_DIRECTORY" ]; then
        echo "Error: '$STRATEGIES_DIRECTORY' directory does not exist."
        exit 1
    else
        STRATEGIES=$(find "$STRATEGIES_DIRECTORY" -maxdepth 1 -type f -name "*.py" -exec basename {} .py \;)
        echo "Available strategies:"
        select STRATEGY in $STRATEGIES; do
            if [[ -n "$STRATEGY" ]]; then
                echo "Selected strategy: $STRATEGY"
                export SELECTED_STRATEGY="$STRATEGY"
                break
            else
                echo "Invalid selection. Please try again."
            fi
        done
    fi
fi

# Check if the config file exists
CONFIG_PATH="$CONFIGS_DIRECTORY/$SELECTED_STRATEGY.json"
if [[ -f "$CONFIG_PATH" ]]; then
    echo "Using provided config: '$CONFIG_PATH'"
    export SELECTED_CONFIG="$CONFIG_PATH"
else
    echo "Error: Config '$CONFIG_PATH' does not exists."
    exit 1
fi

# Update the compose file with the selected strategy
if [[ -n "$SELECTED_STRATEGY" ]]; then
    echo "Using strategy: '$SELECTED_STRATEGY'"
    # Replace the strategy name after '--strategy ' in the compose file
    sed -i -E "s/(--strategy )[^ ]+/\1$SELECTED_STRATEGY/" "$COMPOSE_FILE"

    # Replace the config name after '--config ' in the compose file
    sed -i -E "s#(--config )[^ ]+#\1/$CONFIG_PATH#" "$COMPOSE_FILE"
else
    echo "No strategy selected. Exiting."
    exit 1
fi

# Build the custom image
docker compose -f ${COMPOSE_FILE} build

# Pull latest images
# docker compose -f ${COMPOSE_FILE} pull

# Start FreqTrade
docker compose -f ${COMPOSE_FILE} up -d  --remove-orphans

# See the logs
docker logs -f freqtrade