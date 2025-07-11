# user_data/strategies/ScalpingStrategy.py
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta

class ScalpingStrategy(IStrategy):
    # Strategy interface version - required for modern FreqTrade
    INTERFACE_VERSION = 3
    
    timeframe = '5m'  # scalping strategies usually use small timeframes
    
    # Can this strategy go short?
    can_short: bool = False

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['rsi'] < 30),
            'enter_long'] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (dataframe['rsi'] > 70),
            'exit_long'] = 1
        return dataframe
