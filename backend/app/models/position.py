"""
Position Model - Represents open trading positions.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum as PyEnum
from typing import Optional

from sqlalchemy import DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PositionSide(str, PyEnum):
    """Position side enumeration."""

    LONG = "long"
    SHORT = "short"


class Position(Base):
    """Position database model."""

    __tablename__ = "positions"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Exchange reference
    exchange_position_id: Mapped[Optional[str]] = mapped_column(
        String(100), unique=True
    )

    # Position details
    symbol: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    side: Mapped[PositionSide] = mapped_column(nullable=False)

    # Quantities
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    entry_price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    current_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))

    # Leverage
    leverage: Mapped[int] = mapped_column(default=1)

    # P&L
    unrealized_pnl: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), default=Decimal("0")
    )
    realized_pnl: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal("0"))

    # Risk management
    stop_loss: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    take_profit: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    liquidation_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))

    # Status
    is_open: Mapped[bool] = mapped_column(default=True, index=True)
    is_paper_trading: Mapped[bool] = mapped_column(default=True)

    # Strategy reference
    strategy_name: Mapped[Optional[str]] = mapped_column(String(50))

    # Timestamps
    opened_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    def __repr__(self) -> str:
        return (
            f"<Position(id={self.id}, symbol={self.symbol}, "
            f"side={self.side}, quantity={self.quantity})>"
        )
