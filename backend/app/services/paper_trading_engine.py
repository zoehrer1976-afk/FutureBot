"""
Paper Trading Engine - Simulates order execution without real money.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from app.core.logging import get_logger
from app.models.order import Order, OrderSide, OrderStatus, OrderType
from app.models.position import Position, PositionSide
from app.services.bybit_client import bybit_client

logger = get_logger(__name__)


class PaperTradingEngine:
    """
    Simulates order execution for paper trading.

    Features:
    - Realistic price slippage simulation
    - Position tracking
    - P&L calculation
    - Market price fetching for execution
    """

    def __init__(self, initial_balance: Decimal = Decimal("10000")):
        """
        Initialize paper trading engine.

        Args:
            initial_balance: Starting balance in USDT
        """
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.positions: dict[str, Position] = {}
        logger.info("paper_trading_engine_initialized", balance=float(initial_balance))

    async def execute_order(self, order: Order) -> Order:
        """
        Execute an order in paper trading mode.

        Args:
            order: Order to execute

        Returns:
            Updated order with execution details

        Raises:
            ValueError: If insufficient balance or invalid order
        """
        try:
            # Get current market price
            ticker = await bybit_client.get_ticker(order.symbol)
            current_price = Decimal(ticker["lastPrice"])

            # Determine execution price
            execution_price = self._calculate_execution_price(
                order.order_type,
                order.side,
                current_price,
                order.price,
            )

            # Check if we can afford this order
            position_value = execution_price * order.quantity
            if position_value > self.balance:
                order.status = OrderStatus.REJECTED
                order.notes = "Insufficient balance"
                logger.warning(
                    "order_rejected_insufficient_balance",
                    order_id=order.id,
                    required=float(position_value),
                    available=float(self.balance),
                )
                return order

            # Execute the order
            order.status = OrderStatus.FILLED
            order.filled_quantity = order.quantity
            order.average_fill_price = execution_price
            order.filled_at = datetime.utcnow()
            order.exchange_order_id = f"paper_{uuid4().hex[:16]}"

            # Update balance and positions
            await self._update_positions(order, execution_price)

            logger.info(
                "paper_order_executed",
                order_id=order.id,
                symbol=order.symbol,
                side=order.side,
                quantity=float(order.quantity),
                price=float(execution_price),
            )

            return order

        except Exception as e:
            order.status = OrderStatus.REJECTED
            order.notes = f"Execution error: {str(e)}"
            logger.error(
                "paper_order_execution_failed",
                order_id=order.id,
                error=str(e),
                exc_info=True,
            )
            return order

    def _calculate_execution_price(
        self,
        order_type: OrderType,
        side: OrderSide,
        market_price: Decimal,
        limit_price: Optional[Decimal],
    ) -> Decimal:
        """
        Calculate realistic execution price with slippage.

        Args:
            order_type: Market or Limit order
            side: Buy or Sell
            market_price: Current market price
            limit_price: Limit price (if applicable)

        Returns:
            Execution price
        """
        if order_type == OrderType.MARKET:
            # Simulate slippage (0.05% for market orders)
            slippage = Decimal("0.0005")
            if side == OrderSide.BUY:
                return market_price * (Decimal("1") + slippage)
            else:
                return market_price * (Decimal("1") - slippage)

        elif order_type == OrderType.LIMIT:
            # Limit orders execute at limit price or better
            if limit_price is None:
                raise ValueError("Limit orders require a price")

            if side == OrderSide.BUY:
                # Buy limit: execute if market <= limit
                return min(limit_price, market_price)
            else:
                # Sell limit: execute if market >= limit
                return max(limit_price, market_price)

        return market_price

    async def _update_positions(self, order: Order, execution_price: Decimal) -> None:
        """
        Update positions based on executed order.

        Args:
            order: Executed order
            execution_price: Price at which order was executed
        """
        symbol = order.symbol
        existing_position = self.positions.get(symbol)

        if order.side == OrderSide.BUY:
            if existing_position:
                # Add to existing position
                existing_position.quantity += order.quantity
                # Recalculate average entry price
                total_value = (
                    existing_position.entry_price * existing_position.quantity
                )
                new_value = execution_price * order.quantity
                existing_position.entry_price = (total_value + new_value) / (
                    existing_position.quantity + order.quantity
                )
            else:
                # Create new long position
                position = Position(
                    symbol=symbol,
                    side=PositionSide.LONG,
                    quantity=order.quantity,
                    entry_price=execution_price,
                    current_price=execution_price,
                    leverage=1,
                    is_paper_trading=True,
                    strategy_name=order.strategy_name,
                )
                self.positions[symbol] = position

            # Deduct from balance
            self.balance -= execution_price * order.quantity

        elif order.side == OrderSide.SELL:
            if existing_position:
                # Close or reduce position
                if order.quantity >= existing_position.quantity:
                    # Close entire position
                    pnl = (execution_price - existing_position.entry_price) * existing_position.quantity
                    self.balance += execution_price * existing_position.quantity
                    existing_position.realized_pnl += pnl
                    existing_position.is_open = False
                    existing_position.closed_at = datetime.utcnow()
                    del self.positions[symbol]
                    logger.info(
                        "position_closed",
                        symbol=symbol,
                        pnl=float(pnl),
                        balance=float(self.balance),
                    )
                else:
                    # Partial close
                    existing_position.quantity -= order.quantity
                    pnl = (execution_price - existing_position.entry_price) * order.quantity
                    self.balance += execution_price * order.quantity
                    existing_position.realized_pnl += pnl
            else:
                # Create new short position
                position = Position(
                    symbol=symbol,
                    side=PositionSide.SHORT,
                    quantity=order.quantity,
                    entry_price=execution_price,
                    current_price=execution_price,
                    leverage=1,
                    is_paper_trading=True,
                    strategy_name=order.strategy_name,
                )
                self.positions[symbol] = position
                self.balance += execution_price * order.quantity

    async def update_positions_prices(self) -> None:
        """Update all open positions with current market prices."""
        for symbol, position in self.positions.items():
            try:
                ticker = await bybit_client.get_ticker(symbol)
                current_price = Decimal(ticker["lastPrice"])
                position.current_price = current_price

                # Calculate unrealized P&L
                if position.side == PositionSide.LONG:
                    position.unrealized_pnl = (
                        current_price - position.entry_price
                    ) * position.quantity
                else:  # SHORT
                    position.unrealized_pnl = (
                        position.entry_price - current_price
                    ) * position.quantity

            except Exception as e:
                logger.error(
                    "position_price_update_failed",
                    symbol=symbol,
                    error=str(e),
                )

    def get_total_equity(self) -> Decimal:
        """
        Calculate total equity (balance + unrealized P&L).

        Returns:
            Total account equity
        """
        total_pnl = sum(
            pos.unrealized_pnl for pos in self.positions.values()
        )
        return self.balance + total_pnl

    def get_total_pnl(self) -> Decimal:
        """
        Calculate total P&L (realized + unrealized).

        Returns:
            Total profit/loss
        """
        realized_pnl = sum(
            pos.realized_pnl for pos in self.positions.values()
        )
        unrealized_pnl = sum(
            pos.unrealized_pnl for pos in self.positions.values()
        )
        return realized_pnl + unrealized_pnl

    def get_statistics(self) -> dict:
        """
        Get trading statistics.

        Returns:
            Dictionary with trading stats
        """
        total_equity = self.get_total_equity()
        total_pnl = self.get_total_pnl()
        roi = (
            (total_equity - self.initial_balance) / self.initial_balance * 100
        )

        return {
            "initial_balance": float(self.initial_balance),
            "current_balance": float(self.balance),
            "total_equity": float(total_equity),
            "total_pnl": float(total_pnl),
            "roi_percent": float(roi),
            "open_positions": len(self.positions),
        }


# Global instance for paper trading
paper_trading_engine = PaperTradingEngine()
