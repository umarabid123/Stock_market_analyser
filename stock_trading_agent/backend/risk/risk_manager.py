"""Risk management helpers for paper-trading analysis."""

from __future__ import annotations

from config import Settings


class RiskManager:
    """Create basic stop-loss/take-profit values and risk warnings."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.risk_reward_ratio = 2.0
        self.suggested_position_size_percent = 2

    def build_levels(
        self,
        signal: str,
        latest_price: float,
        atr_value: float,
        confidence: float = 0.0,
        session_volatility: str = "MEDIUM",
    ) -> dict:
        atr = atr_value if atr_value and atr_value > 0 else (latest_price * 0.01 if latest_price else 0.0)
        if atr <= 0 or latest_price <= 0:
            return {
                "entry_price": float(latest_price or 0.0),
                "stop_loss": None,
                "take_profit": None,
                "risk_reward_ratio": None,
                "suggested_lot_risk_percent": 0.5,
                "risk_warning": self._warning(),
            }

        direction = 0
        upper_signal = signal.upper()
        if upper_signal in {"BUY", "STRONG BUY", "WAIT_FOR_BUY"}:
            direction = 1
        elif upper_signal in {"SELL", "STRONG SELL", "WAIT_FOR_SELL"}:
            direction = -1

        if direction == 0:
            return {
                "entry_price": float(latest_price),
                "stop_loss": None,
                "take_profit": None,
                "risk_reward_ratio": None,
                "suggested_lot_risk_percent": round(max(0.25, 0.5 + confidence), 2),
                "risk_warning": self._warning(),
            }

        session_adjustment = 1.0
        if session_volatility.upper() == "HIGH":
            session_adjustment = 1.15
        elif session_volatility.upper() == "LOW":
            session_adjustment = 0.9

        stop_distance = atr * 1.5 * session_adjustment
        take_distance = atr * 3.0 * session_adjustment
        if upper_signal in {"STRONG BUY", "STRONG SELL"}:
            stop_distance = atr * 1.5 * session_adjustment  # Keep same for strong
            take_distance = atr * 3.0 * session_adjustment

        stop_loss = latest_price - (direction * stop_distance)
        take_profit = latest_price + (direction * take_distance)
        risk_reward_ratio = round(abs(take_distance / stop_distance), 2)
        suggested_lot_risk_percent = round(
            max(0.25, min(2.0, 0.5 + (confidence * 1.5) + (0.25 if session_volatility.upper() == "HIGH" else 0.0))),
            2,
        )

        return {
            "entry_price": float(latest_price),
            "stop_loss": float(stop_loss),
            "take_profit": float(take_profit),
            "risk_reward_ratio": risk_reward_ratio,
            "suggested_lot_risk_percent": suggested_lot_risk_percent,
            "risk_warning": self._warning(),
        }

    @staticmethod
    def _warning() -> str:
        return "This platform provides AI-assisted market analysis and probability-based trading signals for educational and research purposes only. It does not guarantee profit or future market prediction."
