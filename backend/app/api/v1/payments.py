"""
결제 API 엔드포인트
카드 결제 처리 및 Smart Wallet 충전
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.web3_service import web3_service
from web3 import Web3
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class CardPaymentRequest(BaseModel):
    amount_wei: str  # 티켓 가격 (wei 단위)
    card_number: str
    card_expiry: str
    card_cvc: str
    card_name: str


@router.post("/process-card")
async def process_card_payment(
    payment: CardPaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    카드 결제 처리 및 Smart Wallet 충전
    
    실제 서비스에서는:
    1. Stripe/PayPal 등 결제 게이트웨이 연동
    2. 결제 성공 시 Smart Wallet에 자금 충전
    3. 충전 완료 후 티켓 구매 진행
    """
    if not current_user.smart_wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Smart wallet not created"
        )
    
    try:
        amount_wei = int(payment.amount_wei)
        
        # TODO: 실제 결제 게이트웨이 연동 (Stripe, PayPal 등)
        # 현재는 테스트용으로 바로 처리
        logger.info(f"Processing card payment: {amount_wei} wei for user {current_user.id}")
        
        # 결제 검증 (실제로는 Stripe/PayPal API 호출)
        # payment_result = stripe_service.charge(
        #     amount=amount_wei,
        #     card_token=payment.card_token
        # )
        
        # 테스트용: 결제 성공 가정
        payment_success = True
        
        if payment_success:
            # Smart Wallet에 자금 충전 (서비스 계정에서)
            smart_wallet_address = Web3.to_checksum_address(current_user.smart_wallet_address)
            
            # 서비스 계정에서 Smart Wallet로 이더 전송
            transfer_tx = web3_service.w3.eth.send_transaction({
                'from': web3_service.address,
                'to': smart_wallet_address,
                'value': amount_wei,
                'gas': 21000,
                'gasPrice': web3_service.w3.eth.gas_price
            })
            
            receipt = web3_service.w3.eth.wait_for_transaction_receipt(transfer_tx, timeout=60)
            
            logger.info(f"Smart Wallet charged: {transfer_tx.hex()}")
            
            return {
                "success": True,
                "tx_hash": transfer_tx.hex(),
                "message": "Payment processed and Smart Wallet charged"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail="Payment failed"
            )
            
    except Exception as e:
        logger.error(f"Failed to process card payment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment processing failed: {str(e)}"
        )

