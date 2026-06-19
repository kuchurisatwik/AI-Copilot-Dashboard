from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.core.database import get_db
from app.core.dependencies import get_current_user_id
from app.schemas.risk import RiskCalculateRequest, RiskCalculateResponse, RiskProfileResponse, RiskProfileUpdate
from app.services.risk_engine import RiskEngineService

router = APIRouter()

@router.get("/profile", response_model=dict)
async def get_risk_profile(
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = RiskEngineService(db)
    profile = await service.get_risk_profile(user_id)
    account_size = await service.get_user_account_size(user_id)
    
    # We can mix account_size into the response since the schema supports it
    profile_data = RiskProfileResponse.model_validate(profile).model_dump()
    profile_data["account_size"] = account_size
    
    return {"status": "success", "data": profile_data}

@router.patch("/profile", response_model=dict)
async def update_risk_profile(
    req: RiskProfileUpdate,
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = RiskEngineService(db)
    profile = await service.update_risk_profile(user_id, req)
    account_size = await service.get_user_account_size(user_id)
    
    profile_data = RiskProfileResponse.model_validate(profile).model_dump()
    profile_data["account_size"] = account_size
    
    return {"status": "success", "data": profile_data}

@router.post("/calculate", response_model=dict)
async def calculate_risk(
    req: RiskCalculateRequest,
    user_id: Any = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> Any:
    service = RiskEngineService(db)
    result = await service.calculate_risk(user_id, req)
    return {"status": "success", "data": result}
