#!/usr/bin/env python3
"""
IPFS 서비스 테스트 스크립트
"""

import sys
import os

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ipfs_service import ipfs_service
import json


def test_connection():
    """Pinata 연결 테스트"""
    print("=" * 50)
    print("1. Pinata 연결 테스트")
    print("=" * 50)
    
    is_connected = ipfs_service.test_connection()
    if is_connected:
        print("✅ Pinata 연결 성공!")
    else:
        print("❌ Pinata 연결 실패")
        print("   .env 파일에 PINATA_API_KEY와 PINATA_SECRET_KEY를 설정해주세요.")
    print()
    return is_connected


def test_upload_json():
    """JSON 업로드 테스트"""
    print("=" * 50)
    print("2. JSON 업로드 테스트")
    print("=" * 50)
    
    test_data = {
        "name": "Test Ticket",
        "description": "This is a test ticket metadata",
        "attributes": [
            {"trait_type": "Event", "value": "Test Event"},
            {"trait_type": "Date", "value": "2024-01-01"},
        ]
    }
    
    print(f"업로드할 데이터: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    print()
    
    ipfs_hash = ipfs_service.upload_json(test_data)
    
    if ipfs_hash:
        print(f"✅ 업로드 성공!")
        print(f"   IPFS Hash: {ipfs_hash}")
        print(f"   IPFS URL: ipfs://{ipfs_hash}")
        print(f"   Gateway URL: {ipfs_service.get_file_url(ipfs_hash)}")
        return ipfs_hash
    else:
        print("❌ 업로드 실패")
        return None


def test_get_json(ipfs_hash: str):
    """JSON 조회 테스트"""
    print("=" * 50)
    print("3. JSON 조회 테스트")
    print("=" * 50)
    
    print(f"조회할 IPFS Hash: {ipfs_hash}")
    print()
    
    data = ipfs_service.get_json(ipfs_hash)
    
    if data:
        print("✅ 조회 성공!")
        print(f"데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")
    else:
        print("❌ 조회 실패")
    print()


def main():
    """메인 테스트 함수"""
    print("\n" + "=" * 50)
    print("IPFS 서비스 테스트")
    print("=" * 50 + "\n")
    
    # 1. 연결 테스트
    if not test_connection():
        print("\n⚠️  Pinata 연결이 실패했습니다. 테스트를 계속 진행하지만 실제 업로드는 작동하지 않습니다.\n")
    
    # 2. JSON 업로드 테스트
    ipfs_hash = test_upload_json()
    
    # 3. JSON 조회 테스트
    if ipfs_hash:
        test_get_json(ipfs_hash)
    
    print("=" * 50)
    print("테스트 완료!")
    print("=" * 50)


if __name__ == "__main__":
    main()

