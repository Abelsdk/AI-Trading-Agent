# src/api/routes/market_data.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.services import market_data_service

router = APIRouter(
    prefix="/api/v1/market-data",
    tags=["market data"],
)

@router.post("/fetch")
def fetch_prices(
    symbol: str = Query(..., description="Ticker symbol e.g. AAPL, BTC-USD"),
    period: str = Query("2y", description="How far back: 1mo, 6mo, 1y, 2y"),
    interval: str = Query("1d", description="Candle size: 1d, 1h, 5m"),
    db: Session = Depends(get_db),
):
    """Fetch and store OHLCV data for a symbol from Yahoo Finance."""
    return market_data_service.fetch_and_store_prices(db, symbol, period, interval)

@router.get("/prices/{symbol}")
def get_prices(
    symbol: str,
    timeframe: str = Query("1d"),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    """Get stored price bars for a symbol."""
    bars = market_data_service.get_price_bars(db, symbol, timeframe, limit)
    return [
        {
            "time": bar.time,
            "open": float(bar.open),
            "high": float(bar.high),
            "low": float(bar.low),
            "close": float(bar.close),
            "volume": bar.volume,
        }
        for bar in bars
    ]

@router.get("/symbols")
def get_symbols(db: Session = Depends(get_db)):
    """Get all symbols that have stored price data."""
    return {"symbols": market_data_service.get_available_symbols(db)}