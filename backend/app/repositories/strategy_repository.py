from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.strategy import Strategy
from app.schemas.strategy import StrategyCreate, StrategyUpdate

class StrategyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, strategy_id: UUID, user_id: UUID) -> Optional[Strategy]:
        result = await self.session.execute(
            select(Strategy).where(Strategy.id == strategy_id, Strategy.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_all_for_user(self, user_id: UUID) -> List[Strategy]:
        result = await self.session.execute(
            select(Strategy).where(Strategy.user_id == user_id).order_by(Strategy.name)
        )
        return list(result.scalars().all())

    def create(self, user_id: UUID, strategy_in: StrategyCreate, is_default: bool = False) -> Strategy:
        strategy_data = strategy_in.model_dump()
        strategy = Strategy(**strategy_data, user_id=user_id, is_default=is_default)
        self.session.add(strategy)
        return strategy

    async def update(self, strategy_id: UUID, user_id: UUID, strategy_in: StrategyUpdate) -> Optional[Strategy]:
        strategy = await self.get_by_id(strategy_id, user_id)
        if not strategy:
            return None
        
        update_data = strategy_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(strategy, field, value)
            
        return strategy

    async def delete(self, strategy_id: UUID, user_id: UUID) -> bool:
        strategy = await self.get_by_id(strategy_id, user_id)
        if not strategy:
            return False
            
        # Soft delete by setting is_active = False
        strategy.is_active = False
        return True
