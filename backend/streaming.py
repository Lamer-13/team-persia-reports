from binance import ThreadedWebsocketManager
import asyncio

class BinanceStreamer:
    def __init__(self, socketio):
        self.socketio = socketio
        self.twm = ThreadedWebsocketManager()
        self.twm.start()

    def handle_socket_message(self, msg):
        """
        This function is called when a message is received from the Binance websocket.
        It emits the message to all connected clients.
        """
        # We are interested in kline data
        if msg['e'] == 'kline':
            kline = msg['k']
            formatted_kline = {
                "time": int(kline['t']) / 1000,
                "open": float(kline['o']),
                "high": float(kline['h']),
                "low": float(kline['l']),
                "close": float(kline['c'])
            }
            # Emit to a room that matches the symbol
            self.socketio.emit(kline['s'], formatted_kline)

    def subscribe_to_kline(self, symbol, interval):
        """
        Subscribes to kline data for a given symbol and interval.
        """
        stream_name = self.twm.start_kline_socket(
            callback=self.handle_socket_message,
            symbol=symbol,
            interval=interval
        )
        print(f"Subscribed to {symbol} kline stream: {stream_name}")

    def stop(self):
        self.twm.stop()

# This part is just for testing and won't be used in the main app
if __name__ == '__main__':
    # A mock socketio for testing
    class MockSocketIO:
        def emit(self, event, data):
            print(f"Emitting event '{event}': {data}")

    async def main():
        streamer = BinanceStreamer(MockSocketIO())
        streamer.subscribe_to_kline('BTCUSDT', '1m')
        # Keep it running for a while
        await asyncio.sleep(30)
        streamer.stop()

    asyncio.run(main())
