import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, Numeric, String, DateTime, ForeignKey, Text
from sqlalchemy.types import Uuid, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base

class Strategy(Base):
    __tablename__ = "strategies"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    risk_appetite = Column(Numeric(5, 2), nullable=False, default=1.0)
    parameters = Column(JSON, default=dict)
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="strategies")
    trades = relationship("Trade", back_populates="strategy")
