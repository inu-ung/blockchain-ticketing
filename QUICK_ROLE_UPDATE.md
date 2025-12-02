# 역할 변경 빠른 가이드

## PostgreSQL에서 역할 변경

### 1. PostgreSQL 접속
```bash
docker exec -it ticketing-postgres psql -U postgres -d ticketing
```

### 2. Enum 값 확인
```sql
SELECT unnest(enum_range(NULL::userrole));
```

### 3. 역할 변경 (올바른 방법)
```sql
-- 주최자로 변경
UPDATE users SET role = 'organizer'::userrole WHERE email = 'organizer@test.com';

-- 관리자로 변경
UPDATE users SET role = 'admin'::userrole WHERE email = 'admin@test.com';

-- 구매자로 변경
UPDATE users SET role = 'buyer'::userrole WHERE email = 'buyer@test.com';
```

### 4. 확인
```sql
SELECT email, role FROM users;
```

## 또는 Python 스크립트 사용

```bash
cd backend
source venv/bin/activate
python << 'PYEOF'
from app.db.database import SessionLocal
from app.models.user import User, UserRole

db = SessionLocal()
try:
    user = db.query(User).filter(User.email == 'organizer@test.com').first()
    if user:
        user.role = UserRole.ORGANIZER
        db.commit()
        print(f"✅ 역할 변경 완료: {user.email} -> {user.role}")
    else:
        print("❌ 사용자를 찾을 수 없습니다")
finally:
    db.close()
PYEOF
```

