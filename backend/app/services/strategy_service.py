from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundException
from app.models.strategy import Strategy
from app.repositories.strategy_repository import StrategyRepository
from app.schemas.strategy import StrategyCreate, StrategyUpdate

class StrategyService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.strategy_repo = StrategyRepository(session)

    async def get_strategies(self, user_id: UUID) -> List[Strategy]:
        return await self.strategy_repo.get_all_for_user(user_id)

    async def get_strategy(self, strategy_id: UUID, user_id: UUID) -> Strategy:
        strategy = await self.strategy_repo.get_by_id(strategy_id, user_id)
        if not strategy:
            raise NotFoundException(detail="Strategy not found")
        return strategy

    async def create_strategy(self, user_id: UUID, strategy_in: StrategyCreate) -> Strategy:
        strategy = self.strategy_repo.create(user_id, strategy_in)
        await self.session.commit()
        await self.session.refresh(strategy)
        return strategy

    async def update_strategy(self, strategy_id: UUID, user_id: UUID, strategy_in: StrategyUpdate) -> Strategy:
        strategy = await self.strategy_repo.update(strategy_id, user_id, strategy_in)
        if not strategy:
            raise NotFoundException(detail="Strategy not found")
        
        await self.session.commit()
        await self.session.refresh(strategy)
        return strategy

    async def delete_strategy(self, strategy_id: UUID, user_id: UUID):
        deleted = await self.strategy_repo.delete(strategy_id, user_id)
        if not deleted:
            raise NotFoundException(detail="Strategy not found")
        await self.session.commit()

    async def seed_default_strategies(self, user_id: UUID) -> List[Strategy]:
        defaults = [
            StrategyCreate(name="Breakout", type="breakout", description="Trading price moving outside a defined support or resistance level with increased volume.", risk_appetite=1.2),
            StrategyCreate(name="Pullback", type="pullback", description="Entering a trade during a temporary reversal within an established trend.", risk_appetite=1.0),
            StrategyCreate(name="Reversal", type="reversal", description="Trading the change in trend direction against the current trend.", risk_appetite=1.5),
            StrategyCreate(name="Trend Following", type="trend", description="Trading in the direction of the established long-term trend.", risk_appetite=0.8),
            StrategyCreate(name="Mean Reversion", type="mean_reversion", description="Trading on the assumption that price will return to its historical average.", risk_appetite=1.1),
            StrategyCreate(name="Scalping", type="scalping", description="Making numerous small trades to capture minor price movements.", risk_appetite=1.3)
        ]
        
        created_strategies = []
        for strategy_in in defaults:
            strategy = self.strategy_repo.create(user_id, strategy_in, is_default=True)
            created_strategies.append(strategy)
            
        await self.session.commit()
        for strategy in created_strategies:
            await self.session.refresh(strategy)
            
        return created_strategies
