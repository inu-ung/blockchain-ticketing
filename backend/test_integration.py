#!/usr/bin/env python3
"""
통합 테스트 스크립트
전체 플로우를 테스트합니다:
1. 사용자 등록/로그인
2. 이벤트 생성 (온체인)
3. 이벤트 승인 (온체인)
4. 티켓 구매 (온체인)
5. 재판매 등록 (온체인)
6. 재판매 구매 (온체인)
7. 환불 요청 및 처리 (온체인)
"""

import sys
import os
import requests
import time
from datetime import datetime, timedelta
import json

# 백엔드 API URL
BASE_URL = "http://localhost:8000/api/v1"

# 테스트 결과 저장
test_results = []

def log_test(name, success, message=""):
    """테스트 결과 로깅"""
    status = "✅" if success else "❌"
    print(f"{status} {name}: {message}")
    test_results.append((name, success, message))
    return success

def test_user_registration():
    """사용자 등록 테스트"""
    print("\n" + "="*60)
    print("1. 사용자 등록 테스트")
    print("="*60)
    
    # 테스트용 사용자 데이터
    user_data = {
        "name": "Test User",
        "email": f"test_{int(time.time())}@example.com",
        "password": "test123",
        "role": "buyer"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        if response.status_code == 201:
            user = response.json()
            log_test("사용자 등록", True, f"User ID: {user.get('id')}")
            return user
        else:
            log_test("사용자 등록", False, f"Status: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        log_test("사용자 등록", False, str(e))
        return None

def test_user_login(email, password):
    """사용자 로그인 테스트"""
    print("\n" + "="*60)
    print("2. 사용자 로그인 테스트")
    print("="*60)
    
    login_data = {
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            log_test("사용자 로그인", True, f"Token: {token[:20]}...")
            return token
        else:
            log_test("사용자 로그인", False, f"Status: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        log_test("사용자 로그인", False, str(e))
        return None

def test_create_event(token):
    """이벤트 생성 테스트 (온체인 포함)"""
    print("\n" + "="*60)
    print("3. 이벤트 생성 테스트 (온체인)")
    print("="*60)
    
    # 먼저 주최자 역할로 사용자 생성
    organizer_data = {
        "name": "Test Organizer",
        "email": f"organizer_{int(time.time())}@example.com",
        "password": "test123",
        "role": "organizer"
    }
    
    try:
        # 주최자 등록
        response = requests.post(f"{BASE_URL}/auth/register", json=organizer_data)
        if response.status_code != 201:
            log_test("주최자 등록", False, f"Status: {response.status_code}")
            return None
        
        organizer = response.json()
        
        # 주최자 로그인
        login_response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": organizer_data["email"],
            "password": "test123"
        })
        if login_response.status_code != 200:
            log_test("주최자 로그인", False, f"Status: {login_response.status_code}")
            return None
        
        organizer_token = login_response.json().get("access_token")
        
        # 지갑 주소 연결 (테스트용)
        wallet_response = requests.post(
            f"{BASE_URL}/auth/wallet/connect",
            json={"wallet_address": "0x70997970C51812dc3A010C7d01b50e0d17dc79C8"},
            headers={"Authorization": f"Bearer {organizer_token}"}
        )
        
        # 이벤트 생성 (판매 기간을 현재 시간부터로 설정)
        now = datetime.utcnow()
        event_data = {
            "name": "Test Concert",
            "description": "This is a test event for integration testing",
            "price_wei": 1000000000000000000,  # 1 ETH
            "max_tickets": 100,
            "start_time": (now - timedelta(hours=1)).isoformat(),  # 1시간 전부터 판매 시작
            "end_time": (now + timedelta(days=1)).isoformat(),  # 1일 후까지 판매
            "event_date": (now + timedelta(days=7)).isoformat()  # 7일 후 이벤트
        }
        
        response = requests.post(
            f"{BASE_URL}/events",
            json=event_data,
            headers={"Authorization": f"Bearer {organizer_token}"}
        )
        
        if response.status_code == 201:
            event = response.json()
            event_id_onchain = event.get("event_id_onchain")
            log_test("이벤트 생성", True, f"Event ID: {event.get('id')}, Onchain ID: {event_id_onchain}")
            return event, organizer_token
        else:
            log_test("이벤트 생성", False, f"Status: {response.status_code}, {response.text}")
            return None, None
    except Exception as e:
        log_test("이벤트 생성", False, str(e))
        return None, None

def test_approve_event(event, admin_token):
    """이벤트 승인 테스트 (온체인)"""
    print("\n" + "="*60)
    print("4. 이벤트 승인 테스트 (온체인)")
    print("="*60)
    
    if not event:
        log_test("이벤트 승인", False, "이벤트가 없습니다")
        return False
    
    try:
        response = requests.post(
            f"{BASE_URL}/events/{event['id']}/approve",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code == 200:
            approved_event = response.json()
            log_test("이벤트 승인", True, f"Event ID: {approved_event.get('id')}, Status: {approved_event.get('status')}")
            return True
        else:
            log_test("이벤트 승인", False, f"Status: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        log_test("이벤트 승인", False, str(e))
        return False

def test_purchase_ticket(event, buyer_token):
    """티켓 구매 테스트 (온체인)"""
    print("\n" + "="*60)
    print("5. 티켓 구매 테스트 (온체인)")
    print("="*60)
    
    if not event:
        log_test("티켓 구매", False, "이벤트가 없습니다")
        return None
    
    try:
        purchase_data = {
            "event_id": event["id"]
        }
        
        response = requests.post(
            f"{BASE_URL}/tickets/purchase",
            json=purchase_data,
            headers={"Authorization": f"Bearer {buyer_token}"}
        )
        
        if response.status_code == 201:
            ticket = response.json()
            token_id = ticket.get("token_id")
            tx_hash = ticket.get("purchase_tx_hash")
            log_test("티켓 구매", True, f"Ticket ID: {ticket.get('id')}, Token ID: {token_id}, TX: {tx_hash}")
            return ticket
        else:
            log_test("티켓 구매", False, f"Status: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        log_test("티켓 구매", False, str(e))
        return None

def test_list_resale(ticket, seller_token):
    """재판매 등록 테스트 (온체인)"""
    print("\n" + "="*60)
    print("6. 재판매 등록 테스트 (온체인)")
    print("="*60)
    
    if not ticket:
        log_test("재판매 등록", False, "티켓이 없습니다")
        return None
    
    try:
        resale_data = {
            "ticket_id": ticket["id"],
            "price_wei": 1500000000000000000  # 1.5 ETH
        }
        
        response = requests.post(
            f"{BASE_URL}/resales",
            json=resale_data,
            headers={"Authorization": f"Bearer {seller_token}"}
        )
        
        if response.status_code == 201:
            resale = response.json()
            log_test("재판매 등록", True, f"Resale ID: {resale.get('id')}, Price: {resale.get('price_wei')}")
            return resale
        else:
            log_test("재판매 등록", False, f"Status: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        log_test("재판매 등록", False, str(e))
        return None

def test_buy_resale(resale, buyer_token):
    """재판매 구매 테스트 (온체인)"""
    print("\n" + "="*60)
    print("7. 재판매 구매 테스트 (온체인)")
    print("="*60)
    
    if not resale:
        log_test("재판매 구매", False, "재판매가 없습니다")
        return False
    
    try:
        response = requests.post(
            f"{BASE_URL}/resales/{resale['id']}/buy",
            headers={"Authorization": f"Bearer {buyer_token}"}
        )
        
        if response.status_code == 200:
            purchased_resale = response.json()
            log_test("재판매 구매", True, f"Resale ID: {purchased_resale.get('id')}, Status: {purchased_resale.get('status')}")
            return True
        else:
            log_test("재판매 구매", False, f"Status: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        log_test("재판매 구매", False, str(e))
        return False

def test_refund_request(ticket, buyer_token):
    """환불 요청 테스트"""
    print("\n" + "="*60)
    print("8. 환불 요청 테스트")
    print("="*60)
    
    if not ticket:
        log_test("환불 요청", False, "티켓이 없습니다")
        return None
    
    try:
        refund_data = {
            "ticket_id": ticket["id"],
            "reason": "Test refund request"
        }
        
        response = requests.post(
            f"{BASE_URL}/refunds/request",
            json=refund_data,
            headers={"Authorization": f"Bearer {buyer_token}"}
        )
        
        if response.status_code == 201:
            refund = response.json()
            log_test("환불 요청", True, f"Refund ID: {refund.get('id')}, Status: {refund.get('status')}")
            return refund
        else:
            log_test("환불 요청", False, f"Status: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        log_test("환불 요청", False, str(e))
        return None

def test_approve_refund(refund, organizer_token):
    """환불 승인 테스트 (온체인)"""
    print("\n" + "="*60)
    print("9. 환불 승인 테스트 (온체인)")
    print("="*60)
    
    if not refund:
        log_test("환불 승인", False, "환불 요청이 없습니다")
        return False
    
    try:
        response = requests.post(
            f"{BASE_URL}/refunds/{refund['id']}/approve",
            headers={"Authorization": f"Bearer {organizer_token}"}
        )
        
        if response.status_code == 200:
            approved_refund = response.json()
            log_test("환불 승인", True, f"Refund ID: {approved_refund.get('id')}, Status: {approved_refund.get('status')}")
            return True
        else:
            log_test("환불 승인", False, f"Status: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        log_test("환불 승인", False, str(e))
        return False

def create_admin_user():
    """관리자 사용자 생성 (테스트용)"""
    admin_data = {
        "name": "Test Admin",
        "email": f"admin_{int(time.time())}@example.com",
        "password": "test123",
        "role": "admin"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=admin_data)
        if response.status_code == 201:
            admin = response.json()
            login_response = requests.post(f"{BASE_URL}/auth/login", json={
                "email": admin_data["email"],
                "password": "test123"
            })
            if login_response.status_code == 200:
                return login_response.json().get("access_token")
    except:
        pass
    return None

def main():
    """메인 테스트 함수"""
    print("="*60)
    print("통합 테스트 시작")
    print("="*60)
    print(f"API URL: {BASE_URL}")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 백엔드 서버 연결 확인
    try:
        response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=5)
        print("✅ 백엔드 서버 연결 확인")
    except:
        print("❌ 백엔드 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        print("   실행 명령: cd backend && source venv/bin/activate && uvicorn main:app --reload")
        return 1
    
    # 1. 사용자 등록
    user = test_user_registration()
    if not user:
        print("\n❌ 사용자 등록 실패로 테스트 중단")
        return 1
    
    # 2. 사용자 로그인
    buyer_token = test_user_login(user["email"], "test123")
    if not buyer_token:
        print("\n❌ 사용자 로그인 실패로 테스트 중단")
        return 1
    
    # 지갑 주소 연결
    try:
        wallet_response = requests.post(
            f"{BASE_URL}/auth/wallet/connect",
            json={"wallet_address": "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC"},
            headers={"Authorization": f"Bearer {buyer_token}"}
        )
        if wallet_response.status_code == 200:
            print(f"✅ 지갑 연결 성공: {wallet_response.json().get('wallet_address')}")
        else:
            print(f"⚠️  지갑 연결 실패: {wallet_response.status_code}, {wallet_response.text}")
    except Exception as e:
        print(f"⚠️  지갑 연결 에러: {e}")
    
    # 3. 이벤트 생성 (온체인)
    event, organizer_token = test_create_event(buyer_token)
    if not event:
        print("\n❌ 이벤트 생성 실패로 테스트 중단")
        return 1
    
    # 관리자 토큰 생성
    admin_token = create_admin_user()
    
    # 4. 이벤트 승인 (온체인)
    if admin_token:
        test_approve_event(event, admin_token)
    
    # 5. 티켓 구매 (온체인)
    ticket = test_purchase_ticket(event, buyer_token)
    
    # 6. 재판매 등록 (온체인) - 티켓이 있는 경우에만
    resale = None
    if ticket:
        resale = test_list_resale(ticket, buyer_token)
    
    # 7. 재판매 구매 (온체인) - 재판매가 있는 경우에만
    # 새로운 구매자 생성
    if resale:
        buyer2 = test_user_registration()
        if buyer2:
            buyer2_token = test_user_login(buyer2["email"], "test123")
            if buyer2_token:
                # 지갑 주소 연결 (다른 주소 사용)
                wallet_response = requests.post(
                    f"{BASE_URL}/auth/wallet/connect",
                    json={"wallet_address": "0x90F79bf6EB2c4f870365E785982E1f101E93b906"},
                    headers={"Authorization": f"Bearer {buyer2_token}"}
                )
                if wallet_response.status_code == 200:
                    print(f"✅ buyer2 지갑 연결 성공: {wallet_response.json().get('wallet_address')}")
                else:
                    print(f"⚠️  buyer2 지갑 연결 실패: {wallet_response.status_code}")
                test_buy_resale(resale, buyer2_token)
    
    # 8. 환불 요청 - 새로운 티켓 구매
    if event and buyer_token:
        ticket2 = test_purchase_ticket(event, buyer_token)
        if ticket2:
            refund = test_refund_request(ticket2, buyer_token)
            # 9. 환불 승인 (온체인)
            if refund and organizer_token:
                test_approve_refund(refund, organizer_token)
    
    # 결과 요약
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)
    
    passed = sum(1 for _, success, _ in test_results if success)
    total = len(test_results)
    
    for name, success, message in test_results:
        status = "✅ 통과" if success else "❌ 실패"
        print(f"{status} - {name}")
        if message and not success:
            print(f"   └─ {message}")
    
    print(f"\n총 {passed}/{total} 테스트 통과")
    print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if passed == total:
        print("\n🎉 모든 테스트 통과!")
        return 0
    else:
        print(f"\n⚠️  {total - passed}개 테스트 실패")
        return 1

if __name__ == "__main__":
    sys.exit(main())

