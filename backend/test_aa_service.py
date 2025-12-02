#!/usr/bin/env python3
"""
Account Abstraction 서비스 테스트
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.aa_service import aa_service
from app.services.web3_service import web3_service
from web3 import Web3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_smart_wallet_address_generation():
    """Smart Wallet 주소 생성 테스트"""
    print("\n" + "=" * 60)
    print("테스트 1: Smart Wallet 주소 생성")
    print("=" * 60)
    
    try:
        user_id = "test-user-123"
        address = aa_service.generate_smart_wallet_address(user_id)
        print(f"✅ Smart Wallet 주소 생성 성공: {address}")
        return address
    except Exception as e:
        print(f"❌ 오류: {e}")
        return None

def test_user_operation_creation():
    """UserOperation 생성 테스트"""
    print("\n" + "=" * 60)
    print("테스트 2: UserOperation 생성")
    print("=" * 60)
    
    try:
        # Smart Wallet 주소
        sender = aa_service.generate_smart_wallet_address("test-user-123")
        
        # 테스트용 컨트랙트 호출 데이터
        target = web3_service.event_manager_address
        if not target:
            print("⚠️  EventManager 주소가 설정되지 않음, 테스트 스킵")
            return None
        
        # 빈 데이터로 테스트
        data = b""
        value = 0
        
        user_op = aa_service.create_user_operation(
            sender=sender,
            target=target,
            data=data,
            value=value
        )
        
        print(f"✅ UserOperation 생성 성공:")
        print(f"   Sender: {user_op['sender']}")
        print(f"   Nonce: {user_op['nonce']}")
        print(f"   Call Gas Limit: {user_op['callGasLimit']}")
        print(f"   Max Fee Per Gas: {user_op['maxFeePerGas']}")
        return user_op
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_user_operation_hash():
    """UserOperation 해시 계산 테스트"""
    print("\n" + "=" * 60)
    print("테스트 3: UserOperation 해시 계산")
    print("=" * 60)
    
    try:
        sender = aa_service.generate_smart_wallet_address("test-user-123")
        target = web3_service.event_manager_address or "0x0000000000000000000000000000000000000000"
        
        user_op = aa_service.create_user_operation(
            sender=sender,
            target=target,
            data=b"",
            value=0
        )
        
        # 해시 계산
        user_op_hash = aa_service._get_user_operation_hash(user_op)
        print(f"✅ UserOperation 해시 계산 성공:")
        print(f"   Hash: {user_op_hash.hex()}")
        return user_op_hash
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_user_operation_signing():
    """UserOperation 서명 테스트"""
    print("\n" + "=" * 60)
    print("테스트 4: UserOperation 서명")
    print("=" * 60)
    
    try:
        sender = aa_service.generate_smart_wallet_address("test-user-123")
        target = web3_service.event_manager_address or "0x0000000000000000000000000000000000000000"
        
        user_op = aa_service.create_user_operation(
            sender=sender,
            target=target,
            data=b"",
            value=0
        )
        
        # 서비스 계정의 private key 사용 (테스트용)
        from app.core.config import settings
        private_key = os.getenv("PRIVATE_KEY", settings.PRIVATE_KEY)
        if not private_key:
            print("⚠️  PRIVATE_KEY가 설정되지 않음, 테스트 스킵")
            return None
        
        signed_user_op = aa_service.sign_user_operation(user_op, private_key)
        
        print(f"✅ UserOperation 서명 성공:")
        print(f"   Signature: {signed_user_op['signature'].hex()[:20]}...")
        return signed_user_op
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_web3_connection():
    """Web3 연결 테스트"""
    print("\n" + "=" * 60)
    print("테스트 0: Web3 연결 확인")
    print("=" * 60)
    
    try:
        if not web3_service.w3:
            print("❌ Web3 연결 실패")
            return False
        
        if not web3_service.w3.is_connected():
            print("❌ Web3 연결되지 않음")
            return False
        
        block_number = web3_service.w3.eth.block_number
        print(f"✅ Web3 연결 성공:")
        print(f"   현재 블록 번호: {block_number}")
        return True
    except Exception as e:
        print(f"❌ 오류: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("\n" + "=" * 60)
    print("Account Abstraction 서비스 테스트 시작")
    print("=" * 60)
    
    # Web3 연결 확인
    if not test_web3_connection():
        print("\n❌ Web3 연결 실패. Hardhat 노드가 실행 중인지 확인하세요.")
        return
    
    # 각 테스트 실행
    test_smart_wallet_address_generation()
    test_user_operation_creation()
    test_user_operation_hash()
    test_user_operation_signing()
    
    print("\n" + "=" * 60)
    print("테스트 완료")
    print("=" * 60)

if __name__ == "__main__":
    main()

