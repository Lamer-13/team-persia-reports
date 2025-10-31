from flask import Flask, jsonify, request
from flask_cors import CORS
from binance.client import Client
from binance.exceptions import BinanceAPIException
import os
import uuid

from bot import TradingBot
from strategies import MovingAverageCrossover, BollingerBands
import database

app = Flask(__name__)
CORS(app)
database.init_db() # Ensure DB is initialized on startup

# --- Binance API Configuration ---
API_KEY = os.environ.get('BINANCE_API_KEY')
API_SECRET = os.environ.get('BINANCE_API_SECRET')

if not API_KEY or not API_SECRET:
    raise ValueError("BINANCE_API_KEY and BINANCE_API_SECRET must be set.")

client = None
try:
    client = Client(API_KEY, API_SECRET, tld='com', testnet=True)
    client.ping()
    print("Successfully connected to Binance Testnet.")
except BinanceAPIException as e:
    print(f"Error connecting to Binance: {e}")

# --- Bot Management ---
active_bots = {}

# --- API Routes ---
@app.route('/api/status', methods=['GET'])
def get_status():
    return jsonify({'status': 'running', 'binance_connection': 'ok' if client else 'error'})

@app.route('/api/balance', methods=['GET'])
def get_balance():
    if client is None:
        return jsonify({"error": "Binance client not initialized."}), 503
    try:
        info = client.get_account()
        balances = [b for b in info.get('balances', []) if float(b['free']) > 0 or float(b['locked']) > 0]
        return jsonify(balances)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/bot/start', methods=['POST'])
def start_bot():
    if client is None:
        return jsonify({"error": "Cannot start bot, Binance client not initialized."}), 503

    params = request.json
    symbol = params.get('symbol', 'BTCUSDT')
    interval = params.get('interval', Client.KLINE_INTERVAL_1MINUTE)
    strategy_name = params.get('strategy', 'ma_crossover')
    quantity = float(params.get('quantity', 0.001))

    if strategy_name == 'ma_crossover':
        strategy = MovingAverageCrossover(client, symbol, interval, quantity)
    elif strategy_name == 'bollinger_bands':
        strategy = BollingerBands(client, symbol, interval, quantity)
    else:
        return jsonify({"error": "Unknown strategy"}), 400

    bot_id = str(uuid.uuid4())
    bot_thread = TradingBot(strategy=strategy)
    bot_thread.start()
    active_bots[bot_id] = bot_thread

    print(f"Started bot {bot_id} for {symbol} with {strategy_name}")
    return jsonify({"message": "Bot started", "bot_id": bot_id})

@app.route('/api/bot/stop/<bot_id>', methods=['POST'])
def stop_bot(bot_id):
    bot_thread = active_bots.get(bot_id)
    if not bot_thread:
        return jsonify({"error": "Bot not found"}), 404

    bot_thread.stop()
    bot_thread.join()
    del active_bots[bot_id]

    print(f"Stopped bot {bot_id}")
    return jsonify({"message": "Bot stopped"})

@app.route('/api/bots/active', methods=['GET'])
def get_active_bots():
    bot_list = []
    for bot_id, bot_thread in active_bots.items():
        bot_list.append({
            "bot_id": bot_id,
            "symbol": bot_thread.strategy.symbol,
            "strategy": bot_thread.strategy.__class__.__name__,
            "is_running": bot_thread.is_alive()
        })
    return jsonify(bot_list)

@app.route('/api/trades', methods=['GET'])
def get_all_trades():
    try:
        trades = database.get_trades()
        return jsonify(trades)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/klines', methods=['GET'])
def get_klines():
    symbol = request.args.get('symbol', 'BTCUSDT')
    interval = request.args.get('interval', Client.KLINE_INTERVAL_1MINUTE)

    if client is None:
        return jsonify({"error": "Binance client not initialized."}), 503

    try:
        klines = client.get_historical_klines(symbol, interval, "1 day ago UTC")
        formatted_klines = [
            {"time": int(k[0])/1000, "open": float(k[1]), "high": float(k[2]), "low": float(k[3]), "close": float(k[4])}
            for k in klines
        ]
        return jsonify(formatted_klines)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
