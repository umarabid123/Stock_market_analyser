"""Simple news sentiment utility for forex, metals, and crypto markets."""

from __future__ import annotations

import json
import os
from typing import Any, Dict
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

POSITIVE = {"beat", "growth", "profit", "surge", "upgrade", "strong", "record", "positive", "supportive", "bullish"}
NEGATIVE = {"loss", "drop", "fall", "lawsuit", "downgrade", "weak", "decline", "negative", "pressure", "bearish"}


def _asset_keywords(symbol: str) -> list[str]:
    normalized = symbol.replace("/", "").replace("_", "").upper()
    keywords = {normalized}
    if "/" in symbol:
        base, quote = [part.strip().upper() for part in symbol.split("/", 1)]
        keywords.update({base, quote, f"{base}{quote}"})
    if normalized.startswith("XAU"):
        keywords.update({"GOLD", "XAUUSD"})
    elif normalized.startswith("XAG"):
        keywords.update({"SILVER", "XAGUSD"})
    elif normalized.startswith("BTC"):
        keywords.update({"BITCOIN", "CRYPTO"})
    elif normalized.startswith("ETH"):
        keywords.update({"ETHEREUM", "CRYPTO"})
    return [keyword for keyword in keywords if keyword]


def _score_text(text: str) -> int:
    score = 0
    lowered = text.lower()
    for token in POSITIVE:
        if token in lowered:
            score += 1
    for token in NEGATIVE:
        if token in lowered:
            score -= 1
    return score


def _sentiment_label(score: float) -> str:
    if score > 0.25:
        return "POSITIVE"
    if score < -0.25:
        return "NEGATIVE"
    return "NEUTRAL"


def _news_from_alpha_vantage(symbol: str) -> Dict[str, Any] | None:
    key = os.getenv("ALPHAVANTAGE_API_KEY", "").strip()
    if not key:
        return None

    query = urlencode({"function": "NEWS_SENTIMENT", "tickers": symbol.replace("/", "").upper(), "limit": 20, "apikey": key})
    try:
        with urlopen(Request(f"https://www.alphavantage.co/query?{query}"), timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return None

    feed = payload.get("feed") or []
    if not feed:
        return None

    total_score = 0.0
    article_count = 0
    for article in feed:
        text = " ".join(str(part or "") for part in (article.get("title"), article.get("summary"), article.get("source")))
        article_score = float(article.get("overall_sentiment_score") or 0.0)
        if article_score == 0.0:
            article_score = _score_text(text) / 4.0
        else:
            article_score = max(-1.0, min(1.0, article_score))
        if article_score != 0.0:
            total_score += article_score
            article_count += 1

    if article_count == 0:
        return None

    score = total_score / article_count
    return {
        "sentiment": _sentiment_label(score),
        "score": round(score, 3),
        "reason": f"AlphaVantage news sentiment across {article_count} articles",
        "source": "AlphaVantage",
    }


def _news_from_finnhub(symbol: str) -> Dict[str, Any] | None:
    key = os.getenv("FINNHUB_API_KEY", "").strip()
    if not key:
        return None

    asset_keywords = set(_asset_keywords(symbol))
    params = {"category": "general", "token": key}

    try:
        with urlopen(Request(f"https://finnhub.io/api/v1/news?{urlencode(params)}"), timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return None

    if not isinstance(payload, list):
        return None

    weighted_score = 0.0
    matched_articles = 0
    for article in payload[:30]:
        text = " ".join(str(part or "") for part in (article.get("headline"), article.get("summary"), article.get("source")))
        if asset_keywords and not any(keyword.lower() in text.lower() for keyword in asset_keywords):
            continue
        article_score = _score_text(text)
        if article_score != 0:
            matched_articles += 1
            weighted_score += article_score

    if matched_articles == 0:
        return None

    score = weighted_score / matched_articles
    return {
        "sentiment": _sentiment_label(score),
        "score": round(score, 3),
        "reason": f"Finnhub news matched {matched_articles} articles",
        "source": "Finnhub",
    }


def get_news_sentiment(symbol: str) -> Dict[str, Any]:
    alpha = _news_from_alpha_vantage(symbol)
    if alpha is not None:
        return alpha

    finnhub = _news_from_finnhub(symbol)
    if finnhub is not None:
        return finnhub

    return {
        "sentiment": "UNAVAILABLE",
        "score": 0,
        "reason": "No compatible news API key configured",
        "source": "Unavailable",
    }
