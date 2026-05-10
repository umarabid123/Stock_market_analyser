"""FastAPI backend for AI Forex & Commodity Trading Assistant."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import json

from config import settings
from data.market_data import MarketDataProvider
from strategy.signal_engine import SignalEngine
from assistant.chatbot import get_chatbot_response

# Initialize FastAPI app
app = FastAPI(
    title="AI Forex Trading Assistant API",
    description="Real-time forex, gold, silver, and crypto analysis",
    version="1.0.0",
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
provider = MarketDataProvider(settings)
engine = SignalEngine(settings)


# ============= Pydantic Models =============

class AnalyzeRequest(BaseModel):
    symbol: str
    timeframe: str = "15m"
    lookback: str = "5d"


class CandlesRequest(BaseModel):
    symbol: str
    timeframe: str = "15m"
    lookback: str = "5d"


class ChatRequest(BaseModel):
    message: str
    current_result: Optional[Dict[str, Any]] = None


class Candle(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class RiskProfile(BaseModel):
    entry_price: float
    stop_loss: Optional[float]
    take_profit: Optional[float]
    risk_reward_ratio: Optional[float]


class Trends(BaseModel):
    _5m: str
    _15m: str
    _1h: str
    _4h: str
    _1d: str


class AnalyzeResponse(BaseModel):
    symbol: str
    latest_price: float
    signal: str
    confidence: float
    market_bias: str
    reason: str
    trends: Dict[str, str]
    risk: RiskProfile
    session: Dict[str, str]
    support_zone: list
    resistance_zone: list
    warning: str


class ChatResponse(BaseModel):
    reply: str


# ============= Health Check =============

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "AI Forex Backend",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ============= Market Analysis =============

@app.post("/api/analyze")
async def analyze_market(request: AnalyzeRequest):
    """
    Analyze market for a given symbol.
    
    Returns: BUY/SELL/HOLD/WAIT_FOR_BUY signal with confidence and risk levels.
    """
    try:
        # Fetch multi-timeframe data
        multi_tf_data = provider.get_multi_timeframe_data(request.symbol)
        
        # Generate signal
        result = engine.analyze_market(request.symbol, multi_tf_data)
        
        # Format response
        support = result.get("support_zone", (None, None))
        resistance = result.get("resistance_zone", (None, None))
        
        support_list = [support[0], support[1]] if support[0] is not None else []
        resistance_list = [resistance[0], resistance[1]] if resistance[0] is not None else []
        
        response = {
            "symbol": result.get("symbol", request.symbol),
            "latest_price": float(result.get("latest_price", 0.0)),
            "signal": result.get("signal", "HOLD"),
            "confidence": float(result.get("confidence", 0.0)),
            "market_bias": result.get("market_bias", "NEUTRAL"),
            "reason": result.get("reason", ""),
            "trends": {
                "5m": result.get("trend_5m", "NEUTRAL"),
                "15m": result.get("trend_15m", "NEUTRAL"),
                "1h": result.get("trend_1h", "NEUTRAL"),
                "4h": result.get("trend_4h", "NEUTRAL"),
                "1d": result.get("trend_1d", "NEUTRAL"),
            },
            "risk": {
                "entry_price": float(result.get("entry_price", 0.0)),
                "stop_loss": float(result.get("stop_loss")) if result.get("stop_loss") is not None else None,
                "take_profit": float(result.get("take_profit")) if result.get("take_profit") is not None else None,
                "risk_reward_ratio": float(result.get("risk_reward_ratio")) if result.get("risk_reward_ratio") is not None else None,
            },
            "session": {
                "active_session": result.get("active_session", "Unknown"),
                "volatility": result.get("session_volatility", "MEDIUM"),
            },
            "support_zone": support_list,
            "resistance_zone": resistance_list,
            "warning": "Educational analysis only. Not financial advice.",
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


# ============= Market Candles =============

@app.get("/api/candles")
async def get_candles(symbol: str, timeframe: str = "15m", lookback: str = "5d"):
    """
    Get candlestick data for a symbol.
    
    Returns: Array of candles [time, open, high, low, close, volume]
    """
    try:
        df = provider.get_ohlcv(symbol, period=lookback, interval=timeframe)
        
        if df is None or df.empty:
            return []
        
        # Convert DataFrame to list of candles
        candles = []
        for idx, row in df.iterrows():
            candle = {
                "time": str(idx),
                "open": float(row.get("Open", 0.0)),
                "high": float(row.get("High", 0.0)),
                "low": float(row.get("Low", 0.0)),
                "close": float(row.get("Close", 0.0)),
                "volume": float(row.get("Volume", 0.0)),
            }
            candles.append(candle)
        
        return candles
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch candles: {str(e)}"
        )


# ============= Chatbot =============

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint for answering questions about signals and trading.
    """
    try:
        current_result = request.current_result or {}
        reply = get_chatbot_response(request.message, current_result)
        
        return {
            "reply": reply
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )


# ============= Root =============

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "AI Forex Trading Assistant API",
        "docs": "/docs",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
