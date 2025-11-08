"""
Orders API Endpoints
Handles order creation, retrieval, and cancellation.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, get_logger
from app.schemas.order import OrderCreate, OrderListResponse, OrderResponse
from app.services.trading_service import TradingService

logger = get_logger(__name__)
router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    Create a new trading order.

    Args:
        order_data: Order creation data
        db: Database session

    Returns:
        Created order

    Raises:
        HTTPException: If order creation fails
    """
    try:
        trading_service = TradingService(db)
        order = await trading_service.create_order(
            symbol=order_data.symbol,
            side=order_data.side,
            order_type=order_data.order_type,
            quantity=order_data.quantity,
            price=order_data.price,
            stop_loss=order_data.stop_loss,
            take_profit=order_data.take_profit,
            strategy_name=order_data.strategy_name,
        )

        logger.info("api_order_created", order_id=order.id, symbol=order.symbol)
        return OrderResponse.model_validate(order)

    except ValueError as e:
        logger.warning("api_order_creation_failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("api_order_creation_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("", response_model=OrderListResponse)
async def list_orders(
    skip: int = Query(0, ge=0, description="Number of orders to skip"),
    limit: int = Query(100, ge=1, le=500, description="Max orders to return"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    db: AsyncSession = Depends(get_db),
) -> OrderListResponse:
    """
    List orders with pagination and filtering.

    Args:
        skip: Pagination offset
        limit: Max results
        symbol: Optional symbol filter
        db: Database session

    Returns:
        Paginated order list
    """
    try:
        trading_service = TradingService(db)
        orders, total = await trading_service.get_orders(
            skip=skip,
            limit=limit,
            symbol=symbol,
        )

        page = skip // limit + 1 if limit > 0 else 1

        return OrderListResponse(
            orders=[OrderResponse.model_validate(o) for o in orders],
            total=total,
            page=page,
            page_size=limit,
        )

    except Exception as e:
        logger.error("api_list_orders_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    Get a specific order by ID.

    Args:
        order_id: Order ID
        db: Database session

    Returns:
        Order details

    Raises:
        HTTPException: If order not found
    """
    try:
        trading_service = TradingService(db)
        order = await trading_service.order_repo.get_by_id(order_id)

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        return OrderResponse.model_validate(order)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("api_get_order_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{order_id}", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
) -> OrderResponse:
    """
    Cancel an existing order.

    Args:
        order_id: Order ID to cancel
        db: Database session

    Returns:
        Cancelled order

    Raises:
        HTTPException: If order not found or cannot be cancelled
    """
    try:
        trading_service = TradingService(db)
        order = await trading_service.cancel_order(order_id)

        logger.info("api_order_cancelled", order_id=order_id)
        return OrderResponse.model_validate(order)

    except ValueError as e:
        logger.warning("api_order_cancellation_failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("api_cancel_order_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
