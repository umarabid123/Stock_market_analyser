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
    data = provider.get_ohlcv(args.symbol, args.period, args.interval)

    if data.empty:
        print("No market data was returned. Check symbol, network, or API keys.")
        return 1

    engine = SignalEngine(settings)
    result = engine.generate_signal(args.symbol, data)

    print(f"Symbol: {result['symbol']}")
    print(f"Latest Price: {result['latest_price']:.2f}")
    print(f"Signal: {result['signal']}")
    print(f"Confidence: {result['confidence']:.2f}")
    print(f"Reason: {result['reason']}")
    print(f"Stop Loss: {result['stop_loss']:.2f}")
    print(f"Take Profit: {result['take_profit']:.2f}")
    print(f"Risk Warning: {result['risk_warning']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
