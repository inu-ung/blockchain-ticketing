from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.event import EventResponse
from app.schemas.refund import RefundRequestResponse
from app.models.event import Event, EventStatus
from app.models.ticket import Ticket, TicketStatus
from app.models.user import User, UserRole
from app.models.refund import RefundRequest, RefundStatus
from app.core.dependencies import get_current_admin
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/events/pending", response_model=List[EventResponse])
async def get_pending_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """승인 대기 이벤트 목록"""
    events = (
        db.query(Event)
        .filter(Event.status == EventStatus.PENDING)
        .order_by(Event.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return events


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """시스템 통계"""
    total_events = db.query(Event).count()
    total_tickets = db.query(Ticket).count()
    total_users = db.query(User).count()
    pending_events = db.query(Event).filter(Event.status == EventStatus.PENDING).count()
    pending_refunds = db.query(RefundRequest).filter(RefundRequest.status == "pending").count()
    
    return {
        "total_events": total_events,
        "total_tickets": total_tickets,
        "total_users": total_users,
        "pending_events": pending_events,
        "pending_refunds": pending_refunds
    }


@router.post("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    new_role: UserRole,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """사용자 역할 변경"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.role = new_role
    db.commit()
    db.refresh(user)
    
    return {"message": "User role updated", "user_id": str(user.id), "new_role": user.role}


@router.post("/refunds/emergency")
async def emergency_refund(
    ticket_id: str,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """긴급 환불 (관리자만, 이벤트 취소 시)"""
    import uuid
    from app.models.ticket import Ticket, TicketStatus
    from app.models.event import Event
    from app.models.refund import RefundRequest, RefundStatus
    from datetime import datetime
    
    try:
        ticket_uuid = uuid.UUID(ticket_id)
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
    
    # 이미 환불된 티켓인지 확인
    if ticket.status == TicketStatus.REFUNDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket already refunded"
        )
    
    # 이벤트 확인
    event = db.query(Event).filter(Event.id == ticket.event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # 이벤트가 취소되었는지 확인
    if not event.cancelled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is not cancelled. Use regular refund process."
        )
    
    # 온체인에서 긴급 환불 처리
    refund_tx_hash = None
    if ticket.token_id is not None:
        try:
            from app.services.web3_service import web3_service
            from app.core.config import settings
            
            # RefundManager의 emergencyRefund 함수 호출
            refund_manager = web3_service._get_contract(settings.REFUND_MANAGER_ADDRESS, "RefundManager")
            function = refund_manager.functions.emergencyRefund(ticket.token_id)
            refund_tx_hash = web3_service._send_transaction(function)
            logger.info(f"Emergency refund processed onchain: tx={refund_tx_hash}")
        except Exception as e:
            logger.error(f"Failed to process emergency refund onchain: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process emergency refund onchain: {str(e)}"
            )
    
    # 환불 요청 생성 또는 업데이트
    existing_refund = (
        db.query(RefundRequest)
        .filter(RefundRequest.ticket_id == ticket_uuid)
        .first()
    )
    
    if existing_refund:
        existing_refund.status = RefundStatus.APPROVED
        existing_refund.processed_at = datetime.utcnow()
        if refund_tx_hash:
            existing_refund.refund_tx_hash = refund_tx_hash
    else:
        # 새 환불 요청 생성
        refund_request = RefundRequest(
            ticket_id=ticket.id,
            user_id=ticket.owner_address,  # 소유자 주소를 임시로 사용
            reason="Emergency refund - Event cancelled",
            status=RefundStatus.APPROVED,
            refund_amount_wei=event.price_wei if event else None,
            refund_tx_hash=refund_tx_hash,
            processed_at=datetime.utcnow()
        )
        db.add(refund_request)
    
    # 티켓 상태 업데이트
    ticket.status = TicketStatus.REFUNDED
    
    db.commit()
    
    return {
        "message": "Emergency refund processed successfully",
        "ticket_id": ticket_id,
        "refund_tx_hash": refund_tx_hash
    }
