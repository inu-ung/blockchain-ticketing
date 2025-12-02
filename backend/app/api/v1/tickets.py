from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime
from app.db.database import get_db
from app.schemas.ticket import TicketResponse, TicketPurchase
from app.models.ticket import Ticket, TicketStatus
from app.models.event import Event, EventStatus
from app.models.user import User
from app.core.dependencies import get_current_user
from app.core.config import settings
from app.services.web3_service import web3_service
from app.services.ipfs_service import ipfs_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[TicketResponse])
async def get_tickets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """내 티켓 목록 조회"""
    # Smart Wallet 주소로 필터링 (UserOperation 사용 시)
    owner_address = current_user.smart_wallet_address or current_user.wallet_address
    if not owner_address:
        return []
    
    tickets = (
        db.query(Ticket)
        .join(Event, Ticket.event_id == Event.id)
        .filter(Ticket.owner_address == owner_address)
        .order_by(Ticket.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    # UUID를 문자열로 변환하여 반환 (이벤트 정보 포함)
    from app.schemas.ticket import TicketResponse
    result = []
    for ticket in tickets:
        event = db.query(Event).filter(Event.id == ticket.event_id).first()
        ticket_dict = {
            "id": str(ticket.id),
            "token_id": ticket.token_id,
            "event_id": str(ticket.event_id),
            "owner_address": ticket.owner_address,
            "ipfs_hash": ticket.ipfs_hash,
            "status": ticket.status,
            "purchase_price_wei": ticket.purchase_price_wei,
            "purchase_tx_hash": ticket.purchase_tx_hash,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
        }
        # 이벤트 정보 추가
        if event:
            ticket_dict["event_name"] = event.name
            ticket_dict["event_date"] = event.event_date
            ticket_dict["event_status"] = event.status
        result.append(ticket_dict)
    return result


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """티켓 상세 조회"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
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
            detail="Not authorized to view this ticket"
        )
    
    # UUID를 문자열로 변환하여 반환
    from app.schemas.ticket import TicketResponse
    return TicketResponse(
        id=str(ticket.id),
        token_id=ticket.token_id,
        event_id=str(ticket.event_id),
        owner_address=ticket.owner_address,
        ipfs_hash=ticket.ipfs_hash,
        status=ticket.status,
        purchase_price_wei=ticket.purchase_price_wei,
        purchase_tx_hash=ticket.purchase_tx_hash,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
    )


@router.post("/purchase", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def purchase_ticket(
    purchase: TicketPurchase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """티켓 구매"""
    # 이벤트 확인 (UUID 변환)
    import uuid
    try:
        event_uuid = uuid.UUID(purchase.event_id)
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
    
    # 이벤트 상태 확인
    if event.status != EventStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is not approved"
        )
    
    # 판매 기간 확인
    now = datetime.utcnow()
    if now < event.start_time or now > event.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not in sale period"
        )
    
    # 티켓 수량 확인
    if event.sold_tickets >= event.max_tickets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tickets sold out"
        )
    
    # Smart Wallet 주소 확인 (UserOperation 사용)
    if not current_user.smart_wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Smart wallet not created. Please create smart wallet first."
        )
    
    # 중복 구매 방지: 같은 이벤트에 대해 이미 구매한 티켓이 있는지 확인
    owner_address = current_user.smart_wallet_address or current_user.wallet_address
    existing_ticket = (
        db.query(Ticket)
        .filter(Ticket.event_id == event_uuid)
        .filter(Ticket.owner_address == owner_address)
        .filter(Ticket.status == TicketStatus.ACTIVE)
        .first()
    )
    if existing_ticket:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already purchased a ticket for this event"
        )
    
    # 티켓 메타데이터 생성 및 IPFS 업로드
    token_uri = purchase.token_uri
    if not token_uri:
        metadata = {
            "name": f"Ticket for {event.name}",
            "description": f"Ticket for event: {event.name}",
            "image": event.ipfs_hash or "",  # 이벤트 이미지가 있다면
            "attributes": [
                {"trait_type": "Event", "value": event.name},
                {"trait_type": "Event Date", "value": event.event_date.isoformat()},
                {"trait_type": "Price", "value": str(event.price_wei)},
            ],
            "event_id": str(event.id),
            "event_name": event.name,
        }
        
        # Pinata 메타데이터 추가
        pinata_metadata = {
            "name": f"Ticket-{event.name}",
            "keyvalues": {
                "event_id": str(event.id),
                "event_name": event.name,
            }
        }
        
        ipfs_hash = ipfs_service.upload_json(metadata, pinata_metadata)
        if not ipfs_hash:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload ticket metadata to IPFS"
            )
        token_uri = f"ipfs://{ipfs_hash}"
    else:
        ipfs_hash = token_uri.replace("ipfs://", "")
    
    # 온체인에서 티켓 구매 (UserOperation 사용)
    tx_hash = None
    token_id = None
    if event.event_id_onchain is not None:
        try:
            # Smart Wallet 주소 확인
            if not current_user.smart_wallet_address:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Smart wallet not created. Please create smart wallet first."
                )
            
            # UserOperation을 사용한 티켓 구매
            from app.services.aa_service import aa_service
            from web3 import Web3
            
            # EventManager 컨트랙트에서 purchaseTicket 함수 호출 데이터 인코딩
            contract = web3_service._get_contract(settings.EVENT_MANAGER_ADDRESS, "EventManager")
            
            # purchaseTicket(eventId, tokenURI) 함수 호출 데이터 인코딩
            function = contract.functions.purchaseTicket(event.event_id_onchain, token_uri)
            
            # 함수 호출 데이터 인코딩 (web3.py v6)
            try:
                # web3.py v6: build_transaction을 사용하여 데이터 추출
                gas_price = web3_service.w3.eth.gas_price
                tx_dict = function.build_transaction({
                    'from': current_user.smart_wallet_address,
                    'value': event.price_wei,
                    'gas': 500000,
                    'gasPrice': gas_price if gas_price else web3_service.w3.to_wei(20, 'gwei')
                })
                call_data = tx_dict['data']
                logger.info(f"Function call data encoded: {call_data[:20]}...")
            except Exception as e:
                logger.error(f"Failed to encode function call with build_transaction: {e}")
                import traceback
                logger.error(traceback.format_exc())
                # 대체 방법: 직접 ABI 인코딩
                from eth_abi import encode as abi_encode
                from eth_utils import keccak, to_hex
                # 함수 시그니처 해시 (purchaseTicket(uint256,string))
                fn_signature = keccak(b"purchaseTicket(uint256,string)")[:4]
                # 인자 인코딩
                encoded_args = abi_encode(['uint256', 'string'], [event.event_id_onchain, token_uri])
                call_data_hex = to_hex(fn_signature + encoded_args)
                call_data = call_data_hex
                logger.info(f"Function call data encoded (fallback): {call_data[:20]}...")
            
            # Smart Wallet에 이더 전송 (티켓 구매 비용)
            # UserOperation의 value는 Smart Wallet에서 지불되므로, 먼저 이더를 전송해야 함
            try:
                smart_wallet_balance = web3_service.w3.eth.get_balance(
                    Web3.to_checksum_address(current_user.smart_wallet_address)
                )
                logger.info(f"Smart Wallet balance: {smart_wallet_balance} wei ({web3_service.w3.from_wei(smart_wallet_balance, 'ether')} ETH)")
                
                if smart_wallet_balance < event.price_wei:
                    # Smart Wallet에 이더 전송 (서비스 계정에서)
                    logger.info(f"Transferring {event.price_wei} wei to Smart Wallet...")
                    transfer_tx = web3_service.w3.eth.send_transaction({
                        'from': web3_service.address,
                        'to': Web3.to_checksum_address(current_user.smart_wallet_address),
                        'value': event.price_wei,
                        'gas': 21000,
                        'gasPrice': web3_service.w3.eth.gas_price
                    })
                    web3_service.w3.eth.wait_for_transaction_receipt(transfer_tx, timeout=60)
                    logger.info(f"ETH transferred to Smart Wallet: {transfer_tx.hex()}")
            except Exception as e:
                logger.warning(f"Failed to transfer ETH to Smart Wallet: {e}")
                # 계속 진행 (테스트 환경에서는 서비스 계정이 처리할 수 있음)
            
            # UserOperation 생성
            # call_data가 이미 bytes인지 확인
            if isinstance(call_data, str):
                call_data_bytes = bytes.fromhex(call_data.replace("0x", ""))
            else:
                call_data_bytes = call_data
            
            user_operation = aa_service.create_user_operation(
                sender=current_user.smart_wallet_address,
                target=settings.EVENT_MANAGER_ADDRESS,
                data=call_data_bytes,
                value=event.price_wei
            )
            
            # Paymaster 데이터 가져오기 (티켓 구매는 스폰서)
            paymaster_data = aa_service.get_paymaster_sponsor_data(
                user_operation,
                target=settings.EVENT_MANAGER_ADDRESS
            )
            user_operation["paymasterAndData"] = paymaster_data
            
            # UserOperation 서명 (서비스 계정의 private key 사용 - 테스트용)
            import os
            private_key = os.getenv("PRIVATE_KEY", settings.PRIVATE_KEY)
            if not private_key:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Private key not configured"
                )
            
            signed_user_op = aa_service.sign_user_operation(user_operation, private_key)
            
            # UserOperation 전송
            op_hash = aa_service.send_user_operation(signed_user_op)
            logger.info(f"UserOperation sent, op_hash: {op_hash}, type: {type(op_hash)}")
            
            # 트랜잭션 영수증 대기 및 tokenId 추출
            # EntryPoint에서 직접 전송한 경우 트랜잭션 해시를 사용
            # op_hash가 문자열인지 확인하고, 트랜잭션 해시 형식인지 확인
            op_hash_str = str(op_hash) if not isinstance(op_hash, str) else op_hash
            if op_hash_str.startswith("0x") and len(op_hash_str) == 66:
                # 트랜잭션 해시인 경우
                try:
                    receipt = web3_service.w3.eth.wait_for_transaction_receipt(op_hash_str, timeout=120)
                    tx_hash = op_hash_str
                    
                    if receipt.status != 1:
                        raise HTTPException(
                            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Transaction failed: {tx_hash}"
                        )
                    
                    # TicketSold 이벤트에서 tokenId 추출
                    # EventManager 컨트랙트 주소에서 발생한 이벤트만 확인
                    event_manager_address_checksum = Web3.to_checksum_address(settings.EVENT_MANAGER_ADDRESS)
                    ticket_sold = contract.events.TicketSold()
                    
                    logger.info(f"Checking {len(receipt.logs)} logs for TicketSold event from EventManager at {event_manager_address_checksum}...")
                    for log in receipt.logs:
                        try:
                            # EventManager 컨트랙트에서 발생한 로그만 확인
                            log_address = log.get('address') if isinstance(log, dict) else log.address
                            if str(log_address).lower() == event_manager_address_checksum.lower():
                                decoded = ticket_sold.process_log(log)
                                if decoded.args.eventId == event.event_id_onchain:
                                    token_id = decoded.args.tokenId
                                    logger.info(f"Ticket purchased via UserOperation: tokenId={token_id}, tx={tx_hash}")
                                    break
                        except Exception as e:
                            logger.debug(f"Failed to process log (address: {log.get('address', 'unknown') if isinstance(log, dict) else log.address}): {e}")
                            continue
                    
                    # token_id를 찾지 못한 경우, TicketNFT에서 직접 조회 시도
                    if token_id is None:
                        logger.warning(f"Token ID not found in logs, trying to query from TicketNFT...")
                        try:
                            # TicketNFT 컨트랙트에서 최근 mint된 token 조회
                            ticket_nft = web3_service._get_contract(settings.TICKET_NFT_ADDRESS, "TicketNFT")
                            # 현재 사용자의 Smart Wallet 주소로 최근 mint된 token 찾기
                            # (간단한 방법: totalSupply를 사용하여 최신 token ID 추정)
                            total_supply = ticket_nft.functions.totalSupply().call()
                            logger.info(f"TicketNFT totalSupply: {total_supply}")
                            if total_supply > 0:
                                # 최근 mint된 token들 확인 (최대 10개)
                                for i in range(min(10, total_supply)):
                                    check_token_id = total_supply - 1 - i
                                    try:
                                        owner = ticket_nft.functions.ownerOf(check_token_id).call()
                                        token_to_event = ticket_nft.functions.tokenToEvent(check_token_id).call()
                                        logger.info(f"Token {check_token_id}: owner={owner}, eventId={token_to_event}")
                                        if (owner.lower() == current_user.smart_wallet_address.lower() and 
                                            token_to_event == event.event_id_onchain):
                                            token_id = check_token_id
                                            logger.info(f"Found token ID from TicketNFT: {token_id}")
                                            break
                                    except Exception as e:
                                        logger.debug(f"Failed to check token {check_token_id}: {e}")
                                        continue
                        except Exception as e:
                            logger.error(f"Failed to query token ID from TicketNFT: {e}")
                            import traceback
                            logger.error(traceback.format_exc())
                    
                    if token_id is None:
                        # token_id를 찾지 못했지만 트랜잭션은 성공한 경우
                        # 임시로 unique하지 않은 값 사용 (나중에 수동 업데이트)
                        logger.error(f"Failed to extract token ID from transaction: {tx_hash}")
                        logger.error(f"Transaction receipt: status={receipt.status}, logs={len(receipt.logs)}")
                        # DB에서 가장 큰 token_id를 찾아서 +1 사용 (임시 해결책)
                        max_token = db.query(func.max(Ticket.token_id)).scalar()
                        if max_token is not None:
                            token_id = max_token + 1
                            logger.warning(f"Using temporary token_id: {token_id} (will need manual update)")
                        else:
                            token_id = 1
                            logger.warning(f"Using temporary token_id: {token_id} (will need manual update)")
                except Exception as e:
                    logger.error(f"Failed to get transaction receipt: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Failed to get transaction receipt: {str(e)}"
                    )
            else:
                # UserOperation 해시인 경우 (Bundler 사용) 또는 형식이 다른 경우
                logger.warning(f"op_hash format unexpected: {op_hash_str}, trying TicketNFT query...")
                tx_hash = op_hash_str
                
                # TicketNFT에서 직접 조회 시도
                try:
                    ticket_nft = web3_service._get_contract(settings.TICKET_NFT_ADDRESS, "TicketNFT")
                    total_supply = ticket_nft.functions.totalSupply().call()
                    logger.info(f"TicketNFT totalSupply: {total_supply}")
                    if total_supply > 0:
                        # 최근 mint된 token들 확인 (최대 10개)
                        for i in range(min(10, total_supply)):
                            check_token_id = total_supply - 1 - i
                            try:
                                owner = ticket_nft.functions.ownerOf(check_token_id).call()
                                token_to_event = ticket_nft.functions.tokenToEvent(check_token_id).call()
                                logger.info(f"Token {check_token_id}: owner={owner}, eventId={token_to_event}")
                                if (owner.lower() == current_user.smart_wallet_address.lower() and 
                                    token_to_event == event.event_id_onchain):
                                    token_id = check_token_id
                                    logger.info(f"Found token ID from TicketNFT: {token_id}")
                                    break
                            except Exception as e:
                                logger.debug(f"Failed to check token {check_token_id}: {e}")
                                continue
                except Exception as e:
                    logger.error(f"Failed to query token ID from TicketNFT: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                
                # token_id를 찾지 못한 경우 fallback
                if token_id is None:
                    logger.error(f"Failed to extract token ID, using fallback...")
                    max_token = db.query(func.max(Ticket.token_id)).scalar()
                    if max_token is not None:
                        token_id = max_token + 1
                        logger.warning(f"Using temporary token_id: {token_id} (will need manual update)")
                    else:
                        token_id = 1
                        logger.warning(f"Using temporary token_id: {token_id} (will need manual update)")
                
        except Exception as e:
            logger.error(f"Failed to purchase ticket with UserOperation: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to purchase ticket onchain: {str(e)}"
            )
    
    # DB에 티켓 저장 (Smart Wallet 주소 사용)
    if not current_user.smart_wallet_address:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Smart wallet address is required"
        )
    
    db_ticket = Ticket(
        token_id=token_id or 0,  # 임시값
        event_id=event.id,
        owner_address=current_user.smart_wallet_address,  # Smart Wallet 주소 사용
        ipfs_hash=ipfs_hash,
        purchase_price_wei=event.price_wei,
        purchase_tx_hash=tx_hash
    )
    db.add(db_ticket)
    
    # 이벤트 판매 수량 업데이트
    event.sold_tickets += 1
    
    db.commit()
    db.refresh(db_ticket)
    
    # UUID를 문자열로 변환하여 반환
    from app.schemas.ticket import TicketResponse
    return TicketResponse(
        id=str(db_ticket.id),
        token_id=db_ticket.token_id,
        event_id=str(db_ticket.event_id),
        owner_address=db_ticket.owner_address,
        ipfs_hash=db_ticket.ipfs_hash,
        status=db_ticket.status,
        purchase_price_wei=db_ticket.purchase_price_wei,
        purchase_tx_hash=db_ticket.purchase_tx_hash,
        created_at=db_ticket.created_at,
        updated_at=db_ticket.updated_at,
    )


@router.get("/{ticket_id}/metadata")
async def get_ticket_metadata(
    ticket_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """티켓 메타데이터 조회 (IPFS에서 실제 데이터 가져오기)"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
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
            detail="Not authorized"
        )
    
    # IPFS에서 메타데이터 조회
    metadata = None
    if ticket.ipfs_hash:
        metadata = ipfs_service.get_json(ticket.ipfs_hash)
    
    return {
        "ipfs_hash": ticket.ipfs_hash,
        "token_uri": f"ipfs://{ticket.ipfs_hash}" if ticket.ipfs_hash else None,
        "metadata": metadata,
        "ipfs_url": ipfs_service.get_file_url(ticket.ipfs_hash) if ticket.ipfs_hash else None
    }
