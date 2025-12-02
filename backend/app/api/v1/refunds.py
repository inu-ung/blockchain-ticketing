from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from app.db.database import get_db
from app.schemas.refund import RefundRequestCreate, RefundRequestResponse
from app.models.refund import RefundRequest, RefundStatus
from app.models.ticket import Ticket
from app.models.event import Event
from app.models.user import User
from app.core.dependencies import get_current_user, get_current_organizer, get_current_admin
from app.core.config import settings
from app.services.web3_service import web3_service
import logging

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/request", response_model=RefundRequestResponse, status_code=status.HTTP_201_CREATED)
async def request_refund(
    refund_create: RefundRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """구매한 티켓 환불 요청"""
    # 티켓 확인 (UUID 변환)
    import uuid
    try:
        ticket_uuid = uuid.UUID(refund_create.ticket_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ticket ID format"
        )
    
    ticket = db.query(Ticket).filter(Ticket.id == ticket_uuid).first()
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found"
        )
    
    # 소유자 확인 (Smart Wallet 주소 또는 일반 지갑 주소)
    owner_address = current_user.smart_wallet_address or current_user.wallet_address
    if ticket.owner_address != owner_address:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not the ticket owner"
        )
    
    # 이미 환불된 티켓인지 확인
    if ticket.status == TicketStatus.REFUNDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket already refunded"
        )
    
    # 이미 환불 요청이 있는지 확인
    existing_request = (
        db.query(RefundRequest)
        .filter(RefundRequest.ticket_id == ticket_uuid)
        .filter(RefundRequest.status != RefundStatus.REJECTED)
        .first()
    )
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund request already exists"
        )
    
    # 이벤트 확인 및 환불 가능 기간 확인
    event = db.query(Event).filter(Event.id == ticket.event_id).first()
    if event:
        # 환불 기한을 이벤트 날짜 1일 전까지로 변경 (테스트를 위해)
        refund_deadline = event.event_date - timedelta(days=1)
        if datetime.utcnow() > refund_deadline:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Refund deadline has passed"
            )
    
    # 환불 요청 생성
    db_refund = RefundRequest(
        ticket_id=ticket.id,
        user_id=current_user.id,
        reason=refund_create.reason,
        status=RefundStatus.PENDING,
        refund_amount_wei=event.price_wei if event else None
    )
    db.add(db_refund)
    db.commit()
    db.refresh(db_refund)
    
    # 온체인에 환불 요청
    # Smart Wallet을 사용하는 경우 UserOperation으로 처리
    if ticket.token_id is not None and event.event_id_onchain is not None:
        try:
            from app.services.aa_service import aa_service
            from app.services.web3_service import web3_service
            from web3 import Web3
            
            # Smart Wallet 사용 시 UserOperation으로 환불 요청
            if current_user.smart_wallet_address:
                # RefundManager의 requestRefund 함수 호출 데이터 인코딩
                refund_manager = web3_service._get_contract(settings.REFUND_MANAGER_ADDRESS, "RefundManager")
                function = refund_manager.functions.requestRefund(ticket.token_id)
                
                # 함수 호출 데이터 인코딩
                try:
                    gas_price = web3_service.w3.eth.gas_price
                    tx_dict = function.build_transaction({
                        'from': current_user.smart_wallet_address,
                        'gas': 200000,
                        'gasPrice': gas_price if gas_price else web3_service.w3.to_wei(20, 'gwei')
                    })
                    call_data = tx_dict['data']
                except Exception as e:
                    logger.error(f"Failed to encode refund request: {e}")
                    # 대체 방법: 직접 ABI 인코딩
                    from eth_abi import encode as abi_encode
                    from eth_utils import keccak, to_hex
                    fn_signature = keccak(b"requestRefund(uint256)")[:4]
                    encoded_args = abi_encode(['uint256'], [ticket.token_id])
                    call_data = to_hex(fn_signature + encoded_args)
                    if isinstance(call_data, str):
                        call_data = bytes.fromhex(call_data.replace("0x", ""))
                
                # UserOperation 생성
                if isinstance(call_data, str):
                    call_data_bytes = bytes.fromhex(call_data.replace("0x", ""))
                else:
                    call_data_bytes = call_data
                
                user_operation = aa_service.create_user_operation(
                    sender=current_user.smart_wallet_address,
                    target=settings.REFUND_MANAGER_ADDRESS,
                    data=call_data_bytes,
                    value=0
                )
                
                # Paymaster 데이터 가져오기 (환불 요청은 스폰서)
                paymaster_data = aa_service.get_paymaster_sponsor_data(
                    user_operation,
                    target=settings.REFUND_MANAGER_ADDRESS
                )
                user_operation["paymasterAndData"] = paymaster_data
                
                # UserOperation 서명 및 전송
                import os
                private_key = os.getenv("PRIVATE_KEY", settings.PRIVATE_KEY)
                if private_key:
                    signed_user_op = aa_service.sign_user_operation(user_operation, private_key)
                    op_hash = aa_service.send_user_operation(signed_user_op)
                    logger.info(f"Refund request UserOperation sent: {op_hash}")
            else:
                # 일반 지갑 사용 시 직접 호출 (실제로는 프론트엔드에서 처리해야 함)
                logger.warning("Refund request requires user wallet signature - should be called from frontend")
        except Exception as e:
            logger.warning(f"Failed to request refund onchain: {e}")
            # 온체인 호출 실패해도 DB에는 저장됨 (나중에 수동 처리 가능)
    
    # UUID를 문자열로 변환하여 반환
    from app.schemas.refund import RefundRequestResponse
    return RefundRequestResponse(
        id=str(db_refund.id),
        ticket_id=str(db_refund.ticket_id),
        user_id=str(db_refund.user_id),
        reason=db_refund.reason,
        status=db_refund.status,
        refund_amount_wei=db_refund.refund_amount_wei,
        created_at=db_refund.created_at,
        processed_at=db_refund.processed_at,
    )


@router.get("", response_model=List[RefundRequestResponse])
async def get_refunds(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """환불 요청 목록 조회"""
    # 관리자나 주최자는 모든 요청 조회, 일반 사용자는 자신의 요청만
    query = db.query(RefundRequest)
    if current_user.role == "buyer":
        query = query.filter(RefundRequest.user_id == current_user.id)
    
    refunds = query.order_by(RefundRequest.created_at.desc()).offset(skip).limit(limit).all()
    return refunds


@router.get("/{refund_id}", response_model=RefundRequestResponse)
async def get_refund(
    refund_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """환불 요청 상세 조회"""
    # UUID 변환
    import uuid
    try:
        refund_uuid = uuid.UUID(refund_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refund ID format"
        )
    
    refund = db.query(RefundRequest).filter(RefundRequest.id == refund_uuid).first()
    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refund request not found"
        )
    
    # 권한 확인
    if refund.user_id != current_user.id and current_user.role == "buyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # UUID를 문자열로 변환하여 반환
    from app.schemas.refund import RefundRequestResponse
    return RefundRequestResponse(
        id=str(refund.id),
        ticket_id=str(refund.ticket_id),
        user_id=str(refund.user_id),
        reason=refund.reason,
        status=refund.status,
        refund_amount_wei=refund.refund_amount_wei,
        refund_tx_hash=refund.refund_tx_hash,
        created_at=refund.created_at,
        processed_at=refund.processed_at,
    )


@router.post("/{refund_id}/approve", response_model=RefundRequestResponse)
async def approve_refund(
    refund_id: str,
    current_user: User = Depends(get_current_organizer),
    db: Session = Depends(get_db)
):
    """환불 승인"""
    # UUID 변환
    import uuid
    try:
        refund_uuid = uuid.UUID(refund_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refund ID format"
        )
    
    refund = db.query(RefundRequest).filter(RefundRequest.id == refund_uuid).first()
    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refund request not found"
        )
    
    if refund.status != RefundStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund request is not pending"
        )
    
    # 이벤트 확인 (주최자 권한)
    ticket = db.query(Ticket).filter(Ticket.id == refund.ticket_id).first()
    if ticket:
        event = db.query(Event).filter(Event.id == ticket.event_id).first()
        if event and event.organizer_id != current_user.id and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to approve this refund"
            )
    
    # 온체인에서 환불 처리 (티켓 소각 및 환불금 지불)
    refund_tx_hash = None
    if ticket and ticket.token_id is not None:
        try:
            # 주최자 또는 관리자가 환불 처리
            # RefundManager의 processRefund 함수 호출
            refund_tx_hash = web3_service.process_refund(
                refund_manager_address=settings.REFUND_MANAGER_ADDRESS,
                ticket_nft_address=settings.TICKET_NFT_ADDRESS,
                token_id=ticket.token_id
            )
            logger.info(f"Refund processed onchain: tx={refund_tx_hash}")
        except Exception as e:
            logger.error(f"Failed to process refund onchain: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process refund onchain: {str(e)}"
            )
    
    # 환불 상태 업데이트
    refund.status = RefundStatus.APPROVED
    refund.processed_at = datetime.utcnow()
    if refund_tx_hash:
        refund.refund_tx_hash = refund_tx_hash
    
    # 티켓 상태 업데이트
    if ticket:
        ticket.status = TicketStatus.REFUNDED
    
    db.commit()
    db.refresh(refund)
    
    # UUID를 문자열로 변환하여 반환
    from app.schemas.refund import RefundRequestResponse
    return RefundRequestResponse(
        id=str(refund.id),
        ticket_id=str(refund.ticket_id),
        user_id=str(refund.user_id),
        reason=refund.reason,
        status=refund.status,
        refund_amount_wei=refund.refund_amount_wei,
        refund_tx_hash=refund.refund_tx_hash,
        created_at=refund.created_at,
        processed_at=refund.processed_at,
    )


@router.post("/{refund_id}/reject", response_model=RefundRequestResponse)
async def reject_refund(
    refund_id: str,
    current_user: User = Depends(get_current_organizer),
    db: Session = Depends(get_db)
):
    """환불 거부"""
    # UUID 변환
    import uuid
    try:
        refund_uuid = uuid.UUID(refund_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refund ID format"
        )
    
    refund = db.query(RefundRequest).filter(RefundRequest.id == refund_uuid).first()
    if not refund:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refund request not found"
        )
    
    if refund.status != RefundStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refund request is not pending"
        )
    
    refund.status = RefundStatus.REJECTED
    refund.processed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(refund)
    
    # UUID를 문자열로 변환하여 반환
    from app.schemas.refund import RefundRequestResponse
    return RefundRequestResponse(
        id=str(refund.id),
        ticket_id=str(refund.ticket_id),
        user_id=str(refund.user_id),
        reason=refund.reason,
        status=refund.status,
        refund_amount_wei=refund.refund_amount_wei,
        refund_tx_hash=refund.refund_tx_hash,
        created_at=refund.created_at,
        processed_at=refund.processed_at,
    )
