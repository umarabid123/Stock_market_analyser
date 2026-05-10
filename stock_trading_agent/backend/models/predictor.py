"""Internal prediction logic for the analysis-only trading assistant."""

from __future__ import annotations

import pandas as pd


class Predictor:
    """Simple internal signal model for reusable market analysis."""

    def predict(self, data: pd.DataFrame) -> dict:
        latest = data.iloc[-1]
        bullish_score = 0.0
        bearish_score = 0.0
        reasons: list[str] = []

        if latest.get("EMA_20", 0) > latest.get("EMA_50", 0):
            bullish_score += 1.0
            reasons.append("EMA 20 is above EMA 50")
        else:
            bearish_score += 1.0
            reasons.append("EMA 20 is below EMA 50")

        if latest.get("Close", 0) > latest.get("SMA_200", 0):
            bullish_score += 1.0
            reasons.append("price is above the 200-period trend")
        else:
            bearish_score += 1.0
            reasons.append("price is below the 200-period trend")

        rsi = latest.get("RSI_14", 50)
        if rsi < 35:
            bullish_score += 0.75
            reasons.append("RSI suggests a potential rebound")
        elif rsi > 65:
            bearish_score += 0.75
            reasons.append("RSI suggests stretched momentum")

        momentum = latest.get("Momentum_5", 0)
        if momentum > 0:
            bullish_score += 1.0
            reasons.append("recent momentum is positive")
        else:
            bearish_score += 1.0
            reasons.append("recent momentum is negative")

        macd_hist = latest.get("MACD_HIST", 0)
        if macd_hist > 0:
            bullish_score += 0.75
            reasons.append("MACD histogram is supportive")
        elif macd_hist < 0:
            bearish_score += 0.75
            reasons.append("MACD histogram is soft")

        close = latest.get("Close", 0)
        bb_upper = latest.get("BB_UPPER")
        bb_lower = latest.get("BB_LOWER")
        if bb_upper is not None and close > bb_upper:
            bullish_score += 0.5
            reasons.append("price is pressing above the upper Bollinger band")
        elif bb_lower is not None and close < bb_lower:
            bearish_score += 0.5
            reasons.append("price is pressing below the lower Bollinger band")

        volume = latest.get("Volume", 0)
        volume_avg = latest.get("Volume_SMA_20", 0)
        if volume_avg and volume > volume_avg * 1.15:
            bullish_score += 0.25
            bearish_score += 0.25
            reasons.append("volume is elevated and confirms participation")

        score_gap = bullish_score - bearish_score
        if score_gap > 1.5:
            signal = "BUY"
            bias = "BULLISH"
        elif score_gap < -1.5:
            signal = "SELL"
            bias = "BEARISH"
        else:
            signal = "HOLD"
            bias = "NEUTRAL"

        total = max(bullish_score + bearish_score, 1.0)
        confidence = min(1.0, abs(score_gap) / total)
        reason = "; ".join(reasons)

        return {
            "signal": signal,
            "bias": bias,
            "confidence": float(confidence),
            "reason": reason,
        }
