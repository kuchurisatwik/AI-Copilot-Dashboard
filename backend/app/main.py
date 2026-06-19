"""
Trader Copilot AI — FastAPI Application Factory

Creates and configures the FastAPI application with:
- CORS middleware
- Global exception handling
- Structured logging
- Database lifecycle management
- API router registration
"""

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import close_db, init_db
from app.core.exceptions import AppException
from app.core.logging import get_logger, setup_logging

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Runs setup on startup and cleanup on shutdown.
    """
    # ── Startup ──
    setup_logging()
    logger.info(
        "Starting application",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )

    if settings.is_development:
        # Auto-create tables in development (Alembic for production)
        await init_db()
        logger.info("Database tables initialized (development mode)")

    yield

    # ── Shutdown ──
    logger.info("Shutting down application")
    await close_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Trading Intelligence & Risk Management Platform. "
            "AI-powered decision support for professional traders."
        ),
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )

    # ── CORS Middleware ──────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Global Exception Handler ─────────────────────────────
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """Handle all domain exceptions with consistent error format."""
        logger.warning(
            "Application error",
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            path=str(request.url),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        """Catch-all for unexpected errors."""
        logger.error(
            "Unhandled exception",
            error=str(exc),
            error_type=type(exc).__name__,
            path=str(request.url),
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {"error": str(exc)} if settings.is_development else {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    # ── Register API Routes ──────────────────────────────────
    app.include_router(api_router)

    return app


# Application instance
app = create_app()
