"""
Position Pydantic Schemas for API validation.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from app.models.position import PositionSide


class PositionResponse(BaseModel):
    """Schema for position API responses."""

    id: int
    exchange_position_id: Optional[str] = None
    symbol: str
    side: PositionSide
    quantity: Decimal
    entry_price: Decimal
    current_price: Optional[Decimal] = None
    leverage: int
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    stop_loss: Optional[Decimal] = None
    take_profit: Optional[Decimal] = None
    liquidation_price: Optional[Decimal] = None
    is_open: bool
    is_paper_trading: bool
    strategy_name: Optional[str] = None
    opened_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class PortfolioStats(BaseModel):
    """Portfolio statistics schema."""

    initial_balance: float
    current_balance: float
    total_equity: float
    total_pnl: float
    roi_percent: float
    open_positions: int
