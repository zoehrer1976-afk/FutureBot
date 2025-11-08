"""
Unit tests for OrderRepository.
"""

from decimal import Decimal

import pytest

from app.models.order import Order, OrderSide, OrderStatus, OrderType
from app.repositories.order_repository import OrderRepository


@pytest.mark.asyncio
async def test_create_order(db_session):
    """Test creating an order."""
    repo = OrderRepository(db_session)

    order = Order(
        symbol="BTCUSDT",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=Decimal("0.001"),
        is_paper_trading=True,
    )

    created_order = await repo.create(order)

    assert created_order.id is not None
    assert created_order.symbol == "BTCUSDT"
    assert created_order.side == OrderSide.BUY
    assert created_order.status == OrderStatus.PENDING


@pytest.mark.asyncio
async def test_get_order_by_id(db_session):
    """Test retrieving an order by ID."""
    repo = OrderRepository(db_session)

    order = Order(
        symbol="ETHUSDT",
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        quantity=Decimal("0.1"),
        price=Decimal("2000"),
        is_paper_trading=True,
    )

    created_order = await repo.create(order)
    retrieved_order = await repo.get_by_id(created_order.id)

    assert retrieved_order is not None
    assert retrieved_order.id == created_order.id
    assert retrieved_order.symbol == "ETHUSDT"


@pytest.mark.asyncio
async def test_get_all_orders(db_session):
    """Test retrieving all orders with pagination."""
    repo = OrderRepository(db_session)

    # Create multiple orders
    for i in range(5):
        order = Order(
            symbol="BTCUSDT",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("0.001"),
            is_paper_trading=True,
        )
        await repo.create(order)

    orders = await repo.get_all(skip=0, limit=10)
    assert len(orders) == 5

    # Test pagination
    first_page = await repo.get_all(skip=0, limit=2)
    assert len(first_page) == 2

    second_page = await repo.get_all(skip=2, limit=2)
    assert len(second_page) == 2


@pytest.mark.asyncio
async def test_update_order(db_session):
    """Test updating an order."""
    repo = OrderRepository(db_session)

    order = Order(
        symbol="BTCUSDT",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        quantity=Decimal("0.001"),
        is_paper_trading=True,
    )

    created_order = await repo.create(order)
    created_order.status = OrderStatus.FILLED
    created_order.filled_quantity = created_order.quantity

    updated_order = await repo.update(created_order)

    assert updated_order.status == OrderStatus.FILLED
    assert updated_order.filled_quantity == Decimal("0.001")


@pytest.mark.asyncio
async def test_get_active_orders(db_session):
    """Test retrieving only active (pending) orders."""
    repo = OrderRepository(db_session)

    # Create pending order
    pending_order = Order(
        symbol="BTCUSDT",
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Decimal("0.001"),
        price=Decimal("40000"),
        status=OrderStatus.PENDING,
        is_paper_trading=True,
    )
    await repo.create(pending_order)

    # Create filled order
    filled_order = Order(
        symbol="ETHUSDT",
        side=OrderSide.SELL,
        order_type=OrderType.MARKET,
        quantity=Decimal("0.1"),
        status=OrderStatus.FILLED,
        is_paper_trading=True,
    )
    await repo.create(filled_order)

    active_orders = await repo.get_active_orders()

    assert len(active_orders) == 1
    assert active_orders[0].status == OrderStatus.PENDING
