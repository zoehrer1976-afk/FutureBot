"""
Market Data API Endpoints
Provides market data from Bybit.
"""

from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query

from app.core import get_logger
from app.schemas.market_data import KlineData, KlineResponse, TickerResponse
from app.services.bybit_client import bybit_client

logger = get_logger(__name__)
router = APIRouter(prefix="/market-data", tags=["market-data"])


@router.get("/ticker/{symbol}", response_model=TickerResponse)
async def get_ticker(symbol: str) -> TickerResponse:
    """
    Get latest ticker information for a symbol.

    Args:
        symbol: Trading pair (e.g., BTCUSDT)

    Returns:
        Ticker data

    Raises:
        HTTPException: If ticker fetch fails
    """
    try:
        ticker = await bybit_client.get_ticker(symbol.upper())

        return TickerResponse(
            symbol=symbol.upper(),
            last_price=Decimal(ticker["lastPrice"]),
            high_24h=Decimal(ticker.get("highPrice24h", 0)),
            low_24h=Decimal(ticker.get("lowPrice24h", 0)),
            volume_24h=Decimal(ticker.get("volume24h", 0)),
            price_change_24h=Decimal(ticker.get("price24hPcnt", 0)),
        )

    except Exception as e:
        logger.error("api_ticker_fetch_error", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch ticker: {str(e)}")


@router.get("/kline/{symbol}", response_model=KlineResponse)
async def get_kline(
    symbol: str,
    interval: str = Query("1", description="Timeframe (1, 5, 15, 60, D, etc.)"),
    limit: int = Query(100, ge=1, le=200, description="Number of candles"),
) -> KlineResponse:
    """
    Get candlestick (kline) data for a symbol.

    Args:
        symbol: Trading pair
        interval: Timeframe
        limit: Number of candles

    Returns:
        Kline data

    Raises:
        HTTPException: If kline fetch fails
    """
    try:
        klines = await bybit_client.get_kline(
            symbol=symbol.upper(),
            interval=interval,
            limit=limit,
        )

        kline_data = [
            KlineData(
                timestamp=int(k[0]),
                open=Decimal(k[1]),
                high=Decimal(k[2]),
                low=Decimal(k[3]),
                close=Decimal(k[4]),
                volume=Decimal(k[5]),
            )
            for k in klines
        ]

        return KlineResponse(
            symbol=symbol.upper(),
            interval=interval,
            data=kline_data,
        )

    except Exception as e:
        logger.error("api_kline_fetch_error", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch kline: {str(e)}")
