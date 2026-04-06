# src/models/price_bar.py
# Defines the price_bars table — stores OHLCV market data.
# This is a TimescaleDB hypertable, meaning it's automatically
# partitioned by time for fast time-series queries.

from sqlalchemy import Column, String, Numeric, BigInteger, DateTime, UniqueConstraint
from src.db.base import Base, TimestampMixin
from datetime import datetime, timezone


class PriceBar(Base, TimestampMixin):
    """
    One row = one OHLCV candle for a symbol at a given timeframe.
    Example: AAPL daily candle for 2024-01-15.
    """
    __tablename__ = "price_bars"

    # Composite primary key — symbol + timeframe + time uniquely identifies a candle
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # e.g. "AAPL", "BTC-USD", "ETH-USD"
    symbol = Column(String(20), nullable=False, index=True)

    # e.g. "1d", "1h", "5m"
    timeframe = Column(String(5), nullable=False)

    # e.g. "stock", "crypto", "forex"
    asset_class = Column(String(10), nullable=False)

    # The timestamp of this candle's open
    time = Column(DateTime(timezone=True), nullable=False, index=True)

    # OHLCV — use Numeric for precision, never Float for financial data
    open = Column(Numeric(18, 8), nullable=False)
    high = Column(Numeric(18, 8), nullable=False)
    low = Column(Numeric(18, 8), nullable=False)
    close = Column(Numeric(18, 8), nullable=False)
    volume = Column(BigInteger, nullable=True)

    # Prevent duplicate candles for same symbol+timeframe+time
    __table_args__ = (
        UniqueConstraint('symbol', 'timeframe', 'time', name='uq_price_bar'),
    )

    def __repr__(self):
        return f"<PriceBar {self.symbol} {self.timeframe} {self.time} close={self.close}>"