from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timezone, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.trade import Trade
from app.models.analytics import AnalyticsSnapshot
from app.models.strategy import Strategy

class AnalyticsEngineService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def calculate_overall_analytics(self, user_id: UUID) -> AnalyticsSnapshot:
        """Calculate all-time analytics snapshot for user."""
        # Get all closed trades
        result = await self.session.execute(
            select(Trade).where(
                Trade.user_id == user_id,
                Trade.status == "closed"
            )
        )
        trades = list(result.scalars().all())
        
        return await self._calculate_metrics(user_id, "all_time", trades)

    async def get_dashboard_metrics(self, user_id: UUID) -> Dict[str, Any]:
        """Get high-level metrics for dashboard."""
        snapshot = await self.calculate_overall_analytics(user_id)
        
        # Get recent trades for win rate trend (last 10 trades)
        result = await self.session.execute(
            select(Trade).where(
                Trade.user_id == user_id,
                Trade.status == "closed"
            ).order_by(Trade.closed_at.desc()).limit(10)
        )
        recent_trades = list(result.scalars().all())
        
        recent_wins = sum(1 for t in recent_trades if t.result == 'win')
        recent_win_rate = (recent_wins / len(recent_trades)) * 100 if recent_trades else 0
        
        return {
            "total_pnl": float(snapshot.total_pnl or 0),
            "win_rate": float(snapshot.win_rate or 0),
            "profit_factor": float(snapshot.profit_factor or 0),
            "total_trades": snapshot.total_trades or 0,
            "recent_win_rate": recent_win_rate,
            "avg_r_multiple": float(snapshot.metrics.get("avg_r_multiple", 0)) if isinstance(snapshot.metrics, dict) else 0
        }

    async def _calculate_metrics(self, user_id: UUID, period_type: str, trades: List[Trade]) -> AnalyticsSnapshot:
        total_trades = len(trades)
        wins = sum(1 for t in trades if t.result == "win")
        losses = sum(1 for t in trades if t.result == "loss")
        breakevens = sum(1 for t in trades if t.result == "breakeven")
        
        gross_profit = sum(float(t.pnl) for t in trades if t.pnl and t.pnl > 0)
        gross_loss = abs(sum(float(t.pnl) for t in trades if t.pnl and t.pnl < 0))
        total_pnl = gross_profit - gross_loss
        
        win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 0)
        
        r_multiples = []
        for t in trades:
            if hasattr(t, "r_multiple") and t.r_multiple is not None:
                r_multiples.append(float(t.r_multiple))
            elif t.pnl is not None and getattr(t, "risk_amount", None) and float(t.risk_amount) > 0:
                r_multiples.append(float(t.pnl) / float(t.risk_amount))
        avg_r_multiple = sum(r_multiples) / len(r_multiples) if r_multiples else 0
        
        # Determine strategy breakdown
        strategy_breakdown = {}
        for t in trades:
            s_id = str(t.strategy_id)
            if s_id not in strategy_breakdown:
                strategy_breakdown[s_id] = {"count": 0, "wins": 0, "pnl": 0}
            
            strategy_breakdown[s_id]["count"] += 1
            if t.result == "win":
                strategy_breakdown[s_id]["wins"] += 1
            if t.pnl:
                strategy_breakdown[s_id]["pnl"] += float(t.pnl)

        # Upsert analytics snapshot
        result = await self.session.execute(
            select(AnalyticsSnapshot).where(
                AnalyticsSnapshot.user_id == user_id
            )
        )
        snapshot = result.scalar_one_or_none()
        
        if not snapshot:
            snapshot = AnalyticsSnapshot(user_id=user_id)
            self.session.add(snapshot)
            
        snapshot.total_trades = total_trades
        snapshot.win_rate = win_rate
        snapshot.profit_factor = profit_factor
        snapshot.total_pnl = total_pnl
        
        # Save additional properties in the JSON metrics column
        snapshot.metrics = {
            "period_type": period_type,
            "winning_trades": wins,
            "losing_trades": losses,
            "breakeven_trades": breakevens,
            "avg_r_multiple": avg_r_multiple,
            "strategy_breakdown": strategy_breakdown,
            "calculated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await self.session.commit()
        await self.session.refresh(snapshot)
        
        return snapshot
