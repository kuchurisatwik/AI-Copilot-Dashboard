from typing import Any, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.analytics_engine import AnalyticsEngineService

class AICoachService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.analytics_service = AnalyticsEngineService(session)

    async def generate_advice(self, user_id: UUID) -> Dict[str, Any]:
        """
        Mock implementation of an AI Coach that generates actionable advice
        based on the user's latest Analytics Snapshot.
        """
        snapshot = await self.analytics_service.calculate_overall_analytics(user_id)
        
        # Rule-based generation
        advice_points = []
        
        # Win Rate Analysis
        win_rate = snapshot.win_rate or 0
        if snapshot.total_trades < 5:
            advice_points.append("You don't have enough trades yet. Focus on building a consistent sample size of at least 20 trades.")
        else:
            if win_rate >= 60:
                advice_points.append(f"Great job! Your win rate is strong at {win_rate:.1f}%. Make sure you aren't cutting winners too early just to secure a win.")
            elif win_rate >= 40:
                advice_points.append(f"Your win rate is decent at {win_rate:.1f}%. With this win rate, your profit factor is the key to profitability.")
            else:
                advice_points.append(f"Your win rate is struggling at {win_rate:.1f}%. Consider reviewing your entry criteria or trading higher timeframes.")
                
        # Profit Factor Analysis
        profit_factor = snapshot.profit_factor or 0
        if snapshot.total_trades >= 5:
            if profit_factor >= 2.0:
                advice_points.append(f"Excellent risk-to-reward ratio! Your profit factor of {profit_factor:.2f} shows you let winners run.")
            elif profit_factor >= 1.0:
                advice_points.append(f"Your profit factor is {profit_factor:.2f}. You are profitable, but there is room to improve by tightening stop losses.")
            else:
                advice_points.append(f"Warning: Your profit factor is {profit_factor:.2f}. You are losing more than you are making. Stop taking trades that don't offer at least 2R.")
                
        # Strategy Analysis
        strategy_breakdown = snapshot.metrics.get("strategy_breakdown", {}) if isinstance(snapshot.metrics, dict) else {}
        if strategy_breakdown:
            best_strategy = None
            best_win_rate = -1
            
            for strat_id, stats in strategy_breakdown.items():
                if stats["count"] >= 3:
                    strat_wr = (stats["wins"] / stats["count"]) * 100
                    if strat_wr > best_win_rate:
                        best_win_rate = strat_wr
                        best_strategy = strat_id
                        
            if best_strategy and best_win_rate >= 50:
                advice_points.append(f"Double down on what works! One of your strategies has a solid {best_win_rate:.1f}% win rate.")
        
        return {
            "summary": "AI Coach Performance Review",
            "metrics": {
                "win_rate": float(win_rate),
                "profit_factor": float(profit_factor),
                "total_trades": snapshot.total_trades
            },
            "advice": advice_points
        }
