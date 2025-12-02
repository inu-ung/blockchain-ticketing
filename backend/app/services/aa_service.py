"""
Account Abstraction 서비스
ERC-4337 기반 UserOperation 생성 및 관리
"""
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
from eth_abi import encode as abi_encode
from typing import Optional, Dict, Any
import json
import os
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class AccountAbstractionService:
    """Account Abstraction 서비스"""
    
    def __init__(self):
        # Web3Service 재사용 (이미 연결되어 있음)
        try:
            from app.services.web3_service import web3_service
            self.web3_service = web3_service
            self.w3 = web3_service.w3
            self.account = web3_service.account
            self.address = web3_service.address
        except Exception as e:
            logger.warning(f"Failed to initialize Web3Service: {e}")
            self.web3_service = None
            self.w3 = None
            self.account = None
            self.address = None
        
        if not self.w3 or not self.w3.is_connected():
            logger.warning("Web3 not connected in AA Service")
        
        logger.info("AA Service initialized")
        
        # Bundler 및 Paymaster 설정
        self.bundler_url = os.getenv("BUNDLER_URL", settings.BUNDLER_URL)
        self.paymaster_url = os.getenv("PAYMASTER_URL", settings.PAYMASTER_URL)
        
        # EntryPoint 주소 (ERC-4337 표준)
        self.entry_point_address = os.getenv(
            "ENTRY_POINT_ADDRESS",
            getattr(settings, 'ENTRY_POINT_ADDRESS', "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789")
        )
        
        # Smart Wallet Factory 주소
        self.factory_address = os.getenv(
            "SMART_WALLET_FACTORY_ADDRESS",
            getattr(settings, 'SMART_WALLET_FACTORY_ADDRESS', "")
        )
    
    def _get_contract(self, contract_address: str, contract_name: str):
        """컨트랙트 인스턴스 가져오기"""
        if not self.web3_service:
            raise Exception("Web3Service not initialized")
        return self.web3_service._get_contract(contract_address, contract_name)
    
    def _send_transaction(self, contract_function, value: int = 0) -> str:
        """트랜잭션 전송 헬퍼"""
        if not self.web3_service:
            raise Exception("Web3Service not initialized")
        return self.web3_service._send_transaction(contract_function, value)
    
    def generate_smart_wallet_address(
        self,
        user_id: str,
        owner_address: Optional[str] = None,
        salt: Optional[int] = None
    ) -> str:
        """
        Deterministic Smart Wallet 주소 생성 및 배포 (CREATE2)
        
        Args:
            user_id: 사용자 고유 ID
            owner_address: Owner 주소 (None이면 서비스 계정 사용)
            salt: 추가 salt 값 (선택사항, None이면 user_id 기반 생성)
        
        Returns:
            Smart Wallet 주소
        """
        if not self.w3:
            raise Exception("Web3 not connected")
        
        # Factory 주소 확인 (이미 __init__에서 설정됨)
        factory_address = self.factory_address
        
        if not factory_address:
            logger.warning("SmartWalletFactory address not configured, using hash-based address")
            # 임시로 해시 기반 주소 생성
            import hashlib
            user_id_str = str(user_id)
            if salt:
                user_id_str += str(salt)
            hash_bytes = hashlib.sha256(user_id_str.encode()).digest()[:20]
            return "0x" + hash_bytes.hex()
        
        # Owner 주소 설정
        if not owner_address:
            owner_address = self.address  # 서비스 계정 사용
        
        # Salt 생성 (user_id 기반)
        if salt is None:
            import hashlib
            salt_bytes = hashlib.sha256(str(user_id).encode()).digest()[:8]
            salt = int.from_bytes(salt_bytes, 'big')
        
        try:
            # Factory 컨트랙트 인스턴스
            factory = self._get_contract(factory_address, "SmartWalletFactory")
            
            # 주소 계산
            calculated_address = factory.functions.getAddress(
                owner_address,
                salt
            ).call()
            
            # 이미 배포되어 있는지 확인
            code = self.w3.eth.get_code(calculated_address)
            if code != b'':
                logger.info(f"Smart wallet already deployed: {calculated_address}")
                return calculated_address
            
            # 배포되지 않았다면 배포
            logger.info(f"Deploying smart wallet for user: {user_id}")
            function = factory.functions.createWallet(owner_address, salt)
            tx_hash = self._send_transaction(function)
            
            logger.info(f"Smart wallet deployed: {calculated_address}, tx: {tx_hash}")
            return calculated_address
            
        except Exception as e:
            logger.error(f"Failed to deploy smart wallet: {e}")
            # 실패 시 임시 주소 반환
            import hashlib
            hash_bytes = hashlib.sha256(str(user_id).encode()).digest()[:20]
            return "0x" + hash_bytes.hex()
    
    def create_user_operation(
        self,
        sender: str,
        target: str,
        data: bytes,
        value: int = 0,
        nonce: Optional[int] = None,
        call_gas_limit: Optional[int] = None,
        verification_gas_limit: Optional[int] = None,
        pre_verification_gas: Optional[int] = None,
        max_fee_per_gas: Optional[int] = None,
        max_priority_fee_per_gas: Optional[int] = None,
        paymaster_and_data: bytes = b""
    ) -> Dict[str, Any]:
        """
        UserOperation 생성
        
        Args:
            sender: Smart Wallet 주소
            target: 호출할 컨트랙트 주소
            data: 호출 데이터
            value: 전송할 이더 값
            nonce: Nonce 값 (None이면 자동 조회)
            call_gas_limit: 호출 가스 한도
            verification_gas_limit: 검증 가스 한도
            pre_verification_gas: 사전 검증 가스
            max_fee_per_gas: 최대 가스비
            max_priority_fee_per_gas: 최대 우선순위 가스비
            paymaster_and_data: Paymaster 데이터
        
        Returns:
            UserOperation 딕셔너리
        """
        if not self.w3:
            raise Exception("Web3 not connected")
        
        # Nonce 조회 (EntryPoint에서)
        if nonce is None:
            try:
                # EntryPoint ABI (getNonce 함수 포함)
                entry_point_abi = [
                    {
                        "inputs": [
                            {"name": "sender", "type": "address"},
                            {"name": "key", "type": "uint192"}
                        ],
                        "name": "getNonce",
                        "outputs": [{"name": "", "type": "uint256"}],
                        "stateMutability": "view",
                        "type": "function"
                    }
                ]
                
                entry_point = self.w3.eth.contract(
                    address=Web3.to_checksum_address(self.entry_point_address),
                    abi=entry_point_abi
                )
                
                # EntryPoint에서 nonce 조회 (key는 0 사용)
                nonce = entry_point.functions.getNonce(
                    Web3.to_checksum_address(sender),
                    0
                ).call()
                logger.info(f"Nonce from EntryPoint: {nonce}")
            except Exception as e:
                logger.warning(f"Failed to get nonce from EntryPoint: {e}, using 0")
                nonce = 0
        
        # 가스비 조회
        if max_fee_per_gas is None or max_priority_fee_per_gas is None:
            fee_history = self.w3.eth.fee_history(1, "latest")
            base_fee = fee_history["baseFeePerGas"][0]
            max_priority_fee_per_gas = self.w3.to_wei(2, "gwei")
            max_fee_per_gas = base_fee + max_priority_fee_per_gas
        
        # 가스 한도 설정
        if call_gas_limit is None:
            call_gas_limit = 100000
        if verification_gas_limit is None:
            verification_gas_limit = 100000
        if pre_verification_gas is None:
            pre_verification_gas = 50000
        
        # UserOperation 구조
        user_operation = {
            "sender": sender,
            "nonce": nonce,
            "initCode": b"",  # Smart Wallet이 이미 배포된 경우 빈 바이트
            "callData": data,
            "callGasLimit": call_gas_limit,
            "verificationGasLimit": verification_gas_limit,
            "preVerificationGas": pre_verification_gas,
            "maxFeePerGas": max_fee_per_gas,
            "maxPriorityFeePerGas": max_priority_fee_per_gas,
            "paymasterAndData": paymaster_and_data,
            "signature": b""  # 나중에 서명 추가
        }
        
        logger.info(f"Created UserOperation: sender={sender}, target={target}")
        return user_operation
    
    def _get_user_operation_hash(
        self,
        user_operation: Dict[str, Any]
    ) -> bytes:
        """
        ERC-4337 표준에 따른 UserOperation 해시 계산
        
        Args:
            user_operation: UserOperation 딕셔너리
        
        Returns:
            UserOperation 해시 (bytes32)
        """
        if not self.w3:
            raise Exception("Web3 not connected")
        
        # EntryPoint 컨트랙트에서 getUserOpHash 호출 시도
        try:
            # EntryPoint ABI (getUserOpHash 함수만 포함)
            entry_point_abi = [
                {
                    "inputs": [
                        {
                            "components": [
                                {"name": "sender", "type": "address"},
                                {"name": "nonce", "type": "uint256"},
                                {"name": "initCode", "type": "bytes"},
                                {"name": "callData", "type": "bytes"},
                                {"name": "callGasLimit", "type": "uint256"},
                                {"name": "verificationGasLimit", "type": "uint256"},
                                {"name": "preVerificationGas", "type": "uint256"},
                                {"name": "maxFeePerGas", "type": "uint256"},
                                {"name": "maxPriorityFeePerGas", "type": "uint256"},
                                {"name": "paymasterAndData", "type": "bytes"},
                                {"name": "signature", "type": "bytes"}
                            ],
                            "name": "userOp",
                            "type": "tuple"
                        }
                    ],
                    "name": "getUserOpHash",
                    "outputs": [{"name": "", "type": "bytes32"}],
                    "stateMutability": "view",
                    "type": "function"
                }
            ]
            
            entry_point = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.entry_point_address),
                abi=entry_point_abi
            )
            
            # UserOperation을 튜플로 변환
            user_op_tuple = (
                Web3.to_checksum_address(user_operation["sender"]),
                user_operation["nonce"],
                user_operation["initCode"],
                user_operation["callData"],
                user_operation["callGasLimit"],
                user_operation["verificationGasLimit"],
                user_operation["preVerificationGas"],
                user_operation["maxFeePerGas"],
                user_operation["maxPriorityFeePerGas"],
                user_operation["paymasterAndData"],
                user_operation.get("signature", b"")
            )
            
            # EntryPoint에서 해시 조회
            user_op_hash = entry_point.functions.getUserOpHash(user_op_tuple).call()
            logger.info(f"UserOperation hash from EntryPoint: {user_op_hash.hex()}")
            return user_op_hash
            
        except Exception as e:
            logger.warning(f"Failed to get hash from EntryPoint: {e}, using manual calculation")
            # EntryPoint가 없거나 호출 실패 시 수동 계산
            # ERC-4337 표준: keccak256(abi.encodePacked(...))
            
            # UserOperation 필드를 순서대로 인코딩
            encoded = abi_encode(
                ['address', 'uint256', 'bytes', 'bytes', 'uint256', 'uint256', 'uint256', 'uint256', 'uint256', 'bytes', 'bytes'],
                [
                    Web3.to_checksum_address(user_operation["sender"]),
                    user_operation["nonce"],
                    user_operation["initCode"],
                    user_operation["callData"],
                    user_operation["callGasLimit"],
                    user_operation["verificationGasLimit"],
                    user_operation["preVerificationGas"],
                    user_operation["maxFeePerGas"],
                    user_operation["maxPriorityFeePerGas"],
                    user_operation["paymasterAndData"],
                    user_operation.get("signature", b"")
                ]
            )
            
            # keccak256 해시 계산
            user_op_hash = Web3.keccak(encoded)
            logger.info(f"UserOperation hash (manual): {user_op_hash.hex()}")
            return user_op_hash
    
    def sign_user_operation(
        self,
        user_operation: Dict[str, Any],
        private_key: str
    ) -> Dict[str, Any]:
        """
        UserOperation 서명 (ERC-4337 표준)
        
        Args:
            user_operation: UserOperation 딕셔너리
            private_key: Owner의 private key (서명에 사용)
        
        Returns:
            서명된 UserOperation
        """
        if not self.w3:
            raise Exception("Web3 not connected")
        
        # UserOperation 해시 계산
        user_op_hash = self._get_user_operation_hash(user_operation)
        
        # Ethereum 서명 메시지 해시로 변환 (EIP-191)
        # ERC-4337에서는 EntryPoint가 이미 메시지 해시를 계산하므로
        # 여기서는 직접 해시를 사용하거나, toEthSignedMessageHash 사용
        
        # EntryPoint에서 받은 해시를 그대로 사용 (EntryPoint가 이미 처리)
        # 또는 toEthSignedMessageHash 사용
        message_hash = encode_defunct(primitive=user_op_hash)
        
        # 서명
        if not private_key.startswith("0x"):
            private_key = "0x" + private_key
        
        account = Account.from_key(private_key)
        signed_message = account.sign_message(message_hash)
        signature = signed_message.signature
        
        # UserOperation에 서명 추가
        user_operation["signature"] = signature
        
        logger.info(f"UserOperation signed by {account.address}")
        return user_operation
    
    def send_user_operation(
        self,
        user_operation: Dict[str, Any]
    ) -> str:
        """
        UserOperation을 Bundler로 전송
        
        Args:
            user_operation: 서명된 UserOperation
        
        Returns:
            UserOperation 해시
        """
        if not self.bundler_url:
            # Bundler URL이 없으면 직접 EntryPoint로 전송 (로컬 테스트용)
            logger.warning("Bundler URL not configured, sending directly to EntryPoint")
            return self._send_user_operation_direct(user_operation)
        
        # Bundler API 호출
        import requests
        
        # UserOperation을 JSON-RPC 형식으로 변환
        user_op_rpc = {
            "sender": user_operation["sender"],
            "nonce": hex(user_operation["nonce"]),
            "initCode": user_operation["initCode"].hex() if isinstance(user_operation["initCode"], bytes) else user_operation["initCode"],
            "callData": user_operation["callData"].hex() if isinstance(user_operation["callData"], bytes) else user_operation["callData"],
            "callGasLimit": hex(user_operation["callGasLimit"]),
            "verificationGasLimit": hex(user_operation["verificationGasLimit"]),
            "preVerificationGas": hex(user_operation["preVerificationGas"]),
            "maxFeePerGas": hex(user_operation["maxFeePerGas"]),
            "maxPriorityFeePerGas": hex(user_operation["maxPriorityFeePerGas"]),
            "paymasterAndData": user_operation["paymasterAndData"].hex() if isinstance(user_operation["paymasterAndData"], bytes) else user_operation["paymasterAndData"],
            "signature": user_operation["signature"].hex() if isinstance(user_operation["signature"], bytes) else user_operation["signature"]
        }
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_sendUserOperation",
            "params": [user_op_rpc, self.entry_point_address]
        }
        
        try:
            response = requests.post(
                self.bundler_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise Exception(f"Bundler error: {result['error']}")
            
            user_op_hash = result.get("result")
            logger.info(f"UserOperation sent to bundler: {user_op_hash}")
            return user_op_hash
            
        except Exception as e:
            logger.error(f"Failed to send UserOperation to bundler: {e}")
            # 실패 시 직접 전송 시도
            logger.info("Falling back to direct EntryPoint call")
            return self._send_user_operation_direct(user_operation)
    
    def _send_user_operation_direct(
        self,
        user_operation: Dict[str, Any]
    ) -> str:
        """
        EntryPoint에 직접 UserOperation 전송 (로컬 테스트용)
        
        Args:
            user_operation: 서명된 UserOperation
        
        Returns:
            트랜잭션 해시
        """
        if not self.w3:
            raise Exception("Web3 not connected")
        
        # EntryPoint ABI (handleOps 함수 포함)
        entry_point_abi = [
            {
                "inputs": [
                    {
                        "components": [
                            {"name": "sender", "type": "address"},
                            {"name": "nonce", "type": "uint256"},
                            {"name": "initCode", "type": "bytes"},
                            {"name": "callData", "type": "bytes"},
                            {"name": "callGasLimit", "type": "uint256"},
                            {"name": "verificationGasLimit", "type": "uint256"},
                            {"name": "preVerificationGas", "type": "uint256"},
                            {"name": "maxFeePerGas", "type": "uint256"},
                            {"name": "maxPriorityFeePerGas", "type": "uint256"},
                            {"name": "paymasterAndData", "type": "bytes"},
                            {"name": "signature", "type": "bytes"}
                        ],
                        "name": "ops",
                        "type": "tuple[]"
                    },
                    {"name": "beneficiary", "type": "address"}
                ],
                "name": "handleOps",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        
        try:
            entry_point = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.entry_point_address),
                abi=entry_point_abi
            )
            
            # UserOperation을 튜플로 변환
            user_op_tuple = (
                Web3.to_checksum_address(user_operation["sender"]),
                user_operation["nonce"],
                user_operation["initCode"],
                user_operation["callData"],
                user_operation["callGasLimit"],
                user_operation["verificationGasLimit"],
                user_operation["preVerificationGas"],
                user_operation["maxFeePerGas"],
                user_operation["maxPriorityFeePerGas"],
                user_operation["paymasterAndData"],
                user_operation["signature"]
            )
            
            # EntryPoint.handleOps 호출
            function = entry_point.functions.handleOps(
                [user_op_tuple],
                self.address  # beneficiary (가스비 수령자)
            )
            
            # 트랜잭션 전송
            tx_hash = self._send_transaction(function)
            logger.info(f"UserOperation sent directly to EntryPoint: {tx_hash}")
            return tx_hash
            
        except Exception as e:
            logger.error(f"Failed to send UserOperation to EntryPoint: {e}")
            raise
    
    def get_paymaster_sponsor_data(
        self,
        user_operation: Dict[str, Any],
        target: Optional[str] = None
    ) -> bytes:
        """
        Paymaster에서 가스비 스폰서 데이터 가져오기
        
        Paymaster 정책:
        - 티켓 구매 (EventManager.purchaseTicket): 스폰서 ✅
        - 환불 (RefundManager.processRefund): 스폰서 ✅
        - 재판매 등록/구매: 사용자 부담 ❌
        
        Args:
            user_operation: UserOperation 딕셔너리
            target: 호출할 컨트랙트 주소 (선택사항)
        
        Returns:
            Paymaster 데이터 (스폰서할 경우 Paymaster 주소 포함, 아니면 빈 바이트)
        """
        if not self.paymaster_url:
            # Paymaster URL이 없으면 외부 Paymaster 서비스 사용 안 함
            # 로컬 테스트에서는 빈 바이트 반환 (사용자가 가스비 부담)
            logger.info("Paymaster URL not configured, skipping sponsor")
            return b""
        
        # target 주소로 어떤 컨트랙트인지 판단
        if target:
            from app.core.config import settings
            
            # 티켓 구매 (EventManager) - 스폰서
            if target.lower() == settings.EVENT_MANAGER_ADDRESS.lower():
                # callData에서 함수 시그니처 확인
                call_data = user_operation.get("callData", b"")
                if isinstance(call_data, str):
                    call_data = bytes.fromhex(call_data.replace("0x", ""))
                
                # purchaseTicket 함수 시그니처: 0x + keccak256("purchaseTicket(uint256,string)")[:4]
                # 실제로는 함수 시그니처를 확인하거나, 간단히 EventManager 호출이면 스폰서
                logger.info("EventManager call detected - Paymaster sponsor enabled")
                return self._get_paymaster_data(user_operation)
            
            # 환불 (RefundManager) - 스폰서
            if target.lower() == settings.REFUND_MANAGER_ADDRESS.lower():
                logger.info("RefundManager call detected - Paymaster sponsor enabled")
                return self._get_paymaster_data(user_operation)
            
            # 재판매 (Marketplace) - 사용자 부담
            if target.lower() == settings.MARKETPLACE_ADDRESS.lower():
                logger.info("Marketplace call detected - user pays gas")
                return b""
        
        # 기본적으로 스폰서하지 않음 (사용자 부담)
        logger.info("Paymaster sponsor not applicable")
        return b""
    
    def _get_paymaster_data(
        self,
        user_operation: Dict[str, Any]
    ) -> bytes:
        """
        Paymaster 서비스에서 스폰서 데이터 가져오기
        
        Args:
            user_operation: UserOperation 딕셔너리
        
        Returns:
            Paymaster 데이터 (Paymaster 주소 + 서명 데이터)
        """
        try:
            import requests
            
            # Paymaster API 호출
            # 실제 Paymaster 서비스가 있다면 이렇게 호출
            payload = {
                "user_operation": {
                    "sender": user_operation["sender"],
                    "nonce": user_operation["nonce"],
                    "callData": user_operation["callData"].hex() if isinstance(user_operation["callData"], bytes) else user_operation["callData"],
                    "callGasLimit": user_operation["callGasLimit"],
                    "verificationGasLimit": user_operation["verificationGasLimit"],
                    "preVerificationGas": user_operation["preVerificationGas"],
                    "maxFeePerGas": user_operation["maxFeePerGas"],
                    "maxPriorityFeePerGas": user_operation["maxPriorityFeePerGas"],
                },
                "entryPoint": self.entry_point_address
            }
            
            response = requests.post(
                f"{self.paymaster_url}/sponsor",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                # Paymaster 데이터 형식: paymaster_address (20 bytes) + paymaster_data (서명 등)
                paymaster_address = result.get("paymaster_address", "")
                paymaster_data = result.get("paymaster_data", "")
                
                if paymaster_address:
                    # 주소를 bytes로 변환 (20 bytes)
                    if paymaster_address.startswith("0x"):
                        paymaster_address_bytes = bytes.fromhex(paymaster_address[2:])
                    else:
                        paymaster_address_bytes = bytes.fromhex(paymaster_address)
                    
                    # paymaster_data도 bytes로 변환
                    if paymaster_data:
                        if isinstance(paymaster_data, str):
                            if paymaster_data.startswith("0x"):
                                paymaster_data_bytes = bytes.fromhex(paymaster_data[2:])
                            else:
                                paymaster_data_bytes = bytes.fromhex(paymaster_data)
                        else:
                            paymaster_data_bytes = paymaster_data
                    else:
                        paymaster_data_bytes = b""
                    
                    # Paymaster 주소 + 데이터 결합
                    paymaster_and_data = paymaster_address_bytes + paymaster_data_bytes
                    logger.info(f"Paymaster sponsor data retrieved: {paymaster_address}")
                    return paymaster_and_data
            
            logger.warning(f"Paymaster API returned error: {response.status_code}")
            return b""
            
        except Exception as e:
            logger.warning(f"Failed to get Paymaster sponsor data: {e}")
            # 실패 시 빈 바이트 반환 (사용자가 가스비 부담)
            return b""


aa_service = AccountAbstractionService()

