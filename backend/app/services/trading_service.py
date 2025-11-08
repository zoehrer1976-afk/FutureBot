"""
Trading Service - Orchestrates order execution (live or paper).
"""

from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.models.order import Order, OrderSide, OrderType
from app.repositories.order_repository import OrderRepository
from app.repositories.position_repository import PositionRepository
from app.services.bybit_client import bybit_client
from app.services.paper_trading_engine import paper_trading_engine

logger = get_logger(__name__)


class TradingService:
    """
    High-level trading service.

    Handles:
    - Order creation and execution
    - Routing to live or paper trading
    - Risk checks before execution
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize trading service.

        Args:
            db: Database session
        """
        self.db = db
        self.order_repo = OrderRepository(db)
        self.position_repo = PositionRepository(db)

    async def create_order(
        self,
        symbol: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: Decimal,
        price: Optional[Decimal] = None,
        stop_loss: Optional[Decimal] = None,
        take_profit: Optional[Decimal] = None,
        strategy_name: Optional[str] = None,
    ) -> Order:
        """
        Create and execute a new order.

        Args:
            symbol: Trading pair
            side: Buy or Sell
            order_type: Market or Limit
            quantity: Order size
            price: Limit price (if applicable)
            stop_loss: Stop loss price
            take_profit: Take profit price
            strategy_name: Name of strategy placing this order

        Returns:
            Created order

        Raises:
            ValueError: If risk checks fail
        """
        # Create order model
        order = Order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            strategy_name=strategy_name,
            is_paper_trading=settings.ENABLE_PAPER_TRADING,
        )

        # Risk checks
        await self._validate_order(order)

        # Save to database
        order = await self.order_repo.create(order)

        # Execute order
        if settings.ENABLE_PAPER_TRADING:
            order = await paper_trading_engine.execute_order(order)
        else:
            order = await self._execute_live_order(order)

        # Update in database
        await self.order_repo.update(order)

        logger.info(
            "order_created_and_executed",
            order_id=order.id,
            status=order.status,
            paper_trading=settings.ENABLE_PAPER_TRADING,
        )

        return order

    async def cancel_order(self, order_id: int) -> Order:
        """
        Cancel an existing order.

        Args:
            order_id: Order ID to cancel

        Returns:
            Cancelled order

        Raises:
            ValueError: If order not found or cannot be cancelled
        """
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order {order_id} not found")

        if order.status != "pending":
            raise ValueError(f"Cannot cancel order with status {order.status}")

        if settings.ENABLE_PAPER_TRADING:
            # Paper trading: just mark as cancelled
            from app.models.order import OrderStatus
            order.status = OrderStatus.CANCELLED
        else:
            # Live trading: cancel on exchange
            if order.exchange_order_id:
                await bybit_client.cancel_order(order.symbol, order.exchange_order_id)
            from app.models.order import OrderStatus
            order.status = OrderStatus.CANCELLED

        await self.order_repo.update(order)
        logger.info("order_cancelled", order_id=order_id)

        return order

    async def get_orders(
        self,
        skip: int = 0,
        limit: int = 100,
        symbol: Optional[str] = None,
    ) -> tuple[list[Order], int]:
        """
        Get orders with pagination.

        Args:
            skip: Number to skip
            limit: Max results
            symbol: Optional symbol filter

        Returns:
            Tuple of (orders list, total count)
        """
        orders = await self.order_repo.get_all(skip=skip, limit=limit, symbol=symbol)
        total = await self.order_repo.count(symbol=symbol)
        return orders, total

    async def get_open_positions(self):
        """Get all open positions."""
        return await self.position_repo.get_open_positions()

    async def _validate_order(self, order: Order) -> None:
        """
        Validate order against risk rules.

        Args:
            order: Order to validate

        Raises:
            ValueError: If validation fails
        """
        # Check max position size
        position_value = order.quantity * (order.price or Decimal("0"))
        if position_value > Decimal(str(settings.MAX_POSITION_SIZE_USD)):
            raise ValueError(
                f"Position size {position_value} exceeds max "
                f"{settings.MAX_POSITION_SIZE_USD}"
            )

        # Check max open positions
        open_positions = await self.position_repo.get_open_positions()
        if len(open_positions) >= settings.MAX_OPEN_POSITIONS:
            # Allow closing positions
            if order.side == OrderSide.SELL:
                pass
            else:
                raise ValueError(
                    f"Max open positions ({settings.MAX_OPEN_POSITIONS}) reached"
                )

        # Additional validations can be added here
        # - Check daily drawdown limit
        # - Check correlation with existing positions
        # - Check liquidity
        # etc.

    async def _execute_live_order(self, order: Order) -> Order:
        """
        Execute order on live exchange.

        Args:
            order: Order to execute

        Returns:
            Updated order with exchange details
        """
        try:
            result = await bybit_client.place_order(
                symbol=order.symbol,
                side=order.side.value,
                order_type=order.order_type.value,
                qty=order.quantity,
                price=order.price,
                stop_loss=order.stop_loss,
                take_profit=order.take_profit,
            )

            # Update order with exchange info
            order.exchange_order_id = result.get("orderId")
            from app.models.order import OrderStatus
            order.status = OrderStatus.PENDING
            # Note: Real status updates would come from webhooks or polling

            logger.info(
                "live_order_placed",
                order_id=order.id,
                exchange_order_id=order.exchange_order_id,
            )

        except Exception as e:
            from app.models.order import OrderStatus
            order.status = OrderStatus.REJECTED
            order.notes = str(e)
            logger.error(
                "live_order_failed",
                order_id=order.id,
                error=str(e),
                exc_info=True,
            )

        return order

    async def get_portfolio_stats(self) -> dict:
        """
        Get portfolio statistics.

        Returns:
            Portfolio stats (balance, P&L, etc.)
        """
        if settings.ENABLE_PAPER_TRADING:
            return paper_trading_engine.get_statistics()
        else:
            # For live trading, fetch from exchange
            wallet = await bybit_client.get_wallet_balance()
            # Parse wallet data and return stats
            # This is simplified - real implementation would be more complex
            return {
                "balance": wallet.get("totalEquity", 0),
                "unrealized_pnl": wallet.get("totalPerpUPL", 0),
            }
