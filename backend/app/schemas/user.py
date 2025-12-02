from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    role: Optional[UserRole] = UserRole.BUYER


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: str
    wallet_address: Optional[str] = None
    smart_wallet_address: Optional[str] = None
    kyc_verified: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, obj):
        """UUID를 문자열로 변환"""
        data = {
            "id": str(obj.id),
            "email": obj.email,
            "role": obj.role,
            "wallet_address": obj.wallet_address,
            "smart_wallet_address": obj.smart_wallet_address,
            "kyc_verified": obj.kyc_verified,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }
        return cls(**data)

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class WalletConnect(BaseModel):
    wallet_address: str

