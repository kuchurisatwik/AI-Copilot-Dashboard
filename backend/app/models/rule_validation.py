import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, Numeric, String, DateTime, ForeignKey, Text
from sqlalchemy.types import Uuid, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base

class RuleValidation(Base):
    __tablename__ = "rule_validations"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trade_id = Column(Uuid(as_uuid=True), ForeignKey("trades.id", ondelete="CASCADE"), index=True, nullable=False, unique=True)
    
    overall_status = Column(String(50), nullable=False)
    passed_rules = Column(JSON, default=list)
    failed_rules = Column(JSON, default=list)
    warnings = Column(JSON, default=list)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    trade = relationship("Trade", back_populates="rule_validation")
