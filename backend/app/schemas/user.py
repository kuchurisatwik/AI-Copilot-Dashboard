from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    account_size: float = Field(..., gt=0)
    default_risk_pct: float = Field(1.0, gt=0, le=10.0)
    timezone: str = "Asia/Kolkata"

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    account_size: Optional[float] = Field(None, gt=0)
    default_risk_pct: Optional[float] = Field(None, gt=0, le=10.0)
    timezone: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    preferences: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
