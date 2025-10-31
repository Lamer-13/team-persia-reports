from abc import ABC, abstractmethod
import pandas as pd

class Strategy(ABC):
    """
    Abstract base class for all trading strategies.
    """
    def __init__(self, client, symbol, interval, quantity):
        self.client = client
        self.symbol = symbol
        self.interval = interval
        self.quantity = quantity

    @abstractmethod
    def analyze(self, df: pd.DataFrame):
        """
        Analyzes historical data and decides whether to buy, sell, or hold.
        Returns 'BUY', 'SELL', or 'HOLD'.
        """
        pass

    def get_historical_data(self, limit=100):
        """
        Fetches historical kline data from Binance.
        """
        klines = self.client.get_historical_klines(self.symbol, self.interval, f"{limit} hours ago UTC")
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
            'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
            'taker_buy_quote_asset_volume', 'ignore'
        ])
        df['close'] = pd.to_numeric(df['close'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df

class MovingAverageCrossover(Strategy):
    """
    A strategy based on the crossover of two moving averages.
    """
    def __init__(self, client, symbol, interval, quantity, short_window=10, long_window=30):
        super().__init__(client, symbol, interval, quantity)
        self.short_window = short_window
        self.long_window = long_window

    def analyze(self, df: pd.DataFrame):
        df['short_ma'] = df['close'].rolling(window=self.short_window).mean()
        df['long_ma'] = df['close'].rolling(window=self.long_window).mean()

        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        if prev_row['short_ma'] < prev_row['long_ma'] and last_row['short_ma'] > last_row['long_ma']:
            return 'BUY'
        elif prev_row['short_ma'] > prev_row['long_ma'] and last_row['short_ma'] < last_row['long_ma']:
            return 'SELL'
        else:
            return 'HOLD'

class BollingerBands(Strategy):
    """
    A strategy based on Bollinger Bands.
    """
    def __init__(self, client, symbol, interval, quantity, window=20, std_dev=2):
        super().__init__(client, symbol, interval, quantity)
        self.window = window
        self.std_dev = std_dev

    def analyze(self, df: pd.DataFrame):
        # Calculate Bollinger Bands
        df['sma'] = df['close'].rolling(window=self.window).mean()
        df['std'] = df['close'].rolling(window=self.window).std()
        df['upper_band'] = df['sma'] + (df['std'] * self.std_dev)
        df['lower_band'] = df['sma'] - (df['std'] * self.std_dev)

        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        # Buy signal: price crosses lower band from below
        if prev_row['close'] < prev_row['lower_band'] and last_row['close'] > last_row['lower_band']:
            return 'BUY'
        # Sell signal: price crosses upper band from above
        elif prev_row['close'] > prev_row['upper_band'] and last_row['close'] < last_row['upper_band']:
            return 'SELL'
        else:
            return 'HOLD'
