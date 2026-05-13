"""Chatbot assistant for forex education and signal explanation."""

from __future__ import annotations

import re
from typing import Any, Dict

import requests

from config import settings


WARNING_TEXT = "This is educational paper-trading analysis, not financial advice."


def _with_warning(text: str) -> str:
    if WARNING_TEXT.lower() in text.lower():
        return text
    return f"{text} {WARNING_TEXT}"


def _detect_intent(question: str) -> str:
    if any(word in question for word in ("hi", "hello", "hey", "how are you")):
        return "greeting"
    if any(word in question for word in ("beginner", "no idea", "guide", "how works", "how work", "how use", "how to use", "how it works", "explain app", "understand")):
        return "beginner"
    if any(word in question for word in ("chart", "graph", "candle", "candlestick", "red candle", "green candle")):
        return "chart"
    if any(word in question for word in ("current signal", "explain signal", "buy", "sell", "strong buy", "strong sell")):
        return "signal"
    if any(word in question for word in ("hold",)):
        return "hold"
    if any(word in question for word in ("risk", "stop loss", "stoploss", "sl", "take profit", "tp", "empty risk")):
        return "risk"
    if any(word in question for word in ("real time", "realtime", "live", "prediction")):
        return "realtime"
    if any(word in question for word in ("timeframe", "15m", "1h", "5m", "4h")):
        return "timeframe"
    if any(word in question for word in ("xau", "gold", "xag", "silver", "gbp", "eur", "btc", "crypto")):
        return "pair"
    return "general"


def _extract_symbol(current_result: Dict[str, Any] | None, symbol: str | None) -> str:
    if symbol:
        return symbol
    if isinstance(current_result, dict):
        value = current_result.get("symbol")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _signal_summary(signal: str) -> str:
    if signal in {"BUY", "STRONG BUY"}:
        return "bullish conditions"
    if signal in {"SELL", "STRONG SELL"}:
        return "bearish conditions"
    if signal == "HOLD":
        return "no clear safe setup"
    if signal == "WAIT_FOR_BUY":
        return "bullish bias, but entry is not confirmed"
    if signal == "WAIT_FOR_SELL":
        return "bearish bias, but entry is not confirmed"
    return "unclear conditions"


def _format_current_result(current_result: Dict[str, Any] | None) -> Dict[str, Any]:
    current_result = current_result if isinstance(current_result, dict) else {}
    trends = current_result.get('trends', {}) if isinstance(current_result.get('trends', {}), dict) else {}
    risk = current_result.get('risk', {}) if isinstance(current_result.get('risk', {}), dict) else {}
    return {
        'signal': current_result.get('signal', 'HOLD').upper(),
        'confidence': current_result.get('confidence', 0.0),
        'market_bias': current_result.get('market_bias', 'NEUTRAL'),
        'trend_1d': trends.get('1d', 'NEUTRAL'),
        'trend_4h': trends.get('4h', 'NEUTRAL'),
        'trend_1h': trends.get('1h', 'NEUTRAL'),
        'trend_15m': trends.get('15m', 'NEUTRAL'),
        'trend_5m': trends.get('5m', 'NEUTRAL'),
        'stop_loss': risk.get('stop_loss'),
        'take_profit': risk.get('take_profit'),
        'risk_reward_ratio': risk.get('risk_reward_ratio'),
        'volatility': current_result.get('session', {}).get('volatility', 'MEDIUM'),
        'active_session': current_result.get('session', {}).get('active_session', 'Unknown'),
    }


def _gemini_chat_response(prompt_text: str) -> str:
    if not settings.gemini_api_key:
        return ''

    model = settings.gemini_model or 'gemini-1.5-mini'
    url = f'https://generativelanguage.googleapis.com/v1beta2/models/{model}:generate'
    params = {}
    headers = {'Content-Type': 'application/json'}
    if settings.gemini_api_key.startswith('ya29.'):
        headers['Authorization'] = f'Bearer {settings.gemini_api_key}'
    else:
        params['key'] = settings.gemini_api_key

    payload = {
        'prompt': {'text': prompt_text},
        'temperature': 0.7,
        'maxOutputTokens': 256,
    }

    try:
        response = requests.post(url, params=params, headers=headers, json=payload, timeout=20)
        if response.ok:
            result = response.json()
            candidates = result.get('candidates') or []
            if candidates and isinstance(candidates, list):
                return candidates[0].get('output', '').strip()
    except Exception:
        pass

    return ''


def get_chatbot_response(user_question: str, result: Dict[str, Any] | None = None, symbol: str | None = None) -> str:
    """Generate a response to user question based on current dashboard result."""
    question = user_question.strip().lower()
    current = _format_current_result(result)
    current_symbol = _extract_symbol(result, symbol)
    risk_empty = not current.get('stop_loss') and not current.get('take_profit') and not current.get('risk_reward_ratio')

    intent = _detect_intent(question)

    if intent == "greeting":
        return _with_warning("Hi! I can help you understand this forex dashboard, signals, chart, risk levels, and how to use it safely.")

    if intent == "beginner":
        return _with_warning(
            "This dashboard helps you analyze forex, gold, silver, and crypto. Step 1: choose a pair such as XAU/USD or GBP/USD. Step 2: choose a timeframe like 15m for short-term or 1h/4h for trend. Step 3: click Analyze. Step 4: read the signal: BUY, SELL, HOLD, or WAIT. Step 5: check confidence, chart trend, stop loss, and take profit. Use it for paper trading and learning only."
        )

    if intent == "chart":
        return _with_warning("The chart shows price movement using candles. Each candle has open, high, low, and close prices. Green candles mean price moved up, and red candles mean price moved down. Use 15m for entry view and 1h/4h for bigger trend.")

    if intent == "signal":
        signal = current['signal']
        if signal == "HOLD":
            explanation = "no clear safe setup"
        elif signal in {"BUY", "STRONG BUY"}:
            explanation = "bullish conditions"
        elif signal in {"SELL", "STRONG SELL"}:
            explanation = "bearish conditions"
        elif signal == "WAIT_FOR_BUY":
            explanation = "bullish bias but entry is not confirmed"
        elif signal == "WAIT_FOR_SELL":
            explanation = "bearish bias but entry is not confirmed"
        else:
            explanation = "unclear conditions"

        return _with_warning(
            f"The current signal is {signal} with {float(current.get('confidence', 0.0)) * 100:.1f}% confidence. This means the system sees {explanation}. It is not guaranteed; confirm with chart and risk levels."
        )

    if intent == "hold":
        return _with_warning("HOLD means there is no clear safe setup right now.")

    if intent == "risk":
        return _with_warning("Risk management shows where a trade idea becomes invalid. Stop loss limits loss. Take profit is the target. If signal is HOLD or WAIT, risk levels may be empty because no active trade is confirmed.")

    if intent == "realtime":
        return _with_warning("This dashboard uses near-real-time market data from APIs and refreshes candles. It gives probability-based analysis, not guaranteed future prediction.")

    if intent == "timeframe":
        return _with_warning("This dashboard uses candle timeframes. 15m is faster and 1h/4h show the larger trend.")

    if intent == "pair":
        return _with_warning("Pairs represent markets. XAU/USD is gold against the US dollar, XAG/USD is silver, GBP/USD is British pound against the US dollar, and BTC/USD is Bitcoin against the US dollar.")

    if settings.gemini_api_key:
        model_prompt = (
            f"Answer in short clear English only. Keep it limited to this forex dashboard, signals, chart, risk, stop loss, take profit, confidence, timeframe, pairs, XAU/USD, crypto, and how to use the dashboard. "
            f"If the question is unrelated, reply with: I can only help with this trading analysis dashboard, its signals, chart, risk, and forex education. "
            f"Question: {user_question}. Symbol: {current_symbol or 'N/A'}. Current signal: {current['signal']}. Confidence: {float(current.get('confidence', 0.0)) * 100:.1f}%. "
            f"Always include: {WARNING_TEXT}"
        )
        gemini_answer = _gemini_chat_response(model_prompt)
        if gemini_answer:
            return _with_warning(gemini_answer)

    app_scope_words = (
        "signal", "chart", "candles", "candle", "risk", "stop loss", "take profit", "confidence", "timeframe",
        "pair", "xau", "xag", "gbp", "eur", "usd", "btc", "crypto", "dashboard", "analyze", "analysis"
    )
    if not any(word in question for word in app_scope_words):
        return "I can only help with this trading analysis dashboard, its signals, chart, risk, and forex education."

    signal = current['signal']
    confidence = float(current.get('confidence', 0.0)) * 100

    if signal == "HOLD":
        return _with_warning("The current signal is HOLD. This means there is no clear safe setup right now.")
    if signal in {"BUY", "STRONG BUY"}:
        return _with_warning(f"The current signal is {signal} with {confidence:.1f}% confidence. This suggests bullish conditions, but it is not guaranteed. Please confirm with the chart and risk levels.")
    if signal in {"SELL", "STRONG SELL"}:
        return _with_warning(f"The current signal is {signal} with {confidence:.1f}% confidence. This suggests bearish conditions, but it is not guaranteed. Please confirm with the chart and risk levels.")
    if signal == "WAIT_FOR_BUY":
        return _with_warning(f"The current signal is WAIT_FOR_BUY with {confidence:.1f}% confidence. It means the market has a bullish bias, but the entry is not confirmed yet.")
    if signal == "WAIT_FOR_SELL":
        return _with_warning(f"The current signal is WAIT_FOR_SELL with {confidence:.1f}% confidence. It means the market has a bearish bias, but the entry is not confirmed yet.")

    return _with_warning(f"The current signal is {signal} with {confidence:.1f}% confidence. Please confirm it with the chart and risk levels.")