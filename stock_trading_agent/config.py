"""Configuration loader for the stock trading agent."""

from __future__ import annotations

import os
from dataclasses import dataclass

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Application settings sourced from environment variables."""

    data_provider: str = os.getenv("DATA_PROVIDER", "auto").strip().lower()
    alpaca_api_key: str = os.getenv("ALPACA_API_KEY", "").strip()
    alpaca_secret_key: str = os.getenv("ALPACA_SECRET_KEY", "").strip()
    alpaca_base_url: str = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets").strip()
    polygon_api_key: str = os.getenv("POLYGON_API_KEY", "").strip()
    finnhub_api_key: str = os.getenv("FINNHUB_API_KEY", "").strip()
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    default_symbol: str = os.getenv("DEFAULT_SYMBOL", "AAPL").strip() or "AAPL"
    default_period: str = os.getenv("DEFAULT_PERIOD", "5d").strip() or "5d"
    default_interval: str = os.getenv("DEFAULT_INTERVAL", "5m").strip() or "5m"
    paper_trading_only: bool = _get_bool("PAPER_TRADING_ONLY", True)

    def provider_priority(self) -> list[str]:
        """Resolve provider selection, supporting auto mode and safe fallback."""
        if self.data_provider != "auto":
            return [self.data_provider, "yfinance"]

        providers: list[str] = []
        if self.polygon_api_key:
            providers.append("polygon")
        if self.alpaca_api_key and self.alpaca_secret_key:
            providers.append("alpaca")
        if self.finnhub_api_key:
            providers.append("finnhub")
        providers.append("yfinance")
        return providers


settings = Settings()
