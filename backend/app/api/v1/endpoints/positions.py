"""
Positions API Endpoints
Handles position retrieval and management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, get_logger
from app.schemas.position import PositionResponse
from app.services.trading_service import TradingService

logger = get_logger(__name__)
router = APIRouter(prefix="/positions", tags=["positions"])


@router.get("", response_model=list[PositionResponse])
async def list_positions(
    db: AsyncSession = Depends(get_db),
) -> list[PositionResponse]:
    """
    Get all open positions.

    Args:
        db: Database session

    Returns:
        List of open positions
    """
    try:
        trading_service = TradingService(db)
        positions = await trading_service.get_open_positions()

        return [PositionResponse.model_validate(p) for p in positions]

    except Exception as e:
        logger.error("api_list_positions_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{position_id}", response_model=PositionResponse)
async def get_position(
    position_id: int,
    db: AsyncSession = Depends(get_db),
) -> PositionResponse:
    """
    Get a specific position by ID.

    Args:
        position_id: Position ID
        db: Database session

    Returns:
        Position details

    Raises:
        HTTPException: If position not found
    """
    try:
        trading_service = TradingService(db)
        position = await trading_service.position_repo.get_by_id(position_id)

        if not position:
            raise HTTPException(status_code=404, detail="Position not found")

        return PositionResponse.model_validate(position)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("api_get_position_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{position_id}/close", response_model=PositionResponse)
async def close_position(
    position_id: int,
    db: AsyncSession = Depends(get_db),
) -> PositionResponse:
    """
    Close an open position.

    Args:
        position_id: Position ID to close
        db: Database session

    Returns:
        Closed position

    Raises:
        HTTPException: If position not found
    """
    try:
        trading_service = TradingService(db)
        position = await trading_service.position_repo.close_position(position_id)

        if not position:
            raise HTTPException(status_code=404, detail="Position not found")

        logger.info("api_position_closed", position_id=position_id)
        return PositionResponse.model_validate(position)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("api_close_position_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
