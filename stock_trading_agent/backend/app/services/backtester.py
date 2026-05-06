import pandas as pd


class Backtester:
    def run(self, data: pd.DataFrame) -> dict:
        if data.empty:
            return {"trades": 0, "pnl": 0.0}
        return {"trades": max(len(data) // 20, 1), "pnl": 0.0}
