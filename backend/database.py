import sqlite3
from datetime import datetime

DATABASE_FILE = "trading_bot.db"

def init_db():
    """Initializes the database and creates the trades table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME NOT NULL,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL, -- 'BUY' or 'SELL'
            price REAL NOT NULL,
            quantity REAL NOT NULL,
            strategy TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

def add_trade(symbol, side, price, quantity, strategy):
    """Adds a new trade record to the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO trades (timestamp, symbol, side, price, quantity, strategy)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (datetime.utcnow(), symbol, side, price, quantity, strategy))

    conn.commit()
    conn.close()

def get_trades():
    """Retrieves all trades from the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row # This allows accessing columns by name
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM trades ORDER BY timestamp DESC")
    trades = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return trades

if __name__ == '__main__':
    # Initialize the database when this script is run directly
    print("Initializing database...")
    init_db()
    print("Database initialized.")
