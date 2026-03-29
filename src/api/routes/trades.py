# src/api/routes/trades.py
# HTTP route handlers for the trading journal.
# Each function handles one API endpoint.
# Routes are intentionally thin — logic lives in services.

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from src.db.database import get_db
from src.schemas.trade import TradeCreate, TradeUpdate, TradeResponse
from src.services import trade_service
from src.models.trade import TradeStatus

# APIRouter groups related endpoints together
# prefix means all routes here start with /api/v1/trades
router = APIRouter(
    prefix="/api/v1/trades",
    tags=["trades"],  # groups them in /docs
)


@router.post("/", response_model=TradeResponse, status_code=201)
def create_trade(
    trade_data: TradeCreate,
    db: Session = Depends(get_db),  # FastAPI injects the DB session
):
    """Log a new trade in the journal."""
    return trade_service.create_trade(db, trade_data)


@router.get("/", response_model=list[TradeResponse])
def list_trades(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    symbol: Optional[str] = Query(None, description="Filter by symbol e.g. AAPL"),
    strategy: Optional[str] = Query(None, description="Filter by strategy name"),
    status: Optional[TradeStatus] = Query(None, description="Filter by OPEN or CLOSED"),
    db: Session = Depends(get_db),
):
    """Get all trades with optional filtering and pagination."""
    return trade_service.get_trades(db, skip, limit, symbol, strategy, status)


@router.get("/{trade_id}", response_model=TradeResponse)
def get_trade(
    trade_id: int,
    db: Session = Depends(get_db),
):
    """Get a single trade by ID."""
    trade = trade_service.get_trade(db, trade_id)
    if not trade:
        raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
    return trade


@router.patch("/{trade_id}", response_model=TradeResponse)
def update_trade(
    trade_id: int,
    update_data: TradeUpdate,
    db: Session = Depends(get_db),
):
    """Update a trade — close it, add notes, update emotion."""
    trade = trade_service.update_trade(db, trade_id, update_data)
    if not trade:
        raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")
    return trade


@router.delete("/{trade_id}", status_code=204)
def delete_trade(
    trade_id: int,
    db: Session = Depends(get_db),
):
    """Delete a trade. Returns 204 No Content on success."""
    deleted = trade_service.delete_trade(db, trade_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Trade {trade_id} not found")