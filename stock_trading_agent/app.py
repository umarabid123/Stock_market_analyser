"""CLI entry point for generating a stock signal."""

from __future__ import annotations

import argparse
import sys

from config import settings
from data.market_data import MarketDataProvider
from strategy.signal_engine import SignalEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stock Trading Agent CLI")
    parser.add_argument("--symbol", default=settings.default_symbol, help="Ticker symbol, e.g. AAPL")
    parser.add_argument("--period", default=settings.default_period, help="Period, e.g. 5d")
    parser.add_argument("--interval", default=settings.default_interval, help="Interval, e.g. 5m")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    provider = MarketDataProvider(settings)
    # Use multi-timeframe fetch for stronger decision support
    multi = provider.get_multi_timeframe_data(args.symbol)
    engine = SignalEngine(settings)
    result = engine.generate_signal(args.symbol, multi)

    def fmt(v):
        if v is None:
            return "-"
        try:
            return f"{v:.2f}"
        except Exception:
            return str(v)

    print(f"Symbol: {result.get('symbol')}")
    print(f"Latest Price: {fmt(result.get('latest_price'))}")
    print(f"Main Signal: {result.get('signal')}")
    print(f"Confidence: {result.get('confidence'):.2f}")
    print(f"Prediction Direction: {result.get('prediction_direction')}")
    print(f"Trend 5m: {result.get('trend_5m')}")
    print(f"Trend 15m: {result.get('trend_15m')}")
    print(f"Trend 1h: {result.get('trend_1h')}")
    print(f"Trend 1d: {result.get('trend_1d')}")
    print(f"Volume Strength: {result.get('volume_strength')}")
    news = result.get('news_sentiment') or {}
    print(f"News Sentiment: {news.get('sentiment')} ({news.get('score')}) - {news.get('reason')}")
    print(f"Reason: {result.get('reason')}")
    print(f"Stop Loss: {fmt(result.get('stop_loss'))}")
    print(f"Take Profit: {fmt(result.get('take_profit'))}")
    print(f"Risk Warning: {result.get('risk_warning')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
