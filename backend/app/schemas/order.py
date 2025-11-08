"""
Order Pydantic Schemas for API validation.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.order import OrderSide, OrderStatus, OrderType


class OrderBase(BaseModel):
    """Base order schema with common fields."""

    symbol: str = Field(..., min_length=3, max_length=20, description="Trading pair")
    side: OrderSide = Field(..., description="Buy or Sell")
    order_type: OrderType = Field(..., description="Order type")
    quantity: Decimal = Field(..., gt=0, description="Order quantity")
    price: Optional[Decimal] = Field(None, gt=0, description="Limit price")
    stop_price: Optional[Decimal] = Field(None, gt=0, description="Stop trigger price")
    stop_loss: Optional[Decimal] = Field(None, gt=0, description="Stop loss price")
    take_profit: Optional[Decimal] = Field(None, gt=0, description="Take profit price")

    @field_validator("symbol")
    @classmethod
    def validate_symbol(cls, v: str) -> str:
        """Ensure symbol is uppercase."""
        return v.upper()


class OrderCreate(OrderBase):
    """Schema for creating a new order."""

    strategy_name: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)

    @field_validator("price")
    @classmethod
    def validate_limit_price(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        """Ensure limit orders have a price."""
        order_type = info.data.get("order_type")
        if order_type in [OrderType.LIMIT, OrderType.STOP_LIMIT] and v is None:
            raise ValueError("Limit orders require a price")
        return v


class OrderUpdate(BaseModel):
    """Schema for updating an existing order."""

    quantity: Optional[Decimal] = Field(None, gt=0)
    price: Optional[Decimal] = Field(None, gt=0)
    stop_loss: Optional[Decimal] = Field(None, gt=0)
    take_profit: Optional[Decimal] = Field(None, gt=0)


class OrderResponse(OrderBase):
    """Schema for order API responses."""

    id: int
    exchange_order_id: Optional[str] = None
    status: OrderStatus
    filled_quantity: Decimal
    average_fill_price: Optional[Decimal] = None
    is_paper_trading: bool
    strategy_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    filled_at: Optional[datetime] = None
    notes: Optional[str] = None

    model_config = {"from_attributes": True}


class OrderListResponse(BaseModel):
    """Schema for paginated order list."""

    orders: list[OrderResponse]
    total: int
    page: int
    page_size: int
