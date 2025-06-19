import datetime
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
import ta

class KamaStrategy(IStrategy):
    INTERFACE_VERSION = 3

    # ROI, stoploss, trailing
    minimal_roi = {"0": 0.03}
    stoploss = -0.20
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.03
    trailing_only_offset_is_reached = True

    # Enable hyperopt
    use_custom_stoploss = False
    use_sell_signal = True
    sell_profit_only = False
    ignore_buying_expired_candle_after = 0

    # Timeframe
    timeframe = '1h'

    # Optimal parameters (for tuning)
    kama_window = IntParameter(10, 50, default=30, space='buy')
    ema_fast = IntParameter(5, 20, default=10, space='buy')
    ema_slow = IntParameter(20, 100, default=50, space='buy')
    adx_threshold = IntParameter(15, 50, default=25, space='buy')

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        # Indicators
        df['kama'] = ta.trend.kaufman_indicator(df['close'], window=int(self.kama_window.value))
        df['ema_fast'] = ta.trend.ema_indicator(df['close'], window=int(self.ema_fast.value))
        df['ema_slow'] = ta.trend.ema_indicator(df['close'], window=int(self.ema_slow.value))
        df['adx'] = ta.trend.adx(df['high'], df['low'], df['close'], window=14)

        return df

    def populate_buy_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        df.loc[
            (
                (df['ema_fast'] > df['ema_slow']) &
                (df['close'] > df['kama']) &
                (df['adx'] > self.adx_threshold.value)
            ),
            'buy'
        ] = 1
        return df

    def populate_sell_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        df.loc[
            (
                (df['close'] < df['kama']) |
                (df['adx'] < self.adx_threshold.value)
            ),
            'sell'
        ] = 1
        return df

    # Enable shorting
    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                            time_in_force: str, current_time: "datetime", entry_tag: str, **kwargs) -> bool:
        return True

    def confirm_trade_exit(self, pair: str, trade, order_type: str, amount: float, rate: float,
                           time_in_force: str, current_time: "datetime", **kwargs) -> bool:
        return True

    def custom_sell(self, pair: str, trade, current_time, current_rate, current_profit, **kwargs):
        return None
