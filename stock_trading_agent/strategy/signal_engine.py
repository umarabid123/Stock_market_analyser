"""Signal engine combining indicators, predictor, and risk logic."""

from __future__ import annotations

import pandas as pd

from config import Settings
from features.indicators import add_indicators
from models.predictor import Predictor
from risk.risk_manager import RiskManager
from features.indicators import get_volume_strength
from features.sentiment import get_news_sentiment
from typing import Dict, Any


def detect_trend(df: pd.DataFrame) -> str:
    """Detect simple trend based on EMA_20, SMA_50 and Close.

    Returns: 'UP', 'DOWN', or 'SIDEWAYS'
    """
    if df is None or df.empty:
        return "SIDEWAYS"
    latest = df.iloc[-1]
    ema = latest.get("EMA_20")
    sma50 = latest.get("SMA_50")
    close = latest.get("Close")
    try:
        if ema is None or sma50 is None or close is None:
            return "SIDEWAYS"
        if ema > sma50 and close > ema:
            return "UP"
        if ema < sma50 and close < ema:
            return "DOWN"
    except Exception:
        return "SIDEWAYS"
    return "SIDEWAYS"


class SignalEngine:
    """Generate trading signals from internal computations."""

    def __init__(self, settings: Settings) -> None:
        self.predictor = Predictor()
        self.risk_manager = RiskManager(settings)

    def _safe_predict(self, df: pd.DataFrame) -> dict:
        try:
            featured = add_indicators(df)
            featured = featured.dropna()
            if featured.empty:
                return {"signal": "HOLD", "confidence": 0.0, "reason": "Insufficient data"}
            return self.predictor.predict(featured)
        except Exception:
            return {"signal": "HOLD", "confidence": 0.0, "reason": "Prediction error"}

    def generate_signal(self, symbol: str, data: pd.DataFrame | Dict[str, pd.DataFrame]) -> dict:
        """Generate a multi-factor signal. 'data' may be a dict of timeframes from MarketDataProvider.get_multi_timeframe_data.

        If a single DataFrame is provided, fall back to the legacy behavior.
        """
        # If single-frame input, keep legacy flow but use new risk manager
        if isinstance(data, pd.DataFrame):
            return self._generate_single_frame(symbol, data)

        # Expecting dict with keys '5m','15m','1h','1d'
        tf = data
        trends = {k: detect_trend(v) for k, v in tf.items()}

        # pick entry frame for prediction: prefer 15m then 5m then 1h
        entry_df = None
        for candidate_key in ("15m", "5m", "1h"):
            candidate_df = tf.get(candidate_key)
            if candidate_df is not None and not candidate_df.empty:
                entry_df = candidate_df
                break

        prediction = (
            self._safe_predict(entry_df)
            if entry_df is not None and not entry_df.empty
            else {"signal": "HOLD", "confidence": 0.0, "reason": "No entry data"}
        )

        # Multi-timeframe confirmation
        tf_1h = trends.get("1h", "SIDEWAYS")
        tf_1d = trends.get("1d", "SIDEWAYS")
        tf_15m = trends.get("15m", "SIDEWAYS")
        tf_5m = trends.get("5m", "SIDEWAYS")

        final_signal = "HOLD"
        if tf_1h == "UP" and (tf_15m == "UP" or tf_5m == "UP"):
            final_signal = "BUY"
        elif tf_1h == "DOWN" and (tf_15m == "DOWN" or tf_5m == "DOWN"):
            final_signal = "SELL"
        else:
            final_signal = "HOLD"

        # Base confidence from predictor
        confidence = float(prediction.get("confidence", 0.0))

        # Volume strength from entry timeframe (prefer 5m)
        vol_df = tf.get("5m")
        if vol_df is None or vol_df.empty:
            vol_df = entry_df
        vol_strength = "WEAK"
        try:
            if vol_df is not None and not vol_df.empty:
                vol_strength = get_volume_strength(vol_df)
        except Exception:
            vol_strength = "WEAK"

        if vol_strength == "STRONG":
            confidence += 0.10
        else:
            confidence -= 0.05

        # News sentiment
        sentiment = get_news_sentiment(symbol)
        sent = sentiment.get("sentiment", "UNAVAILABLE")
        if sent == "POSITIVE" and final_signal == "BUY":
            confidence += 0.05
        if sent == "NEGATIVE" and final_signal == "BUY":
            confidence -= 0.05
        if sent == "NEGATIVE" and final_signal == "SELL":
            confidence += 0.05

        # 1d confirmation adjusts confidence
        if tf_1d == final_signal.replace("BUY", "UP").replace("SELL", "DOWN") or (
            tf_1d == "UP" and final_signal == "BUY"
        ):
            confidence += 0.10
        elif tf_1d != "SIDEWAYS" and ((tf_1d == "UP" and final_signal == "SELL") or (tf_1d == "DOWN" and final_signal == "BUY")):
            confidence -= 0.10

        confidence = max(0.0, min(1.0, confidence))

        # ATR for risk levels from entry frame
        atr_value = 0.0
        latest_price = None
        if entry_df is not None and not entry_df.empty:
            last = entry_df.iloc[-1]
            latest_price = float(last.get("Close", 0.0))
            atr_value = float(last.get("ATR_14", 0.0) or 0.0)

        if final_signal == "HOLD":
            stop_loss = None
            take_profit = None
        else:
            stop_loss, take_profit, _ = self.risk_manager.build_levels(final_signal, latest_price or 0.0, atr_value)

        reason_parts = [prediction.get("reason", "")]
        reason_parts.append(f"Trends: 5m={tf_5m},15m={tf_15m},1h={tf_1h},1d={tf_1d}")
        reason_parts.append(f"Volume: {vol_strength}")
        if sent != "UNAVAILABLE":
            reason_parts.append(f"News: {sent} ({sentiment.get('score',0)})")

        reason = "; ".join([p for p in reason_parts if p])

        risk_warning = "This is a paper-trading decision-support signal only. It is not financial advice."

        return {
            "symbol": symbol,
            "latest_price": latest_price or 0.0,
            "signal": final_signal,
            "confidence": confidence,
            "prediction_direction": final_signal,
            "trend_5m": tf_5m,
            "trend_15m": tf_15m,
            "trend_1h": tf_1h,
            "trend_1d": tf_1d,
            "volume_strength": vol_strength,
            "news_sentiment": sentiment,
            "reason": reason,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "risk_warning": risk_warning,
        }

    def _generate_single_frame(self, symbol: str, data: pd.DataFrame) -> dict:
        featured = add_indicators(data)
        featured = featured.dropna()
        if featured.empty:
            last_close = float(data["Close"].iloc[-1])
            stop, take, warning = self.risk_manager.build_levels("HOLD", last_close, last_close * 0.01)
            return {
                "symbol": symbol,
                "latest_price": last_close,
                "signal": "HOLD",
                "confidence": 0.0,
                "reason": "Not enough data to compute indicators yet.",
                "stop_loss": stop,
                "take_profit": take,
                "risk_warning": warning,
            }

        prediction = self.predictor.predict(featured)
        latest = featured.iloc[-1]
        latest_price = float(latest["Close"])
        atr_value = float(latest.get("ATR_14", 0) or 0)
        stop, take, warning = self.risk_manager.build_levels(
            prediction["signal"], latest_price, atr_value
        )

        return {
            "symbol": symbol,
            "latest_price": latest_price,
            "signal": prediction["signal"],
            "confidence": prediction["confidence"],
            "reason": prediction["reason"],
            "stop_loss": stop,
            "take_profit": take,
            "risk_warning": warning,
        }
