"""Streamlit dashboard for quick manual checks."""

from __future__ import annotations

import streamlit as st

from config import settings
from data.market_data import MarketDataProvider
from strategy.signal_engine import SignalEngine


def main() -> None:
    st.set_page_config(page_title="Stock Trading Agent", layout="wide")
    st.title("Stock Trading Agent")
    st.caption("Market data APIs are data sources only. Signals come from internal logic.")

    symbol = st.text_input("Symbol", value=settings.default_symbol)
    period = st.text_input("Period", value=settings.default_period)
    interval = st.text_input("Interval", value=settings.default_interval)

    if st.button("Generate Signal"):
        provider = MarketDataProvider(settings)
        data = provider.get_ohlcv(symbol, period, interval)
        if data.empty:
            st.error("No market data returned.")
            return

        engine = SignalEngine(settings)
        result = engine.generate_signal(symbol, data)
        st.write(result)
        st.line_chart(data["Close"])


if __name__ == "__main__":
    main()
