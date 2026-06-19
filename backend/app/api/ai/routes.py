from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.services.ai_coach import AICoachService

router = APIRouter()

@router.get("/coach", response_model=dict)
async def get_coach_advice(
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = AICoachService(db)
    advice = await service.generate_advice(user_id)
    return {"status": "success", "data": advice}
