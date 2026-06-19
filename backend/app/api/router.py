"""
Trader Copilot AI — API Router Aggregator

Collects all module routers into a single parent router.
New API modules are registered here.
"""

from fastapi import APIRouter

# Main API router — all module routers are included here
api_router = APIRouter(prefix="/api")


# Health check endpoint (no auth required)
@api_router.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "healthy",
        "service": "Trader Copilot AI",
        "version": "0.1.0",
    }


# ── Module routers will be added here as we build each phase ──
from app.api.auth.routes import router as auth_router
from app.api.strategies.routes import router as strategies_router
from app.api.trades.routes import router as trades_router
from app.api.risk.routes import router as risk_router
from app.api.analytics.routes import router as analytics_router
from app.api.ai.routes import router as ai_router

api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(strategies_router, prefix="/strategies", tags=["Strategies"])
api_router.include_router(trades_router, prefix="/trades", tags=["Trades"])
api_router.include_router(risk_router, prefix="/risk", tags=["Risk Engine"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(ai_router, prefix="/ai", tags=["AI Coach"])
