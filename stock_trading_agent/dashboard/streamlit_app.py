"""Real-time AI Forex & Commodity Trading Dashboard."""

from __future__ import annotations

from datetime import datetime, timezone
import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from data.market_data import MarketDataProvider
from features.indicators import add_indicators
from strategy.signal_engine import SignalEngine
from assistant.chatbot import get_chatbot_response

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None


SUPPORTED_MARKETS = {
    "Forex": ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CAD", "AUD/USD"],
    "Gold": ["XAU/USD"],
    "Silver": ["XAG/USD"],
    "Crypto": ["BTC/USD", "ETH/USD"],
}

TIMEFRAMES = ["1m", "5m", "15m", "1h", "4h", "1d"]
LOOKBACKS = ["1d", "5d", "1mo", "3mo"]


def get_setting(*names: str, default=None):
    for name in names:
        if hasattr(settings, name):
            value = getattr(settings, name)
            if value:
                return value
    return default


def price_decimals(symbol: str) -> int:
    symbol = symbol.upper()
    if symbol.startswith("XAU"):
        return 2
    if symbol.startswith("XAG"):
        return 3  # Silver typically 3 decimals
    if symbol.startswith(("BTC", "ETH")):
        return 2
    if "JPY" in symbol:
        return 3
    return 5


def fmt_price(symbol: str, value) -> str:
    if value is None:
        return "-"
    try:
        return f"{float(value):.{price_decimals(symbol)}f}"
    except Exception:
        return str(value)


def session_info() -> dict:
    now = datetime.now(timezone.utc)
    hour = now.hour
    active = []

    if hour >= 21 or hour < 6:
        active.append("Sydney")
    if hour >= 23 or hour < 8:
        active.append("Tokyo")
    if 7 <= hour < 16:
        active.append("London")
    if 12 <= hour < 21:
        active.append("New York")

    if not active:
        active = ["Market Quiet"]

    overlap = "London" in active and "New York" in active

    return {
        "time": now.strftime("%H:%M:%S UTC"),
        "session": " / ".join(active),
        "volatility": "HIGH" if overlap or "London" in active or "New York" in active else "LOW",
        "status": "NEAR REAL-TIME",
    }


def inject_css():
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%);
            color: #e5e7eb;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a1a 0%, #2a2a2a 100%);
            border-right: 1px solid rgba(255,255,255,.1);
        }

        .top-nav {
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255,255,255,.1);
            padding: 16px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            border-radius: 0 0 16px 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,.3);
        }

        .brand-logo {
            font-size: 20px;
            font-weight: 800;
            background: linear-gradient(45deg, #00d4ff, #090979);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: 1px;
        }

        .nav-info {
            font-size: 13px;
            color: #94a3b8;
            text-align: right;
        }

        .status-live {
            color: #10b981;
            font-weight: 700;
        }

        .metric-card {
            background: linear-gradient(135deg, rgba(30,30,30,.9) 0%, rgba(45,45,45,.8) 100%);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,.1);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,.3);
            transition: all 0.3s ease;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(0,0,0,.4);
        }

        .signal-buy { border-color: rgba(16,185,129,.6); background: linear-gradient(135deg, rgba(16,185,129,.1) 0%, rgba(5,150,105,.05) 100%); }
        .signal-sell { border-color: rgba(239,68,68,.6); background: linear-gradient(135deg, rgba(239,68,68,.1) 0%, rgba(220,38,38,.05) 100%); }
        .signal-hold { border-color: rgba(245,158,11,.6); background: linear-gradient(135deg, rgba(245,158,11,.1) 0%, rgba(217,119,6,.05) 100%); }
        .signal-wait { border-color: rgba(168,85,247,.6); background: linear-gradient(135deg, rgba(168,85,247,.1) 0%, rgba(147,51,234,.05) 100%); }
        .signal-strong { border-color: rgba(16,185,129,.8); background: linear-gradient(135deg, rgba(16,185,129,.2) 0%, rgba(5,150,105,.1) 100%); }

        .card {
            padding: 16px;
            border-radius: 12px;
            border: 1px solid rgba(255,255,255,.1);
            background: rgba(30,30,30,.8);
            box-shadow: 0 4px 12px rgba(0,0,0,.3);
            min-height: 80px;
        }

        .label {
            color: #9ca3af;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: .5px;
            margin-bottom: 8px;
        }

        .value {
            color: white;
            font-size: 20px;
            font-weight: 700;
            line-height: 1.2;
        }

        .sub {
            color: #9ca3af;
            font-size: 11px;
            margin-top: 6px;
        }

        .buy { border-color: rgba(34,197,94,.5); background: rgba(34,197,94,.1); }
        .sell { border-color: rgba(239,68,68,.5); background: rgba(239,68,68,.1); }
        .hold { border-color: rgba(245,158,11,.5); background: rgba(245,158,11,.1); }
        .wait { border-color: rgba(168,85,247,.5); background: rgba(168,85,247,.1); }
        .strong { border-color: rgba(34,197,94,.7); background: rgba(34,197,94,.15); }

        .warn {
            padding: 12px;
            border-radius: 8px;
            background: rgba(245,158,11,.1);
            border: 1px solid rgba(245,158,11,.3);
            color: #fcd34d;
            font-size: 13px;
            margin: 10px 0;
        }

        .section {
            color: #f3f4f6;
            font-weight: 700;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: .5px;
            margin: 15px 0 8px;
        }

        .stButton > button {
            border-radius: 8px;
            height: 44px;
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            font-weight: 700;
            border: 0;
        }

        .chat-container {
            background: rgba(30,30,30,.9);
            border: 1px solid rgba(255,255,255,.1);
            border-radius: 8px;
            padding: 15px;
            margin-top: 15px;
        }

        .chat-message {
            margin: 8px 0;
            padding: 8px 12px;
            border-radius: 6px;
        }

        .chat-user {
            background: rgba(59,130,246,.2);
            text-align: right;
        }

        .chat-bot {
            background: rgba(107,114,128,.2);
        }

        /* Floating Chatbot Styles */
        .chatbot-float-btn {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #00d4ff 0%, #090979 100%);
            border: none;
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.3);
            cursor: pointer;
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            transition: all 0.3s ease;
            animation: pulse 2s infinite;
        }

        .chatbot-float-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 12px 40px rgba(0, 212, 255, 0.5);
        }

        @keyframes pulse {
            0% { box-shadow: 0 8px 32px rgba(0, 212, 255, 0.3); }
            50% { box-shadow: 0 8px 32px rgba(0, 212, 255, 0.6); }
            100% { box-shadow: 0 8px 32px rgba(0, 212, 255, 0.3); }
        }

        .chatbot-panel {
            position: fixed;
            bottom: 100px;
            right: 24px;
            width: 360px;
            height: 500px;
            background: linear-gradient(135deg, rgba(30,30,30,.95) 0%, rgba(45,45,45,.9) 100%);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,.1);
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,.5);
            z-index: 999;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .chatbot-header {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 16px 20px;
            border-bottom: 1px solid rgba(255,255,255,.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chatbot-title {
            font-size: 16px;
            font-weight: 700;
            color: #f1f5f9;
        }

        .chatbot-subtitle {
            font-size: 12px;
            color: #94a3b8;
            margin-top: 2px;
        }

        .chatbot-close {
            background: none;
            border: none;
            color: #94a3b8;
            font-size: 18px;
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;
            transition: all 0.2s ease;
        }

        .chatbot-close:hover {
            background: rgba(239,68,68,.2);
            color: #ef4444;
        }

        .chat-messages {
            flex: 1;
            padding: 16px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        .user-msg {
            align-self: flex-end;
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: white;
            padding: 12px 16px;
            border-radius: 18px 18px 4px 18px;
            max-width: 80%;
            word-wrap: break-word;
        }

        .bot-msg {
            align-self: flex-start;
            background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
            color: #f3f4f6;
            padding: 12px 16px;
            border-radius: 18px 18px 18px 4px;
            max-width: 80%;
            word-wrap: break-word;
        }

        .chat-input-area {
            padding: 16px;
            border-top: 1px solid rgba(255,255,255,.1);
            background: rgba(30,30,30,.8);
        }

        .quick-questions {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 12px;
        }

        .quick-btn {
            background: linear-gradient(135deg, #475569 0%, #334155 100%);
            border: 1px solid rgba(255,255,255,.1);
            color: #e2e8f0;
            padding: 6px 12px;
            border-radius: 16px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .quick-btn:hover {
            background: linear-gradient(135deg, #64748b 0%, #475569 100%);
            transform: translateY(-1px);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def tone(signal: str) -> str:
    s = str(signal).upper()
    if "STRONG BUY" in s:
        return "signal-strong"
    if "BUY" in s and "WAIT" not in s:
        return "signal-buy"
    if "SELL" in s and "WAIT" not in s:
        return "signal-sell"
    if "WAIT" in s:
        return "signal-wait"
    return "signal-hold"


def card(label: str, value: str, sub: str = "", signal: str = "neutral"):
    css = tone(signal)
    st.markdown(
        f"""
        <div class="card {css}">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            <div class="sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_chart(symbol: str, df: pd.DataFrame, result: dict) -> go.Figure:
    df = add_indicators(df.copy())
    df = df.dropna(subset=["Open", "High", "Low", "Close"])

    fig = go.Figure()

    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Candles",
            increasing_line_color="#22c55e",
            decreasing_line_color="#ef4444",
            increasing_fillcolor="#22c55e",
            decreasing_fillcolor="#ef4444",
        )
    )

    overlays = {
        "EMA_20": "#38bdf8",
        "EMA_50": "#f59e0b",
        "SMA_200": "#e5e7eb",
        "BB_UPPER": "rgba(96,165,250,.75)",
        "BB_LOWER": "rgba(96,165,250,.75)",
    }

    for col, color in overlays.items():
        if col in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[col],
                    mode="lines",
                    name=col,
                    line=dict(color=color, width=1.4),
                )
            )

    signal = str(result.get("signal", "HOLD")).upper()
    latest_x = df.index[-1]
    latest_high = float(df["High"].iloc[-1])
    latest_low = float(df["Low"].iloc[-1])
    latest_close = float(df["Close"].iloc[-1])

    if "BUY" in signal and "WAIT" not in signal:
        fig.add_annotation(
            x=latest_x,
            y=latest_low,
            text=f"▲ {signal}",
            showarrow=True,
            arrowcolor="#22c55e",
            arrowwidth=2,
            ax=0,
            ay=45,
            bgcolor="rgba(5,10,18,.9)",
            bordercolor="#22c55e",
            font=dict(color="#22c55e", size=13),
        )
    elif "SELL" in signal and "WAIT" not in signal:
        fig.add_annotation(
            x=latest_x,
            y=latest_high,
            text=f"▼ {signal}",
            showarrow=True,
            arrowcolor="#ef4444",
            arrowwidth=2,
            ax=0,
            ay=-45,
            bgcolor="rgba(5,10,18,.9)",
            bordercolor="#ef4444",
            font=dict(color="#ef4444", size=13),
        )
    else:
        fig.add_annotation(
            x=latest_x,
            y=latest_close,
            text=signal,
            showarrow=False,
            bgcolor="rgba(5,10,18,.9)",
            bordercolor="#f59e0b",
            font=dict(color="#f59e0b", size=13),
        )

    if result.get("stop_loss") is not None:
        fig.add_hline(
            y=float(result["stop_loss"]),
            line_dash="dot",
            line_color="#ef4444",
            annotation_text="Stop Loss",
        )

    if result.get("take_profit") is not None:
        fig.add_hline(
            y=float(result["take_profit"]),
            line_dash="dot",
            line_color="#22c55e",
            annotation_text="Take Profit",
        )

    fig.update_layout(
        template="plotly_dark",
        height=720,
        margin=dict(l=10, r=10, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#050a12",
        title=f"{symbol} Live Forex Candlestick Chart",
        xaxis=dict(rangeslider=dict(visible=False), gridcolor="rgba(148,163,184,.12)"),
        yaxis=dict(gridcolor="rgba(148,163,184,.12)"),
        hovermode="x unified",
        legend=dict(orientation="h", y=1.02, x=1, xanchor="right"),
    )

    return fig


def get_chart_frame(provider, symbol: str, lookback: str, timeframe: str, multi: dict):
    try:
        df = provider.get_ohlcv(symbol, period=lookback, interval=timeframe)
        if df is not None and not df.empty:
            return df
    except Exception:
        pass

    for tf in [timeframe, "15m", "5m", "1h", "4h", "1d"]:
        df = multi.get(tf)
        if df is not None and not df.empty:
            return df

    return None


def render_floating_chatbot(result):
    """Render the floating chatbot icon and panel."""
    # Initialize chat state
    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Floating Chatbot Button
    if st.button("💬", key="chatbot_toggle", help="AI Forex Assistant"):
        st.session_state.chat_open = not st.session_state.chat_open
        st.rerun()

    # Add custom CSS for floating button
    st.markdown(
        """
        <style>
        [data-testid="stButton"][aria-label="AI Forex Assistant"] button {
            position: fixed !important;
            bottom: 24px !important;
            right: 24px !important;
            width: 60px !important;
            height: 60px !important;
            border-radius: 50% !important;
            background: linear-gradient(135deg, #00d4ff 0%, #090979 100%) !important;
            border: none !important;
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.3) !important;
            z-index: 1000 !important;
            font-size: 24px !important;
            animation: pulse 2s infinite !important;
            transition: all 0.3s ease !important;
        }
        [data-testid="stButton"][aria-label="AI Forex Assistant"] button:hover {
            transform: scale(1.1) !important;
            box-shadow: 0 12px 40px rgba(0, 212, 255, 0.5) !important;
        }
        @keyframes pulse {
            0% { box-shadow: 0 8px 32px rgba(0, 212, 255, 0.3) !important; }
            50% { box-shadow: 0 12px 40px rgba(0, 212, 255, 0.6) !important; }
            100% { box-shadow: 0 8px 32px rgba(0, 212, 255, 0.3) !important; }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Chat Panel using Streamlit components
    if st.session_state.chat_open:
        # Panel container with custom styling
        st.markdown(
            """
            <style>
            .chat-panel {
                position: fixed;
                bottom: 100px;
                right: 24px;
                width: 360px;
                height: 500px;
                background: linear-gradient(135deg, rgba(30,30,30,.95) 0%, rgba(45,45,45,.9) 100%);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(255,255,255,.1);
                border-radius: 16px;
                box-shadow: 0 20px 60px rgba(0,0,0,.5);
                z-index: 999;
                padding: 16px;
                display: flex;
                flex-direction: column;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Header
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown("### 🤖 AI Forex Assistant")
            st.caption("Beginner-friendly market guidance")
        with col2:
            if st.button("✖", key="close_chat"):
                st.session_state.chat_open = False
                st.rerun()

        # Messages container
        chat_container = st.container(height=250)
        with chat_container:
            for msg in st.session_state.chat_messages[-20:]:
                if msg["role"] == "user":
                    st.markdown(f'<div style="text-align: right; margin: 8px 0;"><div style="display: inline-block; background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white; padding: 8px 12px; border-radius: 12px 12px 4px 12px; max-width: 80%; font-size: 14px;">{msg["content"]}</div></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div style="text-align: left; margin: 8px 0;"><div style="display: inline-block; background: linear-gradient(135deg, #374151 0%, #1f2937 100%); color: #f3f4f6; padding: 8px 12px; border-radius: 12px 12px 12px 4px; max-width: 80%; font-size: 14px;">{msg["content"]}</div></div>', unsafe_allow_html=True)

        # Quick Questions
        st.markdown("**Quick Questions:**")
        quick_cols = st.columns(2)
        quick_questions = [
            "What does this signal mean?",
            "What is HOLD?",
            "Why no stop loss?",
            "What is XAU/USD?",
            "Is this real-time?"
        ]

        for i, q in enumerate(quick_questions):
            col_idx = i % 2
            with quick_cols[col_idx]:
                if st.button(q, key=f"quick_{i}", use_container_width=True):
                    bot_response = get_chatbot_response(q, result)
                    st.session_state.chat_messages.append({"role": "user", "content": q})
                    st.session_state.chat_messages.append({"role": "bot", "content": bot_response})
                    st.rerun()

        # Chat Input
        chat_input = st.chat_input("Ask about signals, XAU/USD, risk, timeframes...", key="chat_input")
        if chat_input:
            bot_response = get_chatbot_response(chat_input, result)
            st.session_state.chat_messages.append({"role": "user", "content": chat_input})
            st.session_state.chat_messages.append({"role": "bot", "content": bot_response})
            st.rerun()


def main():
    st.set_page_config(
        page_title="AI Forex & Commodity Trading Assistant",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    inject_css()

    # Initialize session state for chat
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    default_market = get_setting("default_market", default="Forex")
    default_pair = get_setting("default_pair", "default_symbol", default="XAU/USD")
    default_timeframe = get_setting("default_timeframe", "default_interval", default="15m")
    default_lookback = get_setting("default_lookback", "default_period", default="5d")

    # Top Navbar
    st.markdown(
        f"""
        <div class="top-nav">
            <div class="brand-logo">AI FX | AI Forex & Commodity Trading Assistant</div>
            <div class="nav-info">
                Pair: {default_pair} | Status: <span class="status-live">NEAR REAL-TIME</span><br>
                Time: {datetime.now().strftime('%H:%M:%S UTC')} | Session: {session_info()['session']} | Data: TwelveData
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Main layout: left sidebar, center chart, right panel
    left_col, center_col, right_col = st.columns([1, 2, 1])

    with left_col:
        st.markdown('<div class="section">📊 Market Controls</div>', unsafe_allow_html=True)
        st.caption("Use 5m/15m for entry and 1h/4h for trend confirmation.")

        market_keys = list(SUPPORTED_MARKETS.keys())
        market = st.selectbox("Market", market_keys, index=market_keys.index(default_market) if default_market in market_keys else 0)

        pairs = SUPPORTED_MARKETS[market]
        pair = st.selectbox("Pair / Asset", pairs, index=pairs.index(default_pair) if default_pair in pairs else 0)

        timeframe = st.selectbox("Timeframe", TIMEFRAMES, index=TIMEFRAMES.index(default_timeframe) if default_timeframe in TIMEFRAMES else 2)

        lookback = st.selectbox("Lookback", LOOKBACKS, index=LOOKBACKS.index(default_lookback) if default_lookback in LOOKBACKS else 1)

        auto_refresh_options = [10, 30, 60]
        refresh_seconds = st.selectbox("Auto Refresh (sec)", auto_refresh_options, index=1)

        analyze = st.button("🔍 Analyze Market", use_container_width=True)

        st.markdown("---")
        st.caption("Educational analysis only. No real trading.")

    # Auto refresh
    if st_autorefresh:
        st_autorefresh(interval=refresh_seconds * 1000, key="forex_refresh")

    if analyze:
        st.session_state["active_request"] = {
            "market": market,
            "pair": pair,
            "timeframe": timeframe,
            "lookback": lookback,
            "ts": time.time(),
        }

    req = st.session_state.get("active_request")


    if not req:
        with center_col:
            st.markdown('<div class="section">📈 Candlestick Chart</div>', unsafe_allow_html=True)
            st.info("Select an asset and click Analyze Market to begin analysis.")
        with right_col:
            st.markdown('<div class="section">📊 Signal Panel</div>', unsafe_allow_html=True)
            card("Signal", "WAITING", "Click Analyze Market", "signal-hold")
        return

    # Analysis
    provider = MarketDataProvider(settings)
    engine = SignalEngine(settings)

    with st.spinner("Analyzing market data..."):
        multi = provider.get_multi_timeframe_data(req["pair"])
        result = engine.analyze_market(req["pair"], multi)

    chart_df = get_chart_frame(provider, req["pair"], req["lookback"], req["timeframe"], multi)

    if chart_df is None or chart_df.empty:
        st.error("No market data available. Check API key and symbol.")
        return

    symbol = req["pair"]
    signal = str(result.get("signal", "HOLD"))
    latest_price = result.get("latest_price") or float(chart_df["Close"].iloc[-1])
    confidence = float(result.get("confidence", 0.0)) * 100

    # Update live price
    live_price_placeholder.markdown(f'<div class="top-bar-info">Price: {fmt_price(symbol, latest_price)}</div>', unsafe_allow_html=True)

    # Center: Chart
    with center_col:
        st.markdown('<div class="section">📈 Candlestick Chart</div>', unsafe_allow_html=True)
        fig = build_chart(symbol, chart_df, result)
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

    # Right: Signal Panel
    with right_col:
        st.markdown('<div class="section">📊 Signal Panel</div>', unsafe_allow_html=True)

        card("Signal", tone(signal), f"{confidence:.1f}% confidence", signal)
        card("Market Bias", result.get("market_bias", "NEUTRAL"), "Overall direction", signal)
        card("Trend Strength", f"{result.get('trend_strength', 0):.2f}", "Multi-timeframe alignment", signal)
        card("Entry Price", fmt_price(symbol, result.get("entry_price") or latest_price), "Reference price", signal)
        card("Stop Loss", fmt_price(symbol, result.get("stop_loss")), "Risk protection", signal)
        card("Take Profit", fmt_price(symbol, result.get("take_profit")), "Profit target", signal)
        card("Risk/Reward", str(result.get("risk_reward_ratio", "-")), "Ratio", signal)
        card("Spread", "N/A", "Bid/Ask difference", signal)
        card("Session Volatility", result.get("session_volatility", "LOW"), "Market activity", signal)

    # Bottom: Multi-timeframe table, news, explanation, chatbot
    st.markdown('<div class="section">📊 Multi-Timeframe Analysis</div>', unsafe_allow_html=True)
    mtf_cols = st.columns(5)
    with mtf_cols[0]:
        card("1D", result.get("trend_1d", "-"), "Daily", "neutral")
    with mtf_cols[1]:
        card("4H", result.get("trend_4h", "-"), "4 Hour", "neutral")
    with mtf_cols[2]:
        card("1H", result.get("trend_1h", "-"), "1 Hour", "neutral")
    with mtf_cols[3]:
        card("15M", result.get("trend_15m", "-"), "15 Min", "neutral")
    with mtf_cols[4]:
        card("5M", result.get("trend_5m", "-"), "5 Min", "neutral")

    # News/Sentiment and Explanation
    news_cols = st.columns(2)
    with news_cols[0]:
        sentiment = result.get("news_sentiment") or {}
        card("News Sentiment", sentiment.get("sentiment", "UNAVAILABLE"), sentiment.get("reason", ""), signal)
    with news_cols[1]:
        st.markdown('<div class="section">📝 Signal Explanation</div>', unsafe_allow_html=True)
        st.info(result.get("reason", "Analysis complete."))

    # Floating Chatbot
    render_floating_chatbot(result)

    # Warning
    st.markdown(
        """
        <div class="warn">
        This is educational AI analysis only. Not financial advice. No guaranteed profits.
        Past performance ≠ future results. Use proper risk management.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()