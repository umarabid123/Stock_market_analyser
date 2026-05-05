"""Indicator calculations used by the strategy engine."""

from __future__ import annotations

import numpy as np
import pandas as pd


def add_indicators(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy()
    frame["SMA_20"] = frame["Close"].rolling(20, min_periods=5).mean()
    frame["SMA_50"] = frame["Close"].rolling(50, min_periods=10).mean()
    frame["EMA_20"] = frame["Close"].ewm(span=20, adjust=False).mean()
    frame["RSI_14"] = _rsi(frame["Close"], period=14)
    frame["ATR_14"] = _atr(frame, period=14)
    frame["Momentum_5"] = frame["Close"].pct_change(5)
    frame["Volume_SMA_20"] = frame["Volume"].rolling(20, min_periods=5).mean()
    return frame


def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = np.where(delta > 0, delta, 0.0)
    loss = np.where(delta < 0, -delta, 0.0)
    avg_gain = pd.Series(gain, index=series.index).rolling(period, min_periods=period).mean()
    avg_loss = pd.Series(loss, index=series.index).rolling(period, min_periods=period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def _atr(frame: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = frame["High"] - frame["Low"]
    high_close = (frame["High"] - frame["Close"].shift(1)).abs()
    low_close = (frame["Low"] - frame["Close"].shift(1)).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period, min_periods=period).mean()


def get_volume_strength(df: pd.DataFrame) -> str:
    """Return 'STRONG' if latest volume > Volume_SMA_20 else 'WEAK'."""
    if "Volume_SMA_20" not in df.columns:
        return "WEAK"
    latest = df.iloc[-1]
    vol = latest.get("Volume", 0)
    vma = latest.get("Volume_SMA_20", 0)
    try:
        if vol > vma and vma > 0:
            return "STRONG"
    except Exception:
        pass
    return "WEAK"
