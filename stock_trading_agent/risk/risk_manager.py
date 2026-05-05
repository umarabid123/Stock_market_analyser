"""Risk management helpers."""

from __future__ import annotations

from config import Settings


class RiskManager:
    """Create basic stop-loss/take-profit values and risk warnings."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def build_levels(self, signal: str, latest_price: float, atr_value: float) -> tuple[float, float, str]:
        atr = atr_value if atr_value and atr_value > 0 else latest_price * 0.01

        if signal == "BUY":
            stop_loss = latest_price - (1.5 * atr)
            take_profit = latest_price + (2.0 * atr)
        elif signal == "SELL":
            stop_loss = latest_price + (1.5 * atr)
            take_profit = latest_price - (2.0 * atr)
        else:
            stop_loss = latest_price - (1.0 * atr)
            take_profit = latest_price + (1.0 * atr)

        warning = "Paper trading mode is ON. Do not treat this as guaranteed profit."
        if not self.settings.paper_trading_only:
            warning = "Live trading enabled. Validate risk carefully; no guaranteed profit."

        return float(stop_loss), float(take_profit), warning
