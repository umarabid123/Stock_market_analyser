from fastapi import APIRouter, HTTPException
from app.services.market_data import MarketDataProvider
from backend.config import settings

router = APIRouter()
provider = MarketDataProvider(settings)


@router.get("/indicators/{symbol}")
def indicators(symbol: str):
    multi = provider.get_multi_timeframe_data(symbol)
    # prefer 1d then 1h
    df = multi.get("1d") or multi.get("1h") or multi.get("15m")
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="No data")
    latest = df.iloc[-1]
    data = {
        "RSI": float(latest.get("RSI_14", 0.0)),
        "MACD": None,
        "Bollinger": None,
        "ATR": float(latest.get("ATR_14", 0.0)),
        "SMA_20": float(latest.get("SMA_20", 0.0)),
        "EMA_20": float(latest.get("EMA_20", 0.0)),
    }
    return {"symbol": symbol, "indicators": data}
