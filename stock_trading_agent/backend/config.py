"""Configuration loader for the AI Forex & Commodity Trading Assistant."""

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

    # Provider settings
    data_provider: str = os.getenv("DATA_PROVIDER", "auto").strip().lower()

    # Forex / commodity APIs
    twelvedata_api_key: str = os.getenv("TWELVEDATA_API_KEY", "").strip()
    
    #print twelvedata_api_key to check if it's loaded correctly
    # print(f"Twelve Data API Key: '{twelvedata_api_key}'")

    oanda_api_key: str = os.getenv("OANDA_API_KEY", "").strip()
    oanda_account_id: str = os.getenv("OANDA_ACCOUNT_ID", "").strip()
    oanda_base_url: str = os.getenv(
        "OANDA_BASE_URL",
        "https://api-fxpractice.oanda.com",
    ).strip()

    alphavantage_api_key: str = os.getenv("ALPHAVANTAGE_API_KEY", "").strip()
    finnhub_api_key: str = os.getenv("FINNHUB_API_KEY", "").strip()
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-1.5-mini").strip()

    # Telegram alerts
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    # Forex dashboard defaults
    default_market: str = os.getenv("DEFAULT_MARKET", "Forex").strip() or "Forex"
    default_pair: str = os.getenv("DEFAULT_PAIR", "EUR/USD").strip() or "EUR/USD"
    default_lookback: str = os.getenv("DEFAULT_LOOKBACK", "5d").strip() or "5d"
    default_timeframe: str = (
        os.getenv("DEFAULT_TIMEFRAME", "15m").strip() or "15m"
    )

    # Backward compatibility with old stock version
    @property
    def default_symbol(self) -> str:
        return self.default_pair

    @property
    def default_period(self) -> str:
        return self.default_lookback

    @property
    def default_interval(self) -> str:
        return self.default_timeframe

    # Safety
    paper_trading_only: bool = _get_bool("PAPER_TRADING_ONLY", True)

    def provider_priority(self) -> list[str]:
        """Resolve provider selection, supporting auto mode and safe fallback."""
        if self.data_provider != "auto":
            return [self.data_provider, "yfinance"]

        providers: list[str] = []

        if self.twelvedata_api_key:
            providers.append("twelvedata")

        if self.oanda_api_key:
            providers.append("oanda")

        if self.alphavantage_api_key:
            providers.append("alphavantage")

        providers.append("yfinance")
        return providers


settings = Settings()