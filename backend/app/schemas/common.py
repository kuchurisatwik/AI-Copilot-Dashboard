"""
Trader Copilot AI — Common/Shared Schemas

Reusable Pydantic models for pagination, error responses, and standard wrappers.
"""

from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


# ── Standard API Response Wrappers ───────────────────────────────

class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response wrapper."""
    status: str = "success"
    data: T


class ErrorResponse(BaseModel):
    """Standard error response wrapper."""
    status: str = "error"
    code: str
    message: str
    details: dict[str, Any] = {}
    timestamp: datetime | None = None


class MessageResponse(BaseModel):
    """Simple message response."""
    status: str = "success"
    message: str


# ── Pagination ───────────────────────────────────────────────────

class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""
    page: int = 1
    page_size: int = 20

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response with metadata."""
    status: str = "success"
    data: list[T]
    pagination: dict[str, int]

    @classmethod
    def create(cls, items: list, total: int, page: int, page_size: int):
        return cls(
            data=items,
            pagination={
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
            },
        )


# ── Base Schema with common config ──────────────────────────────

class BaseSchema(BaseModel):
    """Base schema with ORM mode enabled."""
    model_config = ConfigDict(from_attributes=True)
