# 데이터베이스 접속 가이드

## 현재 설정

프로젝트는 현재 **SQLite**를 사용하고 있습니다.
- 데이터베이스 파일: `backend/ticketing.db`
- 연결 문자열: `sqlite:///./ticketing.db`

## SQLite 데이터베이스 확인 방법

### 1. 터미널에서 직접 확인

```bash
cd backend
sqlite3 ticketing.db
```

SQLite 프롬프트에서:
```sql
-- 테이블 목록 확인
.tables

-- 사용자 테이블 조회
SELECT * FROM users;

-- 이벤트 테이블 조회
SELECT * FROM events;

-- 티켓 테이블 조회
SELECT * FROM tickets;

-- 종료
.quit
```

### 2. SQLite 브라우저 도구 사용

#### DB Browser for SQLite (무료)
- 다운로드: https://sqlitebrowser.org/
- 설치 후 `backend/ticketing.db` 파일 열기

#### VS Code 확장 프로그램
- "SQLite Viewer" 또는 "SQLite" 확장 설치
- `ticketing.db` 파일을 VS Code에서 열기

### 3. Python 스크립트로 확인

```python
import sqlite3

conn = sqlite3.connect('backend/ticketing.db')
cursor = conn.cursor()

# 테이블 목록
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())

# 사용자 조회
cursor.execute("SELECT * FROM users;")
print("Users:", cursor.fetchall())

conn.close()
```

## PostgreSQL로 전환하기

이미지에서 보이는 것처럼 PostgreSQL을 사용하고 싶다면:

### 1. PostgreSQL 설치

```bash
# macOS
brew install postgresql@14
brew services start postgresql@14

# 또는 Docker 사용
docker run --name postgres-ticketing \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=ticketing \
  -p 5432:5432 \
  -d postgres:14
```

### 2. 데이터베이스 생성

```bash
# PostgreSQL 접속
psql -U postgres

# 데이터베이스 생성
CREATE DATABASE ticketing;
\q
```

### 3. .env 파일 수정

`backend/.env` 파일에 추가:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ticketing
```

### 4. 마이그레이션 실행

```bash
cd backend
source venv/bin/activate

# Alembic 마이그레이션 (아직 설정되지 않았다면)
alembic upgrade head
```

### 5. SQLTools 연결 설정

이미지에서 보이는 SQLTools에서:

- **Connection name**: `Ticketing DB`
- **Server Address**: `localhost`
- **Port**: `5432`
- **Database**: `ticketing`
- **Username**: `postgres`
- **Password**: `postgres` (설정한 비밀번호)

## 현재 데이터베이스 스키마

### 주요 테이블

1. **users** - 사용자 정보
   - id, email, hashed_password, wallet_address, role, kyc_verified

2. **events** - 이벤트 정보
   - id, organizer_id, name, description, ipfs_hash, price_wei, max_tickets, sold_tickets

3. **tickets** - 티켓 정보
   - id, token_id, event_id, owner_address, ipfs_hash, status

4. **resales** - 재판매 정보
   - id, ticket_id, token_id, seller_address, price_wei, status

5. **refund_requests** - 환불 요청
   - id, ticket_id, user_id, reason, status, refund_amount_wei

6. **transactions** - 트랜잭션 기록
   - id, user_id, ticket_id, tx_hash, amount_wei, type

## 빠른 데이터 확인

```bash
# 사용자 수 확인
sqlite3 backend/ticketing.db "SELECT COUNT(*) FROM users;"

# 이벤트 목록
sqlite3 backend/ticketing.db "SELECT id, name, status FROM events;"

# 티켓 목록
sqlite3 backend/ticketing.db "SELECT id, token_id, owner_address FROM tickets;"
```

