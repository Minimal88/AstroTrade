# docker compose run --rm freqtrade download-data --timeframe 30m
# docker compose run --rm freqtrade backtesting --strategy KamaStrategy --timeframe 30m



# docker compose run --rm freqtrade download-data --exchange ftx -t 30m --timerange 20240606-
# docker compose run --rm freqtrade backtesting --strategy KamaStrategy --timeframe 30m



# Commands for Binance KamaStrategy backtesting:
# Not good 30m
docker compose run --rm freqtrade download-data --exchange binance -t 30m --timerange 20240606-
docker compose run --rm freqtrade backtesting --strategy KamaStrategy -i 30m --datadir user_data/data/binance --export trades --stake-amount 1000 --timerange 20240606-

# GOOD 15m
docker compose run --rm freqtrade download-data --exchange binance -t 15m --timerange 20240606-
docker compose run --rm freqtrade backtesting --strategy KamaStrategy -i 15m --datadir user_data/data/binance --export trades --stake-amount 1000 --timerange 20240606-

# Not good 5m
docker compose run --rm freqtrade download-data --exchange binance -t 5m --timerange 20240606-
docker compose run --rm freqtrade backtesting --strategy KamaStrategy -i 5m --datadir user_data/data/binance --export trades --stake-amount 1000 --timerange 20240606-


