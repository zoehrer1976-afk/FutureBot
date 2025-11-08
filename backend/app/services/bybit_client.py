"""
Bybit API Client - Wrapper for Bybit exchange API.
Handles market data, order execution, and account information.
"""

from typing import Any, Optional
from decimal import Decimal

from pybit.unified_trading import HTTP
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class BybitClient:
    """
    Bybit API client with retry logic and error handling.

    Wraps the pybit library for:
    - Market data retrieval
    - Order placement and management
    - Position tracking
    - Account information
    """

    def __init__(self):
        """Initialize Bybit client with API credentials."""
        self.client = HTTP(
            testnet=settings.BYBIT_TESTNET,
            api_key=settings.BYBIT_API_KEY,
            api_secret=settings.BYBIT_API_SECRET,
        )
        logger.info(
            "bybit_client_initialized",
            testnet=settings.BYBIT_TESTNET,
            base_url=settings.BYBIT_BASE_URL,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def get_ticker(self, symbol: str) -> dict[str, Any]:
        """
        Get latest ticker information for a symbol.

        Args:
            symbol: Trading pair (e.g., "BTCUSDT")

        Returns:
            Ticker data including last price, volume, etc.

        Raises:
            Exception: If API request fails after retries
        """
        try:
            response = self.client.get_tickers(category="linear", symbol=symbol)
            if response["retCode"] == 0:
                logger.debug("ticker_fetched", symbol=symbol)
                return response["result"]["list"][0]
            else:
                error_msg = response.get("retMsg", "Unknown error")
                logger.error("ticker_fetch_failed", symbol=symbol, error=error_msg)
                raise Exception(f"Failed to fetch ticker: {error_msg}")
        except Exception as e:
            logger.error("ticker_fetch_exception", symbol=symbol, error=str(e))
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def get_kline(
        self,
        symbol: str,
        interval: str = "1",
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        """
        Get candlestick (kline) data.

        Args:
            symbol: Trading pair
            interval: Timeframe (1, 3, 5, 15, 30, 60, 120, 240, 360, 720, D, W, M)
            limit: Number of candles (max 200)

        Returns:
            List of kline data
        """
        try:
            response = self.client.get_kline(
                category="linear",
                symbol=symbol,
                interval=interval,
                limit=limit,
            )
            if response["retCode"] == 0:
                logger.debug(
                    "kline_fetched",
                    symbol=symbol,
                    interval=interval,
                    count=len(response["result"]["list"]),
                )
                return response["result"]["list"]
            else:
                raise Exception(f"Failed to fetch kline: {response.get('retMsg')}")
        except Exception as e:
            logger.error("kline_fetch_exception", symbol=symbol, error=str(e))
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        qty: Decimal,
        price: Optional[Decimal] = None,
        stop_loss: Optional[Decimal] = None,
        take_profit: Optional[Decimal] = None,
    ) -> dict[str, Any]:
        """
        Place an order on Bybit.

        Args:
            symbol: Trading pair
            side: "Buy" or "Sell"
            order_type: "Market" or "Limit"
            qty: Order quantity
            price: Limit price (required for Limit orders)
            stop_loss: Stop loss price
            take_profit: Take profit price

        Returns:
            Order response with order ID

        Raises:
            Exception: If order placement fails
        """
        try:
            params: dict[str, Any] = {
                "category": "linear",
                "symbol": symbol,
                "side": side.capitalize(),
                "orderType": order_type.capitalize(),
                "qty": str(qty),
            }

            if price is not None:
                params["price"] = str(price)

            if stop_loss is not None:
                params["stopLoss"] = str(stop_loss)

            if take_profit is not None:
                params["takeProfit"] = str(take_profit)

            response = self.client.place_order(**params)

            if response["retCode"] == 0:
                order_id = response["result"]["orderId"]
                logger.info(
                    "order_placed",
                    symbol=symbol,
                    side=side,
                    order_type=order_type,
                    qty=qty,
                    order_id=order_id,
                )
                return response["result"]
            else:
                error_msg = response.get("retMsg", "Unknown error")
                logger.error("order_placement_failed", error=error_msg, params=params)
                raise Exception(f"Order placement failed: {error_msg}")

        except Exception as e:
            logger.error("order_placement_exception", error=str(e), exc_info=True)
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2))
    async def cancel_order(self, symbol: str, order_id: str) -> dict[str, Any]:
        """
        Cancel an existing order.

        Args:
            symbol: Trading pair
            order_id: Bybit order ID

        Returns:
            Cancellation response
        """
        try:
            response = self.client.cancel_order(
                category="linear",
                symbol=symbol,
                orderId=order_id,
            )

            if response["retCode"] == 0:
                logger.info("order_cancelled", symbol=symbol, order_id=order_id)
                return response["result"]
            else:
                raise Exception(f"Cancel failed: {response.get('retMsg')}")

        except Exception as e:
            logger.error("order_cancel_exception", error=str(e))
            raise

    async def get_positions(self, symbol: Optional[str] = None) -> list[dict[str, Any]]:
        """
        Get open positions.

        Args:
            symbol: Optional symbol filter

        Returns:
            List of open positions
        """
        try:
            params: dict[str, Any] = {"category": "linear", "settleCoin": "USDT"}
            if symbol:
                params["symbol"] = symbol

            response = self.client.get_positions(**params)

            if response["retCode"] == 0:
                positions = response["result"]["list"]
                logger.debug("positions_fetched", count=len(positions))
                return positions
            else:
                raise Exception(f"Get positions failed: {response.get('retMsg')}")

        except Exception as e:
            logger.error("positions_fetch_exception", error=str(e))
            raise

    async def get_wallet_balance(self) -> dict[str, Any]:
        """
        Get account wallet balance.

        Returns:
            Wallet balance information
        """
        try:
            response = self.client.get_wallet_balance(accountType="UNIFIED")

            if response["retCode"] == 0:
                balance = response["result"]
                logger.debug("wallet_balance_fetched")
                return balance
            else:
                raise Exception(f"Get balance failed: {response.get('retMsg')}")

        except Exception as e:
            logger.error("wallet_balance_exception", error=str(e))
            raise


# Singleton instance
bybit_client = BybitClient()
