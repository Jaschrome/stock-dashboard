import yfinance as yf
import pandas as pd
from database import get_connection
from datetime import datetime, timedelta


def fetch_and_store(symbol: str):
    """
    Fetches 1 year of stock data for a symbol using yfinance,
    computes metrics, and stores it in SQLite.
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1y")

        if df.empty:
            return False, f"No data found for symbol: {symbol}"

        df.reset_index(inplace=True)

        # Normalize column names
        df.rename(columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Volume": "volume"
        }, inplace=True)

        # Convert date to string
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

        # Drop rows with missing close prices
        df.dropna(subset=["close"], inplace=True)

        # ── Calculated Metrics ──────────────────────────────────────────
        # Daily Return = (Close - Open) / Open
        df["daily_return"] = ((df["close"] - df["open"]) / df["open"]).round(6)

        # 7-day Moving Average of Close
        df["ma_7"] = df["close"].rolling(window=7).mean().round(4)

        # ── Store in DB ─────────────────────────────────────────────────
        conn = get_connection()
        cursor = conn.cursor()

        rows = df[["date", "open", "high", "low", "close", "volume", "daily_return", "ma_7"]].values.tolist()

        cursor.executemany("""
            INSERT OR REPLACE INTO stock_data
            (symbol, date, open, high, low, close, volume, daily_return, ma_7)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [(symbol, *row) for row in rows])

        conn.commit()
        conn.close()

        return True, f"Fetched and stored {len(df)} rows for {symbol}"

    except Exception as e:
        return False, str(e)


def get_last_n_days(symbol: str, days: int = 30):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT date, open, high, low, close, volume, daily_return, ma_7
        FROM stock_data
        WHERE symbol = ?
        ORDER BY date DESC
        LIMIT ?
    """, (symbol, days))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows][::-1]  # Return in chronological order


def get_summary(symbol: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            MAX(high)  AS week52_high,
            MIN(low)   AS week52_low,
            ROUND(AVG(close), 2) AS avg_close,
            ROUND(AVG(daily_return) * 100, 4) AS avg_daily_return_pct,
            ROUND(
                (
                    SELECT close FROM stock_data WHERE symbol = ? ORDER BY date DESC LIMIT 1
                ) -
                (
                    SELECT close FROM stock_data WHERE symbol = ? ORDER BY date ASC LIMIT 1
                ), 2
            ) AS yearly_change
        FROM stock_data
        WHERE symbol = ?
    """, (symbol, symbol, symbol))

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return {}


def get_volatility(symbol: str):
    """Custom metric: annualized volatility score based on std dev of daily returns."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT daily_return FROM stock_data WHERE symbol = ?
    """, (symbol,))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None

    returns = [r["daily_return"] for r in rows if r["daily_return"] is not None]
    series = pd.Series(returns)
    # Annualized volatility = daily std dev * sqrt(252 trading days)
    volatility = round(series.std() * (252 ** 0.5) * 100, 2)
    return volatility


def compare_stocks(symbol1: str, symbol2: str):
    """Compare two stocks: return % change over available period."""
    result = {}

    for symbol in [symbol1, symbol2]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT close, date FROM stock_data WHERE symbol = ?
            ORDER BY date ASC LIMIT 1
        """, (symbol,))
        first = cursor.fetchone()

        cursor.execute("""
            SELECT close, date FROM stock_data WHERE symbol = ?
            ORDER BY date DESC LIMIT 1
        """, (symbol,))
        last = cursor.fetchone()
        conn.close()

        if first and last:
            pct_change = round(((last["close"] - first["close"]) / first["close"]) * 100, 2)
            result[symbol] = {
                "start_date": first["date"],
                "end_date": last["date"],
                "start_price": round(first["close"], 2),
                "end_price": round(last["close"], 2),
                "pct_change": pct_change
            }

    return result
