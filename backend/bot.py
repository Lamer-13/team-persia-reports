import time
from threading import Thread, Event
import database

class TradingBot(Thread):
    """
    A generic trading bot that runs a given strategy in a loop.
    """
    def __init__(self, strategy):
        super().__init__()
        self.strategy = strategy
        self.running = False
        self._stop_event = Event()

    def run(self):
        """Main bot loop."""
        if not self.strategy.client:
            print(f"Bot for {self.strategy.symbol} cannot run without a valid Binance client.")
            return

        self.running = True
        print(f"Bot started for {self.strategy.symbol} with strategy: {self.strategy.__class__.__name__}")

        while not self._stop_event.is_set():
            try:
                df = self.strategy.get_historical_data()
                signal = self.strategy.analyze(df)

                if signal != 'HOLD':
                    print(f"[{time.ctime()}] {signal} signal for {self.strategy.symbol}")
                    order = self.strategy.client.create_test_order(
                        symbol=self.strategy.symbol,
                        side=signal,
                        type='MARKET',
                        quantity=self.strategy.quantity
                    )

                    # Log the trade to the database
                    # For a real MARKET order, the price is not specified, so we'd get it from the order response.
                    # create_test_order returns an empty dict, so we'll use the latest close price for logging.
                    price = df.iloc[-1]['close']
                    database.add_trade(
                        symbol=self.strategy.symbol,
                        side=signal,
                        price=price,
                        quantity=self.strategy.quantity,
                        strategy=self.strategy.__class__.__name__
                    )
                    print(f"Logged {signal} trade for {self.strategy.symbol} at ~{price}")

            except Exception as e:
                print(f"An error occurred in bot loop for {self.strategy.symbol}: {e}")

            time.sleep(60)

        print(f"Bot for {self.strategy.symbol} has been stopped.")
        self.running = False

    def stop(self):
        """Stops the bot loop."""
        self._stop_event.set()
