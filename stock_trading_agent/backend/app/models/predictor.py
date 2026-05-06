import pandas as pd


class Predictor:
    def predict(self, data: pd.DataFrame) -> dict:
        latest = data.iloc[-1]
        bullish_score = 0
        bearish_score = 0
        reasons: list[str] = []

        if latest.get("SMA_20", 0) > latest.get("SMA_50", 0):
            bullish_score += 1
            reasons.append("short trend above long trend")
        else:
            bearish_score += 1
            reasons.append("short trend below long trend")

        rsi = latest.get("RSI_14", 50)
        if rsi < 35:
            bullish_score += 1
            reasons.append("RSI indicates potential rebound")
        elif rsi > 65:
            bearish_score += 1
            reasons.append("RSI indicates possible cooldown")

        momentum = latest.get("Momentum_5", 0)
        if momentum > 0:
            bullish_score += 1
            reasons.append("recent momentum is positive")
        else:
            bearish_score += 1
            reasons.append("recent momentum is negative")

        if bullish_score > bearish_score:
            signal = "BUY"
        elif bearish_score > bullish_score:
            signal = "SELL"
        else:
            signal = "HOLD"

        total = max(bullish_score + bearish_score, 1)
        confidence = max(bullish_score, bearish_score) / total
        reason = "; ".join(reasons)

        return {
            "signal": signal,
            "confidence": float(confidence),
            "reason": reason,
        }
