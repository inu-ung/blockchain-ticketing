from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token, WalletConnect
from app.models.user import User
from app.services.auth_service import create_user, authenticate_user, create_access_token_for_user
from app.core.dependencies import get_current_user
from app.core.security import get_password_hash

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """회원가입"""
    try:
        user = create_user(db, user_create)
        # UUID를 문자열로 변환하여 반환
        return UserResponse(
            id=str(user.id),
            email=user.email,
            role=user.role,
            wallet_address=user.wallet_address,
            smart_wallet_address=user.smart_wallet_address,
            kyc_verified=user.kyc_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """로그인 (이메일/비밀번호)"""
    user = authenticate_user(db, user_login.email, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/google")
async def google_login():
    """Google 소셜 로그인 (구현 예정)"""
    # TODO: Google OAuth 구현
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google login not implemented yet"
    )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """로그아웃"""
    # JWT는 stateless이므로 서버에서 별도 처리 불필요
    # 클라이언트에서 토큰 삭제하면 됨
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """현재 로그인한 사용자 정보"""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        role=current_user.role,
        wallet_address=current_user.wallet_address,
        smart_wallet_address=current_user.smart_wallet_address,
        kyc_verified=current_user.kyc_verified,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.post("/wallet/connect")
async def connect_wallet(
    wallet_info: WalletConnect,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """지갑 연결 (Account Abstraction)"""
    # 지갑 주소 업데이트
    try:
        current_user.wallet_address = wallet_info.wallet_address
        # TODO: Account Abstraction 지갑 생성 로직
        # current_user.smart_wallet_address = generate_smart_wallet(...)
        
        db.commit()
        db.refresh(current_user)
        
        return {
            "message": "Wallet connected successfully",
            "wallet_address": current_user.wallet_address
        }
    except Exception as e:
        db.rollback()
        # UNIQUE 제약 에러인 경우 무시 (이미 다른 사용자가 사용 중일 수 있음)
        if "UNIQUE constraint" in str(e) or "unique" in str(e).lower():
            # 기존 지갑 주소를 그대로 사용
            if current_user.wallet_address:
                return {
                    "message": "Wallet already connected",
                    "wallet_address": current_user.wallet_address
                }
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect wallet: {str(e)}"
        )


@router.post("/wallet/create")
async def create_smart_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Smart Wallet 생성 (Account Abstraction)"""
    # 이미 Smart Wallet이 있으면 반환
    if current_user.smart_wallet_address:
        return {
            "message": "Smart wallet already exists",
            "smart_wallet_address": current_user.smart_wallet_address
        }
    
    try:
        # Account Abstraction 서비스 사용
        from app.services.aa_service import aa_service
        
        # Deterministic 주소 생성 및 배포
        # owner_address는 사용자의 MetaMask 주소 사용 (사용자가 서명할 수 있도록)
        # 현재는 사용자 주소가 없으면 서비스 계정 사용 (나중에 사용자가 연결하면 업데이트)
        owner_address = current_user.wallet_address if current_user.wallet_address else None
        smart_wallet_address = aa_service.generate_smart_wallet_address(
            user_id=str(current_user.id),
            owner_address=owner_address  # 사용자 주소 또는 None (서비스 계정 사용)
        )
        
        current_user.smart_wallet_address = smart_wallet_address
        db.commit()
        db.refresh(current_user)
        
        return {
            "message": "Smart wallet created successfully",
            "smart_wallet_address": smart_wallet_address
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create smart wallet: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create smart wallet: {str(e)}"
        )
