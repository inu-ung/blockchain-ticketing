from web3 import Web3
from eth_account import Account
from app.core.config import settings
from typing import Optional, Tuple
import json
import os
import logging

logger = logging.getLogger(__name__)


class Web3Service:
    def __init__(self):
        # RPC 연결 (로컬 네트워크 우선)
        rpc_url = os.getenv("POLYGON_MUMBAI_RPC_URL", settings.POLYGON_MUMBAI_RPC_URL)
        if not rpc_url or rpc_url == "":
            rpc_url = "http://localhost:8545"  # 기본값: 로컬 Hardhat 노드
        
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if not self.w3.is_connected():
            logger.warning(f"Web3 connection failed to {rpc_url}")
            self.w3 = None
            return
        
        logger.info(f"Web3 connected to {rpc_url}")
        
        # 서비스 계정 설정
        private_key = os.getenv("PRIVATE_KEY", settings.PRIVATE_KEY)
        if private_key:
            if not private_key.startswith("0x"):
                private_key = "0x" + private_key
            self.account = Account.from_key(private_key)
            self.address = self.account.address
            logger.info(f"Service account: {self.address}")
        else:
            logger.warning("PRIVATE_KEY not set, some functions may not work")
            self.account = None
            self.address = None
        
        # 컨트랙트 주소
        self.event_manager_address = os.getenv("EVENT_MANAGER_ADDRESS", settings.EVENT_MANAGER_ADDRESS)
        self.ticket_nft_address = os.getenv("TICKET_NFT_ADDRESS", settings.TICKET_NFT_ADDRESS)
        self.marketplace_address = os.getenv("MARKETPLACE_ADDRESS", settings.MARKETPLACE_ADDRESS)
        self.refund_manager_address = os.getenv("REFUND_MANAGER_ADDRESS", settings.REFUND_MANAGER_ADDRESS)
    
    def _load_abi(self, contract_name: str) -> list:
        """ABI 파일 로드"""
        abi_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "contracts",
            f"{contract_name}.json"
        )
        
        try:
            with open(abi_path, 'r') as f:
                artifact = json.load(f)
                return artifact.get("abi", [])
        except FileNotFoundError:
            logger.error(f"ABI file not found: {abi_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse ABI: {e}")
            return []
    
    def _get_contract(self, contract_address: str, contract_name: str):
        """컨트랙트 인스턴스 가져오기"""
        if not self.w3:
            raise Exception("Web3 not connected")
        
        abi = self._load_abi(contract_name)
        if not abi:
            raise Exception(f"Failed to load ABI for {contract_name}")
        
        return self.w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=abi)
    
    def _send_transaction(self, contract_function, value: int = 0) -> str:
        """트랜잭션 전송"""
        if not self.account:
            raise Exception("Service account not configured")
        
        if not self.w3:
            raise Exception("Web3 not connected")
        
        # 트랜잭션 빌드
        transaction = contract_function.build_transaction({
            'from': self.address,
            'nonce': self.w3.eth.get_transaction_count(self.address),
            'gas': 500000,  # 가스 한도
            'gasPrice': self.w3.eth.gas_price,
            'value': value,
        })
        
        # 서명
        signed_txn = self.account.sign_transaction(transaction)
        
        # 전송 (eth_account의 SignedTransaction 객체는 raw_transaction 속성을 가짐)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        
        # 트랜잭션 영수증 대기
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        if receipt.status != 1:
            raise Exception(f"Transaction failed: {tx_hash.hex()}")
        
        logger.info(f"Transaction successful: {tx_hash.hex()}")
        return tx_hash.hex()
    
    def create_event_onchain(
        self,
        event_manager_address: str,
        ipfs_hash: str,
        price: int,
        max_tickets: int,
        start_time: int,
        end_time: int,
        event_date: int
    ) -> Optional[int]:
        """온체인에 이벤트 생성"""
        try:
            contract = self._get_contract(event_manager_address, "EventManager")
            
            # createEvent 함수 호출
            function = contract.functions.createEvent(
                ipfs_hash,
                price,
                max_tickets,
                start_time,
                end_time,
                event_date
            )
            
            tx_hash = self._send_transaction(function)
            
            # 트랜잭션 로그에서 eventId 추출
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            event_created = contract.events.EventCreated()
            
            for log in receipt.logs:
                try:
                    decoded = event_created.process_log(log)
                    event_id = decoded.args.eventId
                    logger.info(f"Event created onchain: eventId={event_id}, tx={tx_hash}")
                    return event_id
                except:
                    continue
            
            # 로그에서 추출 실패 시 컨트랙트에서 직접 조회
            current_id = contract.functions.getCurrentEventId().call()
            return current_id - 1  # 방금 생성된 이벤트 ID
            
        except Exception as e:
            logger.error(f"Failed to create event onchain: {e}")
            raise
    
    def approve_event_onchain(self, event_manager_address: str, event_id: int) -> Optional[str]:
        """온체인에서 이벤트 승인"""
        try:
            contract = self._get_contract(event_manager_address, "EventManager")
            
            function = contract.functions.approveEvent(event_id)
            tx_hash = self._send_transaction(function)
            
            logger.info(f"Event approved onchain: eventId={event_id}, tx={tx_hash}")
            return tx_hash
            
        except Exception as e:
            logger.error(f"Failed to approve event onchain: {e}")
            raise
    
    def purchase_ticket_onchain(
        self,
        event_manager_address: str,
        event_id: int,
        token_uri: str,
        value: int,
        buyer_address: str
    ) -> Tuple[Optional[str], Optional[int]]:
        """온체인에서 티켓 구매"""
        try:
            contract = self._get_contract(event_manager_address, "EventManager")
            
            # purchaseTicket 함수 호출 (payable)
            function = contract.functions.purchaseTicket(event_id, token_uri)
            
            tx_hash = self._send_transaction(function, value=value)
            
            # 트랜잭션 로그에서 tokenId 추출
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            ticket_sold = contract.events.TicketSold()
            
            for log in receipt.logs:
                try:
                    decoded = ticket_sold.process_log(log)
                    token_id = decoded.args.tokenId
                    logger.info(f"Ticket purchased onchain: tokenId={token_id}, tx={tx_hash}")
                    return tx_hash, token_id
                except:
                    continue
            
            # 로그에서 추출 실패 시 None 반환
            logger.warning(f"Could not extract tokenId from transaction: {tx_hash}")
            return tx_hash, None
            
        except Exception as e:
            logger.error(f"Failed to purchase ticket onchain: {e}")
            raise
    
    def list_ticket_for_resale(
        self,
        marketplace_address: str,
        ticket_nft_address: str,
        token_id: int,
        price: int
    ) -> Optional[str]:
        """티켓을 재판매 마켓플레이스에 등록"""
        try:
            # 1. TicketNFT 컨트랙트에서 approve
            ticket_nft = self._get_contract(ticket_nft_address, "TicketNFT")
            approve_function = ticket_nft.functions.approve(marketplace_address, token_id)
            approve_tx = self._send_transaction(approve_function)
            logger.info(f"Ticket approved for marketplace: tx={approve_tx}")
            
            # 2. TicketMarketplace 컨트랙트에서 listTicketForResale
            marketplace = self._get_contract(marketplace_address, "TicketMarketplace")
            list_function = marketplace.functions.listTicketForResale(token_id, price)
            list_tx = self._send_transaction(list_function)
            
            logger.info(f"Ticket listed for resale: tokenId={token_id}, price={price}, tx={list_tx}")
            return list_tx
            
        except Exception as e:
            logger.error(f"Failed to list ticket for resale: {e}")
            raise
    
    def buy_resale_ticket(
        self,
        marketplace_address: str,
        token_id: int,
        value: int,
        buyer_address: str
    ) -> Optional[str]:
        """재판매 티켓 구매"""
        try:
            marketplace = self._get_contract(marketplace_address, "TicketMarketplace")
            
            function = marketplace.functions.buyResaleTicket(token_id)
            tx_hash = self._send_transaction(function, value=value)
            
            logger.info(f"Resale ticket purchased: tokenId={token_id}, tx={tx_hash}")
            return tx_hash
            
        except Exception as e:
            logger.error(f"Failed to buy resale ticket: {e}")
            raise
    
    def request_refund_onchain(
        self,
        refund_manager_address: str,
        token_id: int
    ) -> Optional[str]:
        """온체인에 환불 요청"""
        try:
            refund_manager = self._get_contract(refund_manager_address, "RefundManager")
            
            function = refund_manager.functions.requestRefund(token_id)
            tx_hash = self._send_transaction(function)
            
            logger.info(f"Refund requested onchain: tokenId={token_id}, tx={tx_hash}")
            return tx_hash
            
        except Exception as e:
            logger.error(f"Failed to request refund onchain: {e}")
            raise
    
    def process_refund(
        self,
        refund_manager_address: str,
        ticket_nft_address: str,
        token_id: int
    ) -> Optional[str]:
        """환불 처리 (티켓 소각)"""
        try:
            refund_manager = self._get_contract(refund_manager_address, "RefundManager")
            
            function = refund_manager.functions.processRefund(token_id)
            tx_hash = self._send_transaction(function)
            
            logger.info(f"Refund processed: tokenId={token_id}, tx={tx_hash}")
            return tx_hash
            
        except Exception as e:
            logger.error(f"Failed to process refund: {e}")
            raise
    
    def get_event_onchain(self, event_manager_address: str, event_id: int) -> Optional[dict]:
        """온체인에서 이벤트 정보 조회"""
        try:
            contract = self._get_contract(event_manager_address, "EventManager")
            event = contract.functions.getEvent(event_id).call()
            
            return {
                "eventId": event[0],
                "organizer": event[1],
                "ipfsHash": event[2],
                "price": event[3],
                "maxTickets": event[4],
                "soldTickets": event[5],
                "startTime": event[6],
                "endTime": event[7],
                "eventDate": event[8],
                "approved": event[9],
                "cancelled": event[10],
            }
        except Exception as e:
            logger.error(f"Failed to get event onchain: {e}")
            return None


web3_service = Web3Service()
