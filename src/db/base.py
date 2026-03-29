# src/db/base.py
# Defines the base class that all database models inherit from.
# SQLAlchemy uses this to know which classes are database tables.

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime
from datetime import datetime, timezone


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class TimestampMixin:
    """
    Adds created_at and updated_at to any model that inherits it.
    We'll use this on every table — it's good practice to always
    know when records were created and last changed.
    """
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )