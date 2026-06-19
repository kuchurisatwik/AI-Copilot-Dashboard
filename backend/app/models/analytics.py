import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, Numeric, String, DateTime, ForeignKey, Text
from sqlalchemy.types import Uuid, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base

class AnalyticsSnapshot(Base):
    __tablename__ = "analytics_snapshots"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    win_rate = Column(Numeric(5, 2), nullable=True)
    profit_factor = Column(Numeric(10, 2), nullable=True)
    total_pnl = Column(Numeric(15, 2), nullable=True)
    total_trades = Column(Numeric(10, 0), nullable=True)
    
    metrics = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="analytics_snapshots")
