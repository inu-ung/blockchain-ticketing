#!/usr/bin/env python3
"""
IPFS 서비스 완전 테스트 스크립트
"""
import sys
from app.services.ipfs_service import ipfs_service
import json

def test_connection():
    """연결 테스트"""
    print("=" * 60)
    print("1️⃣  Pinata 연결 테스트")
    print("=" * 60)
    
    if not ipfs_service.is_configured:
        print("❌ API 키가 설정되지 않았습니다")
        print("\n💡 확인 사항:")
        print("   1. backend/.env 파일이 있는지")
        print("   2. PINATA_API_KEY와 PINATA_SECRET_KEY가 입력되었는지")
        print("   3. 서버를 재시작했는지")
        return False
    
    print(f"✅ API 키 설정됨: {ipfs_service.is_configured}")
    print("\n📡 Pinata 서버에 연결 중...")
    
    is_connected = ipfs_service.test_connection()
    
    if is_connected:
        print("✅ Pinata 연결 성공!")
        return True
    else:
        print("❌ Pinata 연결 실패")
        print("\n💡 확인 사항:")
        print("   1. API 키가 올바른지")
        print("   2. 인터넷 연결 확인")
        print("   3. Pinata 대시보드에서 키가 활성화되어 있는지")
        return False

def test_upload():
    """업로드 테스트"""
    print("\n" + "=" * 60)
    print("2️⃣  IPFS 업로드 테스트")
    print("=" * 60)
    
    test_data = {
        "name": "블록체인 티켓팅 테스트",
        "description": "IPFS 업로드 테스트용 데이터",
        "type": "test",
        "timestamp": "2024-12-01"
    }
    
    print("\n📝 업로드할 데이터:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    print("\n⬆️  IPFS에 업로드 중...")
    
    ipfs_hash = ipfs_service.upload_json(test_data)
    
    if not ipfs_hash:
        print("❌ 업로드 실패")
        return None
    
    print(f"✅ 업로드 성공!")
    print(f"   IPFS 해시: {ipfs_hash}")
    print(f"   IPFS URL: {ipfs_service.get_file_url(ipfs_hash)}")
    
    return ipfs_hash

def test_retrieve(ipfs_hash):
    """조회 테스트"""
    print("\n" + "=" * 60)
    print("3️⃣  IPFS 데이터 조회 테스트")
    print("=" * 60)
    
    print(f"\n📥 해시로 데이터 조회: {ipfs_hash}")
    print("   (IPFS 네트워크에 전파되는데 시간이 걸릴 수 있습니다)")
    
    retrieved_data = ipfs_service.get_json(ipfs_hash)
    
    if retrieved_data:
        print("✅ 조회 성공!")
        print("\n📄 조회된 데이터:")
        print(json.dumps(retrieved_data, indent=2, ensure_ascii=False))
        return True
    else:
        print("⚠️  조회 실패")
        print("\n💡 가능한 원인:")
        print("   1. IPFS 네트워크에 아직 전파되지 않음 (몇 분 기다려보세요)")
        print("   2. 게이트웨이 접근 문제")
        print("   3. 해시가 잘못됨")
        return False

def main():
    """메인 테스트"""
    print("\n🚀 IPFS 서비스 완전 테스트 시작\n")
    
    # 1. 연결 테스트
    if not test_connection():
        print("\n❌ 연결 테스트 실패. 다음 단계를 진행할 수 없습니다.")
        sys.exit(1)
    
    # 2. 업로드 테스트
    ipfs_hash = test_upload()
    if not ipfs_hash:
        print("\n❌ 업로드 테스트 실패")
        sys.exit(1)
    
    # 3. 조회 테스트
    success = test_retrieve(ipfs_hash)
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("=" * 60)
    print(f"✅ 연결 테스트: 성공")
    print(f"✅ 업로드 테스트: 성공 (해시: {ipfs_hash})")
    print(f"{'✅' if success else '⚠️ '} 조회 테스트: {'성공' if success else '실패 (일시적 문제일 수 있음)'}")
    
    if success:
        print("\n🎉 모든 테스트 통과!")
        print(f"\n📌 테스트 데이터 IPFS URL:")
        print(f"   {ipfs_service.get_file_url(ipfs_hash)}")
    else:
        print("\n⚠️  조회 테스트 실패했지만 업로드는 성공했습니다.")
        print("   몇 분 후 다시 조회해보세요.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()

