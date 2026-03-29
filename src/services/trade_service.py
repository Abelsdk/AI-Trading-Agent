# src/services/trade_service.py
# Business logic for trade operations.
# This layer sits between your API routes and the database.
# Routes should never query the database directly.

from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional
from datetime import datetime, timezone
from src.models.trade import Trade, TradeStatus
from src.schemas.trade import TradeCreate, TradeUpdate


def create_trade(db: Session, trade_data: TradeCreate) -> Trade:
    """
    Create a new trade record in the database.
    Takes validated Pydantic data, converts to ORM model, saves it.
    """
    trade = Trade(
        symbol=trade_data.symbol.upper(),  # always store uppercase
        direction=trade_data.direction,
        entry_price=trade_data.entry_price,
        quantity=trade_data.quantity,
        stop_loss=trade_data.stop_loss,
        take_profit=trade_data.take_profit,
        risk_percent=trade_data.risk_percent,
        strategy=trade_data.strategy,
        reasoning=trade_data.reasoning,
        emotion=trade_data.emotion,
        entry_time=trade_data.entry_time or datetime.now(timezone.utc),
        status=TradeStatus.OPEN,
    )
    db.add(trade)
    db.commit()
    db.refresh(trade)  # reloads the object with DB-generated values (id, timestamps)
    return trade


def get_trade(db: Session, trade_id: int) -> Optional[Trade]:
    """Fetch a single trade by ID. Returns None if not found."""
    return db.query(Trade).filter(Trade.id == trade_id).first()


def get_trades(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    symbol: Optional[str] = None,
    strategy: Optional[str] = None,
    status: Optional[TradeStatus] = None,
) -> list[Trade]:
    """
    Fetch multiple trades with optional filtering.
    skip/limit = pagination (skip first N results, return next M).
    """
    query = db.query(Trade)

    # Apply filters only if provided
    if symbol:
        query = query.filter(Trade.symbol == symbol.upper())
    if strategy:
        query = query.filter(Trade.strategy == strategy)
    if status:
        query = query.filter(Trade.status == status)

    # Most recent trades first
    query = query.order_by(desc(Trade.entry_time))

    return query.offset(skip).limit(limit).all()


def update_trade(
    db: Session,
    trade_id: int,
    update_data: TradeUpdate,
) -> Optional[Trade]:
    """
    Update an existing trade — typically used to close a trade
    by adding exit price and exit time.
    """
    trade = get_trade(db, trade_id)
    if not trade:
        return None

    # Only update fields that were actually provided
    update_fields = update_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(trade, field, value)

    # Auto-set exit time when closing a trade
    if update_data.status == TradeStatus.CLOSED and not trade.exit_time:
        trade.exit_time = datetime.now(timezone.utc)

    db.commit()
    db.refresh(trade)
    return trade


def delete_trade(db: Session, trade_id: int) -> bool:
    """
    Delete a trade. Returns True if deleted, False if not found.
    In production you'd soft-delete instead, but this is fine for V1.
    """
    trade = get_trade(db, trade_id)
    if not trade:
        return False
    db.delete(trade)
    db.commit()
    return True