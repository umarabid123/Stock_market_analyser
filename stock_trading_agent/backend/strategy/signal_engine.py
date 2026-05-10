"""Signal engine combining indicators, sentiment, session logic, and risk."""

from __future__ import annotations

from datetime import datetime, timezone
import pandas as pd

from config import Settings
from features.indicators import add_indicators, get_volume_strength
from models.predictor import Predictor
from risk.risk_manager import RiskManager
from features.sentiment import get_news_sentiment
from typing import Dict, Any


TIMEFRAME_WEIGHTS = {"5m": 1.0, "15m": 1.5, "1h": 2.0, "4h": 3.0, "1d": 4.0}


def detect_trend(df: pd.DataFrame) -> str:
    """Detect a trend label from core technical indicators."""
    if df is None or df.empty:
        return "NEUTRAL"
    latest = df.iloc[-1]
    ema = latest.get("EMA_20")
    ema50 = latest.get("EMA_50")
    sma200 = latest.get("SMA_200")
    macd_hist = latest.get("MACD_HIST")
    rsi = latest.get("RSI_14")
    close = latest.get("Close")
    try:
        if ema is None or ema50 is None or sma200 is None or close is None:
            return "NEUTRAL"
        bullish = 0
        bearish = 0
        if close > ema:
            bullish += 1
        else:
            bearish += 1
        if ema > ema50:
            bullish += 1
        else:
            bearish += 1
        if close > sma200:
            bullish += 1
        else:
            bearish += 1
        if macd_hist is not None and macd_hist > 0:
            bullish += 1
        elif macd_hist is not None and macd_hist < 0:
            bearish += 1
        if rsi is not None and rsi >= 60:
            bullish += 1
        elif rsi is not None and rsi <= 40:
            bearish += 1
        if bullish - bearish >= 2:
            return "BULLISH"
        if bearish - bullish >= 2:
            return "BEARISH"
    except Exception:
        return "NEUTRAL"
    return "NEUTRAL"


def _structure_from_frame(df: pd.DataFrame) -> dict[str, object]:
    if df is None or df.empty:
        return {
            "market_structure": "Neutral",
            "bos": "None",
            "liquidity_sweep": "None",
            "support_zone": (None, None),
            "resistance_zone": (None, None),
        }

    working = add_indicators(df)
    latest = working.iloc[-1]
    recent = working.tail(20)
    atr = float(latest.get("ATR_14", 0) or 0)
    support = float(recent["Low"].min()) if not recent.empty else float(latest.get("Low", 0) or 0)
    resistance = float(recent["High"].max()) if not recent.empty else float(latest.get("High", 0) or 0)
    prev_high = float(working["High"].tail(20).iloc[:-1].max()) if len(working) >= 2 else resistance
    prev_low = float(working["Low"].tail(20).iloc[:-1].min()) if len(working) >= 2 else support
    close = float(latest.get("Close", 0) or 0)
    high = float(latest.get("High", 0) or 0)
    low = float(latest.get("Low", 0) or 0)

    market_structure = "Bullish" if latest.get("EMA_20", 0) > latest.get("EMA_50", 0) and close >= latest.get("SMA_200", close) else "Bearish" if latest.get("EMA_20", 0) < latest.get("EMA_50", 0) and close <= latest.get("SMA_200", close) else "Neutral"
    bos = "Bullish BOS" if close > prev_high else "Bearish BOS" if close < prev_low else "None"
    liquidity_sweep = "Bearish sweep" if high > resistance and close < resistance else "Bullish sweep" if low < support and close > support else "None"

    padding = atr * 0.6 if atr > 0 else abs(close) * 0.002
    support_zone = (round(support - padding, 6), round(support + padding, 6)) if support else (None, None)
    resistance_zone = (round(resistance - padding, 6), round(resistance + padding, 6)) if resistance else (None, None)
    return {
        "market_structure": market_structure,
        "bos": bos,
        "liquidity_sweep": liquidity_sweep,
        "support_zone": support_zone,
        "resistance_zone": resistance_zone,
    }


def _market_session(now_utc: datetime | None = None) -> dict[str, str]:
    moment = now_utc or datetime.now(timezone.utc)
    hour = moment.hour
    active: list[str] = []

    if hour >= 21 or hour < 6:
        active.append("Sydney")
    if 23 <= hour or hour < 8:
        active.append("Tokyo")
    if 7 <= hour < 16:
        active.append("London")
    if 12 <= hour < 21:
        active.append("New York")

    if {"London", "New York"}.issubset(set(active)):
        volatility = "HIGH"
    elif "London" in active or "New York" in active:
        volatility = "MEDIUM"
    elif active:
        volatility = "LOW"
    else:
        active = ["Sydney"]
        volatility = "LOW"

    session_label = " / ".join(active[:2]) if len(active) > 1 else active[0]
    if {"London", "New York"}.issubset(set(active)):
        session_label = "London / New York Overlap"

    return {
        "active_session": session_label,
        "session_volatility": volatility,
        "current_time": moment.strftime("%H:%M UTC"),
    }


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

    @staticmethod
    def _get_frame(tf: Dict[str, pd.DataFrame], key: str) -> pd.DataFrame | None:
        frame = tf.get(key)
        if frame is not None and not frame.empty:
            return frame
        return None

    def _select_entry_frame(self, tf: Dict[str, pd.DataFrame]) -> pd.DataFrame | None:
        for candidate_key in ("15m", "1h", "5m", "4h"):
            frame = self._get_frame(tf, candidate_key)
            if frame is not None:
                return frame
        return None

    @staticmethod
    def _format_zone(zone: tuple[float | None, float | None]) -> str:
        low, high = zone
        if low is None or high is None:
            return "-"
        return f"{low:.5f} - {high:.5f}"

    @staticmethod
    def _weighted_bias(trends: Dict[str, str], keys: list[str]) -> float:
        value = 0.0
        for key in keys:
            weight = TIMEFRAME_WEIGHTS.get(key, 1.0)
            trend = trends.get(key, "NEUTRAL")
            if trend == "BULLISH":
                value += weight
            elif trend == "BEARISH":
                value -= weight
        return value

    @staticmethod
    def _classify_signal(higher_bias: float, confirmation_bias: float, trends: Dict[str, str]) -> str:
        bullish_count = sum(1 for value in trends.values() if value == "BULLISH")
        bearish_count = sum(1 for value in trends.values() if value == "BEARISH")

        if higher_bias > 0 and confirmation_bias > 0:
            return "STRONG BUY" if bullish_count >= 4 else "BUY"
        if higher_bias < 0 and confirmation_bias < 0:
            return "STRONG SELL" if bearish_count >= 4 else "SELL"
        if higher_bias > 0 and confirmation_bias <= 0:
            return "WAIT_FOR_BUY"
        if higher_bias < 0 and confirmation_bias >= 0:
            return "WAIT_FOR_SELL"
        return "HOLD"

    @staticmethod
    def _trend_strength(trends: Dict[str, str]) -> float:
        total = 0.0
        for key, trend in trends.items():
            weight = TIMEFRAME_WEIGHTS.get(key, 1.0)
            if trend == "BULLISH":
                total += weight
            elif trend == "BEARISH":
                total -= weight
        max_score = sum(TIMEFRAME_WEIGHTS.get(key, 1.0) for key in trends) or 1.0
        return round(abs(total) / max_score, 3)

    @staticmethod
    def _confidence_adjustments(base: float, final_signal: str, trends: Dict[str, str], sentiment: dict, volume_strength: str, session: dict, structure: dict) -> float:
        confidence = base
        higher_bias = sum(TIMEFRAME_WEIGHTS.get(key, 1.0) for key in ("1d", "4h", "1h") if trends.get(key) == "BULLISH") - sum(TIMEFRAME_WEIGHTS.get(key, 1.0) for key in ("1d", "4h", "1h") if trends.get(key) == "BEARISH")
        lower_bias = sum(TIMEFRAME_WEIGHTS.get(key, 1.0) for key in ("15m", "5m") if trends.get(key) == "BULLISH") - sum(TIMEFRAME_WEIGHTS.get(key, 1.0) for key in ("15m", "5m") if trends.get(key) == "BEARISH")

        if final_signal in {"BUY", "STRONG BUY"} and higher_bias > 0:
            confidence += 0.08
        if final_signal in {"SELL", "STRONG SELL"} and higher_bias < 0:
            confidence += 0.08
        if final_signal in {"WAIT_FOR_BUY", "WAIT_FOR_SELL"}:
            confidence -= 0.05
        if volume_strength == "STRONG":
            confidence += 0.08
        elif volume_strength == "MODERATE":
            confidence += 0.04
        else:
            confidence -= 0.03

        if session.get("session_volatility") == "HIGH":
            confidence += 0.08
        elif session.get("active_session") in {"London", "New York"}:
            confidence += 0.04

        sentiment_label = sentiment.get("sentiment", "UNAVAILABLE")
        if sentiment_label == "POSITIVE" and final_signal in {"BUY", "STRONG BUY", "WAIT_FOR_BUY"}:
            confidence += 0.05
        elif sentiment_label == "NEGATIVE" and final_signal in {"SELL", "STRONG SELL", "WAIT_FOR_SELL"}:
            confidence += 0.05
        elif sentiment_label == "NEGATIVE" and final_signal in {"BUY", "STRONG BUY"}:
            confidence -= 0.04
        elif sentiment_label == "POSITIVE" and final_signal in {"SELL", "STRONG SELL"}:
            confidence -= 0.04

        if structure.get("market_structure") == "Bullish" and final_signal in {"BUY", "STRONG BUY", "WAIT_FOR_BUY"}:
            confidence += 0.04
        if structure.get("market_structure") == "Bearish" and final_signal in {"SELL", "STRONG SELL", "WAIT_FOR_SELL"}:
            confidence += 0.04

        if lower_bias > 0 and final_signal in {"BUY", "STRONG BUY", "WAIT_FOR_BUY"}:
            confidence += 0.03
        if lower_bias < 0 and final_signal in {"SELL", "STRONG SELL", "WAIT_FOR_SELL"}:
            confidence += 0.03

        return max(0.0, min(1.0, confidence))

    def analyze_market(self, symbol: str, data: pd.DataFrame | Dict[str, pd.DataFrame]) -> dict:
        """Generate a multi-factor signal. 'data' may be a dict of timeframes from MarketDataProvider.get_multi_timeframe_data.

        If a single DataFrame is provided, fall back to the legacy behavior.
        """
        # If the input is not a dict of timeframes, keep the legacy single-frame flow.
        if not isinstance(data, dict):
            return self._generate_single_frame(symbol, data)

        # Expecting dict with keys '5m','15m','1h','4h','1d'
        tf: Dict[str, pd.DataFrame] = data
        trends = {k: detect_trend(v) for k, v in tf.items()}
        session = _market_session()
        structure = _structure_from_frame(self._select_entry_frame(tf))

        # pick entry frame for prediction: prefer 15m then 1h then 5m then 4h
        entry_df = self._select_entry_frame(tf)

        if entry_df is None:
            return {
                "symbol": symbol,
                "display_symbol": symbol,
                "latest_price": 0.0,
                "signal": "HOLD",
                "confidence": 0.0,
                "prediction_direction": "HOLD",
                "trend_5m": trends.get("5m", "SIDEWAYS"),
                "trend_15m": trends.get("15m", "SIDEWAYS"),
                "trend_1h": trends.get("1h", "SIDEWAYS"),
                "trend_4h": trends.get("4h", "SIDEWAYS"),
                "trend_1d": trends.get("1d", "SIDEWAYS"),
                "market_bias": "NEUTRAL",
                "trend_strength": 0.0,
                "volume_strength": "WEAK",
                "news_sentiment": {"sentiment": "UNAVAILABLE", "score": 0, "reason": "No entry data", "source": "Unavailable"},
                "market_structure": structure.get("market_structure", "Neutral"),
                "bos": structure.get("bos", "None"),
                "liquidity_sweep": structure.get("liquidity_sweep", "None"),
                "support_zone": structure.get("support_zone", (None, None)),
                "resistance_zone": structure.get("resistance_zone", (None, None)),
                "active_session": session["active_session"],
                "session_volatility": session["session_volatility"],
                "current_time": session["current_time"],
                "entry_price": 0.0,
                "reason": "No entry data",
                "stop_loss": None,
                "take_profit": None,
                "risk_reward_ratio": None,
                "suggested_lot_risk_percent": 0.5,
                "risk_warning": "This is a paper-trading decision-support signal only. It is not financial advice.",
            }

        prediction = self._safe_predict(entry_df)

        higher_bias = self._weighted_bias(trends, ["1d", "4h", "1h"])
        confirmation_bias = self._weighted_bias(trends, ["15m", "5m"])
        final_signal = self._classify_signal(higher_bias, confirmation_bias, trends)

        # Base confidence from predictor
        confidence = float(prediction.get("confidence", 0.0))

        # Volume strength from entry timeframe (prefer 5m)
        vol_df = self._get_frame(tf, "5m")
        if vol_df is None:
            vol_df = entry_df
        vol_strength = "WEAK"
        try:
            if vol_df is not None and not vol_df.empty:
                vol_strength = get_volume_strength(vol_df)
        except Exception:
            vol_strength = "WEAK"

        # News sentiment
        sentiment = get_news_sentiment(symbol)
        sent = sentiment.get("sentiment", "UNAVAILABLE")
        confidence = self._confidence_adjustments(confidence, final_signal, trends, sentiment, vol_strength, session, structure)

        market_bias = "BULLISH" if higher_bias > 0 else "BEARISH" if higher_bias < 0 else "NEUTRAL"
        trend_strength = self._trend_strength(trends)

        # ATR for risk levels from entry frame
        atr_value = 0.0
        latest_price = None
        if entry_df is not None and not entry_df.empty:
            last = entry_df.iloc[-1]
            latest_price = float(last.get("Close", 0.0))
            atr_value = float(last.get("ATR_14", 0.0) or 0.0)

        risk_profile = self.risk_manager.build_levels(
            final_signal,
            latest_price or 0.0,
            atr_value,
            confidence=confidence,
            session_volatility=session["session_volatility"],
        )

        reason_parts = [prediction.get("reason", "")]
        reason_parts.append(
            f"Trends: 5m={trends.get('5m', 'NEUTRAL')},15m={trends.get('15m', 'NEUTRAL')},1h={trends.get('1h', 'NEUTRAL')},4h={trends.get('4h', 'NEUTRAL')},1d={trends.get('1d', 'NEUTRAL')}"
        )
        reason_parts.append(f"Market bias: {market_bias}")
        reason_parts.append(f"Volume: {vol_strength}")
        reason_parts.append(f"Structure: {structure.get('market_structure')} | BOS: {structure.get('bos')}")
        reason_parts.append(f"Session: {session['active_session']} ({session['session_volatility']})")
        if sent != "UNAVAILABLE":
            reason_parts.append(f"News: {sent} ({sentiment.get('score',0)})")

        reason = "; ".join([p for p in reason_parts if p])

        return {
            "symbol": symbol,
            "display_symbol": symbol,
            "latest_price": latest_price or 0.0,
            "signal": final_signal,
            "confidence": confidence,
            "prediction_direction": final_signal,
            "trend_5m": trends.get("5m", "NEUTRAL"),
            "trend_15m": trends.get("15m", "NEUTRAL"),
            "trend_1h": trends.get("1h", "NEUTRAL"),
            "trend_4h": trends.get("4h", "NEUTRAL"),
            "trend_1d": trends.get("1d", "NEUTRAL"),
            "market_bias": market_bias,
            "trend_strength": trend_strength,
            "volume_strength": vol_strength,
            "news_sentiment": sentiment,
            "market_structure": structure.get("market_structure", "Neutral"),
            "bos": structure.get("bos", "None"),
            "liquidity_sweep": structure.get("liquidity_sweep", "None"),
            "support_zone": structure.get("support_zone", (None, None)),
            "resistance_zone": structure.get("resistance_zone", (None, None)),
            "active_session": session["active_session"],
            "session_volatility": session["session_volatility"],
            "current_time": session["current_time"],
            "entry_price": risk_profile["entry_price"],
            "reason": reason,
            "stop_loss": risk_profile["stop_loss"],
            "take_profit": risk_profile["take_profit"],
            "risk_reward_ratio": risk_profile["risk_reward_ratio"],
            "suggested_lot_risk_percent": risk_profile["suggested_lot_risk_percent"],
            "risk_warning": risk_profile["risk_warning"],
        }

    def _generate_single_frame(self, symbol: str, data: pd.DataFrame) -> dict:
        featured = add_indicators(data)
        featured = featured.dropna()
        if featured.empty:
            last_close = float(data["Close"].iloc[-1])
            risk = self.risk_manager.build_levels("HOLD", last_close, last_close * 0.01)
            return {
                "symbol": symbol,
                "display_symbol": symbol,
                "latest_price": last_close,
                "signal": "HOLD",
                "confidence": 0.0,
                "market_bias": "NEUTRAL",
                "trend_strength": 0.0,
                "reason": "Not enough data to compute indicators yet.",
                "stop_loss": risk["stop_loss"],
                "take_profit": risk["take_profit"],
                "risk_reward_ratio": risk["risk_reward_ratio"],
                "suggested_lot_risk_percent": risk["suggested_lot_risk_percent"],
                "risk_warning": risk["risk_warning"],
            }

        prediction = self.predictor.predict(featured)
        latest = featured.iloc[-1]
        latest_price = float(latest["Close"])
        atr_value = float(latest.get("ATR_14", 0) or 0)
        risk = self.risk_manager.build_levels(
            prediction["signal"], latest_price, atr_value, confidence=float(prediction.get("confidence", 0.0))
        )

        return {
            "symbol": symbol,
            "display_symbol": symbol,
            "latest_price": latest_price,
            "signal": prediction["signal"],
            "confidence": prediction["confidence"],
            "market_bias": prediction.get("bias", "NEUTRAL"),
            "trend_strength": 0.0,
            "reason": prediction["reason"],
            "stop_loss": risk["stop_loss"],
            "take_profit": risk["take_profit"],
            "risk_reward_ratio": risk["risk_reward_ratio"],
            "suggested_lot_risk_percent": risk["suggested_lot_risk_percent"],
            "risk_warning": risk["risk_warning"],
        }
