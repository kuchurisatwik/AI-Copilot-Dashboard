import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, Numeric, String, DateTime, ForeignKey, Text
from sqlalchemy.types import Uuid, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base

class TradeNote(Base):
    __tablename__ = "trade_notes"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trade_id = Column(Uuid(as_uuid=True), ForeignKey("trades.id", ondelete="CASCADE"), index=True, nullable=False)
    
    content = Column(Text, nullable=False)
    note_type = Column(String(50), default="general")
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    trade = relationship("Trade", back_populates="notes")
