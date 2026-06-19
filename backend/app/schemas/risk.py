from pydantic import BaseModel

from typing import Optional, List
from uuid import UUID
from datetime import datetime

class RiskProfileBase(BaseModel):
    max_risk_per_trade_pct: float
    max_daily_drawdown_pct: float
    max_open_trades: int

class RiskProfileUpdate(BaseModel):
    account_size: Optional[float] = None
    max_risk_per_trade_pct: Optional[float] = None
    max_daily_drawdown_pct: Optional[float] = None
    max_open_trades: Optional[int] = None

class RiskProfileResponse(RiskProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    account_size: float | None = None

    class Config:
        from_attributes = True

class RiskCalculateRequest(BaseModel):
    symbol: str
    entry_price: float
    stop_loss: float
    take_profit: float
    direction: str

class RiskCalculateResponse(BaseModel):
    account_size: float
    risk_pct: float
    risk_amount: float
    risk_per_unit: float
    position_size: float
    position_value: float
    max_loss: float
    potential_profit: float
    reward_risk_ratio: float
    capital_exposure_pct: float
    current_daily_loss_pct: float
    current_weekly_loss_pct: float
    current_consecutive_losses: int
    warnings: List[str] = []
