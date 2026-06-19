from typing import Optional
from pydantic import BaseModel, EmailStr
from app.schemas.user import UserResponse

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class AuthResponse(BaseModel):
    status: str = "success"
    data: dict

class AuthData(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RegisterResponse(AuthResponse):
    data: AuthData

class LoginResponse(AuthResponse):
    data: AuthData
