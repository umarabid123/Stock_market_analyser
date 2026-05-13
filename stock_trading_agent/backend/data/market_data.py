"""Market data provider with forex and commodity API fallbacks."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

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
                "twelvedata": self._fetch_twelvedata,
                "oanda": self._fetch_oanda,
                "alphavantage": self._fetch_alphavantage,
                "yfinance": self._fetch_yfinance,
            }.get(provider)

            if fetcher is None:
                continue

            frame = fetcher(symbol, period, interval)
            df = self._normalize(frame) if frame is not None and not frame.empty else pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
            print("Provider:", provider, "Symbol:", symbol, "Interval:", interval, "Rows:", len(df))
            if not df.empty:
                return df

        return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

    def get_multi_timeframe_data(self, symbol: str) -> dict:
        """Fetch multiple timeframes and attach indicators.

        Returns a dict with keys: '5m', '15m', '1h', '4h', '1d'. Each value is a DataFrame (may be empty).
        """
        out: dict = {}
        specs = {
            "5m": ("5d", "5m"),
            "15m": ("5d", "15m"),
            "1h": ("1mo", "1h"),
            "4h": ("3mo", "4h"),
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
                if df is None or df.empty:
                    out[key] = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
                    continue
                out[key] = df
            except Exception:
                out[key] = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

        return out

    def _fetch_yfinance(self, symbol: str, period: str, interval: str) -> pd.DataFrame | None:
        try:
            import yfinance as yf

            ticker = self._yfinance_symbol(symbol)
            download_interval = interval if interval != "4h" else "1h"
            frame = yf.download(ticker, period=period, interval=download_interval, auto_adjust=False, progress=False)
            if frame is None or frame.empty:
                return None
            frame = self._flatten_yfinance_frame(frame)
            if interval == "4h":
                frame = self._resample(frame, "4H")
            return frame
        except Exception:
            return None

    def _fetch_twelvedata(self, symbol: str, period: str, interval: str) -> pd.DataFrame | None:
        if not self.settings.twelvedata_api_key:
            return None

        try:
            params = {
                "symbol": symbol,
                "interval": self._twelvedata_interval(interval),
                "outputsize": self._outputsize(period),
                "format": "JSON",
                "apikey": self.settings.twelvedata_api_key,
            }
            payload = self._api_get_json("https://api.twelvedata.com/time_series", params)
            if not isinstance(payload, dict) or payload.get("status") != "ok":
                return None
            values = payload.get("values") or []
            if not values:
                return None
            frame = pd.DataFrame(values)
            frame["datetime"] = pd.to_datetime(frame["datetime"], utc=True, errors="coerce")
            frame = frame.dropna(subset=["datetime"]).set_index("datetime")
            rename_map = {"open": "Open", "high": "High", "low": "Low", "close": "Close", "volume": "Volume"}
            frame = frame.rename(columns=rename_map)
            return self._normalize(frame)
        except Exception:
            return None

    def _fetch_oanda(self, symbol: str, period: str, interval: str) -> pd.DataFrame | None:
        if not self.settings.oanda_api_key:
            return None

        try:
            instrument = self._oanda_instrument(symbol)
            params = {
                "granularity": self._oanda_granularity(interval),
                "price": "M",
                "count": self._period_to_count(period, interval),
            }
            payload = self._api_get_json(
                f"{self.settings.oanda_base_url.rstrip('/')}/v3/instruments/{instrument}/candles",
                params,
                headers={"Authorization": f"Bearer {self.settings.oanda_api_key}"},
            )
            candles = payload.get("candles") if isinstance(payload, dict) else None
            if not candles:
                return None
            rows = []
            for candle in candles:
                mid = candle.get("mid") or {}
                rows.append(
                    {
                        "datetime": pd.to_datetime(candle.get("time"), utc=True, errors="coerce"),
                        "Open": float(mid.get("o", candle.get("o", 0)) or 0),
                        "High": float(mid.get("h", candle.get("h", 0)) or 0),
                        "Low": float(mid.get("l", candle.get("l", 0)) or 0),
                        "Close": float(mid.get("c", candle.get("c", 0)) or 0),
                        "Volume": float(candle.get("volume", 0) or 0),
                    }
                )
            frame = pd.DataFrame(rows).dropna(subset=["datetime"]).set_index("datetime")
            return self._normalize(frame)
        except Exception:
            return None

    def _fetch_alphavantage(self, symbol: str, period: str, interval: str) -> pd.DataFrame | None:
        if not self.settings.alphavantage_api_key:
            return None

        try:
            normalized = symbol.replace("/", "").upper()
            params: dict[str, str] = {"apikey": self.settings.alphavantage_api_key, "outputsize": self._alpha_outputsize(period)}
            url = ""
            if normalized in {"BTCUSD", "ETHUSD"}:
                params.update({"function": "DIGITAL_CURRENCY_INTRADAY", "symbol": normalized[:-3], "market": "USD", "interval": self._alpha_interval(interval)})
                url = "https://www.alphavantage.co/query"
            elif "/" in symbol and not normalized.startswith(("XAU", "XAG")):
                base, quote = [part.strip().upper() for part in symbol.split("/", 1)]
                params.update({"function": "FX_INTRADAY", "from_symbol": base, "to_symbol": quote, "interval": self._alpha_interval(interval)})
                url = "https://www.alphavantage.co/query"
            else:
                return None
            payload = self._api_get_json(url, params)
            if not isinstance(payload, dict):
                return None

            if params["function"] == "FX_INTRADAY":
                series_key = next((key for key in payload.keys() if key.startswith("Time Series FX")), None)
                if not series_key:
                    return None
                frame = self._alpha_to_frame(payload[series_key], price_keys={"1. open": "Open", "2. high": "High", "3. low": "Low", "4. close": "Close", "5. volume": "Volume"})
            else:
                series_key = next((key for key in payload.keys() if key.startswith("Time Series")), None)
                if not series_key:
                    return None
                frame = self._alpha_to_frame(payload[series_key], price_keys={"1a. open (USD)": "Open", "2a. high (USD)": "High", "3a. low (USD)": "Low", "4a. close (USD)": "Close", "6. volume": "Volume"})

            return frame
        except Exception:
            return None

    @staticmethod
    def _normalize(frame: pd.DataFrame) -> pd.DataFrame:
        if frame is None or frame.empty:
            return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])

        # yfinance may return MultiIndex columns when downloading multiple assets.
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

        required_prices = ["Open", "High", "Low", "Close"]
        if not all(col in clean.columns for col in required_prices):
            return pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
        if "Volume" not in clean.columns:
            clean["Volume"] = 0.0

        clean = clean[["Open", "High", "Low", "Close", "Volume"]]
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            clean[col] = pd.to_numeric(clean[col], errors="coerce")
        clean = clean.dropna(subset=required_prices)
        clean = clean.sort_index()
        return clean

    @staticmethod
    def _flatten_yfinance_frame(frame: pd.DataFrame) -> pd.DataFrame:
        if isinstance(frame.columns, pd.MultiIndex):
            frame = frame.copy()
            frame.columns = ["_".join([str(part) for part in column if part is not None and str(part).strip()]) for column in frame.columns]
        rename_map = {}
        for column in frame.columns:
            lower = str(column).lower()
            if lower.startswith("open"):
                rename_map[column] = "Open"
            elif lower.startswith("high"):
                rename_map[column] = "High"
            elif lower.startswith("low"):
                rename_map[column] = "Low"
            elif lower.startswith("close"):
                rename_map[column] = "Close"
            elif lower.startswith("volume"):
                rename_map[column] = "Volume"
        frame = frame.rename(columns=rename_map)
        if "Adj Close" in frame.columns:
            frame = frame.drop(columns=["Adj Close"])
        if "Open" not in frame.columns and "Close" in frame.columns:
            frame["Open"] = frame["Close"]
        if "High" not in frame.columns and "Close" in frame.columns:
            frame["High"] = frame["Close"]
        if "Low" not in frame.columns and "Close" in frame.columns:
            frame["Low"] = frame["Close"]
        if "Volume" not in frame.columns:
            frame["Volume"] = 0.0
        return frame[["Open", "High", "Low", "Close", "Volume"]].dropna().sort_index()

    @staticmethod
    def _resample(frame: pd.DataFrame, rule: str) -> pd.DataFrame:
        resampled = frame.resample(rule).agg(
            {
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum",
            }
        )
        return resampled.dropna().sort_index()

    @staticmethod
    def _twelvedata_interval(interval: str) -> str:
        value = interval.strip().lower()
        return {
            "1m": "1min",
            "5m": "5min",
            "15m": "15min",
            "1h": "1h",
            "4h": "4h",
            "1d": "1day",
        }.get(value, value)

    @staticmethod
    def _outputsize(period: str) -> str:
        value = period.strip().lower()
        if value in {"1d", "5d"}:
            return "500"
        if value == "1mo":
            return "1000"
        return "5000"

    @staticmethod
    def _alpha_outputsize(period: str) -> str:
        value = period.strip().lower()
        return "compact" if value in {"1d", "5d"} else "full"

    @staticmethod
    def _alpha_interval(interval: str) -> str:
        value = interval.strip().lower()
        if value == "1m":
            return "1min"
        if value == "5m":
            return "5min"
        if value == "15m":
            return "15min"
        if value == "1h":
            return "60min"
        return "60min"

    @staticmethod
    def _oanda_granularity(interval: str) -> str:
        value = interval.strip().lower()
        return {"1m": "M1", "5m": "M5", "15m": "M15", "1h": "H1", "4h": "H4", "1d": "D"}.get(value, "M15")

    @staticmethod
    def _period_to_count(period: str, interval: str) -> int:
        value = period.strip().lower()
        if value.endswith("d") and value[:-1].isdigit():
            days = max(int(value[:-1]), 1)
            return max(days * 30, 100)
        if value.endswith("mo") and value[:-2].isdigit():
            months = max(int(value[:-2]), 1)
            return max(months * 300, 200)
        if value.endswith("y") and value[:-1].isdigit():
            years = max(int(value[:-1]), 1)
            return max(years * 1800, 500)
        return 300

    @staticmethod
    def _oanda_instrument(symbol: str) -> str:
        return symbol.strip().upper().replace("/", "_")

    @staticmethod
    def _yfinance_symbol(symbol: str) -> str:
        YFINANCE_SYMBOLS = {
            "EUR/USD": "EURUSD=X",
            "GBP/USD": "GBPUSD=X",
            "USD/JPY": "JPY=X",
            "USD/CAD": "CAD=X",
            "AUD/USD": "AUDUSD=X",
            "XAU/USD": "GC=F",
            "XAG/USD": "SI=F",
            "BTC/USD": "BTC-USD",
            "ETH/USD": "ETH-USD",
        }
        return YFINANCE_SYMBOLS.get(symbol.strip().upper(), symbol)

    @staticmethod
    def _api_get_json(url: str, params: dict[str, object], headers: dict[str, str] | None = None) -> dict | list | None:
        query = urlencode({key: value for key, value in params.items() if value is not None})
        request = Request(f"{url}?{query}", headers=headers or {})
        try:
            with urlopen(request, timeout=20) as response:
                content = response.read().decode("utf-8")
                return json.loads(content)
        except (URLError, TimeoutError, json.JSONDecodeError, ValueError):
            return None

    @staticmethod
    def _alpha_to_frame(series: dict, price_keys: dict[str, str]) -> pd.DataFrame | None:
        if not series:
            return None
        rows = []
        for timestamp, values in series.items():
            rows.append(
                {
                    "datetime": pd.to_datetime(timestamp, utc=True, errors="coerce"),
                    **{target: float(values.get(source, 0) or 0) for source, target in price_keys.items()},
                }
            )
        frame = pd.DataFrame(rows).dropna(subset=["datetime"]).set_index("datetime").sort_index()
        if "Volume" not in frame.columns:
            frame["Volume"] = 0.0
        return frame[["Open", "High", "Low", "Close", "Volume"]].dropna()

