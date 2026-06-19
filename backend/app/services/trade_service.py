from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, BadRequestException
from app.models.trade import Trade
from app.repositories.trade_repository import TradeRepository
from app.schemas.trade import TradeCreate, TradeUpdate, TradeClose, FullTradeResponse
from app.schemas.risk import RiskCalculateRequest
from app.services.risk_engine import RiskEngineService
from app.services.rule_engine import RuleEngineService

class TradeService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.trade_repo = TradeRepository(session)
        self.risk_engine = RiskEngineService(session)
        self.rule_engine = RuleEngineService(session)

    async def create_trade_plan(self, user_id: UUID, trade_in: TradeCreate) -> Dict[str, Any]:
        # 1. Create Trade record (draft)
        trade_data = trade_in.model_dump()
        trade_data["user_id"] = user_id
        trade_data["status"] = "draft"
        
        trade = self.trade_repo.create(trade_data)
        await self.session.flush() # Get trade.id
        
        # 2. Run Risk Engine
        risk_req = RiskCalculateRequest(
            symbol=trade.symbol,
            entry_price=trade.entry_price,
            stop_loss=trade.stop_loss,
            take_profit=trade.take_profit,
            direction=trade.direction
        )
        risk_calc = await self.risk_engine.calculate_risk(user_id, risk_req)
        
        # Update trade position size based on risk calculation
        trade.position_size = risk_calc.position_size
        
        # Save RiskCalculation
        rc_data = {
            "trade_id": trade.id,
            "account_size": risk_calc.account_size,
            "risk_pct": risk_calc.risk_pct,
            "risk_amount": risk_calc.risk_amount,
            "position_size": risk_calc.position_size,
            "risk_reward_ratio": risk_calc.reward_risk_ratio,
            "warnings": risk_calc.warnings
        }
        self.trade_repo.add_risk_calculation(rc_data)
        
        # 3. Run Rule Engine
        validation = await self.rule_engine.validate_trade(user_id, risk_calc)
        
        # Save RuleValidation
        passed_rules = [r for r in validation["rule_results"] if r["status"] == "pass"]
        failed_rules = [r for r in validation["rule_results"] if r["status"] == "block"]
        warnings = [r for r in validation["rule_results"] if r["status"] == "warning"]
        
        rv_data = {
            "trade_id": trade.id,
            "overall_status": validation["overall_status"],
            "passed_rules": passed_rules,
            "failed_rules": failed_rules,
            "warnings": warnings
        }
        self.trade_repo.add_rule_validation(rv_data)
        
        # 4. Save basic Market Context
        mc_data = {
            "trade_id": trade.id,
            # In a real app, we'd call an external API to get these
            "trend": "bullish" if trade.direction == "long" else "bearish",
            "volatility": "medium",
            "timeframe": "1H"
        }
        self.trade_repo.add_market_context(mc_data)
        
        # Update status based on validation
        if validation["overall_status"] == "block":
            trade.status = "blocked"
        else:
            trade.status = "validated"
            
        await self.session.commit()
        await self.session.refresh(trade)
        
        return {
            "trade": trade,
            "risk_calculation": risk_calc.model_dump(),
            "rule_validation": validation,
            "market_context": mc_data
        }

    async def get_trade_details(self, trade_id: UUID, user_id: UUID) -> Dict[str, Any]:
        trade = await self.trade_repo.get_by_id(trade_id, user_id)
        if not trade:
            raise NotFoundException("Trade not found")
            
        rc = await self.trade_repo.get_risk_calculation(trade.id)
        rv = await self.trade_repo.get_rule_validation(trade.id)
        mc = await self.trade_repo.get_market_context(trade.id)
        
        return {
            "trade": trade,
            "risk_calculation": {
                "account_size": float(rc.account_size),
                "risk_pct": float(rc.risk_pct),
                "risk_amount": float(rc.risk_amount),
                "position_size": float(rc.position_size),
                "risk_reward_ratio": float(rc.risk_reward_ratio) if rc.risk_reward_ratio else None,
                "warnings": rc.warnings
            } if rc else None,
            "rule_validation": {
                "overall_status": rv.overall_status,
                "passed_rules": rv.passed_rules,
                "failed_rules": rv.failed_rules,
                "warnings": rv.warnings
            } if rv else None,
            "market_context": {
                "trend_direction": mc.trend,
                "market_regime": "ranging",
                "volatility_level": mc.volatility
            } if mc else None
        }

    async def get_user_trades(
        self, 
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        status: str = None,
        strategy_id: UUID = None,
        symbol: str = None,
        result: str = None
    ) -> List[Trade]:
        return await self.trade_repo.get_all_for_user(
            user_id, skip=skip, limit=limit, 
            status=status, strategy_id=strategy_id, 
            symbol=symbol, result=result
        )

    async def open_trade(self, trade_id: UUID, user_id: UUID) -> Trade:
        trade = await self.trade_repo.get_by_id(trade_id, user_id)
        if not trade:
            raise NotFoundException("Trade not found")
            
        if trade.status in ["blocked", "closed", "cancelled"]:
            raise BadRequestException(f"Cannot open trade with status: {trade.status}")
            
        trade.status = "open"
        trade.opened_at = datetime.now(timezone.utc)
        
        await self.session.commit()
        await self.session.refresh(trade)
        return trade
        
    async def close_trade(self, trade_id: UUID, user_id: UUID, close_data: TradeClose) -> Trade:
        trade = await self.trade_repo.get_by_id(trade_id, user_id)
        if not trade:
            raise NotFoundException("Trade not found")
            
        if trade.status != "open":
            raise BadRequestException("Can only close open trades")
            
        trade.status = "closed"
        trade.closed_at = datetime.now(timezone.utc)
        trade.exit_price = close_data.exit_price
        
        if close_data.notes:
            trade.thesis = f"{trade.thesis}\n\nExit Notes: {close_data.notes}" if trade.thesis else close_data.notes
            
        # Calculate PnL
        diff = float(trade.exit_price) - float(trade.entry_price)
        if trade.direction == "short":
            diff = -diff
            
        trade.pnl = diff * float(trade.position_size)
        
        rc = await self.trade_repo.get_risk_calculation(trade.id)
        if rc:
            risk_amount = float(rc.risk_amount)
            if risk_amount > 0:
                trade.r_multiple = float(trade.pnl) / risk_amount
            else:
                trade.r_multiple = 0
                
        if trade.pnl > 0:
            trade.result = "win"
        elif trade.pnl < 0:
            trade.result = "loss"
        else:
            trade.result = "breakeven"
            
        await self.session.commit()
        await self.session.refresh(trade)
        
        # Trigger analytics recalculation asynchronously here in real app
        return trade
        
    async def add_trade_note(self, trade_id: UUID, user_id: UUID, content: str, note_type: str = "pre_trade"):
        trade = await self.trade_repo.get_by_id(trade_id, user_id)
        if not trade:
            raise NotFoundException("Trade not found")
            
        from app.models.trade_note import TradeNote
        note = TradeNote(
            trade_id=trade_id,
            content=content,
            note_type=note_type
        )
        self.session.add(note)
        await self.session.commit()
        await self.session.refresh(note)
        return note
        
    async def get_trade_notes(self, trade_id: UUID, user_id: UUID):
        trade = await self.trade_repo.get_by_id(trade_id, user_id)
        if not trade:
            raise NotFoundException("Trade not found")
            
        from app.models.trade_note import TradeNote
        from sqlalchemy import select
        result = await self.session.execute(
            select(TradeNote)
            .where(TradeNote.trade_id == trade_id)
            .order_by(TradeNote.created_at.desc())
        )
        return list(result.scalars().all())
