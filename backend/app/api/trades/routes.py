from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any, List

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.schemas.trade import TradeCreate, TradeClose, TradeResponse, FullTradeResponse
from app.services.trade_service import TradeService

router = APIRouter()

@router.post("/plan", response_model=FullTradeResponse, status_code=status.HTTP_201_CREATED)
async def plan_trade(
    trade_in: TradeCreate,
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = TradeService(db)
    result = await service.create_trade_plan(user_id, trade_in)
    return result

@router.get("", response_model=dict)
async def list_trades(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    strategy_id: str = None,
    symbol: str = None,
    result: str = None,
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = TradeService(db)
    
    # Parse strategy_id to UUID if provided
    strategy_uuid = None
    if strategy_id:
        from uuid import UUID
        try:
            strategy_uuid = UUID(strategy_id)
        except ValueError:
            pass
            
    trades = await service.get_user_trades(
        user_id, skip=skip, limit=limit,
        status=status, strategy_id=strategy_uuid,
        symbol=symbol, result=result
    )
    return {"status": "success", "data": trades}

from uuid import UUID

@router.get("/{trade_id}", response_model=dict)
async def get_trade(
    trade_id: UUID,
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = TradeService(db)
    result = await service.get_trade_details(trade_id, user_id)
    return {"status": "success", "data": result}

@router.post("/{trade_id}/open", response_model=dict)
async def open_trade(
    trade_id: UUID,
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = TradeService(db)
    trade = await service.open_trade(trade_id, user_id)
    return {"status": "success", "data": TradeResponse.model_validate(trade).model_dump(mode='json')}

@router.post("/{trade_id}/close", response_model=dict)
async def close_trade(
    trade_id: UUID,
    close_data: TradeClose,
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = TradeService(db)
    trade = await service.close_trade(trade_id, user_id, close_data)
    return {"status": "success", "data": TradeResponse.model_validate(trade).model_dump(mode='json')}

from app.schemas.trade_note import TradeNoteCreate, TradeNoteResponse
@router.post("/{trade_id}/notes", response_model=dict)
async def add_trade_note(
    trade_id: UUID,
    note_data: TradeNoteCreate,
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = TradeService(db)
    note = await service.add_trade_note(trade_id, user_id, note_data.content, note_data.note_type)
    return {"status": "success", "data": TradeNoteResponse.model_validate(note).model_dump(mode='json')}
    
@router.get("/{trade_id}/notes", response_model=dict)
async def get_trade_notes(
    trade_id: UUID,
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = TradeService(db)
    notes = await service.get_trade_notes(trade_id, user_id)
    return {"status": "success", "data": [TradeNoteResponse.model_validate(n).model_dump(mode='json') for n in notes]}
