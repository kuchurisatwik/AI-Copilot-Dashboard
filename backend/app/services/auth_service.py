from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import BadRequestException, UnauthorizedException
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.models.user import User
from app.models.risk_profile import RiskProfile
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate

class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def register_user(self, user_in: UserCreate) -> Tuple[User, str, str]:
        # Check if user exists
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise BadRequestException(detail="Email already registered")

        # Create user
        user_data = user_in.model_dump(exclude={"password"})
        user_data["password_hash"] = hash_password(user_in.password)
        
        user = self.user_repo.create(user_data)
        await self.session.flush() # To get user.id

        # Create default risk profile
        risk_profile = RiskProfile(
            user_id=user.id,
            max_risk_per_trade_pct=user.default_risk_pct,
        )
        self.session.add(risk_profile)
        
        # Seed default strategies
        from app.services.strategy_service import StrategyService
        strategy_service = StrategyService(self.session)
        await strategy_service.seed_default_strategies(user.id)
        
        await self.session.commit()
        await self.session.refresh(user)

        # Generate tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return user, access_token, refresh_token

    async def login(self, login_in: LoginRequest) -> Tuple[User, str, str]:
        user = await self.user_repo.get_by_email(login_in.email)
        if not user or not verify_password(login_in.password, user.password_hash):
            raise UnauthorizedException(detail="Incorrect email or password")
        
        if not user.is_active:
            raise BadRequestException(detail="Inactive user")

        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return user, access_token, refresh_token
