"""
Order Model - Represents trading orders in the database.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class OrderStatus(str, Enum):
    """Order status enumeration."""

    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class OrderSide(str, Enum):
    """Order side enumeration."""

    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    """Order type enumeration."""

    MARKET = "market"
    LIMIT = "limit"
    STOP_MARKET = "stop_market"
    STOP_LIMIT = "stop_limit"


class Order(Base):
    """Order database model."""

    __tablename__ = "orders"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Exchange reference
    exchange_order_id: Mapped[Optional[str]] = mapped_column(
        String(100), unique=True, index=True
    )

    # Order details
    symbol: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    side: Mapped[OrderSide] = mapped_column(nullable=False)
    order_type: Mapped[OrderType] = mapped_column(nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        default=OrderStatus.PENDING, index=True
    )

    # Quantities and prices
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    filled_quantity: Mapped[Decimal] = mapped_column(
        Numeric(20, 8), default=Decimal("0")
    )
    price: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    average_fill_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))

    # Stop orders
    stop_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))

    # Risk management
    stop_loss: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))
    take_profit: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 8))

    # Trading mode
    is_paper_trading: Mapped[bool] = mapped_column(default=True)

    # Strategy reference
    strategy_name: Mapped[Optional[str]] = mapped_column(String(50))

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    filled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Metadata
    notes: Mapped[Optional[str]] = mapped_column(String(500))

    def __repr__(self) -> str:
        return (
            f"<Order(id={self.id}, symbol={self.symbol}, "
            f"side={self.side}, status={self.status})>"
        )
