from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.risk_profile import RiskProfile
from app.models.user import User
from app.models.trade import Trade
from app.schemas.risk import RiskCalculateRequest, RiskCalculateResponse, RiskProfileUpdate
from app.core.exceptions import NotFoundException

class RiskEngineService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_risk_profile(self, user_id: UUID) -> RiskProfile:
        result = await self.session.execute(
            select(RiskProfile).where(RiskProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        if not profile:
            raise NotFoundException("Risk profile not found")
        return profile

    async def get_user_account_size(self, user_id: UUID) -> float:
        result = await self.session.execute(
            select(User.account_size).where(User.id == user_id)
        )
        account_size = result.scalar_one_or_none()
        if account_size is None:
            raise NotFoundException("User not found")
        return float(account_size)

    async def update_risk_profile(self, user_id: UUID, req: RiskProfileUpdate) -> RiskProfile:
        profile = await self.get_risk_profile(user_id)
        
        if req.max_risk_per_trade_pct is not None:
            profile.max_risk_per_trade_pct = req.max_risk_per_trade_pct
        if req.max_daily_drawdown_pct is not None:
            profile.max_daily_drawdown_pct = req.max_daily_drawdown_pct
        if req.max_open_trades is not None:
            profile.max_open_trades = req.max_open_trades
            
        if req.account_size is not None:
            user_result = await self.session.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if user:
                user.account_size = req.account_size

        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def calculate_risk(self, user_id: UUID, req: RiskCalculateRequest) -> RiskCalculateResponse:
        profile = await self.get_risk_profile(user_id)
        account_size = await self.get_user_account_size(user_id)
        
        risk_pct = float(profile.max_risk_per_trade_pct)
        risk_amount = account_size * (risk_pct / 100.0)
        
        # Risk per unit is the absolute difference between entry and SL
        risk_per_unit = abs(req.entry_price - req.stop_loss)
        if risk_per_unit == 0:
            risk_per_unit = 0.0001 # Prevent division by zero
            
        position_size = risk_amount / risk_per_unit
        position_value = position_size * req.entry_price
        
        max_loss = position_size * risk_per_unit
        
        potential_profit_per_unit = abs(req.take_profit - req.entry_price)
        potential_profit = position_size * potential_profit_per_unit
        
        reward_risk_ratio = potential_profit_per_unit / risk_per_unit if risk_per_unit > 0 else 0
        
        # Calculate exposure from currently open trades
        open_trades_result = await self.session.execute(
            select(func.sum(Trade.position_size * Trade.entry_price))
            .where(Trade.user_id == user_id, Trade.status == "open")
        )
        open_exposure = open_trades_result.scalar() or 0.0
        open_exposure = float(open_exposure)
        
        capital_exposure_pct = ((position_value + open_exposure) / account_size) * 100.0
        
        # Current daily and weekly losses
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_week = start_of_day - timedelta(days=now.weekday())
        
        daily_pnl_result = await self.session.execute(
            select(func.sum(Trade.pnl))
            .where(
                Trade.user_id == user_id,
                Trade.status == "closed",
                Trade.closed_at >= start_of_day,
                Trade.pnl < 0
            )
        )
        daily_loss = float(daily_pnl_result.scalar() or 0.0)
        current_daily_loss_pct = (abs(daily_loss) / account_size) * 100.0 if account_size > 0 else 0.0
        
        weekly_pnl_result = await self.session.execute(
            select(func.sum(Trade.pnl))
            .where(
                Trade.user_id == user_id,
                Trade.status == "closed",
                Trade.closed_at >= start_of_week,
                Trade.pnl < 0
            )
        )
        weekly_loss = float(weekly_pnl_result.scalar() or 0.0)
        current_weekly_loss_pct = (abs(weekly_loss) / account_size) * 100.0 if account_size > 0 else 0.0
        
        # Consecutive losses
        recent_trades = await self.session.execute(
            select(Trade)
            .where(Trade.user_id == user_id, Trade.status == "closed")
            .order_by(Trade.closed_at.desc())
            .limit(10)
        )
        consecutive_losses = 0
        for trade in recent_trades.scalars():
            if trade.pnl is not None and trade.pnl < 0:
                consecutive_losses += 1
            else:
                break
        
        warnings = []
        if risk_pct > float(profile.max_risk_per_trade_pct):
            warnings.append(f"Risk per trade exceeds maximum of {profile.max_risk_per_trade_pct}%")
        
        if (current_daily_loss_pct + (max_loss / account_size) * 100.0) > float(profile.max_daily_drawdown_pct):
            warnings.append(f"This trade may exceed your daily drawdown limit of {profile.max_daily_drawdown_pct}%")
            
        open_trades_count_result = await self.session.execute(
            select(func.count(Trade.id)).where(Trade.user_id == user_id, Trade.status == "open")
        )
        open_trades_count = open_trades_count_result.scalar() or 0
        if open_trades_count >= int(profile.max_open_trades):
            warnings.append(f"You have reached your maximum of {profile.max_open_trades} open trades.")

        return RiskCalculateResponse(
            account_size=account_size,
            risk_pct=risk_pct,
            risk_amount=risk_amount,
            risk_per_unit=risk_per_unit,
            position_size=position_size,
            position_value=position_value,
            max_loss=max_loss,
            potential_profit=potential_profit,
            reward_risk_ratio=reward_risk_ratio,
            capital_exposure_pct=capital_exposure_pct,
            current_daily_loss_pct=current_daily_loss_pct,
            current_weekly_loss_pct=current_weekly_loss_pct,
            current_consecutive_losses=consecutive_losses,
            warnings=warnings
        )
