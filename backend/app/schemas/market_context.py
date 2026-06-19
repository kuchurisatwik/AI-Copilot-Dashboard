from pydantic import BaseModel
from typing import Optional

class MarketContextResponse(BaseModel):
    atr: Optional[float] = None
    rsi: Optional[float] = None
    vwap: Optional[float] = None
    volume: Optional[float] = None
    trend_direction: Optional[str] = None
    market_regime: Optional[str] = None
    volatility_level: Optional[str] = None
    
    class Config:
        from_attributes = True
