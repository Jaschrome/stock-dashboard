Stock Data Intelligence Dashboard

A mini financial data platform built as part of the JarNox Software Internship Assignment.


Features

Real-time stock data via yfinance (NSE, BSE, US markets)
Local SQLite database — data stored after first fetch, instant on reload
FastAPI backend with auto-generated Swagger docs
Computed metrics: Daily Return, 7-Day Moving Average, 52-Week High/Low
Custom metric: Annualized Volatility Score
Interactive dashboard with Chart.js
Top Gainers & Losers panel
Stock comparison tool


Tech Stack
LayerTechnologyLanguagePython 3.10+BackendFastAPIDatabaseSQLiteData Sourceyfinance, PandasFrontendHTML + Chart.js

Setup & Installation
1. Clone the repository
bashgit clone https://github.com/YOUR_USERNAME/stock-dashboard.git
cd stock-dashboard
2. Install dependencies
bashpip install fastapi uvicorn yfinance pandas numpy requests python-multipart
3. Run the server
bashuvicorn main:app --reload
4. Open in browser
PageURL Dashboardhttp://localhost:8000 API Docs (Swagger)http://localhost:8000/docs

API Endpoints
EndpointMethodDescription/companiesGETList all tracked companies/data/{symbol}?days=30GETLast N days of OHLCV stock data/summary/{symbol}GET52W high/low, avg close, volatility/compare?symbol1=X&symbol2=YGETCompare two stocks side by side/gainers-losersGETTop 3 gainers and losers/fetch/{symbol}POSTManually trigger data fetch/fetch-allPOSTFetch data for all companies

Calculated Metrics
MetricFormulaDaily Return(Close - Open) / Open7-Day Moving AverageRolling 7-day mean of Close price52-Week HighMaximum High price over 1 year52-Week LowMinimum Low price over 1 yearVolatility Scorestd(daily_returns) × √252 × 100

Custom Metric — Volatility Score
The Volatility Score measures how much a stock's price fluctuates over time.

Formula: σ × √252 × 100 where σ = standard deviation of daily returns
Higher score = riskier, more volatile stock
Lower score = stable, predictable stock
This is a standard metric used by financial analysts to assess investment risk


Project Structure
stock-dashboard/
├── main.py          # FastAPI app — all API endpoints
├── data.py          # Data fetching, cleaning, metrics calculation
├── database.py      # SQLite setup and connection helpers
├── static/
│   └── index.html   # Frontend dashboard (Chart.js)
├── requirements.txt
└── README.md

Design Decisions

SQLite over PostgreSQL — Zero setup, portable, perfect for a local data platform
yfinance — Free, no API key required, supports global markets including NSE/BSE
FastAPI — Auto-generates Swagger docs, fast, beginner-friendly
Vanilla HTML + Chart.js — No framework overhead, loads instantly


Author

Name: Jairaj Singh Jabbal
Email: jaschrome040@gmail.com
GitHub: www.github.com/Jaschrome


Built with ❤️ for the JarNox Software Internship Assignment
