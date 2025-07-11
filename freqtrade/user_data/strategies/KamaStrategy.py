# https://jesse.trade/strategies/kama-trendfollowing
import datetime
from freqtrade.strategy import IStrategy, IntParameter, DecimalParameter
from pandas import DataFrame
import ta

class KamaStrategy(IStrategy):
    """
    KamaStrategy implements a Freqtrade trading strategy based on the Kaufman's Adaptive Moving Average (KAMA),
    ADX, Choppiness Index, Bollinger Band width, and ATR indicators.

    Attributes:
        INTERFACE_VERSION (int): Freqtrade strategy interface version.
        minimal_roi (dict): Minimal return on investment configuration.
        stoploss (float): Stoploss value.
        trailing_stop (bool): Enable trailing stop.
        trailing_stop_positive (float): Trailing stop positive threshold.
        trailing_stop_positive_offset (float): Trailing stop positive offset.
        trailing_only_offset_is_reached (bool): Only trail after offset is reached.
        use_custom_stoploss (bool): Use custom stoploss logic.
        use_exit_signal (bool): Use sell signal logic.
        exit_profit_only (bool): Only sell if profitable.
        ignore_buying_expired_candle_after (int): Ignore buying after N candles.
        kama_window (IntParameter): Window size for KAMA calculation.
        adx_threshold (IntParameter): ADX threshold for trend strength.
        chop_threshold (IntParameter): Choppiness Index threshold for trendiness.
        bb_width_threshold (DecimalParameter): Bollinger Band width threshold.

    Methods:
        populate_indicators(df, metadata):
            Adds KAMA, ADX, Choppiness Index, Bollinger Band width, ATR, and long-term KAMA indicators to the dataframe.

        populate_buy_trend(df, metadata):
            Sets buy signal when close is above KAMA and long-term KAMA, ADX and trendiness thresholds are met,
            and Bollinger Band width is below threshold.

        populate_sell_trend(df, metadata):
            Sets sell signal when close is below KAMA and long-term KAMA, ADX and trendiness thresholds are met,
            and Bollinger Band width is below threshold.

        custom_exit(pair, trade, current_time, current_rate, current_profit, **kwargs):
            (Optional) Example placeholder for ATR-based custom sell logic.
    """
    INTERFACE_VERSION = 3
    # Enable shorting
    can_short = True
    minimal_roi = {"0": 0.03}
    stoploss = -0.30
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.03
    trailing_only_offset_is_reached = True

    use_custom_stoploss = False
    use_exit_signal = True
    exit_profit_only = False
    ignore_buying_expired_candle_after = 0

    # timeframe = '30m'
    # For multi-timeframe, you need to set this and implement populate_indicators accordingly
    # informative_timeframes = {'4h': '4h'}

    kama_window = IntParameter(10, 50, default=30, space='buy')
    adx_threshold = IntParameter(40, 60, default=50, space='buy')
    chop_threshold = IntParameter(40, 60, default=50, space='buy')
    bb_width_threshold = DecimalParameter(0.01, 0.07, default=0.07, space='buy')

    def populate_indicators(self, df: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds all required technical indicators to the dataframe for use in buy/sell logic.

        Indicators added:
            - KAMA (Kaufman's Adaptive Moving Average)
            - ADX (Average Directional Index)
            - Choppiness Index (custom implementation)
            - Bollinger Band width
            - ATR (Average True Range)
            - Long-term KAMA (approximated by rolling mean of KAMA)

        Args:
            df (DataFrame): The input DataFrame with OHLCV data.
            metadata (dict): Additional information (not used here).

        Returns:
            DataFrame: The DataFrame with new indicator columns added.
        """
        # Calculate KAMA (Kaufman's Adaptive Moving Average)
        df['kama'] = ta.momentum.KAMAIndicator(df['close'], window=int(self.kama_window.value)).kama()
        # Calculate ADX (Average Directional Index)
        df['adx'] = ta.trend.ADXIndicator(df['high'], df['low'], df['close'], window=14).adx()
        # Choppiness Index is not in ta, so we implement it
        def choppiness(high, low, close, window=14):
            # Calculate True Range (TR)
            tr = ta.volatility.AverageTrueRange(high, low, close, window=1).average_true_range()
            # Highest high and lowest low over the window
            high_max = high.rolling(window).max()
            low_min = low.rolling(window).min()
            # Sum of TR over the window
            sum_tr = tr.rolling(window).sum()
            # Choppiness Index formula
            chop = 100 * np.log10(sum_tr / (high_max - low_min)) / np.log10(window)
            return chop
        import numpy as np
        # Calculate Choppiness Index
        df['chop'] = choppiness(df['high'], df['low'], df['close'], window=14)
        # Calculate Bollinger Band width
        bb = ta.volatility.BollingerBands(df['close'], window=20, window_dev=2)
        df['bb_width'] = (bb.bollinger_hband() - bb.bollinger_lband()) / df['close']
        # Calculate ATR (Average True Range)
        df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
        # Calculate long-term KAMA as a rolling mean of KAMA (approximate higher timeframe trend)
        df['long_term_kama'] = df['kama'].rolling(8).mean()  # Approximate 4h trend

        # For tracking last trade index, Freqtrade doesn't support this natively in the dataframe
        # You can use custom logic in custom_buy/sell if needed

        return df

    def populate_entry_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        """
        Populates the 'enter_long' signal in the DataFrame based on custom trading conditions for Long positions.

        This function evaluates a set of technical indicators and assigns a value of 1 to the 'enter_long' column
        for rows where all the following conditions are met:
            - The closing price is above the Kaufman's Adaptive Moving Average (KAMA).
            - The Average Directional Index (ADX) is greater than a specified threshold.
            - The closing price is above a long-term KAMA.
            - The Choppiness Index (CHOP) is below a specified threshold.
            - The Bollinger Band width is below a specified threshold.

        Note:
            - There is no direct implementation for ensuring at least 10 candles have passed since the last trade,
              as this is not natively supported in Freqtrade's strategy framework.

        Args:
            df (DataFrame): The input DataFrame containing price and indicator data.
            metadata (dict): Additional information, not used in this function.

        Returns:
            DataFrame: The DataFrame with the 'enter_long' column updated according to the strategy's buy conditions.
        """
        df.loc[
            (
                (df['close'] > df['kama']) &
                (df['adx'] > self.adx_threshold.value) &
                (df['close'] > df['long_term_kama']) &
                (df['chop'] < self.chop_threshold.value) &
                (df['bb_width'] < float(self.bb_width_threshold.value))
                # No direct way to check "at least 10 candles since last trade" in Freqtrade
            ),
            'enter_long'
        ] = 1
        
        return df

    def populate_short_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        """
        Populates the 'enter_short' signal in the DataFrame based on custom trading conditions for Short positions.

        This function evaluates a set of technical indicators and assigns a value of 1 to the 'enter_short' column
        for rows where all the following conditions are met:
            - The closing price is below the Kaufman's Adaptive Moving Average (KAMA).
            - The Average Directional Index (ADX) is greater than a specified threshold.
            - The closing price is below a long-term KAMA.
            - The Choppiness Index (CHOP) is below a specified threshold.
            - The Bollinger Band width is below a specified threshold.

        Args:
            df (DataFrame): The input DataFrame containing price and indicator data.
            metadata (dict): Additional information, not used in this function.

        Returns:
            DataFrame: The DataFrame with the 'enter_short' column updated according to the strategy's short conditions.
        """
        df.loc[
            (
                (df['close'] < df['kama']) &
                (df['adx'] > self.adx_threshold.value) &
                (df['close'] < df['long_term_kama']) &
                (df['chop'] < self.chop_threshold.value) &
                (df['bb_width'] < float(self.bb_width_threshold.value))
            ),
            'enter_short'
        ] = 1
        return df

    def populate_exit_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        """
        Populates the 'exit_long' and 'exit_short' signals in the DataFrame based on multiple technical indicators.

        This function applies a set of conditions to the input DataFrame `df` to determine when an exit signal should be generated.
        The exit signal is set to 1 for rows where all of the following conditions are met:
            - The closing price is below the KAMA (Kaufman's Adaptive Moving Average).
            - The ADX (Average Directional Index) is above a specified threshold, indicating a strong trend.
            - The closing price is below the long-term KAMA, suggesting a bearish trend.
            - The Choppiness Index is below a specified threshold, indicating the market is trending rather than ranging.
            - The Bollinger Band width is below a specified threshold, indicating low volatility.

        Args:
            df (DataFrame): The input DataFrame containing price and indicator columns.
            metadata (dict): Additional metadata (not used in this function, but required by the interface).

        Returns:
            DataFrame: The input DataFrame with the 'exit_long' and 'exit_short' columns updated where the exit conditions are met.
        """
        # Exit long positions
        df.loc[
            (
                (df['close'] < df['kama']) &
                (df['adx'] > self.adx_threshold.value) &
                (df['close'] < df['long_term_kama']) &
                (df['chop'] < self.chop_threshold.value) &
                (df['bb_width'] < float(self.bb_width_threshold.value))
            ),
            'exit_long'
        ] = 1
        
        # Exit short positions (opposite conditions)
        df.loc[
            (
                (df['close'] > df['kama']) &
                (df['adx'] > self.adx_threshold.value) &
                (df['close'] > df['long_term_kama']) &
                (df['chop'] < self.chop_threshold.value) &
                (df['bb_width'] < float(self.bb_width_threshold.value))
            ),
            'exit_short'
        ] = 1
        
        return df

    # ATR-based stoploss/takeprofit is not natively supported in Freqtrade, but you can use custom_stoploss
    # or custom_exit for advanced logic if needed.

    def custom_exit(self, pair: str, trade, current_time, current_rate, current_profit, **kwargs):
        # Example: ATR-based take profit/stoploss (not exactly like Jesse, but similar)
        # You can access indicators via self.dp.get_analyzed_dataframe(pair, self.timeframe)
        df_tuple = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if df_tuple is None or trade is None:
            return None

        df = df_tuple[0] if isinstance(df_tuple, tuple) else df_tuple
        if df is None or len(df) == 0:
            return None

        # Find the current candle
        last_candle = df.iloc[-1]
        atr = last_candle.get('atr', None)
        if atr is None:
            return None

        # Example logic: Sell if price drops below entry - 2*ATR (trailing stop)
        if current_rate < (trade.open_rate - 2 * atr):
            return 'atr_stoploss'

        # Example logic: Take profit if price exceeds entry + 3*ATR
        if current_rate > (trade.open_rate + 3 * atr):
            return 'atr_takeprofit'
        return None
