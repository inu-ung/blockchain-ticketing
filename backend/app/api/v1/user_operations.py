"""
UserOperation API 엔드포인트
Account Abstraction 트랜잭션 생성 및 전송
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.aa_service import aa_service
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/create")
async def create_user_operation(
    target: str,
    data: str,  # hex encoded bytes
    value: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    UserOperation 생성
    
    Args:
        target: 호출할 컨트랙트 주소
        data: 호출 데이터 (hex string)
        value: 전송할 이더 값 (wei)
    """
    if not current_user.smart_wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Smart wallet not created. Please create smart wallet first."
        )
    
    try:
        # hex string을 bytes로 변환
        call_data = bytes.fromhex(data.replace("0x", ""))
        
        # UserOperation 생성
        user_operation = aa_service.create_user_operation(
            sender=current_user.smart_wallet_address,
            target=target,
            data=call_data,
            value=value
        )
        
        # Paymaster 데이터 가져오기 (가스비 스폰서)
        paymaster_data = aa_service.get_paymaster_sponsor_data(
            user_operation,
            target=target
        )
        user_operation["paymasterAndData"] = paymaster_data
        
        # UserOperation을 JSON 직렬화 가능한 형태로 변환
        return {
            "user_operation": {
                "sender": user_operation["sender"],
                "nonce": user_operation["nonce"],
                "initCode": user_operation["initCode"].hex() if isinstance(user_operation["initCode"], bytes) else user_operation["initCode"],
                "callData": user_operation["callData"].hex() if isinstance(user_operation["callData"], bytes) else user_operation["callData"],
                "callGasLimit": user_operation["callGasLimit"],
                "verificationGasLimit": user_operation["verificationGasLimit"],
                "preVerificationGas": user_operation["preVerificationGas"],
                "maxFeePerGas": user_operation["maxFeePerGas"],
                "maxPriorityFeePerGas": user_operation["maxPriorityFeePerGas"],
                "paymasterAndData": user_operation["paymasterAndData"].hex() if isinstance(user_operation["paymasterAndData"], bytes) else user_operation["paymasterAndData"],
                "signature": user_operation.get("signature", b"").hex() if isinstance(user_operation.get("signature", b""), bytes) else user_operation.get("signature", ""),
            },
            "target": target,
            "value": value,
            "message": "UserOperation created. Signature required."
        }
    except Exception as e:
        logger.error(f"Failed to create UserOperation: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create UserOperation: {str(e)}"
        )


@router.post("/send")
async def send_user_operation(
    user_operation: dict,
    signature: Optional[str] = None,  # hex encoded signature (선택적, 백엔드에서 서명 가능)
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    서명된 UserOperation 전송
    
    Args:
        user_operation: UserOperation 딕셔너리
        signature: 서명 (hex string, 선택적 - 없으면 백엔드에서 서명)
    """
    if not current_user.smart_wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Smart wallet not created"
        )
    
    try:
        # UserOperation을 bytes로 변환
        user_op_bytes = {
            "sender": user_operation["sender"],
            "nonce": user_operation["nonce"],
            "initCode": bytes.fromhex(user_operation.get("initCode", "").replace("0x", "")) if user_operation.get("initCode") else b"",
            "callData": bytes.fromhex(user_operation.get("callData", "").replace("0x", "")),
            "callGasLimit": user_operation["callGasLimit"],
            "verificationGasLimit": user_operation["verificationGasLimit"],
            "preVerificationGas": user_operation["preVerificationGas"],
            "maxFeePerGas": user_operation["maxFeePerGas"],
            "maxPriorityFeePerGas": user_operation["maxPriorityFeePerGas"],
            "paymasterAndData": bytes.fromhex(user_operation.get("paymasterAndData", "").replace("0x", "")) if user_operation.get("paymasterAndData") else b"",
            "signature": bytes.fromhex(signature.replace("0x", "")) if signature else b""
        }
        
        # 서명이 없으면 백엔드에서 서명 (테스트용 - 실제로는 프론트엔드에서 서명해야 함)
        if not signature:
            # TODO: 사용자의 private key를 안전하게 관리해야 함
            # 현재는 서비스 계정의 private key 사용 (테스트용)
            import os
            from app.core.config import settings
            private_key = os.getenv("PRIVATE_KEY", settings.PRIVATE_KEY)
            if not private_key:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Private key not configured for signing"
                )
            
            # UserOperation 서명
            signed_user_op = aa_service.sign_user_operation(user_op_bytes, private_key)
            user_op_bytes["signature"] = signed_user_op["signature"]
        
        # UserOperation 전송
        op_hash = aa_service.send_user_operation(user_op_bytes)
        
        return {
            "user_operation_hash": op_hash,
            "message": "UserOperation sent successfully"
        }
    except Exception as e:
        logger.error(f"Failed to send UserOperation: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send UserOperation: {str(e)}"
        )

