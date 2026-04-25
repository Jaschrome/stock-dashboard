from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import init_db, get_connection
from data import fetch_and_store, get_last_n_days, get_summary, get_volatility, compare_stocks, get_currency
import yfinance as yf
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── App Setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="📈 Stock Data Intelligence Dashboard",
    description="A mini financial data platform built for the JarNox internship assignment.",
    version="1.0.0"
)

# Initialize DB on startup
@app.on_event("startup")
def startup():
    init_db()

# Serve static files (dashboard HTML)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


# ── Root → Dashboard ─────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    return FileResponse(os.path.join(BASE_DIR, "static", "index.html"))


# ── 1. GET /companies ─────────────────────────────────────────────────────────
@app.get("/companies", tags=["Data"])
def list_companies():
    """Returns a list of all available companies in the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT symbol, name, sector FROM companies")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ── 1b. GET /search ───────────────────────────────────────────────────────────
@app.get("/search", tags=["Data"])
def search_stocks(q: str = Query(..., description="Company name or symbol e.g. Tesla or TSLA")):
    """
    Search for stocks by company name or symbol using yfinance.
    Returns up to 8 matching results.
    """
    try:
        results = yf.Search(q, max_results=8).quotes
        if not results:
            return []

        cleaned = []
        for r in results:
            symbol = r.get("symbol", "")
            name = r.get("longname") or r.get("shortname") or symbol
            type_ = r.get("quoteType", "")
            exchange = r.get("exchange", "")

            # Only return stocks and ETFs, skip futures/crypto/etc
            if type_ in ("EQUITY", "ETF") and symbol:
                cleaned.append({
                    "symbol": symbol,
                    "name": name,
                    "exchange": exchange,
                    "type": type_
                })

        return cleaned

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── 2. GET /data/{symbol} ─────────────────────────────────────────────────────
@app.get("/data/{symbol}", tags=["Data"])
def get_stock_data(symbol: str, days: int = Query(30, ge=1, le=365)):
    """
    Returns last N days of stock data for a symbol.
    Default is 30 days. Use ?days=90 for 90 days, etc.
    """
    symbol = symbol.upper()
    data = get_last_n_days(symbol, days)

    if not data:
        # Auto-fetch if not in DB
        success, msg = fetch_and_store(symbol)
        if not success:
            raise HTTPException(status_code=404, detail=msg)
        data = get_last_n_days(symbol, days)

    return {
        "symbol": symbol,
        "days": days,
        "count": len(data),
        "data": data
    }


# ── 3. GET /summary/{symbol} ──────────────────────────────────────────────────
@app.get("/summary/{symbol}", tags=["Data"])
def get_stock_summary(symbol: str):
    """
    Returns 52-week high, low, average close, yearly change,
    and annualized volatility for a symbol.
    """
    symbol = symbol.upper()
    summary = get_summary(symbol)

    if not summary or summary.get("week52_high") is None:
        success, msg = fetch_and_store(symbol)
        if not success:
            raise HTTPException(status_code=404, detail=msg)
        summary = get_summary(symbol)

    volatility = get_volatility(symbol)
    summary["volatility_score_pct"] = volatility
    summary["currency"] = get_currency(symbol)

    return {"symbol": symbol, **summary}


# ── 4. GET /compare ───────────────────────────────────────────────────────────
@app.get("/compare", tags=["Data"])
def compare(
    symbol1: str = Query(..., description="First stock symbol e.g. INFY"),
    symbol2: str = Query(..., description="Second stock symbol e.g. TCS.NS")
):
    """
    Compares two stocks' performance over 1 year.
    Returns % change, start/end prices for each.
    """
    s1 = symbol1.upper()
    s2 = symbol2.upper()

    # Ensure both are fetched
    for sym in [s1, s2]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM stock_data WHERE symbol = ?", (sym,))
        count = cursor.fetchone()["cnt"]
        conn.close()

        if count == 0:
            success, msg = fetch_and_store(sym)
            if not success:
                raise HTTPException(status_code=404, detail=f"Could not fetch {sym}: {msg}")

    result = compare_stocks(s1, s2)
    return {"comparison": result}


# ── 5. POST /fetch/{symbol} ───────────────────────────────────────────────────
@app.post("/fetch/{symbol}", tags=["Admin"])
def fetch_data(symbol: str):
    """
    Manually trigger data fetch for a symbol.
    Fetches 1 year of data from yfinance and stores it.
    """
    success, msg = fetch_and_store(symbol.upper())
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}


# ── 6. POST /fetch-all ────────────────────────────────────────────────────────
@app.post("/fetch-all", tags=["Admin"])
def fetch_all_companies(background_tasks: BackgroundTasks):
    """
    Fetches data for all companies in the database.
    Runs in the background.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT symbol FROM companies")
    symbols = [row["symbol"] for row in cursor.fetchall()]
    conn.close()

    results = []
    for sym in symbols:
        success, msg = fetch_and_store(sym)
        results.append({"symbol": sym, "status": "ok" if success else "error", "message": msg})

    return {"fetched": len(symbols), "results": results}


# ── 7. GET /gainers-losers ────────────────────────────────────────────────────
@app.get("/gainers-losers", tags=["Insights"])
def top_gainers_losers():
    """
    Returns top 3 gainers and losers based on yesterday's daily return.
    Custom insight endpoint.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT sd.symbol, sd.daily_return, sd.close, sd.date
        FROM stock_data sd
        WHERE sd.date = (
            SELECT MAX(date) FROM stock_data WHERE symbol = sd.symbol
        )
        ORDER BY sd.daily_return DESC
    """)

    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    gainers = rows[:3]
    losers = rows[-3:][::-1]

    return {
        "top_gainers": gainers,
        "top_losers": losers
    }
