from __future__ import annotations


class RiskManager:
    def __init__(self, settings=None) -> None:
        self.settings = settings
        self.risk_reward_ratio = 2.0
        self.suggested_position_size_percent = 2

    def build_levels(self, signal: str, latest_price: float, atr_value: float) -> tuple[float | None, float | None, str]:
        atr = atr_value if atr_value and atr_value > 0 else (latest_price * 0.01 if latest_price else 0.0)

        if signal == "BUY":
            stop_loss = latest_price - (1.5 * atr)
            take_profit = latest_price + (3.0 * atr)
        elif signal == "SELL":
            stop_loss = latest_price + (1.5 * atr)
            take_profit = latest_price - (3.0 * atr)
        else:
            stop_loss = None
            take_profit = None

        warning = "This is a paper-trading decision-support signal only. It is not financial advice."

        return (None if stop_loss is None else float(stop_loss)), (None if take_profit is None else float(take_profit)), warning
