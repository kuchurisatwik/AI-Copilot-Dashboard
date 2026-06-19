import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, Numeric, String, DateTime, ForeignKey, Text
from sqlalchemy.types import Uuid, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base

class RiskCalculation(Base):
    __tablename__ = "risk_calculations"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trade_id = Column(Uuid(as_uuid=True), ForeignKey("trades.id", ondelete="CASCADE"), index=True, nullable=False, unique=True)
    
    account_size = Column(Numeric(15, 2), nullable=False)
    risk_pct = Column(Numeric(5, 2), nullable=False)
    risk_amount = Column(Numeric(15, 2), nullable=False)
    
    position_size = Column(Numeric(15, 5), nullable=False)
    leverage = Column(Numeric(5, 2), nullable=True)
    
    risk_reward_ratio = Column(Numeric(10, 2), nullable=True)
    
    is_valid = Column(Boolean, default=True)
    warnings = Column(JSON, default=list)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    trade = relationship("Trade", back_populates="risk_calculation")
