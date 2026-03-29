# src/models/trade.py
# Defines the Trade table in PostgreSQL.
# Each class attribute = one column in the database.
# SQLAlchemy reads this class and creates/manages the table.

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, Enum
from sqlalchemy.orm import Mapped
from src.db.base import Base, TimestampMixin
from datetime import datetime, timezone
import enum


class TradeDirection(str, enum.Enum):
    """Whether we're buying (LONG) or selling short (SHORT)."""
    LONG = "LONG"
    SHORT = "SHORT"


class TradeStatus(str, enum.Enum):
    """Whether the trade is still open or has been closed."""
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class Trade(Base, TimestampMixin):
    """
    Represents a single trade in the journal.
    Every trade you make gets one row in this table.
    """
    __tablename__ = "trades"

    # Primary key — auto-increments for each new trade
    id = Column(Integer, primary_key=True, index=True)

    # What asset (e.g. AAPL, BTC, EUR/USD)
    symbol = Column(String(20), nullable=False, index=True)

    # LONG = buying, SHORT = selling
    direction = Column(
        Enum(TradeDirection),
        nullable=False,
    )

    # Price when you entered the trade
    entry_price = Column(Numeric(18, 8), nullable=False)

    # Price when you exited (null if still open)
    exit_price = Column(Numeric(18, 8), nullable=True)

    # Where you planned to cut losses
    stop_loss = Column(Numeric(18, 8), nullable=True)

    # Where you planned to take profit
    take_profit = Column(Numeric(18, 8), nullable=True)

    # How many units/shares/coins
    quantity = Column(Numeric(18, 8), nullable=False)

    # What % of your account you risked
    risk_percent = Column(Numeric(5, 2), nullable=True)

    # Which strategy you used (e.g. "breakout", "mean reversion")
    strategy = Column(String(100), nullable=True, index=True)

    # Your reasoning at the time — this is the most valuable field
    reasoning = Column(Text, nullable=True)

    # How you felt — helps detect emotional trading patterns
    emotion = Column(String(50), nullable=True)

    # Notes after the trade closed
    notes = Column(Text, nullable=True)

    # OPEN or CLOSED
    status = Column(
        Enum(TradeStatus),
        nullable=False,
        default=TradeStatus.OPEN,
    )

    # When you entered and exited
    entry_time = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    exit_time = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Trade {self.symbol} {self.direction} @ {self.entry_price}>"