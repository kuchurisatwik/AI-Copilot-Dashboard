import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, Numeric, String, DateTime, ForeignKey, Text
from sqlalchemy.types import Uuid, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    strategy_id = Column(Uuid(as_uuid=True), ForeignKey("strategies.id", ondelete="SET NULL"), index=True, nullable=True)
    
    symbol = Column(String(50), index=True, nullable=False)
    direction = Column(String(20), nullable=False)
    status = Column(String(20), default="planned")
    order_type = Column(String(20), nullable=False)
    
    entry_price = Column(Numeric(15, 5), nullable=True)
    stop_loss = Column(Numeric(15, 5), nullable=True)
    take_profit = Column(Numeric(15, 5), nullable=True)
    
    actual_entry_price = Column(Numeric(15, 5), nullable=True)
    actual_exit_price = Column(Numeric(15, 5), nullable=True)
    
    position_size = Column(Numeric(15, 5), nullable=True)
    risk_amount = Column(Numeric(15, 2), nullable=True)
    
    pnl = Column(Numeric(15, 2), nullable=True)
    pnl_pct = Column(Numeric(10, 2), nullable=True)
    result = Column(String(20), nullable=True)
    
    thesis = Column(Text, nullable=True)
    
    opened_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="trades")
    strategy = relationship("Strategy", back_populates="trades")
    
    market_context = relationship("MarketContext", back_populates="trade", uselist=False, cascade="all, delete-orphan")
    risk_calculation = relationship("RiskCalculation", back_populates="trade", uselist=False, cascade="all, delete-orphan")
    rule_validation = relationship("RuleValidation", back_populates="trade", uselist=False, cascade="all, delete-orphan")
    notes = relationship("TradeNote", back_populates="trade", cascade="all, delete-orphan")
