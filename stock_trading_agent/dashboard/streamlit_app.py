"""Streamlit dashboard for quick manual checks."""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go

from config import settings
from data.market_data import MarketDataProvider
from strategy.signal_engine import SignalEngine
from features.indicators import add_indicators


SAMPLE_PRESETS = {
    "AAPL": {"symbol": "AAPL", "period": "5d", "interval": "5m"},
    "MSFT": {"symbol": "MSFT", "period": "1mo", "interval": "15m"},
    "TSLA": {"symbol": "TSLA", "period": "5d", "interval": "1h"},
}


def _apply_preset(name: str) -> None:
    preset = SAMPLE_PRESETS[name]
    st.session_state["symbol_input"] = preset["symbol"]
    st.session_state["period_input"] = preset["period"]
    st.session_state["interval_input"] = preset["interval"]


def _signal_color(signal: str) -> str:
    mapping = {"BUY": "green", "SELL": "red", "HOLD": "orange"}
    return mapping.get(signal.upper(), "blue")


def _signal_summary(signal: str) -> str:
    mapping = {
        "BUY": "Trend and momentum are leaning bullish.",
        "SELL": "Trend and momentum are leaning bearish.",
        "HOLD": "Mixed or weak conditions, so the engine is waiting.",
    }
    return mapping.get(signal.upper(), "No summary available.")


def main() -> None:
    st.set_page_config(page_title="Stock Trading Agent", layout="wide")
    st.title("Stock Trading Agent Dashboard")
    st.caption("Enter a symbol, choose a time range, then press Analyze. Market APIs provide data only; the signal comes from internal indicators.")

    with st.sidebar:
        st.header("How to use")
        st.write("1. Choose a preset or type your own symbol.")
        st.write("2. Select the lookback period and candle interval.")
        st.write("3. Click **Analyze Market** to generate the result.")
        st.divider()
        st.subheader("Quick presets")
        for name in SAMPLE_PRESETS:
            if st.button(f"Load {name}", use_container_width=True):
                _apply_preset(name)
        st.divider()
        st.subheader("Input guide")
        st.write("Symbol: AAPL, MSFT, TSLA")
        st.write("Period: 5d, 1mo, 3mo")
        st.write("Interval: 5m, 15m, 1h, 1d")

    top_left, top_right = st.columns([2, 1])
    with top_left:
        st.subheader("Analyze a stock")
        st.write("The model reads price candles, calculates indicators, and then turns that into a simple trade signal.")
    with top_right:
        st.metric("Mode", "Paper-safe", help="This app is for learning and paper trading support only.")

    input_col1, input_col2, input_col3 = st.columns([1.2, 1, 1])
    with input_col1:
        symbol = st.text_input("Stock symbol", value=st.session_state.get("symbol_input", settings.default_symbol), key="symbol_input", help="Example: AAPL, MSFT, TSLA")
    with input_col2:
        period = st.selectbox(
            "Lookback period",
            ["5d", "1mo", "3mo", "6mo", "1y"],
            index=["5d", "1mo", "3mo", "6mo", "1y"].index(st.session_state.get("period_input", settings.default_period) if st.session_state.get("period_input", settings.default_period) in ["5d", "1mo", "3mo", "6mo", "1y"] else "5d"),
            key="period_input",
            help="How much recent market history to load.",
        )
    with input_col3:
        interval = st.selectbox(
            "Candle interval",
            ["5m", "15m", "1h", "1d"],
            index=["5m", "15m", "1h", "1d"].index(st.session_state.get("interval_input", settings.default_interval) if st.session_state.get("interval_input", settings.default_interval) in ["5m", "15m", "1h", "1d"] else "5m"),
            key="interval_input",
            help="Smaller intervals show more detail; larger ones are smoother.",
        )

    analyze = st.button("Analyze Market", type="primary", use_container_width=True)

    st.info("Tip: If you are not sure what to enter, use the quick preset buttons in the left panel.")

    if not analyze:
        st.subheader("What you will see after analysis")
        preview_col1, preview_col2, preview_col3 = st.columns(3)
        preview_col1.metric("Signal", "BUY / SELL / HOLD")
        preview_col2.metric("Confidence", "0.00 - 1.00")
        preview_col3.metric("Risk", "Stop Loss / Take Profit")
        st.write("Click **Analyze Market** to load data and generate the result.")
        return

    provider = MarketDataProvider(settings)
    with st.spinner("Loading market data and calculating signal..."):
        data = provider.get_ohlcv(symbol, period, interval)

    if data.empty:
        st.error("No market data returned for this symbol/timeframe.")
        st.write("Try another symbol, a different period, or check your internet/API keys.")
        return

    engine = SignalEngine(settings)
    result = engine.generate_signal(symbol, data)

    signal = str(result["signal"])
    color = _signal_color(signal)
    summary = _signal_summary(signal)

    st.subheader("Result")
    result_col1, result_col2, result_col3, result_col4 = st.columns(4)
    result_col1.metric("Symbol", result["symbol"])
    result_col2.metric("Latest Price", f"{result['latest_price']:.2f}")
    result_col3.metric("Signal", signal)
    result_col4.metric("Confidence", f"{result['confidence']:.2f}")

    st.markdown(f"**Signal meaning:** <span style='color:{color}; font-weight:700;'>{summary}</span>", unsafe_allow_html=True)

    detail_col1, detail_col2 = st.columns([1, 1])
    with detail_col1:
        st.markdown("### Reason")
        st.write(result["reason"])
        st.markdown("### Risk")
        st.write(f"Stop Loss: {result['stop_loss']:.2f}")
        st.write(f"Take Profit: {result['take_profit']:.2f}")
        st.warning(result["risk_warning"])
    with detail_col2:
        st.markdown("### Price chart")
        # Ensure indicators are available for plotting
        plot_data = data.copy()
        try:
            plot_data = add_indicators(plot_data)
        except Exception:
            # If indicators fail, continue with raw data
            pass

        # Build candlestick trace
        candlestick = go.Candlestick(
            x=plot_data.index,
            open=plot_data["Open"],
            high=plot_data["High"],
            low=plot_data["Low"],
            close=plot_data["Close"],
            name="Price",
        )

        traces = [candlestick]

        # Add SMA lines when present
        if "SMA_20" in plot_data.columns:
            traces.append(
                go.Scatter(x=plot_data.index, y=plot_data["SMA_20"], mode="lines", line=dict(width=1.5, color="cyan"), name="SMA 20")
            )
        if "SMA_50" in plot_data.columns:
            traces.append(
                go.Scatter(x=plot_data.index, y=plot_data["SMA_50"], mode="lines", line=dict(width=1.5, color="magenta"), name="SMA 50")
            )

        fig = go.Figure(data=traces)
        fig.update_layout(
            template="plotly_dark",
            xaxis=dict(rangeslider=dict(visible=True)),
            hovermode="x unified",
            margin=dict(l=10, r=10, t=30, b=20),
        )

        st.plotly_chart(fig, use_container_width=True)
        st.markdown("### Latest candles")
        st.dataframe(plot_data.tail(10), use_container_width=True)

    with st.expander("How this dashboard works"):
        st.write("The dashboard first downloads price candles for the selected symbol and timeframe.")
        st.write("Then it calculates internal indicators like moving averages, RSI, momentum, and ATR.")
        st.write("Finally it produces a simple BUY, SELL, or HOLD signal with confidence and basic risk levels.")
        st.write("It does not use market APIs to predict the future and does not guarantee profit.")


if __name__ == "__main__":
    main()
