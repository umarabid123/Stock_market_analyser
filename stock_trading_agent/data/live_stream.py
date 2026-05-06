"""Live market data streaming for dashboard refresh.

This module only streams live bars/prices for display purposes.
It does not place orders or execute real-money trading.
"""

from __future__ import annotations

import inspect
import os
import threading
from typing import Any, Callable, Optional


class LiveMarketStreamer:
    """Background Alpaca WebSocket streamer for live bar updates."""

    def __init__(self) -> None:
        self._stream = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._running_symbol: Optional[str] = None
        self._latest_bar: Optional[dict[str, Any]] = None
        self.last_error: Optional[str] = None

    @property
    def latest_bar(self) -> Optional[dict[str, Any]]:
        with self._lock:
            return None if self._latest_bar is None else dict(self._latest_bar)

    def start_stream(self, symbol: str, on_bar_callback: Callable[[Any], Any]) -> Optional[str]:
        """Start a live bar stream for one symbol.

        Returns a clear error message when Alpaca is unavailable, or None on success.
        """
        symbol = (symbol or "").strip().upper()
        if not symbol:
            self.last_error = "Symbol is required for live streaming"
            return self.last_error

        # Reuse the existing stream when already running for the same symbol.
        if self._thread and self._thread.is_alive() and self._running_symbol == symbol:
            return None

        self.stop_stream()

        api_key = os.getenv("ALPACA_API_KEY", "").strip()
        secret_key = os.getenv("ALPACA_SECRET_KEY", "").strip()
        if not api_key or not secret_key:
            self.last_error = (
                "Live stream unavailable: ALPACA_API_KEY and ALPACA_SECRET_KEY must be configured"
            )
            return self.last_error

        try:
            from alpaca.data.enums import DataFeed
            from alpaca.data.live import StockDataStream
        except Exception:
            self.last_error = "Live stream unavailable: alpaca-py is not installed"
            return self.last_error

        async def _bar_handler(bar: Any) -> None:
            bar_data = self._normalize_bar(bar)
            with self._lock:
                self._latest_bar = bar_data
            result = on_bar_callback(bar_data)
            if inspect.isawaitable(result):
                await result

        try:
            self._stream = StockDataStream(api_key, secret_key, feed=DataFeed.IEX)
            self._stream.subscribe_bars(_bar_handler, symbol)
        except Exception as exc:
            self._stream = None
            self.last_error = f"Live stream unavailable: {exc}"
            return self.last_error

        self.last_error = None
        self._running_symbol = symbol
        self._thread = threading.Thread(target=self._run_stream, daemon=True)
        self._thread.start()
        return None

    def stop_stream(self) -> None:
        """Stop the live stream without raising."""
        stream = self._stream
        self._stream = None
        self._running_symbol = None

        if stream is not None:
            try:
                stream.stop()
            except Exception:
                pass

        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=1.0)
        self._thread = None

    def _run_stream(self) -> None:
        try:
            if self._stream is not None:
                self._stream.run()
        except Exception as exc:
            self.last_error = f"Live stream stopped: {exc}"
        finally:
            self._stream = None
            self._thread = None

    @staticmethod
    def _normalize_bar(bar: Any) -> dict[str, Any]:
        """Convert Alpaca bar objects or raw dicts into a compact dict."""
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
