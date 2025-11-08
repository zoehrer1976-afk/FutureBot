"""
Data Service - Market data retrieval and processing.
Provides clean interface for market data access.
"""

from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.core.logging import get_logger
from app.services.bybit_client import bybit_client

logger = get_logger(__name__)


class DataService:
    """
    Service for retrieving and processing market data.

    Features:
    - Real-time ticker data
    - Historical kline/candlestick data
    - Order book data
    - Data validation and formatting
    """

    def __init__(self):
        """Initialize data service with Bybit client."""
        self.client = bybit_client
        logger.info("data_service_initialized")

    async def get_ticker(self, symbol: str) -> dict:
        """
        Get current ticker/price information for a symbol.

        Args:
            symbol: Trading pair (e.g., "BTCUSDT")

        Returns:
            Formatted ticker data
        """
        try:
            ticker_data = await self.client.get_ticker(symbol)

            # Format the response
            formatted = {
                "symbol": symbol,
                "last_price": float(ticker_data.get("lastPrice", 0)),
                "bid_price": float(ticker_data.get("bid1Price", 0)),
                "ask_price": float(ticker_data.get("ask1Price", 0)),
                "volume_24h": float(ticker_data.get("volume24h", 0)),
                "price_change_24h": float(ticker_data.get("price24hPcnt", 0)) * 100,
                "high_24h": float(ticker_data.get("highPrice24h", 0)),
                "low_24h": float(ticker_data.get("lowPrice24h", 0)),
                "timestamp": datetime.now().isoformat(),
            }

            logger.debug("ticker_retrieved", symbol=symbol, price=formatted["last_price"])
            return formatted

        except Exception as e:
            logger.error("ticker_retrieval_failed", symbol=symbol, error=str(e))
            raise

    async def get_klines(
        self,
        symbol: str,
        interval: str = "15",
        limit: int = 100,
    ) -> list[dict]:
        """
        Get candlestick/kline data for charting.

        Args:
            symbol: Trading pair
            interval: Timeframe in minutes (1, 3, 5, 15, 30, 60, 120, 240, 360, 720, D, W, M)
            limit: Number of candles (max 200)

        Returns:
            List of formatted kline data
        """
        try:
            klines = await self.client.get_kline(
                symbol=symbol,
                interval=interval,
                limit=limit,
            )

            # Format klines for frontend
            formatted_klines = []
            for kline in klines:
                formatted_klines.append({
                    "timestamp": int(kline[0]),  # Start time
                    "open": float(kline[1]),
                    "high": float(kline[2]),
                    "low": float(kline[3]),
                    "close": float(kline[4]),
                    "volume": float(kline[5]),
                })

            logger.debug(
                "klines_retrieved",
                symbol=symbol,
                interval=interval,
                count=len(formatted_klines),
            )
            return formatted_klines

        except Exception as e:
            logger.error(
                "klines_retrieval_failed",
                symbol=symbol,
                interval=interval,
                error=str(e),
            )
            raise

    async def get_orderbook(self, symbol: str, depth: int = 20) -> dict:
        """
        Get current order book (bids and asks).

        Args:
            symbol: Trading pair
            depth: Number of price levels (max 50)

        Returns:
            Formatted order book data
        """
        try:
            # Bybit orderbook endpoint
            response = self.client.client.get_orderbook(
                category="linear",
                symbol=symbol,
                limit=min(depth, 50),
            )

            if response["retCode"] != 0:
                raise Exception(f"Failed to fetch orderbook: {response.get('retMsg')}")

            result = response["result"]

            formatted = {
                "symbol": symbol,
                "bids": [
                    {"price": float(bid[0]), "quantity": float(bid[1])}
                    for bid in result.get("b", [])
                ],
                "asks": [
                    {"price": float(ask[0]), "quantity": float(ask[1])}
                    for ask in result.get("a", [])
                ],
                "timestamp": datetime.now().isoformat(),
            }

            logger.debug(
                "orderbook_retrieved",
                symbol=symbol,
                bids=len(formatted["bids"]),
                asks=len(formatted["asks"]),
            )
            return formatted

        except Exception as e:
            logger.error("orderbook_retrieval_failed", symbol=symbol, error=str(e))
            raise

    async def get_multiple_tickers(self, symbols: list[str]) -> list[dict]:
        """
        Get ticker data for multiple symbols.

        Args:
            symbols: List of trading pairs

        Returns:
            List of ticker data
        """
        tickers = []
        for symbol in symbols:
            try:
                ticker = await self.get_ticker(symbol)
                tickers.append(ticker)
            except Exception as e:
                logger.warning("ticker_fetch_failed_for_symbol", symbol=symbol, error=str(e))
                continue

        return tickers


# Singleton instance
data_service = DataService()
