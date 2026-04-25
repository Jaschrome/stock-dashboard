import sqlite3
import os

DB_PATH = "stocks.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            sector TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            daily_return REAL,
            ma_7 REAL,
            UNIQUE(symbol, date)
        )
    """)

    # Seed some default companies (popular Indian + US stocks)
    companies = [
        ("INFY", "Infosys", "IT"),
        ("TCS.NS", "Tata Consultancy Services", "IT"),
        ("RELIANCE.NS", "Reliance Industries", "Energy"),
        ("HDFCBANK.NS", "HDFC Bank", "Finance"),
        ("AAPL", "Apple Inc.", "Technology"),
        ("GOOGL", "Alphabet Inc.", "Technology"),
        ("MSFT", "Microsoft", "Technology"),
        ("TSLA", "Tesla", "Automotive"),
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO companies (symbol, name, sector) VALUES (?, ?, ?)",
        companies
    )

    conn.commit()
    conn.close()
    print("✅ Database initialized.")
