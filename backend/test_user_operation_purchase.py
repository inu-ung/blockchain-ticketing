#!/usr/bin/env python3
"""
UserOperation을 사용한 티켓 구매 테스트
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
import json
from datetime import datetime, timedelta

API_URL = "http://localhost:8000"

def test_user_operation_purchase():
    """UserOperation을 사용한 티켓 구매 테스트"""
    print("\n" + "=" * 60)
    print("UserOperation 티켓 구매 테스트")
    print("=" * 60)
    
    # 1. 로그인
    print("\n1. 로그인...")
    login_data = {
        "email": "buyer@test.com",
        "password": "test123"
    }
    
    response = requests.post(f"{API_URL}/api/v1/auth/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ 로그인 실패: {response.status_code}")
        print(f"   {response.text}")
        return False
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ 로그인 성공")
    
    # 2. 이벤트 목록 조회
    print("\n2. 이벤트 목록 조회...")
    response = requests.get(f"{API_URL}/api/v1/events", headers=headers)
    if response.status_code != 200:
        print(f"❌ 이벤트 목록 조회 실패: {response.status_code}")
        return False
    
    events = response.json()
    if not events:
        print("⚠️  이벤트가 없습니다. 먼저 이벤트를 생성하세요.")
        return False
    
    # 승인된 이벤트 찾기
    approved_event = None
    for event in events:
        if event.get("status") == "approved":
            approved_event = event
            break
    
    if not approved_event:
        print("⚠️  승인된 이벤트가 없습니다.")
        return False
    
    print(f"✅ 이벤트 찾음: {approved_event['name']} (ID: {approved_event['id']})")
    
    # 3. 티켓 구매 (UserOperation 사용)
    print("\n3. 티켓 구매 (UserOperation)...")
    purchase_data = {
        "event_id": approved_event["id"]
    }
    
    response = requests.post(
        f"{API_URL}/api/v1/tickets/purchase",
        json=purchase_data,
        headers=headers
    )
    
    if response.status_code != 201:
        print(f"❌ 티켓 구매 실패: {response.status_code}")
        print(f"   {response.text}")
        return False
    
    ticket = response.json()
    print("✅ 티켓 구매 성공!")
    print(f"   Ticket ID: {ticket['id']}")
    print(f"   Token ID: {ticket.get('token_id', 'N/A')}")
    print(f"   Transaction Hash: {ticket.get('purchase_tx_hash', 'N/A')}")
    
    return True

if __name__ == "__main__":
    try:
        success = test_user_operation_purchase()
        if success:
            print("\n" + "=" * 60)
            print("✅ 테스트 성공!")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ 테스트 실패")
            print("=" * 60)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

