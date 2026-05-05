"""Notification utilities."""

from __future__ import annotations

from config import Settings


class Notifier:
    """Simple notifier placeholder for future Telegram integration."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def send(self, message: str) -> bool:
        if not self.settings.telegram_bot_token or not self.settings.telegram_chat_id:
            return False
        # Keep this simple and safe by default.
        return True
