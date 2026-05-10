"""Optional live market refresh helper for dashboard updates.

This module only streams live bars/prices for display purposes.
It does not place orders or execute real-money trading.
"""

from __future__ import annotations

import threading
import time
from typing import Any, Callable, Optional

from config import Settings, settings
from data.market_data import MarketDataProvider


class LiveMarketStreamer:
    """Background poller for live bar updates."""

    def __init__(self, app_settings: Settings | None = None, poll_seconds: int = 5) -> None:
        self.settings = app_settings or settings
        self.poll_seconds = poll_seconds
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._running_symbol: Optional[str] = None
        self._latest_bar: Optional[dict[str, Any]] = None
        self._on_bar_callback: Optional[Callable[[Any], Any]] = None
        self.last_error: Optional[str] = None

    @property
    def latest_bar(self) -> Optional[dict[str, Any]]:
        with self._lock:
            return None if self._latest_bar is None else dict(self._latest_bar)

    def start_stream(self, symbol: str, on_bar_callback: Callable[[Any], Any]) -> Optional[str]:
        """Start a live polling loop for one symbol."""
        symbol = (symbol or "").strip().upper()
        if not symbol:
            self.last_error = "Symbol is required for live streaming"
            return self.last_error

        # Reuse the existing stream when already running for the same symbol.
        if self._thread and self._thread.is_alive() and self._running_symbol == symbol:
            return None

        self.stop_stream()

        self.last_error = None
        self._running_symbol = symbol
        self._on_bar_callback = on_bar_callback
        self._thread = threading.Thread(target=self._run_stream, daemon=True)
        self._thread.start()
        return None

    def stop_stream(self) -> None:
        """Stop the live stream without raising."""
        self._running_symbol = None
        self._on_bar_callback = None

        thread = self._thread
        if thread is not None and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=1.0)
        self._thread = None

    def _run_stream(self) -> None:
        provider = MarketDataProvider(self.settings)
        try:
            while self._running_symbol:
                frame = provider.get_ohlcv(self._running_symbol, period="1d", interval="1m")
                if frame is not None and not frame.empty:
                    latest = frame.iloc[-1]
                    bar_data = self._normalize_bar(
                        {
                            "symbol": self._running_symbol,
                            "timestamp": frame.index[-1].isoformat() if hasattr(frame.index[-1], "isoformat") else frame.index[-1],
                            "open": latest.get("Open"),
                            "high": latest.get("High"),
                            "low": latest.get("Low"),
                            "close": latest.get("Close"),
                            "volume": latest.get("Volume"),
                        }
                    )
                    with self._lock:
                        self._latest_bar = bar_data
                    callback = self._on_bar_callback
                    if callback is not None:
                        try:
                            callback(bar_data)
                        except Exception:
                            pass
                time.sleep(self.poll_seconds)
        except Exception as exc:
            self.last_error = f"Live stream stopped: {exc}"
        finally:
            self._thread = None

    @staticmethod
    def _normalize_bar(bar: Any) -> dict[str, Any]:
        """Convert bar objects or raw dicts into a compact dict."""
        if isinstance(bar, dict):
            timestamp = bar.get("t") or bar.get("timestamp")
            open_price = bar.get("o") or bar.get("open")
            high = bar.get("h") or bar.get("high")
            low = bar.get("l") or bar.get("low")
            close = bar.get("c") or bar.get("close")
            volume = bar.get("v") or bar.get("volume")
            symbol = bar.get("S") or bar.get("symbol")
        else:
            timestamp = getattr(bar, "timestamp", None)
            open_price = getattr(bar, "open", None)
            high = getattr(bar, "high", None)
            low = getattr(bar, "low", None)
            close = getattr(bar, "close", None)
            volume = getattr(bar, "volume", None)
            symbol = getattr(bar, "symbol", None)

        return {
            "symbol": symbol,
            "timestamp": timestamp,
            "open": open_price,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
