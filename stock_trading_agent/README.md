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
python -m streamlit run dashboard/streamlit_app.py
```

If you see a launcher error like `Unable to create process`, use the `python -m streamlit` form above instead of the `streamlit` command.

### How the dashboard works

- Use the left panel to load a preset or read the input examples.
- Enter a stock symbol such as `AAPL`, `MSFT`, or `TSLA`.
- Choose a lookback period like `5d`, `1mo`, or `3mo`.
- Choose an interval like `5m`, `15m`, `1h`, or `1d`.
- Click **Analyze Market**.
- The app will then show:
	- Latest price
	- Signal: `BUY`, `SELL`, or `HOLD`
	- Confidence score
	- Human-readable reason
	- Stop loss and take profit

### What the result means

- `BUY` means the internal indicators are leaning bullish.
- `SELL` means the internal indicators are leaning bearish.
- `HOLD` means the signal is mixed or not strong enough.
- Confidence is a simple score from `0.00` to `1.00`.
- The app is for learning and paper-trading support only, not guaranteed profit.
