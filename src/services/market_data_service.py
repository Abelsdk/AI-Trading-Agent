# src/services/market_data_service.py
# Fetches OHLCV data from Yahoo Finance and stores it in the database.
# yfinance is free, requires no API key, and covers stocks, ETFs, and crypto.

import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timezone
from typing import Optional
from src.models.price_bar import PriceBar


# Maps yfinance period strings to our timeframe labels
TIMEFRAME_MAP = {
    "1d": "1d",
    "1h": "1h",
    "5m": "5m",
}

# Determines asset class from symbol naming convention
def detect_asset_class(symbol: str) -> str:
    symbol = symbol.upper()
    if "-USD" in symbol or symbol in ["BTC", "ETH", "SOL", "ADA", "XRP"]:
        return "crypto"
    elif "/" in symbol:
        return "forex"
    else:
        return "stock"


def fetch_and_store_prices(
    db: Session,
    symbol: str,
    period: str = "2y",       # how far back: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y
    interval: str = "1d",     # candle size: 1m, 5m, 15m, 1h, 1d, 1wk
) -> dict:
    """
    Fetch OHLCV data from Yahoo Finance and upsert into the database.
    Returns a summary of what was fetched and stored.
    
    'Upsert' means: insert if not exists, skip if already there.
    This makes the function safe to call multiple times — no duplicates.
    """
    symbol = symbol.upper()
    asset_class = detect_asset_class(symbol)

    print(f"Fetching {symbol} {interval} data for {period}...")

    # Download from Yahoo Finance
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval)

    if df.empty:
        return {"symbol": symbol, "status": "error", "message": "No data returned from Yahoo Finance"}

    # Clean up the DataFrame
    df = df.reset_index()
    df.columns = [c.lower() for c in df.columns]

    # Handle timezone — ensure all timestamps are UTC
    if "datetime" in df.columns:
        df = df.rename(columns={"datetime": "date"})
    
    time_col = "date" if "date" in df.columns else df.columns[0]
    df[time_col] = pd.to_datetime(df[time_col], utc=True)

    # Build list of records to insert
    records = []
    for _, row in df.iterrows():
        records.append({
            "symbol": symbol,
            "timeframe": interval,
            "asset_class": asset_class,
            "time": row[time_col].to_pydatetime(),
            "open": float(row["open"]),
            "high": float(row["high"]),
            "low": float(row["low"]),
            "close": float(row["close"]),
            "volume": int(row.get("volume", 0) or 0),
        })

    if not records:
        return {"symbol": symbol, "status": "error", "message": "No valid records to insert"}

    # Upsert — insert new records, skip duplicates
    stmt = insert(PriceBar).values(records)
    stmt = stmt.on_conflict_do_nothing(
        index_elements=None,
        constraint="uq_price_bar"
    )
    db.execute(stmt)
    db.commit()

    return {
        "symbol": symbol,
        "interval": interval,
        "period": period,
        "asset_class": asset_class,
        "records_fetched": len(records),
        "status": "success",
    }


def get_price_bars(
    db: Session,
    symbol: str,
    timeframe: str = "1d",
    limit: int = 100,
) -> list[PriceBar]:
    """Retrieve stored price bars for a symbol, most recent first."""
    return (
        db.query(PriceBar)
        .filter(PriceBar.symbol == symbol.upper())
        .filter(PriceBar.timeframe == timeframe)
        .order_by(PriceBar.time.desc())
        .limit(limit)
        .all()
    )


def get_available_symbols(db: Session) -> list[str]:
    """Return list of symbols that have data stored."""
    results = db.query(PriceBar.symbol).distinct().all()
    return [r[0] for r in results]