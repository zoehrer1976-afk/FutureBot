"""
Market Data Pydantic Schemas.
"""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class TickerResponse(BaseModel):
    """Ticker data response schema."""

    symbol: str
    last_price: Decimal
    high_24h: Optional[Decimal] = None
    low_24h: Optional[Decimal] = None
    volume_24h: Optional[Decimal] = None
    price_change_24h: Optional[Decimal] = None
    price_change_percent_24h: Optional[Decimal] = None


class KlineData(BaseModel):
    """Single kline/candlestick data."""

    timestamp: int
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


class KlineResponse(BaseModel):
    """Kline data response schema."""

    symbol: str
    interval: str
    data: list[KlineData]
