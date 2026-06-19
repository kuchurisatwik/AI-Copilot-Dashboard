from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import date, datetime

class AnalyticsSnapshotBase(BaseModel):
    period_type: str
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    breakeven_trades: int = 0
    
    win_rate: Optional[float] = None
    profit_factor: Optional[float] = None
    total_pnl: float = 0.0
    avg_r_multiple: Optional[float] = None
    max_drawdown_pct: Optional[float] = None
    
    strategy_breakdown: Dict[str, Any] = {}

class AnalyticsSnapshotResponse(AnalyticsSnapshotBase):
    id: UUID
    user_id: UUID
    calculated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
