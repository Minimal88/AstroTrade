# user_data/strategies/ScalpingStrategy.py
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class ScalpingStrategy(IStrategy):
    timeframe = '5m'  # scalping strategies usually use small timeframes

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['rsi'] < 30),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['rsi'] > 70),
            'sell'] = 1
        return dataframe
