#!/usr/bin/env python3
"""
Web3 서비스 테스트 스크립트
로컬 네트워크에서 Web3 서비스가 제대로 작동하는지 확인
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.web3_service import web3_service
from app.core.config import settings
import time

def test_web3_connection():
    """Web3 연결 테스트"""
    print("🔍 Web3 연결 테스트...")
    if not web3_service.w3:
        print("❌ Web3 연결 실패")
        return False
    
    if not web3_service.w3.is_connected():
        print("❌ Web3 연결 실패")
        return False
    
    print(f"✅ Web3 연결 성공: {web3_service.w3.eth.chain_id}")
    return True

def test_account():
    """서비스 계정 테스트"""
    print("\n🔍 서비스 계정 테스트...")
    if not web3_service.account:
        print("❌ 서비스 계정이 설정되지 않음")
        return False
    
    print(f"✅ 서비스 계정: {web3_service.address}")
    
    # 잔액 확인
    balance = web3_service.w3.eth.get_balance(web3_service.address)
    print(f"   잔액: {web3_service.w3.from_wei(balance, 'ether')} ETH")
    return True

def test_contract_addresses():
    """컨트랙트 주소 테스트"""
    print("\n🔍 컨트랙트 주소 테스트...")
    addresses = {
        "EventManager": web3_service.event_manager_address,
        "TicketNFT": web3_service.ticket_nft_address,
        "Marketplace": web3_service.marketplace_address,
        "RefundManager": web3_service.refund_manager_address,
    }
    
    all_set = True
    for name, address in addresses.items():
        if address:
            print(f"✅ {name}: {address}")
        else:
            print(f"❌ {name}: 설정되지 않음")
            all_set = False
    
    return all_set

def test_contract_instances():
    """컨트랙트 인스턴스 생성 테스트"""
    print("\n🔍 컨트랙트 인스턴스 생성 테스트...")
    
    try:
        event_manager = web3_service._get_contract(
            web3_service.event_manager_address,
            "EventManager"
        )
        print("✅ EventManager 인스턴스 생성 성공")
        
        # 간단한 view 함수 호출 테스트
        current_id = event_manager.functions.getCurrentEventId().call()
        print(f"   현재 이벤트 ID: {current_id}")
        
        return True
    except Exception as e:
        print(f"❌ 컨트랙트 인스턴스 생성 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("=" * 60)
    print("Web3 서비스 테스트 시작")
    print("=" * 60)
    
    results = []
    
    # 1. Web3 연결 테스트
    results.append(("Web3 연결", test_web3_connection()))
    
    # 2. 서비스 계정 테스트
    results.append(("서비스 계정", test_account()))
    
    # 3. 컨트랙트 주소 테스트
    results.append(("컨트랙트 주소", test_contract_addresses()))
    
    # 4. 컨트랙트 인스턴스 테스트
    results.append(("컨트랙트 인스턴스", test_contract_instances()))
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 통과" if result else "❌ 실패"
        print(f"{name}: {status}")
    
    print(f"\n총 {passed}/{total} 테스트 통과")
    
    if passed == total:
        print("\n🎉 모든 테스트 통과!")
        return 0
    else:
        print("\n⚠️  일부 테스트 실패")
        return 1

if __name__ == "__main__":
    sys.exit(main())

