from fastapi import APIRouter, HTTPException
from app.services.market_data import MarketDataProvider
from backend.config import settings
import numpy as np
from datetime import datetime, timedelta

router = APIRouter()
provider = MarketDataProvider(settings)


@router.get("/forecast/{symbol}")
def forecast(symbol: str):
    # Get recent daily closes
    df = provider.get_ohlcv(symbol, period="180d", interval="1d")
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail="No data")

    closes = df["Close"].dropna()
    last = float(closes.iloc[-1])
    # baseline daily return
    returns = closes.pct_change().dropna()
    mu = float(returns.mean()) if not returns.empty else 0.0
    sigma = float(returns.std()) if not returns.empty else 0.0

    days = []
    price = last
    for i in range(1, 6):
        # predict by applying mean return
        price = price * (1 + mu)
        # confidence interval via volatility
        ci_half = price * (1.96 * sigma)
        change_pct = (price - float(closes.iloc[-1])) / float(closes.iloc[-1]) * 100
        day_date = (datetime.utcnow().date() + timedelta(days=i)).isoformat()
        days.append({
            "day": i,
            "date": day_date,
            "predicted_price": round(float(price), 6),
            "change_percent": round(float(change_pct), 4),
            "ci_low": round(float(price - ci_half), 6),
            "ci_high": round(float(price + ci_half), 6),
        })

    # trend: simple slope over last 5 days
    if len(closes) >= 5:
        recent = closes.iloc[-5:]
        slope = np.polyfit(np.arange(len(recent)), recent.values, 1)[0]
        if slope > 0:
            overall = "BULLISH"
        elif slope < 0:
            overall = "BEARISH"
        else:
            overall = "NEUTRAL"
    else:
        overall = "NEUTRAL"

    confidence = max(20, min(95, int((1 - sigma) * 100))) if sigma >= 0 else 50

    return {"symbol": symbol, "forecast": days, "trend": overall, "confidence": confidence}
