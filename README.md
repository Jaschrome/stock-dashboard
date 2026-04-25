#  Stock Data Intelligence Dashboard

A mini financial data platform built as part of the **JarNox Software Internship Assignment**.

---

##  Features

- ✅ Fetches **real stock data** using `yfinance` (NSE, BSE, US markets)
- ✅ Stores and manages data in **SQLite** (zero setup)
- ✅ **FastAPI** backend with auto-generated Swagger docs
- ✅ Computed metrics: Daily Return, 7-day Moving Average, 52-week High/Low
- ✅ Custom metric: **Annualized Volatility Score**
- ✅ Interactive **dashboard** with Chart.js
- ✅ Top Gainers / Losers insight panel
- ✅ Stock comparison tool

---

##  Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.10+ |
| Backend | FastAPI |
| Database | SQLite |
| Data | yfinance, Pandas |
| Frontend | HTML + Chart.js |

---

##  Setup Instructions

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/stock-dashboard.git
cd stock-dashboard
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the server
```bash
uvicorn main:app --reload
```

### 5. Open the dashboard
```
http://localhost:8000
```

### 6. View API docs (Swagger)
```
http://localhost:8000/docs
```

---

##  API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/companies` | GET | List all tracked companies |
| `/data/{symbol}?days=30` | GET | Last N days of stock data |
| `/summary/{symbol}` | GET | 52-week high/low, avg close, volatility |
| `/compare?symbol1=INFY&symbol2=TCS.NS` | GET | Compare two stocks |
| `/gainers-losers` | GET | Top 3 gainers and losers |
| `/fetch/{symbol}` | POST | Manually trigger data fetch |
| `/fetch-all` | POST | Fetch data for all companies |

---

##  Calculated Metrics

| Metric | Formula |
|--------|---------|
| Daily Return | `(Close - Open) / Open` |
| 7-day Moving Average | Rolling 7-day mean of Close price |
| 52-week High / Low | Max High / Min Low over 1 year |
| Volatility Score | `std(daily_returns) × √252 × 100` (annualized) |

---

##  Custom Insight: Volatility Score

The **Volatility Score** is a custom metric that measures how much a stock's price fluctuates over time.

- Calculated as: `σ × √252 × 100` where σ is the standard deviation of daily returns
- Higher score = riskier stock
- Lower score = more stable stock

This is a standard finance metric used by analysts to assess investment risk.

---

##  Project Structure

```
stock-dashboard/
├── main.py          # FastAPI app — all API endpoints
├── data.py          # Data fetching, cleaning, and storage logic
├── database.py      # SQLite setup and connection helpers
├── static/
│   └── index.html   # Frontend dashboard
├── requirements.txt
└── README.md
```

---

##  Design Decisions

- **SQLite over PostgreSQL**: Chosen for zero-setup simplicity and portability. Can be swapped to PostgreSQL easily via SQLAlchemy.
- **yfinance**: Provides free, reliable access to global stock data with no API key.
- **FastAPI**: Auto-generates Swagger docs, has excellent type checking, and is production-ready.
- **No heavy frontend framework**: Pure HTML + Chart.js keeps the setup simple and fast.

---

##  Author

- **Name** : Jairaj Singh Jabbal
- **Email** : jaschrome040@gmail.com
- **Github** : www.github.com/Jaschrome

Built with ❤️ for the JarNox Internship Assignment.
