import time
from threading import Thread, Event
import database

class TradingBot(Thread):
    def __init__(self, strategy, socketio):
        super().__init__()
        self.strategy = strategy
        self.socketio = socketio
        self.running = False
        self._stop_event = Event()

    def run(self):
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

                    price = df.iloc[-1]['close']
                    database.add_trade(
                        symbol=self.strategy.symbol,
                        side=signal,
                        price=price,
                        quantity=self.strategy.quantity,
                        strategy=self.strategy.__class__.__name__
                    )

                    # Emit trade event via WebSocket
                    trade_data = {
                        'symbol': self.strategy.symbol,
                        'side': signal,
                        'price': price,
                        'quantity': self.strategy.quantity,
                        'time': time.time()
                    }
                    self.socketio.emit('trade_executed', trade_data)
                    print(f"Logged and emitted {signal} trade for {self.strategy.symbol}")

            except Exception as e:
                print(f"An error occurred in bot loop for {self.strategy.symbol}: {e}")

            time.sleep(60)

        print(f"Bot for {self.strategy.symbol} has been stopped.")
        self.running = False

    def stop(self):
        self._stop_event.set()
