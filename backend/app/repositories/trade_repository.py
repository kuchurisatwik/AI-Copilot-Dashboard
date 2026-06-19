from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.trade import Trade
from app.models.risk_calculation import RiskCalculation
from app.models.rule_validation import RuleValidation
from app.models.market_context import MarketContext

class TradeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, trade_id: UUID, user_id: UUID) -> Optional[Trade]:
        result = await self.session.execute(
            select(Trade).where(Trade.id == trade_id, Trade.user_id == user_id)
        )
        return result.scalar_one_or_none()
        
    async def get_all_for_user(
        self, 
        user_id: UUID, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[str] = None,
        strategy_id: Optional[UUID] = None,
        symbol: Optional[str] = None,
        result: Optional[str] = None
    ) -> List[Trade]:
        query = select(Trade).where(Trade.user_id == user_id)
        
        if status:
            query = query.where(Trade.status == status)
        if strategy_id:
            query = query.where(Trade.strategy_id == strategy_id)
        if symbol:
            query = query.where(Trade.symbol.ilike(f"%{symbol}%"))
        if result:
            query = query.where(Trade.result == result)
            
        query = query.order_by(Trade.created_at.desc()).offset(skip).limit(limit)
        
        result_set = await self.session.execute(query)
        return list(result_set.scalars().all())

    def create(self, trade_data: dict) -> Trade:
        trade = Trade(**trade_data)
        self.session.add(trade)
        return trade
        
    def add_risk_calculation(self, data: dict) -> RiskCalculation:
        rc = RiskCalculation(**data)
        self.session.add(rc)
        return rc
        
    def add_rule_validation(self, data: dict) -> RuleValidation:
        rv = RuleValidation(**data)
        self.session.add(rv)
        return rv
        
    def add_market_context(self, data: dict) -> MarketContext:
        mc = MarketContext(**data)
        self.session.add(mc)
        return mc

    async def get_risk_calculation(self, trade_id: UUID) -> Optional[RiskCalculation]:
        result = await self.session.execute(
            select(RiskCalculation).where(RiskCalculation.trade_id == trade_id)
        )
        return result.scalar_one_or_none()
        
    async def get_rule_validation(self, trade_id: UUID) -> Optional[RuleValidation]:
        result = await self.session.execute(
            select(RuleValidation).where(RuleValidation.trade_id == trade_id)
        )
        return result.scalar_one_or_none()
        
    async def get_market_context(self, trade_id: UUID) -> Optional[MarketContext]:
        result = await self.session.execute(
            select(MarketContext).where(MarketContext.trade_id == trade_id)
        )
        return result.scalar_one_or_none()
