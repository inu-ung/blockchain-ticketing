from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.resale import ResaleCreate, ResaleResponse
from app.models.resale import Resale, ResaleStatus
from app.models.ticket import Ticket
from app.models.event import Event
from app.models.user import User
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.services.web3_service import web3_service
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[ResaleResponse])
async def get_resales(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """재판매 목록 조회"""
    try:
        resales = (
            db.query(Resale)
            .filter(Resale.status == ResaleStatus.LISTED)
            .order_by(Resale.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        # UUID를 문자열로 변환하여 반환
        return [
            ResaleResponse(
                id=str(resale.id),
                ticket_id=str(resale.ticket_id),
                token_id=resale.token_id,
                seller_address=resale.seller_address,
                price_wei=resale.price_wei,
                status=resale.status,
                created_at=resale.created_at,
                sold_at=resale.sold_at,
                sale_tx_hash=resale.sale_tx_hash,
            ) for resale in resales
        ]
    except Exception as e:
        logger.error(f"Failed to get resales: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get resales: {str(e)}"
        )


@router.get("/{resale_id}", response_model=ResaleResponse)
async def get_resale(resale_id: str, db: Session = Depends(get_db)):
    """재판매 상세 조회"""
    # UUID 변환
    import uuid
    try:
        resale_uuid = uuid.UUID(resale_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resale ID format"
        )
    
    resale = db.query(Resale).filter(Resale.id == resale_uuid).first()
    if not resale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resale not found"
        )
    
    # UUID를 문자열로 변환하여 반환
    from app.schemas.resale import ResaleResponse
    return ResaleResponse(
        id=str(resale.id),
        ticket_id=str(resale.ticket_id),
        token_id=resale.token_id,
        seller_address=resale.seller_address,
        price_wei=resale.price_wei,
        status=resale.status,
        created_at=resale.created_at,
        sold_at=resale.sold_at,
        sale_tx_hash=resale.sale_tx_hash,
    )


@router.post("", response_model=ResaleResponse, status_code=status.HTTP_201_CREATED)
async def create_resale(
    resale_create: ResaleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """구매한 티켓을 재판매 마켓플레이스에 등록"""
    # 티켓 확인 (UUID 변환)
    import uuid
    try:
        ticket_uuid = uuid.UUID(resale_create.ticket_id)
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
    
    # 이미 환불된 티켓은 재판매 불가
    if ticket.status == "refunded":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot resale a refunded ticket"
        )
    
    # 이미 등록된 재판매 확인
    existing_resale = (
        db.query(Resale)
        .filter(Resale.ticket_id == ticket_uuid)
        .filter(Resale.status == ResaleStatus.LISTED)
        .first()
    )
    if existing_resale:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticket already listed for resale"
        )
    
    # 가격 상한선 확인
    event = db.query(Event).filter(Event.id == ticket.event_id).first()
    if event:
        max_price = (event.price_wei * 20000) // 10000  # 200%
        if resale_create.price_wei > max_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Price exceeds maximum (max: {max_price} wei)"
            )
    
    # 온체인에 재판매 등록 (마켓플레이스에 티켓 등록)
    # Smart Wallet 사용 시 UserOperation으로 처리
    if ticket.token_id is not None:
        try:
            # Smart Wallet 사용 시 UserOperation으로 재판매 등록
            if current_user.smart_wallet_address:
                from app.services.aa_service import aa_service
                from web3 import Web3
                
                # 1. TicketNFT에서 마켓플레이스에 approve (UserOperation)
                ticket_nft = web3_service._get_contract(settings.TICKET_NFT_ADDRESS, "TicketNFT")
                approve_function = ticket_nft.functions.approve(settings.MARKETPLACE_ADDRESS, ticket.token_id)
                
                try:
                    gas_price = web3_service.w3.eth.gas_price
                    tx_dict = approve_function.build_transaction({
                        'from': current_user.smart_wallet_address,
                        'gas': 100000,
                        'gasPrice': gas_price if gas_price else web3_service.w3.to_wei(20, 'gwei')
                    })
                    approve_data = tx_dict['data']
                except Exception as e:
                    logger.error(f"Failed to encode approve: {e}")
                    from eth_abi import encode as abi_encode
                    from eth_utils import keccak, to_hex
                    fn_signature = keccak(b"approve(address,uint256)")[:4]
                    encoded_args = abi_encode(['address', 'uint256'], [settings.MARKETPLACE_ADDRESS, ticket.token_id])
                    approve_data = to_hex(fn_signature + encoded_args)
                
                if isinstance(approve_data, str):
                    approve_data_bytes = bytes.fromhex(approve_data.replace("0x", ""))
                else:
                    approve_data_bytes = approve_data
                
                # Approve UserOperation 생성 및 전송
                approve_op = aa_service.create_user_operation(
                    sender=current_user.smart_wallet_address,
                    target=settings.TICKET_NFT_ADDRESS,
                    data=approve_data_bytes,
                    value=0
                )
                
                import os
                private_key = os.getenv("PRIVATE_KEY", settings.PRIVATE_KEY)
                if private_key:
                    signed_approve_op = aa_service.sign_user_operation(approve_op, private_key)
                    aa_service.send_user_operation(signed_approve_op)
                    logger.info("Ticket approved for marketplace via UserOperation")
                
                # 2. TicketMarketplace에 재판매 등록 (UserOperation)
                marketplace = web3_service._get_contract(settings.MARKETPLACE_ADDRESS, "TicketMarketplace")
                list_function = marketplace.functions.listTicketForResale(ticket.token_id, resale_create.price_wei)
                
                try:
                    gas_price = web3_service.w3.eth.gas_price
                    tx_dict = list_function.build_transaction({
                        'from': current_user.smart_wallet_address,
                        'gas': 200000,
                        'gasPrice': gas_price if gas_price else web3_service.w3.to_wei(20, 'gwei')
                    })
                    list_data = tx_dict['data']
                except Exception as e:
                    logger.error(f"Failed to encode listTicketForResale: {e}")
                    from eth_abi import encode as abi_encode
                    from eth_utils import keccak, to_hex
                    fn_signature = keccak(b"listTicketForResale(uint256,uint256)")[:4]
                    encoded_args = abi_encode(['uint256', 'uint256'], [ticket.token_id, resale_create.price_wei])
                    list_data = to_hex(fn_signature + encoded_args)
                
                if isinstance(list_data, str):
                    list_data_bytes = bytes.fromhex(list_data.replace("0x", ""))
                else:
                    list_data_bytes = list_data
                
                # List UserOperation 생성 및 전송
                list_op = aa_service.create_user_operation(
                    sender=current_user.smart_wallet_address,
                    target=settings.MARKETPLACE_ADDRESS,
                    data=list_data_bytes,
                    value=0
                )
                
                # 재판매 등록은 사용자가 가스비 지불 (Paymaster 사용 안 함)
                list_op["paymasterAndData"] = b""
                
                if private_key:
                    signed_list_op = aa_service.sign_user_operation(list_op, private_key)
                    aa_service.send_user_operation(signed_list_op)
                    logger.info("Ticket listed for resale via UserOperation")
            else:
                # 일반 지갑 사용 시 직접 호출
                web3_service.list_ticket_for_resale(
                    marketplace_address=settings.MARKETPLACE_ADDRESS,
                    ticket_nft_address=settings.TICKET_NFT_ADDRESS,
                    token_id=ticket.token_id,
                    price=resale_create.price_wei
                )
        except Exception as e:
            logger.error(f"Failed to list ticket for resale onchain: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to list ticket for resale onchain: {str(e)}"
            )
    
    # DB에 재판매 저장
    seller_address = current_user.smart_wallet_address or current_user.wallet_address
    db_resale = Resale(
        ticket_id=ticket.id,
        token_id=ticket.token_id,  # NFT 토큰 ID (블록체인에서 티켓을 식별하는 고유 번호)
        seller_address=seller_address,
        price_wei=resale_create.price_wei,
        status=ResaleStatus.LISTED
    )
    db.add(db_resale)
    db.commit()
    db.refresh(db_resale)
    
    # UUID를 문자열로 변환하여 반환
    from app.schemas.resale import ResaleResponse
    return ResaleResponse(
        id=str(db_resale.id),
        ticket_id=str(db_resale.ticket_id),
        token_id=db_resale.token_id,
        seller_address=db_resale.seller_address,
        price_wei=db_resale.price_wei,
        status=db_resale.status,
        created_at=db_resale.created_at,
        sold_at=db_resale.sold_at,
    )


@router.post("/{resale_id}/buy", response_model=ResaleResponse)
async def buy_resale(
    resale_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """재판매 티켓 구매"""
    # UUID 변환
    import uuid
    try:
        resale_uuid = uuid.UUID(resale_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid resale ID format"
        )
    
    resale = db.query(Resale).filter(Resale.id == resale_uuid).first()
    if not resale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resale not found"
        )
    
    if resale.status != ResaleStatus.LISTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resale is not available"
        )
    
    seller_address = current_user.smart_wallet_address or current_user.wallet_address
    if resale.seller_address == seller_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot buy your own ticket"
        )
    
    # 온체인에서 구매
    if resale.token_id is not None:
        try:
            web3_service.buy_resale_ticket(
                marketplace_address=settings.MARKETPLACE_ADDRESS,
                token_id=resale.token_id,
                value=resale.price_wei,
                buyer_address=current_user.wallet_address
            )
        except Exception as e:
            logger.error(f"Failed to buy resale ticket onchain: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to buy resale ticket onchain: {str(e)}"
            )
    
    # 재판매 상태 업데이트
    resale.status = ResaleStatus.SOLD
    resale.sold_at = datetime.utcnow()
    
    # 티켓 소유자 변경
    ticket = db.query(Ticket).filter(Ticket.id == resale.ticket_id).first()
    if ticket:
        buyer_address = current_user.smart_wallet_address or current_user.wallet_address
        ticket.owner_address = buyer_address
        ticket.status = "active"  # 재판매 구매 후 활성 상태
    
    db.commit()
    db.refresh(resale)
    
    # UUID를 문자열로 변환하여 반환
    from app.schemas.resale import ResaleResponse
    return ResaleResponse(
        id=str(resale.id),
        ticket_id=str(resale.ticket_id),
        token_id=resale.token_id,
        seller_address=resale.seller_address,
        price_wei=resale.price_wei,
        status=resale.status,
        created_at=resale.created_at,
        sold_at=resale.sold_at,
        sale_tx_hash=resale.sale_tx_hash,
    )


@router.delete("/{resale_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_resale(
    resale_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """재판매 등록 취소"""
    resale = db.query(Resale).filter(Resale.id == resale_id).first()
    if not resale:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resale not found"
        )
    
    if resale.seller_address != current_user.wallet_address:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    resale.status = ResaleStatus.CANCELLED
    db.commit()
    return None
