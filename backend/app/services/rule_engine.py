from typing import Dict, Any, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.risk import RiskCalculateResponse
from app.models.risk_profile import RiskProfile
from app.services.risk_engine import RiskEngineService

class RuleEngineService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.risk_engine = RiskEngineService(session)

    async def validate_trade(self, user_id: UUID, risk_calc: RiskCalculateResponse) -> Dict[str, Any]:
        profile = await self.risk_engine.get_risk_profile(user_id)
        
        rules = []
        overall_status = "pass"
        
        # Rule 1: Max Risk Per Trade
        max_risk = float(profile.max_risk_per_trade_pct)
        if risk_calc.risk_pct > max_risk:
            rules.append({
                "rule": "max_risk_per_trade",
                "status": "block",
                "message": f"Risk {risk_calc.risk_pct:.2f}% exceeds {max_risk:.2f}% limit"
            })
            overall_status = "block"
        else:
            rules.append({
                "rule": "max_risk_per_trade",
                "status": "pass",
                "message": f"Risk {risk_calc.risk_pct:.2f}% within {max_risk:.2f}% limit"
            })
            
        # Rule 2: Daily Loss Limit
        daily_limit = float(profile.max_daily_drawdown_pct)
        if risk_calc.current_daily_loss_pct + (risk_calc.max_loss / risk_calc.account_size) * 100 > daily_limit:
            rules.append({
                "rule": "daily_loss_limit",
                "status": "block",
                "message": f"Potential daily loss exceeds {daily_limit:.2f}% limit"
            })
            overall_status = "block"
        else:
            rules.append({
                "rule": "daily_loss_limit",
                "status": "pass",
                "message": f"Daily loss within {daily_limit:.2f}% limit"
            })
            
        # Rule 3: Consecutive Losses
        CONSECUTIVE_LOSS_LIMIT = 3
        if risk_calc.current_consecutive_losses >= CONSECUTIVE_LOSS_LIMIT:
            rules.append({
                "rule": "consecutive_loss",
                "status": "warning",
                "message": f"{risk_calc.current_consecutive_losses} consecutive losses (limit: {CONSECUTIVE_LOSS_LIMIT})"
            })
            if overall_status == "pass":
                overall_status = "warning"
        else:
            rules.append({
                "rule": "consecutive_loss",
                "status": "pass",
                "message": "Consecutive losses within limits"
            })

        return {
            "overall_status": overall_status,
            "rule_results": rules
        }
