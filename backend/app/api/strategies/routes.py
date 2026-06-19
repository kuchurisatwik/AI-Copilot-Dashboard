from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.schemas.strategy import StrategyCreate, StrategyUpdate, StrategyResponse
from app.services.strategy_service import StrategyService

router = APIRouter()

@router.get("", response_model=dict)
async def list_strategies(
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = StrategyService(db)
    strategies = await service.get_strategies(user_id)
    return {"status": "success", "data": [StrategyResponse.model_validate(s).model_dump() for s in strategies]}

@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    strategy_in: StrategyCreate,
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = StrategyService(db)
    strategy = await service.create_strategy(user_id, strategy_in)
    return {"status": "success", "data": StrategyResponse.model_validate(strategy).model_dump()}

@router.get("/{strategy_id}", response_model=dict)
async def get_strategy(
    strategy_id: str,
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = StrategyService(db)
    strategy = await service.get_strategy(strategy_id, user_id)
    return {"status": "success", "data": StrategyResponse.model_validate(strategy).model_dump()}

@router.patch("/{strategy_id}", response_model=dict)
async def update_strategy(
    strategy_id: str,
    strategy_in: StrategyUpdate,
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = StrategyService(db)
    strategy = await service.update_strategy(strategy_id, user_id, strategy_in)
    return {"status": "success", "data": StrategyResponse.model_validate(strategy).model_dump()}

@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(
    strategy_id: str,
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    service = StrategyService(db)
    await service.delete_strategy(strategy_id, user_id)

@router.post("/seed-defaults", response_model=dict, status_code=status.HTTP_201_CREATED)
async def seed_defaults(
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = StrategyService(db)
    strategies = await service.seed_default_strategies(user_id)
    return {"status": "success", "data": [StrategyResponse.model_validate(s).model_dump() for s in strategies]}
