import os

models_dir = r"c:\Users\kuchu\OneDrive\Documents\AI-Copilot-Dashboard\backend\app\models"

init_py = """from .user import User
from .strategy import Strategy
from .trade import Trade
from .market_context import MarketContext
from .risk_calculation import RiskCalculation
from .rule_validation import RuleValidation
from .trade_note import TradeNote
from .risk_profile import RiskProfile
from .analytics import AnalyticsSnapshot
"""

user_py = """import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, Numeric, String, DateTime, ForeignKey, Text
from sqlalchemy.types import Uuid, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    account_size = Column(Numeric(15, 2), nullable=False, default=100000.00)
    default_risk_pct = Column(Numeric(5, 2), nullable=False, default=1.00)
    timezone = Column(String(50), default="Asia/Kolkata")
    preferences = Column(JSON, default=dict)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    risk_profiles = relationship("RiskProfile", back_populates="user", cascade="all, delete-orphan")
    strategies = relationship("Strategy", back_populates="user", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="user", cascade="all, delete-orphan")
    analytics_snapshots = relationship("AnalyticsSnapshot", back_populates="user", cascade="all, delete-orphan")
"""

strategy_py = """import uuid
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
"""

trade_py = """import uuid
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
"""

market_context_py = """import uuid
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
"""

risk_calculation_py = """import uuid
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
"""

rule_validation_py = """import uuid
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
"""

trade_note_py = """import uuid
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
"""

risk_profile_py = """import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, Numeric, String, DateTime, ForeignKey, Text
from sqlalchemy.types import Uuid, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base

class RiskProfile(Base):
    __tablename__ = "risk_profiles"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    
    max_risk_per_trade_pct = Column(Numeric(5, 2), nullable=False, default=1.0)
    max_daily_drawdown_pct = Column(Numeric(5, 2), nullable=False, default=3.0)
    max_open_trades = Column(Numeric(5, 0), nullable=False, default=3)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("User", back_populates="risk_profiles")
"""

analytics_py = """import uuid
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
"""

files = {
    "__init__.py": init_py,
    "user.py": user_py,
    "strategy.py": strategy_py,
    "trade.py": trade_py,
    "market_context.py": market_context_py,
    "risk_calculation.py": risk_calculation_py,
    "rule_validation.py": rule_validation_py,
    "trade_note.py": trade_note_py,
    "risk_profile.py": risk_profile_py,
    "analytics.py": analytics_py
}

for name, content in files.items():
    with open(os.path.join(models_dir, name), "w", encoding="utf-8") as f:
        f.write(content)

print("Recreated models successfully.")
