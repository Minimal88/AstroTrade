# Pulls the freqTrade docker image
# mkdir -p ft
# cd ft
# curl https://raw.githubusercontent.com/freqtrade/freqtrade/stable/docker-compose.yml -o docker-compose.yml
docker-compose pull

# Creates the file and folder structure
# docker-compose run --rm freqtrade create-userdir --userdir user_data

# Setup the FreqTrade config
# docker-compose run --rm freqtrade new-config --config user_data/config.json

# On your docker-compose.yml remove "127.0.0.1" to match:
# ports:
#     - "8080:8080"

# Start FreqTrade
docker-compose up -d