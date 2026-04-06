# src/api/routes/analytics.py
# HTTP endpoints for trading performance analytics.

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from src.db.database import get_db
from src.services import analytics_service

router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["analytics"],
)


@router.get("/summary")
def get_summary(
    strategy: Optional[str] = Query(None),
    symbol: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get full performance summary from your trade journal."""
    return analytics_service.get_performance_summary(db, strategy, symbol)


@router.get("/strategies")
def get_strategy_breakdown(db: Session = Depends(get_db)):
    """Performance broken down by strategy — shows which strategies work best."""
    return analytics_service.get_strategy_breakdown(db)