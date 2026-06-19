from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.services.analytics_engine import AnalyticsEngineService

router = APIRouter()

@router.get("/dashboard", response_model=dict)
async def get_dashboard_metrics(
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = AnalyticsEngineService(db)
    metrics = await service.get_dashboard_metrics(user_id)
    return {"status": "success", "data": metrics}

@router.get("/all-time", response_model=dict)
async def get_all_time_analytics(
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = AnalyticsEngineService(db)
    snapshot = await service.calculate_overall_analytics(user_id)
    return {"status": "success", "data": snapshot}
