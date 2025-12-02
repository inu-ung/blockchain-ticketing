from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Optional
from app.models.user import User, UserRole
from app.schemas.user import UserCreate
from app.core.security import verify_password, get_password_hash, create_access_token
from datetime import timedelta
from app.core.config import settings


def create_user(db: Session, user_create: UserCreate) -> User:
    """사용자 생성"""
    # 이메일 중복 확인
    existing_user = db.query(User).filter(User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 비밀번호 해싱
    hashed_password = get_password_hash(user_create.password)
    
    # 사용자 생성
    db_user = User(
        email=user_create.email,
        hashed_password=hashed_password,
        role=user_create.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """사용자 인증"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not user.hashed_password:
        return None
    # 비밀번호 검증
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token_for_user(user: User) -> str:
    """사용자용 액세스 토큰 생성"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    return access_token

