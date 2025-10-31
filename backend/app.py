from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from binance.client import Client
from binance.exceptions import BinanceAPIException
import os
import uuid

from bot import TradingBot
from strategies import MovingAverageCrossover, BollingerBands
import database
from streaming import BinanceStreamer

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")
database.init_db()

# --- Binance API & Streaming ---
API_KEY = os.environ.get('BINANCE_API_KEY')
API_SECRET = os.environ.get('BINANCE_API_SECRET')

if not API_KEY or not API_SECRET:
    raise ValueError("BINANCE_API_KEY and BINANCE_API_SECRET must be set.")

client = None
streamer = None
try:
    client = Client(API_KEY, API_SECRET, tld='com', testnet=True)
    client.ping()
    streamer = BinanceStreamer(socketio)
    print("Successfully connected to Binance.")
except (BinanceAPIException, Exception) as e:
    print(f"Error connecting to Binance: {e}")

# --- Bot Management ---
active_bots = {}

# --- WebSocket Events ---
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('subscribe_klines')
def handle_subscribe_klines(data):
    symbol = data.get('symbol')
    interval = data.get('interval')
    if streamer and symbol and interval:
        streamer.subscribe_to_kline(symbol.upper(), interval)
        print(f"Client subscribed to {symbol}")

# --- API Routes ---
@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({'status': 'running', 'binance_connection': 'ok' if client else 'error'})

@app.route('/api/balance', methods=['GET'])
def get_balance():
    if client is None: return jsonify({"error": "Binance client not initialized."}), 503
    try:
        info = client.get_account()
        balances = [b for b in info.get('balances', []) if float(b['free']) > 0 or float(b['locked']) > 0]
        return jsonify(balances)
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    if client is None: return jsonify({"error": "Cannot start bot, Binance client not initialized."}), 503
    params = request.json
    symbol = params.get('symbol', 'BTCUSDT')
    interval = params.get('interval', Client.KLINE_INTERVAL_1MINUTE)
    strategy_name = params.get('strategy', 'ma_crossover')
    quantity = float(params.get('quantity', 0.001))

    if strategy_name == 'ma_crossover': strategy = MovingAverageCrossover(client, symbol, interval, quantity)
    elif strategy_name == 'bollinger_bands': strategy = BollingerBands(client, symbol, interval, quantity)
    else: return jsonify({"error": "Unknown strategy"}), 400

    bot_id = str(uuid.uuid4())
    bot_thread = TradingBot(strategy=strategy, socketio=socketio)
    bot_thread.start()
    active_bots[bot_id] = bot_thread
    return jsonify({"message": "Bot started", "bot_id": bot_id})

@app.route('/api/bot/stop/<bot_id>', methods=['POST'])
def stop_bot(bot_id):
    bot_thread = active_bots.get(bot_id)
    if not bot_thread: return jsonify({"error": "Bot not found"}), 404
    bot_thread.stop(); bot_thread.join(); del active_bots[bot_id]
    return jsonify({"message": "Bot stopped"})

@app.route('/api/bots/active', methods=['GET'])
def get_active_bots():
    return jsonify([{
        "bot_id": bot_id, "symbol": bot.strategy.symbol,
        "strategy": bot.strategy.__class__.__name__, "is_running": bot.is_alive()
    } for bot_id, bot in active_bots.items()])

@app.route('/api/trades', methods=['GET'])
def get_all_trades():
    try: return jsonify(database.get_trades())
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route('/api/klines', methods=['GET'])
def get_klines():
    symbol = request.args.get('symbol', 'BTCUSDT')
    interval = request.args.get('interval', Client.KLINE_INTERVAL_1MINUTE)
    if client is None: return jsonify({"error": "Binance client not initialized."}), 503
    try:
        klines = client.get_historical_klines(symbol, interval, "1 day ago UTC")
        formatted_klines = [{"time": int(k[0])/1000, "open": float(k[1]), "high": float(k[2]), "low": float(k[3]), "close": float(k[4])} for k in klines]
        return jsonify(formatted_klines)
    except Exception as e: return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
