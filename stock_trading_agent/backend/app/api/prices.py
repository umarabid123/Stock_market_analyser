from fastapi import APIRouter, HTTPException
from app.services.market_data import MarketDataProvider
from backend.config import settings

router = APIRouter()
provider = MarketDataProvider(settings)


@router.get("/prices/{symbol}")
def price(symbol: str):
    df = provider.get_ohlcv(symbol, period="5d", interval="1d")
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="No data")
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else last
    latest_price = float(last.get("Close", 0.0))
    prev_price = float(prev.get("Close", latest_price))
    change = latest_price - prev_price
    change_pct = (change / prev_price) * 100 if prev_price else 0.0
    return {
        "symbol": symbol,
        "latest_price": latest_price,
        "change": change,
        "change_percent": change_pct,
        "timestamp": str(last.name),
    }
