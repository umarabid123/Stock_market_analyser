# Stock Trading Agent

A beginner-friendly Python project for market-data-driven signal generation.

This project is designed to:
- Collect market data from multiple providers with automatic fallback
- Compute internal indicators
- Produce a simple trade signal and risk parameters

This project is **not financial advice** and **does not guarantee profit**.

## Project Structure

```
stock_trading_agent/
├── app.py
├── config.py
├── .env.example
├── requirements.txt
├── README.md
├── __init__.py
├── agents/
├── alerts/
├── backtest/
├── dashboard/
├── data/
├── features/
├── models/
├── risk/
└── strategy/
```

## Setup

1. Create and activate a Python environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and add keys as needed.

## Run CLI

From inside `stock_trading_agent`:

```bash
python app.py --symbol AAPL --period 5d --interval 5m
```

Expected output fields:
- Symbol
- Latest Price
- Signal
- Confidence
- Reason
- Stop Loss
- Take Profit
- Risk Warning

## Data Provider Order (`DATA_PROVIDER=auto`)

1. Polygon (if `POLYGON_API_KEY` exists)
2. Alpaca (if `ALPACA_API_KEY` and `ALPACA_SECRET_KEY` exist)
3. Finnhub (if `FINNHUB_API_KEY` exists)
4. yfinance fallback

## Streamlit Dashboard

From inside `stock_trading_agent`:

```bash
streamlit run dashboard/streamlit_app.py
```
