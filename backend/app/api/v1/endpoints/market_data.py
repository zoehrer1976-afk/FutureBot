"""
Market Data API Endpoints
Provides market data from Bybit.
"""

from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query

from app.core import get_logger
from app.schemas.market_data import KlineData, KlineResponse, TickerResponse
from app.services.data_service import data_service

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
        ticker = await data_service.get_ticker(symbol.upper())

        return TickerResponse(
            symbol=ticker["symbol"],
            last_price=Decimal(str(ticker["last_price"])),
            high_24h=Decimal(str(ticker["high_24h"])),
            low_24h=Decimal(str(ticker["low_24h"])),
            volume_24h=Decimal(str(ticker["volume_24h"])),
            price_change_24h=Decimal(str(ticker["price_change_24h"])),
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
        klines = await data_service.get_klines(
            symbol=symbol.upper(),
            interval=interval,
            limit=limit,
        )

        kline_data = [
            KlineData(
                timestamp=k["timestamp"],
                open=Decimal(str(k["open"])),
                high=Decimal(str(k["high"])),
                low=Decimal(str(k["low"])),
                close=Decimal(str(k["close"])),
                volume=Decimal(str(k["volume"])),
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


@router.get("/{symbol}/orderbook")
async def get_orderbook(
    symbol: str,
    depth: int = Query(20, ge=1, le=50, description="Order book depth"),
) -> dict:
    """
    Get order book (bids and asks) for a symbol.

    Args:
        symbol: Trading pair
        depth: Number of price levels

    Returns:
        Order book data

    Raises:
        HTTPException: If orderbook fetch fails
    """
    try:
        orderbook = await data_service.get_orderbook(symbol.upper(), depth)
        return orderbook

    except Exception as e:
        logger.error("api_orderbook_fetch_error", symbol=symbol, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch orderbook: {str(e)}")


@router.get("")
async def get_market_data(
    symbols: str = Query(None, description="Comma-separated list of symbols"),
) -> list[dict]:
    """
    Get market data for multiple symbols.

    Args:
        symbols: Comma-separated symbols (e.g., "BTCUSDT,ETHUSDT")

    Returns:
        List of ticker data

    Raises:
        HTTPException: If market data fetch fails
    """
    try:
        # Default symbols if none provided
        symbol_list = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]

        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(",")]

        tickers = await data_service.get_multiple_tickers(symbol_list)
        return tickers

    except Exception as e:
        logger.error("api_market_data_fetch_error", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {str(e)}")
