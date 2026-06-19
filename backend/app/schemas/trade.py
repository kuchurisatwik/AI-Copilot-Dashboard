from datetime import datetime
from typing import Optional, Any, Dict, List
from uuid import UUID
from pydantic import BaseModel, Field

class TradeBase(BaseModel):
    strategy_id: UUID
    symbol: str = Field(..., min_length=1, max_length=50)
    direction: str = Field(..., pattern="^(long|short)$")
    order_type: str = Field("limit", pattern="^(market|limit|stop)$")
    entry_price: float = Field(..., gt=0)
    stop_loss: float = Field(..., gt=0)
    take_profit: float = Field(..., gt=0)
    thesis: Optional[str] = None

class TradeCreate(TradeBase):
    pass

class TradeUpdate(BaseModel):
    status: Optional[str] = None
    actual_entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    r_multiple: Optional[float] = None
    result: Optional[str] = None
    thesis: Optional[str] = None

class TradeClose(BaseModel):
    exit_price: float = Field(..., gt=0)
    notes: Optional[str] = None

class TradeResponse(TradeBase):
    id: UUID
    user_id: UUID
    status: str
    quantity: Optional[float] = None
    actual_entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None
    r_multiple: Optional[float] = None
    result: Optional[str] = None
    session: Optional[str] = None
    created_at: datetime
    opened_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    updated_at: datetime

    class Config:
        from_attributes = True

class FullTradeResponse(BaseModel):
    trade: TradeResponse
    risk_calculation: Optional[Dict[str, Any]] = None
    rule_validation: Optional[Dict[str, Any]] = None
    market_context: Optional[Dict[str, Any]] = None
