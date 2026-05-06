from fastapi import APIRouter, Query, HTTPException
from app.services.market_data import MarketDataProvider
from backend.config import settings

router = APIRouter()
provider = MarketDataProvider(settings)


@router.get("/history/{symbol}")
def history(symbol: str, period: str = Query("3mo"), interval: str = Query("1d")):
    df = provider.get_ohlcv(symbol, period=period, interval=interval)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="No data")
    # Return OHLCV as list of dicts
    records = []
    for idx, row in df.iterrows():
        records.append({
            "timestamp": str(idx),
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": int(row["Volume"]),
        })
    return {"symbol": symbol, "candles": records}
