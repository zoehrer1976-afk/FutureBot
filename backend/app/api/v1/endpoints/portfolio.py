"""
Portfolio API Endpoints
Handles portfolio statistics and performance tracking.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_db, get_logger
from app.schemas.position import PortfolioStats
from app.services.trading_service import TradingService

logger = get_logger(__name__)
router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/stats", response_model=PortfolioStats)
async def get_portfolio_stats(
    db: AsyncSession = Depends(get_db),
) -> PortfolioStats:
    """
    Get portfolio statistics.

    Returns:
        Portfolio stats including balance, P&L, ROI, etc.
    """
    try:
        trading_service = TradingService(db)
        stats = await trading_service.get_portfolio_stats()

        return PortfolioStats(**stats)

    except Exception as e:
        logger.error("api_portfolio_stats_error", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
