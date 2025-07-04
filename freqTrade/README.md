# FreqTrade Container Usage 
https://www.omgthecloud.com/freqtrade-plain-os-to-running-in-minutes/

## Start FreqTrade Container
```
./startFreqTrade.sh
```
or webserver mode:
```
./startFreqTrade.sh webserver
```

## Logs an terminal
See the Container logs:
```
docker logs -f freqtrade
```

Enter into the Freqtrade Container
```
docker exec -it freqtrade /bin/bash
```

## Stop and Remove FreqTrade Container
```
./stopFreqTrade.sh
```



# FreqTrade Trading Usage

## Download historical data

```
docker exec -it freqtrade freqtrade download-data --timeframe 5m --exchange binance
```

You can specify a pair like this:
```
docker exec -it freqtrade freqtrade download-data --timeframe 5m --exchange binance --pairs BTC/USDT
```


## Run the backtest

```
docker exec -it freqtrade freqtrade backtesting --strategy ScalpingStrategy
```

If you want more detailed output or a specific pair:

```
docker exec -it freqtrade freqtrade backtesting --strategy ScalpingStrategy --timeframe 5m --pairs BTC/USDT --export trades
```

## (Optional) Check the results



# 📲 Setting up Telegram Notifications for Freqtrade

This guide shows you how to set up Telegram with your Freqtrade bot to receive trade updates, errors, and interact with the bot via Telegram commands.

---

## ✅ Step 1: Create a Telegram Bot

1. Open Telegram and search for `@BotFather`.
2. Start a chat and send the command:
```
/newbot
```
3. Follow the instructions to set up your bot.
4. BotFather will give you a **Bot Token** — save it securely.

## ✅ Step 2: Get Your Telegram Chat ID

1. Open a private chat with your new bot and **send it a message** like `/start`.
2. Visit the following URL in your browser (replace `YOUR_BOT_TOKEN` with your actual token)
```
https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
# Example
https://api.telegram.org/bot123456789:ABCdefGHIjklMNOpqrSTUvwxYZ/getUpdates

```

3. Look for something like this in the JSON response:

```json
"chat": {
  "id": 123456789,
  "type": "private",
  "username": "yourusername"
}
Copy the ```id``` — this is your Telegram Chat ID.

