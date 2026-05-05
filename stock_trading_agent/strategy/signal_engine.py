"""Signal engine combining indicators, predictor, and risk logic."""

from __future__ import annotations

import pandas as pd

from config import Settings
from features.indicators import add_indicators
from models.predictor import Predictor
from risk.risk_manager import RiskManager


class SignalEngine:
    """Generate trading signals from internal computations."""

    def __init__(self, settings: Settings) -> None:
        self.predictor = Predictor()
        self.risk_manager = RiskManager(settings)

    def generate_signal(self, symbol: str, data: pd.DataFrame) -> dict:
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
