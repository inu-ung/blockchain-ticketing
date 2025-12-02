"""
샘플 이벤트 데이터 추가 스크립트
실제 의미 있는 콘서트 데이터를 DB에 추가합니다.
"""
import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.event import Event, EventStatus
from app.models.user import User
from datetime import datetime, timedelta
from web3 import Web3
import uuid

# 샘플 이벤트 데이터
SAMPLE_EVENTS = [
    {
        "name": "BIGBANG 2024 WORLD TOUR - SEOUL",
        "description": "빅뱅의 전 세계 투어 서울 공연! 10년 만의 완전체 컴백 콘서트입니다. 최고의 무대와 음악을 경험하세요.",
        "price_wei": int(Web3.to_wei(150, 'ether')),  # 150 USDC
        "max_tickets": 5000,
        "event_date": datetime(2024, 8, 15, 19, 0),  # 2024년 8월 15일 오후 7시
        "start_time": datetime(2024, 7, 1, 0, 0),  # 7월 1일부터 판매 시작
        "end_time": datetime(2024, 8, 10, 23, 59),  # 8월 10일까지 판매
    },
    {
        "name": "BLACKPINK BORN PINK WORLD TOUR - SEOUL",
        "description": "블랙핑크의 전 세계 투어 서울 공연! 화려한 퍼포먼스와 최신 히트곡들을 만나보세요.",
        "price_wei": int(Web3.to_wei(180, 'ether')),  # 180 USDC
        "max_tickets": 8000,
        "event_date": datetime(2024, 9, 20, 18, 30),
        "start_time": datetime(2024, 8, 1, 0, 0),
        "end_time": datetime(2024, 9, 15, 23, 59),
    },
    {
        "name": "BTS SUGA | Agust D TOUR - SEOUL",
        "description": "BTS 슈가의 솔로 투어 서울 공연! Agust D의 독특한 음악 세계를 경험하세요.",
        "price_wei": int(Web3.to_wei(200, 'ether')),  # 200 USDC
        "max_tickets": 3000,
        "event_date": datetime(2024, 10, 5, 19, 30),
        "start_time": datetime(2024, 9, 1, 0, 0),
        "end_time": datetime(2024, 9, 30, 23, 59),
    },
    {
        "name": "IU 2024 CONCERT - THE GOLDEN HOUR",
        "description": "아이유의 황금빛 무대! 감동적인 보컬과 따뜻한 무대 매너를 선사합니다.",
        "price_wei": int(Web3.to_wei(120, 'ether')),  # 120 USDC
        "max_tickets": 6000,
        "event_date": datetime(2024, 11, 10, 19, 0),
        "start_time": datetime(2024, 10, 1, 0, 0),
        "end_time": datetime(2024, 11, 5, 23, 59),
    },
    {
        "name": "NewJeans 2024 FAN MEETING - SEOUL",
        "description": "뉴진스의 첫 번째 팬미팅! 특별한 무대와 팬들과의 소통 시간을 가집니다.",
        "price_wei": int(Web3.to_wei(100, 'ether')),  # 100 USDC
        "max_tickets": 4000,
        "event_date": datetime(2024, 12, 25, 18, 0),
        "start_time": datetime(2024, 11, 1, 0, 0),
        "end_time": datetime(2024, 12, 20, 23, 59),
    },
]


def add_sample_events():
    """샘플 이벤트 데이터를 DB에 추가"""
    db: Session = SessionLocal()
    
    try:
        # 관리자 또는 주최자 계정 찾기 (없으면 첫 번째 사용자 사용)
        organizer = db.query(User).filter(
            (User.role == "organizer") | (User.role == "admin")
        ).first()
        
        if not organizer:
            # 일반 사용자 중 첫 번째 사용자 사용
            organizer = db.query(User).first()
            if not organizer:
                print("❌ 사용자가 없습니다. 먼저 회원가입을 해주세요.")
                return
        
        print(f"✅ 주최자로 사용: {organizer.email} (ID: {organizer.id})")
        
        added_count = 0
        for event_data in SAMPLE_EVENTS:
            # 이미 같은 이름의 이벤트가 있는지 확인
            existing = db.query(Event).filter(Event.name == event_data["name"]).first()
            if existing:
                print(f"⏭️  이미 존재하는 이벤트: {event_data['name']}")
                continue
            
            # IPFS 해시 생성 (실제로는 IPFS에 업로드해야 하지만, 여기서는 임시 해시 사용)
            ipfs_hash = f"QmSample{uuid.uuid4().hex[:16]}"
            
            # 이벤트 생성
            event = Event(
                organizer_id=organizer.id,
                name=event_data["name"],
                description=event_data["description"],
                ipfs_hash=ipfs_hash,
                price_wei=event_data["price_wei"],
                max_tickets=event_data["max_tickets"],
                sold_tickets=0,
                start_time=event_data["start_time"],
                end_time=event_data["end_time"],
                event_date=event_data["event_date"],
                status=EventStatus.APPROVED  # 바로 승인 상태로 생성
            )
            
            db.add(event)
            added_count += 1
            print(f"✅ 이벤트 추가: {event_data['name']}")
        
        db.commit()
        print(f"\n🎉 총 {added_count}개의 샘플 이벤트가 추가되었습니다!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("샘플 이벤트 데이터 추가")
    print("=" * 60)
    add_sample_events()

