from fastapi import APIRouter, HTTPException
from app.services.market_data import MarketDataProvider
from app.services.signal_engine import SignalEngine
from backend.config import settings

router = APIRouter()
provider = MarketDataProvider(settings)
engine = SignalEngine(settings)


@router.get("/signal/{symbol}")
def signal(symbol: str):
    multi = provider.get_multi_timeframe_data(symbol)
    if not multi:
        raise HTTPException(status_code=404, detail="No data")
    result = engine.analyze_market(symbol, multi)
    # Map to required response shape
    return {
        "symbol": symbol,
        "signal": result.get("signal"),
        "confidence": result.get("confidence"),
        "reason": result.get("reason"),
        "trend_5m": result.get("trend_5m"),
        "trend_15m": result.get("trend_15m"),
        "trend_1h": result.get("trend_1h"),
        "trend_1d": result.get("trend_1d"),
        "volume_strength": result.get("volume_strength"),
        "news_sentiment": result.get("news_sentiment"),
        "stop_loss": result.get("stop_loss"),
        "take_profit": result.get("take_profit"),
    }
