"""
Order Repository - Data access layer for orders.
Handles all database operations for orders.
"""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.order import Order, OrderStatus

logger = get_logger(__name__)


class OrderRepository:
    """Repository for Order database operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            db: SQLAlchemy async session
        """
        self.db = db

    async def create(self, order: Order) -> Order:
        """
        Create a new order in the database.

        Args:
            order: Order model instance

        Returns:
            Created order with ID
        """
        self.db.add(order)
        await self.db.flush()
        await self.db.refresh(order)
        logger.info("order_created", order_id=order.id, symbol=order.symbol)
        return order

    async def get_by_id(self, order_id: int) -> Optional[Order]:
        """
        Get order by ID.

        Args:
            order_id: Order ID

        Returns:
            Order if found, None otherwise
        """
        result = await self.db.execute(select(Order).where(Order.id == order_id))
        return result.scalar_one_or_none()

    async def get_by_exchange_id(self, exchange_order_id: str) -> Optional[Order]:
        """
        Get order by exchange order ID.

        Args:
            exchange_order_id: Bybit order ID

        Returns:
            Order if found, None otherwise
        """
        result = await self.db.execute(
            select(Order).where(Order.exchange_order_id == exchange_order_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[OrderStatus] = None,
        symbol: Optional[str] = None,
    ) -> list[Order]:
        """
        Get all orders with optional filters.

        Args:
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            status: Filter by order status
            symbol: Filter by trading symbol

        Returns:
            List of orders
        """
        query = select(Order).order_by(Order.created_at.desc())

        if status:
            query = query.where(Order.status == status)

        if symbol:
            query = query.where(Order.symbol == symbol)

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count(
        self,
        status: Optional[OrderStatus] = None,
        symbol: Optional[str] = None,
    ) -> int:
        """
        Count orders with optional filters.

        Args:
            status: Filter by order status
            symbol: Filter by trading symbol

        Returns:
            Total count of orders
        """
        query = select(func.count(Order.id))

        if status:
            query = query.where(Order.status == status)

        if symbol:
            query = query.where(Order.symbol == symbol)

        result = await self.db.execute(query)
        return result.scalar_one()

    async def update(self, order: Order) -> Order:
        """
        Update an existing order.

        Args:
            order: Order instance with updated fields

        Returns:
            Updated order
        """
        await self.db.flush()
        await self.db.refresh(order)
        logger.info("order_updated", order_id=order.id, status=order.status)
        return order

    async def delete(self, order_id: int) -> bool:
        """
        Delete an order (soft delete by setting status).

        Args:
            order_id: Order ID to delete

        Returns:
            True if deleted, False if not found
        """
        order = await self.get_by_id(order_id)
        if order:
            order.status = OrderStatus.CANCELLED
            await self.update(order)
            logger.info("order_deleted", order_id=order_id)
            return True
        return False

    async def get_active_orders(self, symbol: Optional[str] = None) -> list[Order]:
        """
        Get all active (pending) orders.

        Args:
            symbol: Optional symbol filter

        Returns:
            List of active orders
        """
        query = select(Order).where(Order.status == OrderStatus.PENDING)

        if symbol:
            query = query.where(Order.symbol == symbol)

        result = await self.db.execute(query)
        return list(result.scalars().all())
