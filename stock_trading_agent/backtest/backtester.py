"""Minimal backtesting scaffold."""

from __future__ import annotations

import pandas as pd


class Backtester:
    """Very small placeholder backtester for future expansion."""

    def run(self, data: pd.DataFrame) -> dict:
        if data.empty:
            return {"trades": 0, "pnl": 0.0}
        return {"trades": max(len(data) // 20, 1), "pnl": 0.0}
