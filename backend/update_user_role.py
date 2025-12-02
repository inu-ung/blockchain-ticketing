#!/usr/bin/env python3
"""
사용자 역할 변경 스크립트
"""
import sys
from app.db.database import SessionLocal
from app.models.user import User, UserRole

def update_user_role(email: str, role: str):
    """사용자 역할 변경"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"❌ 사용자를 찾을 수 없습니다: {email}")
            return False
        
        # 역할 문자열을 UserRole enum으로 변환
        role_map = {
            'admin': UserRole.ADMIN,
            'organizer': UserRole.ORGANIZER,
            'buyer': UserRole.BUYER,
        }
        
        if role.lower() not in role_map:
            print(f"❌ 유효하지 않은 역할: {role}")
            print(f"   사용 가능한 역할: {', '.join(role_map.keys())}")
            return False
        
        old_role = user.role
        user.role = role_map[role.lower()]
        db.commit()
        
        print(f"✅ 역할 변경 완료:")
        print(f"   이메일: {email}")
        print(f"   이전 역할: {old_role.value}")
        print(f"   새 역할: {user.role.value}")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ 오류 발생: {e}")
        return False
    finally:
        db.close()

def list_users():
    """모든 사용자 목록 조회"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("\n" + "=" * 60)
        print("사용자 목록")
        print("=" * 60)
        for user in users:
            print(f"  {user.email:30} | {user.role.value:10} | {user.wallet_address or 'N/A'}")
        print("=" * 60 + "\n")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법:")
        print("  python update_user_role.py <email> <role>")
        print("  python update_user_role.py list  # 사용자 목록 조회")
        print("\n예시:")
        print("  python update_user_role.py organizer@test.com organizer")
        print("  python update_user_role.py admin@test.com admin")
        print("  python update_user_role.py buyer@test.com buyer")
        print("\n사용 가능한 역할: admin, organizer, buyer")
        sys.exit(1)
    
    if sys.argv[1] == "list":
        list_users()
    else:
        email = sys.argv[1]
        role = sys.argv[2]
        update_user_role(email, role)

