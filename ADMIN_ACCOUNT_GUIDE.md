# 관리자 계정 생성 및 테스트 가이드

## 관리자 계정 정보

- **이메일**: `admin@test.com`
- **비밀번호**: `test123`
- **역할**: `admin`

## 로그인 방법

1. 프론트엔드 접속: http://localhost:5173/login
2. 이메일/비밀번호 입력
3. 로그인 클릭

## 관리자 기능 확인

### 1. 관리자 메뉴 표시
- 로그인 후 상단 메뉴에 **"관리자"** 메뉴가 표시되는지 확인
- 주최자(organizer)나 구매자(buyer)에게는 표시되지 않음

### 2. 관리자 페이지 접속
- "관리자" 메뉴 클릭
- 또는 직접 접속: http://localhost:5173/admin

### 3. 관리자 기능
- **이벤트 승인**: 대기 중인 이벤트 목록 확인 및 승인
- **이벤트 관리**: 모든 이벤트 조회 및 관리

## 테스트 시나리오

### 시나리오 1: 이벤트 승인 플로우

1. **주최자로 이벤트 생성**
   - `organizer@test.com`으로 로그인
   - "이벤트 생성" 메뉴에서 이벤트 생성
   - 상태: "대기 중"

2. **관리자로 이벤트 승인**
   - 로그아웃
   - `admin@test.com`으로 로그인
   - "관리자" 메뉴 클릭
   - 대기 중인 이벤트 확인
   - "승인" 버튼 클릭
   - ✅ 이벤트 상태가 "승인됨"으로 변경

3. **구매자로 티켓 구매**
   - 로그아웃
   - `buyer@test.com`으로 로그인
   - "이벤트" 메뉴에서 승인된 이벤트 확인
   - 티켓 구매

## 역할 변경 방법

### Python 스크립트 사용 (추천)

```bash
cd backend
source venv/bin/activate

# 관리자로 변경
python update_user_role.py admin@test.com admin

# 주최자로 변경
python update_user_role.py organizer@test.com organizer

# 구매자로 변경
python update_user_role.py buyer@test.com buyer

# 사용자 목록 확인
python update_user_role.py list
```

### PostgreSQL 직접 사용

```bash
docker exec -it ticketing-postgres psql -U postgres -d ticketing
```

```sql
-- 역할 변경
UPDATE users SET role = 'admin'::userrole WHERE email = 'admin@test.com';

-- 확인
SELECT email, role FROM users;
```

## 역할별 메뉴 비교

| 역할 | 이벤트 | 마켓플레이스 | 내 티켓 | 이벤트 생성 | 관리자 |
|------|--------|--------------|---------|------------|--------|
| buyer | ✅ | ✅ | ✅ | ❌ | ❌ |
| organizer | ✅ | ✅ | ✅ | ✅ | ❌ |
| admin | ✅ | ✅ | ✅ | ❌ | ✅ |

## 문제 해결

### 관리자 메뉴가 안 보여요
- 역할이 제대로 설정되었는지 확인:
  ```bash
  python update_user_role.py list
  ```
- 새로고침 후 다시 확인
- 로그아웃 후 다시 로그인

### 이벤트 승인 버튼이 안 보여요
- 관리자 권한 확인
- 이벤트가 "대기 중" 상태인지 확인
- 브라우저 콘솔에서 에러 확인 (F12)

