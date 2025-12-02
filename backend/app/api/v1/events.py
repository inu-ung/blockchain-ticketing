from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.schemas.event import EventCreate, EventUpdate, EventResponse
from app.models.event import Event, EventStatus
from app.models.user import User
from app.core.dependencies import get_current_user, get_current_organizer, get_current_admin
from app.core.config import settings
from app.services.web3_service import web3_service
from app.services.ipfs_service import ipfs_service
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[EventResponse])
async def get_events(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[EventStatus] = None,
    db: Session = Depends(get_db)
):
    """이벤트 목록 조회"""
    try:
        query = db.query(Event)
        
        if status_filter:
            if status_filter == EventStatus.ACTIVE:
                # "판매 중" 필터: 승인되었고, 현재 시간이 판매 기간 내에 있는 이벤트
                now = datetime.utcnow()
                query = query.filter(
                    Event.status == EventStatus.APPROVED,
                    Event.start_time <= now,
                    Event.end_time >= now
                )
            else:
                query = query.filter(Event.status == status_filter)
        
        events = query.order_by(Event.created_at.desc()).offset(skip).limit(limit).all()
        
        # UUID를 문자열로 변환하여 반환
        return [
            EventResponse(
                id=str(event.id),
                event_id_onchain=event.event_id_onchain,
                organizer_id=str(event.organizer_id),
                name=event.name,
                description=event.description,
                ipfs_hash=event.ipfs_hash,
                price_wei=event.price_wei,
                max_tickets=event.max_tickets,
                sold_tickets=event.sold_tickets,
                start_time=event.start_time,
                end_time=event.end_time,
                event_date=event.event_date,
                status=event.status,
                created_at=event.created_at,
                updated_at=event.updated_at,
            ) for event in events
        ]
    except Exception as e:
        logger.error(f"Failed to get events: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get events: {str(e)}"
        )


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, db: Session = Depends(get_db)):
    """이벤트 상세 조회"""
    try:
        event_uuid = uuid.UUID(event_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event ID format"
        )
    
    event = db.query(Event).filter(Event.id == event_uuid).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # UUID를 문자열로 변환하여 반환
    return EventResponse(
        id=str(event.id),
        event_id_onchain=event.event_id_onchain,
        organizer_id=str(event.organizer_id),
        name=event.name,
        description=event.description,
        ipfs_hash=event.ipfs_hash,
        price_wei=event.price_wei,
        max_tickets=event.max_tickets,
        sold_tickets=event.sold_tickets,
        start_time=event.start_time,
        end_time=event.end_time,
        event_date=event.event_date,
        status=event.status,
        created_at=event.created_at,
        updated_at=event.updated_at,
    )


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_create: EventCreate,
    current_user: User = Depends(get_current_organizer),
    db: Session = Depends(get_db)
):
    """이벤트 생성"""
    # IPFS에 메타데이터 업로드
    metadata = {
        "name": event_create.name,
        "description": event_create.description,
        "event_date": event_create.event_date.isoformat(),
    }
    ipfs_hash = ipfs_service.upload_json(metadata)
    
    # DB에 이벤트 저장
    db_event = Event(
        organizer_id=current_user.id,
        name=event_create.name,
        description=event_create.description,
        ipfs_hash=ipfs_hash,
        price_wei=event_create.price_wei,
        max_tickets=event_create.max_tickets,
        start_time=event_create.start_time,
        end_time=event_create.end_time,
        event_date=event_create.event_date,
        status=EventStatus.PENDING
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    
    # 온체인에 이벤트 생성
    try:
        event_id_onchain = web3_service.create_event_onchain(
            event_manager_address=settings.EVENT_MANAGER_ADDRESS,
            ipfs_hash=ipfs_hash or "",
            price=event_create.price_wei,
            max_tickets=event_create.max_tickets,
            start_time=int(event_create.start_time.timestamp()),
            end_time=int(event_create.end_time.timestamp()),
            event_date=int(event_create.event_date.timestamp())
        )
        if event_id_onchain is not None:
            db_event.event_id_onchain = event_id_onchain
            db.commit()
            db.refresh(db_event)
    except Exception as e:
        logger.error(f"Failed to create event onchain: {e}")
        # 온체인 생성 실패해도 DB에는 저장 (나중에 재시도 가능)
    
    # UUID를 문자열로 변환하여 반환
    from app.schemas.event import EventResponse
    return EventResponse(
        id=str(db_event.id),
        organizer_id=str(db_event.organizer_id),
        name=db_event.name,
        description=db_event.description,
        ipfs_hash=db_event.ipfs_hash,
        price_wei=db_event.price_wei,
        max_tickets=db_event.max_tickets,
        sold_tickets=db_event.sold_tickets,
        start_time=db_event.start_time,
        end_time=db_event.end_time,
        event_date=db_event.event_date,
        status=db_event.status,
        event_id_onchain=db_event.event_id_onchain,
        created_at=db_event.created_at,
        updated_at=db_event.updated_at,
    )


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    event_update: EventUpdate,
    current_user: User = Depends(get_current_organizer),
    db: Session = Depends(get_db)
):
    """이벤트 수정"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # 권한 확인
    if event.organizer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this event"
        )
    
    # 수정 가능한 필드만 업데이트
    update_data = event_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_organizer),
    db: Session = Depends(get_db)
):
    """이벤트 삭제"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # 권한 확인
    if event.organizer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this event"
        )
    
    db.delete(event)
    db.commit()
    return None


@router.post("/{event_id}/approve", response_model=EventResponse)
async def approve_event(
    event_id: str,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """이벤트 승인 (관리자)"""
    # UUID 변환
    import uuid
    try:
        event_uuid = uuid.UUID(event_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid event ID format"
        )
    
    event = db.query(Event).filter(Event.id == event_uuid).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if event.status != EventStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is not in pending status"
        )
    
    # 온체인에서 승인
    if event.event_id_onchain is not None:
        try:
            web3_service.approve_event_onchain(
                event_manager_address=settings.EVENT_MANAGER_ADDRESS,
                event_id=event.event_id_onchain
            )
        except Exception as e:
            logger.error(f"Failed to approve event onchain: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to approve event onchain: {str(e)}"
            )
    
    event.status = EventStatus.APPROVED
    db.commit()
    db.refresh(event)
    
    # UUID를 문자열로 변환하여 반환
    from app.schemas.event import EventResponse
    return EventResponse(
        id=str(event.id),
        organizer_id=str(event.organizer_id),
        name=event.name,
        description=event.description,
        ipfs_hash=event.ipfs_hash,
        price_wei=event.price_wei,
        max_tickets=event.max_tickets,
        sold_tickets=event.sold_tickets,
        start_time=event.start_time,
        end_time=event.end_time,
        event_date=event.event_date,
        status=event.status,
        event_id_onchain=event.event_id_onchain,
        created_at=event.created_at,
        updated_at=event.updated_at,
    )


@router.post("/{event_id}/cancel", response_model=EventResponse)
async def cancel_event(
    event_id: str,
    current_user: User = Depends(get_current_organizer),
    db: Session = Depends(get_db)
):
    """이벤트 취소"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    # 권한 확인
    if event.organizer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this event"
        )
    
    event.status = EventStatus.CANCELLED
    db.commit()
    db.refresh(event)
    
    return event
