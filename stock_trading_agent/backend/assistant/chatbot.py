"""Chatbot assistant for forex education and signal explanation."""

from __future__ import annotations

import re
from typing import Dict, Any


def get_chatbot_response(user_question: str, current_result: Dict[str, Any]) -> str:
    """Generate a response to user question based on current dashboard result."""
    question = user_question.strip().lower()

    # Extract signal and key info
    signal = current_result.get("signal", "HOLD").upper()
    confidence = current_result.get("confidence", 0.0)
    market_bias = current_result.get("market_bias", "NEUTRAL")
    trend_1d = current_result.get("trend_1d", "NEUTRAL")
    trend_4h = current_result.get("trend_4h", "NEUTRAL")
    trend_1h = current_result.get("trend_1h", "NEUTRAL")
    trend_15m = current_result.get("trend_15m", "NEUTRAL")
    trend_5m = current_result.get("trend_5m", "NEUTRAL")
    stop_loss = current_result.get("stop_loss")
    take_profit = current_result.get("take_profit")
    risk_reward = current_result.get("risk_reward_ratio")

    # Simple keyword matching
    if "what does" in question and "mean" in question:
        if "hold" in question:
            return "HOLD ka matlab hai system ko abhi clear safe trade setup nahi mil raha. Forex mein no trade bhi acha decision hota hai."
        elif "buy" in question:
            return "BUY ka matlab hai analysis bullish conditions dikha raha hai. Ye guarantee nahi hai - always proper risk management use karein."
        elif "sell" in question:
            return "SELL ka matlab hai analysis bearish conditions dikha raha hai. Ye guarantee nahi hai - always proper risk management use karein."
        elif "strong buy" in question:
            return "STRONG BUY ka matlab hai multiple timeframes bullish align hain. Higher confidence but still guaranteed nahi."
        elif "strong sell" in question:
            return "STRONG SELL ka matlab hai multiple timeframes bearish align hain. Higher confidence but still guaranteed nahi."
        elif "wait" in question:
            return "WAIT_FOR_BUY ya WAIT_FOR_SELL ka matlab hai higher timeframes aligned hain, but lower timeframe confirmation chahiye. Right entry ke liye patient rahiye."

    if "why" in question and ("risk" in question or "stop" in question or "empty" in question):
        if signal == "HOLD":
            return "Risk levels sirf BUY ya SELL confirmed signal par calculate hoti hain. HOLD par stop loss aur take profit active nahi hote. Ye favorable conditions mein trading avoid karne ke liye hai."
        elif "wait" in signal:
            return "WAIT signals ke liye entry abhi confirmed nahi hai. Lower-timeframe confirmation ka wait karein risk levels calculate karne se pehle."
        else:
            return f"Risk ATR (volatility) use karke calculate hota hai. Stop loss 1.5 ATR away, take profit 3 ATR away. Current risk/reward ratio: {risk_reward}"

    if "what is" in question:
        if "xau" in question or "gold" in question:
            return "XAU/USD Gold vs US Dollar hai. Ye commodity pair hai jo gold price ko dollars mein show karta hai. Gold often USD strength ke opposite move karta hai."
        elif "xag" in question or "silver" in question:
            return "XAG/USD Silver vs US Dollar hai. Silver gold se zyada volatile hota hai aur industrial demand par depend karta hai."
        elif "timeframe" in question:
            return "Timeframe candle period hai (5m=5 minutes, 1h=1 hour, etc.). Higher timeframes long-term trends show karte hain, lower timeframes short-term movements."
        elif "confidence" in question:
            return f"Confidence signal ki belief hai (0-100%). Current confidence: {confidence:.1f}%. Higher better hai, but kabhi 100% guaranteed nahi."
        elif "spread" in question:
            return "Spread bid aur ask prices ka difference hai. Real trading mein costs ke liye important hai."
        elif "atr" in question:
            return "ATR (Average True Range) volatility ko measure karta hai. Stop loss aur take profit distances set karne ke liye use hota hai."

    if "should i" in question or "can i" in question or "trade now" in question:
        return "Main trading advice nahi de sakta. Ye educational analysis hai. Kabhi bhi afford karne se zyada risk mat lo. Pehle paper trading try karein."

    if "real" in question and "time" in question:
        return "Ye near-real-time market analysis hai jo latest available candles aur API updates par based hai. Ye guaranteed future prediction nahi hai."

    if "explain" in question and "signal" in question:
        explanation = f"Current signal: {signal}. "
        if signal == "HOLD":
            explanation += "Higher timeframe trend mixed hai aur lower timeframe confirmation weak hai. System risky entry avoid kar raha hai."
        elif signal == "BUY":
            explanation += f"Bullish movement support karte hain conditions, but stop loss aur risk control use karein."
        elif signal == "STRONG BUY":
            explanation += f"Very bullish - 1D, 4H, 1H, 15M sab align hain. {confidence:.1f}% confidence."
        elif signal == "SELL":
            explanation += f"Bearish movement support karte hain conditions, but stop loss aur risk control use karein."
        elif signal == "STRONG SELL":
            explanation += f"Very bearish - 1D, 4H, 1H, 15M sab align hain. {confidence:.1f}% confidence."
        elif "WAIT_FOR_BUY" in signal:
            explanation += "Higher timeframes bullish, but 5M confirm nahi kar raha. Lower timeframe alignment ka wait karein."
        elif "WAIT_FOR_SELL" in signal:
            explanation += "Higher timeframes bearish, but 5M confirm nahi kar raha. Lower timeframe alignment ka wait karein."
        return explanation

    # Default responses
    if signal == "HOLD":
        return "Current signal HOLD hai - abhi koi active trade recommended nahi. Aksar ye safest choice hota hai uncertain markets mein."
    elif "BUY" in signal:
        return f"Analysis {signal} suggest karta hai {confidence:.1f}% confidence ke saath. Remember, ye financial advice nahi hai - proper risk management use karein."
    elif "SELL" in signal:
        return f"Analysis {signal} suggest karta hai {confidence:.1f}% confidence ke saath. Remember, ye financial advice nahi hai - proper risk management use karein."
    elif "WAIT" in signal:
        return f"Signal {signal} hai - higher timeframes aligned but confirmation ka wait karo. Forex mein patience key hai."

    return "Main forex concepts aur signals explain karne mein help kar sakta hoon. HOLD kya matlab hai? Risk kyun empty hai? XAU/USD kya hai? Pucho!"