from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

class StrategyBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    type: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    risk_appetite: float = Field(1.0, gt=0, le=5.0)
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_active: bool = True

class StrategyCreate(StrategyBase):
    pass

class StrategyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    type: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None
    risk_appetite: Optional[float] = Field(None, gt=0, le=5.0)
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class StrategyResponse(StrategyBase):
    id: UUID
    user_id: UUID
    is_default: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
