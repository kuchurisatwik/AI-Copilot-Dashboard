from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterResponse, LoginResponse, RefreshRequest, TokenResponse, AuthResponse
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.auth_service import AuthService
from app.core.security import verify_refresh_token, create_access_token, create_refresh_token
from app.core.exceptions import UnauthorizedException

router = APIRouter()

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)) -> Any:
    auth_service = AuthService(db)
    user, access_token, refresh_token = await auth_service.register_user(user_in)
    
    return {
        "status": "success",
        "data": {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    }

@router.post("/login", response_model=LoginResponse)
async def login(login_in: LoginRequest, db: AsyncSession = Depends(get_db)) -> Any:
    auth_service = AuthService(db)
    user, access_token, refresh_token = await auth_service.login(login_in)
    
    return {
        "status": "success",
        "data": {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    }

@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(refresh_in: RefreshRequest, db: AsyncSession = Depends(get_db)) -> Any:
    payload = verify_refresh_token(refresh_in.refresh_token)
    if not payload or not payload.get("sub"):
        raise UnauthorizedException(detail="Invalid or expired refresh token")
    
    user_id = payload.get("sub")
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})
    
    return {
        "status": "success",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    }

@router.get("/me", response_model=AuthResponse)
async def read_current_user(current_user: User = Depends(get_current_user)) -> Any:
    return {
        "status": "success",
        "data": current_user
    }

@router.patch("/me", response_model=AuthResponse)
async def update_current_user(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return {
        "status": "success",
        "data": current_user
    }
