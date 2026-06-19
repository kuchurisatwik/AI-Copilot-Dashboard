import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, Numeric, String, DateTime, ForeignKey, Text
from sqlalchemy.types import Uuid, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base

class MarketContext(Base):
    __tablename__ = "market_contexts"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trade_id = Column(Uuid(as_uuid=True), ForeignKey("trades.id", ondelete="CASCADE"), index=True, nullable=False, unique=True)
    
    trend = Column(String(50), nullable=True)
    volatility = Column(String(50), nullable=True)
    indicators = Column(JSON, default=dict)
    timeframe = Column(String(20), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    trade = relationship("Trade", back_populates="market_context")
