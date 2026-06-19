from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime

class TradeNoteBase(BaseModel):
    content: str
    note_type: str = "pre_trade"

class TradeNoteCreate(TradeNoteBase):
    pass

class TradeNoteResponse(TradeNoteBase):
    id: UUID
    trade_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
