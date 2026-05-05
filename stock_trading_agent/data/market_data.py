"""Market data provider with optional API clients and safe fallbacks."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd

from config import Settings
from features.indicators import add_indicators


class MarketDataProvider:
    """Fetch OHLCV data while gracefully handling missing optional dependencies."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def get_ohlcv(self, symbol: str, period: str = "5d", interval: str = "5m") -> pd.DataFrame:
        for provider in self.settings.provider_priority():
            fetcher = {
                "polygon": self._fetch_polygon,
                "alpaca": self._fetch_alpaca,
                "finnhub": self._fetch_finnhub,
                "yfinance": self._fetch_yfinance,
            }.get(provider)

            if fetcher is None:
                continue

            frame = fetcher(symbol, period, interval)
            if frame is not None and not frame.empty:
                return self._normalize(frame)

        return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

    def get_multi_timeframe_data(self, symbol: str) -> dict:
        """Fetch multiple timeframes and attach indicators.

        Returns a dict with keys: '5m', '15m', '1h', '1d'. Each value is a DataFrame (may be empty).
        """
        out: dict = {}
        specs = {
            "5m": ("5d", "5m"),
            "15m": ("5d", "15m"),
            "1h": ("1mo", "1h"),
            "1d": ("6mo", "1d"),
        }

        for key, (period, interval) in specs.items():
            try:
                df = self.get_ohlcv(symbol, period=period, interval=interval)
                if df is None or df.empty:
                    out[key] = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
                    continue
                try:
                    df = add_indicators(df)
                except Exception:
                    # If indicators fail, keep raw frame but ensure expected columns exist
                    pass
                out[key] = df
            except Exception:
                out[key] = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

        return out

    def _fetch_yfinance(self, symbol: str, period: str, interval: str) -> pd.DataFrame | None:
        try:
            import yfinance as yf

            frame = yf.download(symbol, period=period, interval=interval, auto_adjust=False, progress=False)
            return frame
        except Exception:
            return None

    def _fetch_polygon(self, symbol: str, period: str, interval: str) -> pd.DataFrame | None:
        if not self.settings.polygon_api_key:
            return None

        try:
            from polygon import RESTClient
        except ImportError:
            return None

        multiplier, timespan = self._polygon_interval(interval)
        start_date, end_date = self._estimate_range(period)

        try:
            client = RESTClient(api_key=self.settings.polygon_api_key)
            bars = client.list_aggs(
                ticker=symbol,
                multiplier=multiplier,
                timespan=timespan,
                from_=start_date,
                to=end_date,
                limit=50000,
            )

            rows = []
            for bar in bars:
                rows.append(
                    {
                        "Date": datetime.fromtimestamp(bar.timestamp / 1000, tz=timezone.utc),
                        "Open": bar.open,
                        "High": bar.high,
                        "Low": bar.low,
                        "Close": bar.close,
                        "Volume": bar.volume,
                    }
                )

            if not rows:
                return None

            frame = pd.DataFrame(rows).set_index("Date")
            return frame
        except Exception:
            return None

    def _fetch_alpaca(self, symbol: str, period: str, interval: str) -> pd.DataFrame | None:
        if not (self.settings.alpaca_api_key and self.settings.alpaca_secret_key):
            return None

        try:
            from alpaca.data.historical import StockHistoricalDataClient
            from alpaca.data.requests import StockBarsRequest
            from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
        except ImportError:
            return None

        tf = self._alpaca_timeframe(interval, TimeFrame, TimeFrameUnit)
        start_date, end_date = self._estimate_range(period)
        try:
            client = StockHistoricalDataClient(
                api_key=self.settings.alpaca_api_key,
                secret_key=self.settings.alpaca_secret_key,
            )
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=tf,
                start=datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc),
                end=datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc),
            )
            bars = client.get_stock_bars(request)
            frame = bars.df
            if frame.empty:
                return None

            if isinstance(frame.index, pd.MultiIndex):
                frame = frame.xs(symbol, level=0, drop_level=True)

            rename_map = {
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume",
            }
            frame = frame.rename(columns=rename_map)
            return frame
        except Exception:
            return None

    def _fetch_finnhub(self, symbol: str, period: str, interval: str) -> pd.DataFrame | None:
        if not self.settings.finnhub_api_key:
            return None

        try:
            import finnhub
        except ImportError:
            return None

        resolution = self._finnhub_resolution(interval)
        start_date, end_date = self._estimate_range(period)
        start_ts = int(datetime.fromisoformat(start_date).replace(tzinfo=timezone.utc).timestamp())
        end_ts = int(datetime.fromisoformat(end_date).replace(tzinfo=timezone.utc).timestamp())

        try:
            client = finnhub.Client(api_key=self.settings.finnhub_api_key)
            data = client.stock_candles(symbol, resolution, start_ts, end_ts)
            if data.get("s") != "ok":
                return None

            frame = pd.DataFrame(
                {
                    "Date": pd.to_datetime(data["t"], unit="s", utc=True),
                    "Open": data["o"],
                    "High": data["h"],
                    "Low": data["l"],
                    "Close": data["c"],
                    "Volume": data["v"],
                }
            ).set_index("Date")
            return frame
        except Exception:
            return None

    @staticmethod
    def _normalize(frame: pd.DataFrame) -> pd.DataFrame:
        # yfinance may return MultiIndex columns, e.g. ('Open', 'AAPL').
        normalized_names: dict[object, str] = {}
        for col in frame.columns:
            if isinstance(col, tuple):
                parts = [str(part) for part in col if part is not None and str(part).strip()]
                flat = "_".join(parts).lower()
            else:
                flat = str(col).lower()
            normalized_names[col] = flat

        lookup: dict[str, list[str]] = {
            "Open": ["open"],
            "High": ["high"],
            "Low": ["low"],
            "Close": ["close"],
            "Volume": ["volume"],
        }

        clean = pd.DataFrame(index=frame.index)
        for target, options in lookup.items():
            for option in options:
                match = next(
                    (
                        original
                        for original, normalized in normalized_names.items()
                        if normalized == option or normalized.startswith(f"{option}_")
                    ),
                    None,
                )
                if match is not None:
                    clean[target] = frame[match]
                    break

        required = ["Open", "High", "Low", "Close", "Volume"]
        if not all(col in clean.columns for col in required):
            return pd.DataFrame(columns=required)

        clean = clean[required].dropna()
        clean = clean.sort_index()
        return clean

    @staticmethod
    def _estimate_range(period: str) -> tuple[str, str]:
        now = datetime.now(timezone.utc)
        value = period.strip().lower()
        if value.endswith("d"):
            delta = timedelta(days=max(int(value[:-1]), 1))
        elif value.endswith("mo"):
            delta = timedelta(days=30 * max(int(value[:-2]), 1))
        elif value.endswith("y"):
            delta = timedelta(days=365 * max(int(value[:-1]), 1))
        else:
            delta = timedelta(days=5)

        start = (now - delta).date().isoformat()
        end = now.date().isoformat()
        return start, end

    @staticmethod
    def _polygon_interval(interval: str) -> tuple[int, str]:
        value = interval.strip().lower()
        if value.endswith("m") and value[:-1].isdigit():
            return int(value[:-1]), "minute"
        if value.endswith("h") and value[:-1].isdigit():
            return int(value[:-1]), "hour"
        if value == "1d":
            return 1, "day"
        return 5, "minute"

    @staticmethod
    def _finnhub_resolution(interval: str) -> str:
        value = interval.strip().lower()
        if value.endswith("m") and value[:-1].isdigit():
            return value[:-1]
        if value.endswith("h") and value[:-1].isdigit():
            minutes = int(value[:-1]) * 60
            return str(minutes)
        if value == "1d":
            return "D"
        return "5"

    @staticmethod
    def _alpaca_timeframe(interval: str, timeframe_cls, unit_cls):
        value = interval.strip().lower()
        if value.endswith("m") and value[:-1].isdigit():
            return timeframe_cls(int(value[:-1]), unit_cls.Minute)
        if value.endswith("h") and value[:-1].isdigit():
            return timeframe_cls(int(value[:-1]), unit_cls.Hour)
        return timeframe_cls(1, unit_cls.Day)
