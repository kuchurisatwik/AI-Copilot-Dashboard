"""
Trader Copilot AI — FastAPI Dependencies

Reusable dependency injection functions for routes.
"""

from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_access_token

# Bearer token scheme for Swagger UI
security_scheme = HTTPBearer()

# Type alias for database session dependency
DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
) -> UUID:
    """
    Validate the JWT access token and extract the user ID.
    Used as a dependency in protected routes.

    Raises:
        HTTPException 401 if token is invalid, expired, or missing.
    """
    payload = verify_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing user identifier",
        )

    try:
        return UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identifier in token",
        )


# Type alias for authenticated user ID dependency
CurrentUserId = Annotated[UUID, Depends(get_current_user_id)]


async def get_current_user(
    user_id: CurrentUserId,
    db: DbSession,
):
    """
    Fetch the complete user object from the database based on the authenticated user ID.
    """
    from sqlalchemy import select
    from app.models.user import User

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return user

CurrentUser = Annotated[Any, Depends(get_current_user)]
