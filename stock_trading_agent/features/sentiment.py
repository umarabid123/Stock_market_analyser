"""Simple news sentiment utility using Finnhub news when available.

Returns a small dict with sentiment and a score. Non-fatal if Finnhub not configured.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Dict, Any

POSITIVE = {"beat", "growth", "profit", "surge", "upgrade", "strong", "record", "positive"}
NEGATIVE = {"loss", "drop", "fall", "lawsuit", "downgrade", "weak", "decline", "negative"}


def get_news_sentiment(symbol: str) -> Dict[str, Any]:
    key = os.getenv("FINNHUB_API_KEY", "").strip()
    if not key:
        return {"sentiment": "UNAVAILABLE", "score": 0, "reason": "Finnhub API key not configured"}

    try:
        import finnhub
    except Exception:
        return {"sentiment": "UNAVAILABLE", "score": 0, "reason": "Finnhub client not installed"}

    client = finnhub.Client(api_key=key)
    to_dt = datetime.utcnow().date()
    from_dt = to_dt - timedelta(days=7)
    try:
        news = client.company_news(symbol, _from=from_dt.isoformat(), to=to_dt.isoformat())
    except Exception as exc:
        return {"sentiment": "UNAVAILABLE", "score": 0, "reason": f"Finnhub error: {exc}"}

    score = 0
    count = 0
    for item in news or []:
        text = (item.get("headline", "") + " " + item.get("summary", "")).lower()
        found = False
        for p in POSITIVE:
            if p in text:
                score += 1
                found = True
        for n in NEGATIVE:
            if n in text:
                score -= 1
                found = True
        if found:
            count += 1

    if count == 0:
        sentiment = "NEUTRAL"
        reason = "No strong keywords in recent news"
    else:
        if score > 0:
            sentiment = "POSITIVE"
        elif score < 0:
            sentiment = "NEGATIVE"
        else:
            sentiment = "NEUTRAL"
        reason = f"Keywords found in {count} articles"

    return {"sentiment": sentiment, "score": int(score), "reason": reason}
