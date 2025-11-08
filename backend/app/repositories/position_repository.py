"""
Position Repository - Data access layer for positions.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.position import Position

logger = get_logger(__name__)


class PositionRepository:
    """Repository for Position database operations."""

    def __init__(self, db: AsyncSession):
        """Initialize repository with database session."""
        self.db = db

    async def create(self, position: Position) -> Position:
        """Create a new position."""
        self.db.add(position)
        await self.db.flush()
        await self.db.refresh(position)
        logger.info("position_created", position_id=position.id, symbol=position.symbol)
        return position

    async def get_by_id(self, position_id: int) -> Optional[Position]:
        """Get position by ID."""
        result = await self.db.execute(
            select(Position).where(Position.id == position_id)
        )
        return result.scalar_one_or_none()

    async def get_by_symbol(self, symbol: str) -> Optional[Position]:
        """Get open position by symbol."""
        result = await self.db.execute(
            select(Position).where(
                Position.symbol == symbol,
                Position.is_open == True,
            )
        )
        return result.scalar_one_or_none()

    async def get_open_positions(self) -> list[Position]:
        """Get all open positions."""
        result = await self.db.execute(
            select(Position).where(Position.is_open == True)
        )
        return list(result.scalars().all())

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        is_open: Optional[bool] = None,
    ) -> list[Position]:
        """Get all positions with pagination."""
        query = select(Position).order_by(Position.opened_at.desc())

        if is_open is not None:
            query = query.where(Position.is_open == is_open)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update(self, position: Position) -> Position:
        """Update an existing position."""
        await self.db.flush()
        await self.db.refresh(position)
        logger.info("position_updated", position_id=position.id)
        return position

    async def close_position(self, position_id: int) -> Optional[Position]:
        """Close a position."""
        position = await self.get_by_id(position_id)
        if position:
            position.is_open = False
            from datetime import datetime
            position.closed_at = datetime.utcnow()
            await self.update(position)
            logger.info("position_closed", position_id=position_id)
            return position
        return None
