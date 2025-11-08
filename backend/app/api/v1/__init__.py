"""
API v1 Router
Combines all v1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import market_data, orders, portfolio, positions

# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(orders.router)
api_router.include_router(positions.router)
api_router.include_router(portfolio.router)
api_router.include_router(market_data.router)

__all__ = ["api_router"]
