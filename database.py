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

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_meta (
            symbol TEXT PRIMARY KEY,
            currency TEXT DEFAULT 'USD',
            name TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized.")
