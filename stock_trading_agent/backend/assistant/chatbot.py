"""Chatbot assistant for forex education and signal explanation."""

from __future__ import annotations

import re
from typing import Dict, Any

import requests

from config import settings


def _format_current_result(current_result: Dict[str, Any]) -> Dict[str, Any]:
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


def get_chatbot_response(user_question: str, current_result: Dict[str, Any]) -> str:
    """Generate a response to user question based on current dashboard result."""
    question = user_question.strip().lower()
    current = _format_current_result(current_result)

    if settings.gemini_api_key:
        model_prompt = (
            f"Answer this question in simple English for a non-expert user. "
            f"Question: {user_question}. "
            f"Current market signal: {current['signal']}, confidence: {current['confidence'] * 100:.1f}%, "
            f"market bias: {current['market_bias']}, 1D trend: {current['trend_1d']}, 4H trend: {current['trend_4h']}, "
            f"1H trend: {current['trend_1h']}, 15M trend: {current['trend_15m']}, 5M trend: {current['trend_5m']}. "
            f"Stop loss: {current['stop_loss']}, take profit: {current['take_profit']}, risk reward: {current['risk_reward_ratio']}."
        )
        gemini_answer = _gemini_chat_response(model_prompt)
        if gemini_answer:
            return gemini_answer

    # Extract signal and key info
    signal = current['signal']
    confidence = current['confidence']
    market_bias = current['market_bias']
    trend_1d = current['trend_1d']
    trend_4h = current['trend_4h']
    trend_1h = current['trend_1h']
    trend_15m = current['trend_15m']
    trend_5m = current['trend_5m']
    stop_loss = current['stop_loss']
    take_profit = current['take_profit']
    risk_reward = current['risk_reward_ratio']

    # Simple keyword matching
    if "what does" in question and "mean" in question:
        if "hold" in question:
            return "HOLD means there is no clear setup right now. It is usually safer to wait when the market is uncertain."
        elif "buy" in question:
            return "BUY means the analysis shows bullish pressure. It is not a guarantee, so always use proper risk management."
        elif "sell" in question:
            return "SELL means the analysis shows bearish pressure. It is not a guarantee, so always use proper risk management."
        elif "strong buy" in question:
            return "STRONG BUY means multiple timeframes are aligned bullish. It is stronger than a normal BUY, but still not guaranteed."
        elif "strong sell" in question:
            return "STRONG SELL means multiple timeframes are aligned bearish. It is stronger than a normal SELL, but still not guaranteed."
        elif "wait" in question:
            return "WAIT signals mean the market is not ready for a clear trade yet. It is better to wait for confirmation."

    if "why" in question and ("risk" in question or "stop" in question or "empty" in question):
        if signal == "HOLD":
            return "Risk values only appear when a trade signal is active. On HOLD, the system avoids trades because the market is unclear."
        elif "wait" in signal:
            return "WAIT signals mean the system is waiting for a clearer setup before calculating risk and targets."
        else:
            return f"Risk is based on market volatility. The stop loss protects the trade, and the take profit aims for a healthy risk/reward ratio of about {risk_reward or 'N/A'}."

    if "what is" in question:
        if "xau" in question or "gold" in question:
            return "XAU/USD is the gold price expressed in US dollars. It is a commodity pair and often moves opposite USD strength."
        elif "xag" in question or "silver" in question:
            return "XAG/USD is the silver price expressed in US dollars. Silver can be more volatile than gold and is influenced by industrial demand."
        elif "timeframe" in question:
            return "A timeframe shows how long each candle lasts. For example, 5m means 5 minutes and 1h means 1 hour. Lower timeframes show short-term moves, higher timeframes show the bigger trend."
        elif "confidence" in question:
            return f"Confidence shows how strong the signal looks. Current confidence is {confidence * 100:.1f}%. Higher is better, but it is not a guarantee."
        elif "spread" in question:
            return "Spread is the difference between buy and sell prices. It is the trading cost you pay when opening a position."
        elif "atr" in question:
            return "ATR measures average market movement. Traders use it to set stop loss and take profit levels based on volatility."

    if "should i" in question or "can i" in question or "trade now" in question:
        return "I cannot provide personal trading advice. This tool is for learning. Always manage your risk and only trade what you can afford to lose."

    if "real" in question and "time" in question:
        return "This is near-real-time analysis using recent market data, but it is not a prediction and not guaranteed."

    if "explain" in question and "signal" in question:
        explanation = f"Current signal: {signal}. "
        if signal == "HOLD":
            explanation += "The market does not have a clear trade setup right now, so the system is avoiding trades."
        elif signal == "BUY":
            explanation += "The analysis shows bullish pressure. Use a stop loss and manage your risk."
        elif signal == "STRONG BUY":
            explanation += f"Multiple timeframes are aligned bullish. Confidence is {confidence * 100:.1f}%. Treat this as informed analysis, not a promise."
        elif signal == "SELL":
            explanation += "The analysis shows bearish pressure. Use a stop loss and manage your risk."
        elif signal == "STRONG SELL":
            explanation += f"Multiple timeframes are aligned bearish. Confidence is {confidence * 100:.1f}%. Treat this as informed analysis, not a promise."
        elif "WAIT_FOR_BUY" in signal:
            explanation += "Higher timeframes are bullish, but the 5-minute chart is not yet confirming. Wait for lower timeframe alignment."
        elif "WAIT_FOR_SELL" in signal:
            explanation += "Higher timeframes are bearish, but the 5-minute chart is not yet confirming. Wait for lower timeframe alignment."
        return explanation

    # Default responses
    if signal == "HOLD":
        return "Current signal is HOLD. No active trade is recommended right now. This is often the safest choice in uncertain markets."
    elif "BUY" in signal:
        return f"The system suggests {signal} with {confidence * 100:.1f}% confidence. Remember, this is educational analysis, not financial advice."
    elif "SELL" in signal:
        return f"The system suggests {signal} with {confidence * 100:.1f}% confidence. Remember, this is educational analysis, not financial advice."
    elif "WAIT" in signal:
        return f"The signal is {signal}, which means the market is not fully confirmed yet. Wait for better confirmation before trading."

    return "I can help explain the current market signal, risk management, or asset basics. Ask me about signal meaning, risk, or XAU/USD."