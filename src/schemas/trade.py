# src/schemas/trade.py
# Pydantic schemas define the shape of data at the API boundary.
# Separate from database models — this is intentional.
# Your API contract can evolve independently from your DB schema.

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal
from src.models.trade import TradeDirection, TradeStatus


class TradeCreate(BaseModel):
    """Schema for creating a new trade. All required fields must be present."""
    symbol: str = Field(..., min_length=1, max_length=20, description="Asset ticker e.g. AAPL, BTC")
    direction: TradeDirection = Field(..., description="LONG or SHORT")
    entry_price: Decimal = Field(..., gt=0, description="Price at entry")
    quantity: Decimal = Field(..., gt=0, description="Number of units")
    stop_loss: Optional[Decimal] = Field(None, gt=0)
    take_profit: Optional[Decimal] = Field(None, gt=0)
    risk_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    strategy: Optional[str] = Field(None, max_length=100)
    reasoning: Optional[str] = Field(None, description="Why you took this trade")
    emotion: Optional[str] = Field(None, max_length=50, description="e.g. confident, fearful, neutral")
    entry_time: Optional[datetime] = None


class TradeUpdate(BaseModel):
    """Schema for closing or updating a trade."""
    exit_price: Optional[Decimal] = Field(None, gt=0)
    exit_time: Optional[datetime] = None
    status: Optional[TradeStatus] = None
    notes: Optional[str] = None
    emotion: Optional[str] = Field(None, max_length=50)



class TradeResponse(BaseModel):
    """Schema for what we send back in API responses."""
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={Decimal: lambda v: float(round(v, 8))}
    )

    id: int
    symbol: str
    direction: TradeDirection
    entry_price: float
    exit_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    quantity: float
    risk_percent: Optional[float]
    strategy: Optional[str]
    reasoning: Optional[str]
    emotion: Optional[str]
    notes: Optional[str]
    status: TradeStatus
    entry_time: datetime
    exit_time: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    # Computed field — calculated on the fly, not stored in DB
    @property
    def pnl(self) -> Optional[Decimal]:
        """Profit/loss. Only available when trade is closed."""
        if self.exit_price is None:
            return None
        if self.direction == TradeDirection.LONG:
            return (self.exit_price - self.entry_price) * self.quantity
        else:
            return (self.entry_price - self.exit_price) * self.quantity