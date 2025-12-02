# PostgreSQL 설정 완료

## Docker 컨테이너 실행

PostgreSQL이 Docker로 실행 중입니다.

### 컨테이너 관리

```bash
# 컨테이너 시작
docker-compose up -d

# 컨테이너 중지
docker-compose down

# 컨테이너 상태 확인
docker ps | grep ticketing-postgres

# 로그 확인
docker logs ticketing-postgres
```

## SQLTools 연결 설정

이미지에서 보이는 SQLTools에서 다음 정보를 입력하세요:

- **Connection name**: `Ticketing DB` (원하는 이름)
- **Connection group**: (선택사항)
- **Connect using**: `Server and Port`
- **Server Address**: `localhost`
- **Port**: `5432`
- **Database**: `ticketing`
- **Username**: `postgres`
- **Use password**: `SQLTools Driver Credentials` 선택
- **Password**: `postgres`

## 데이터베이스 접속 확인

### psql로 직접 접속

```bash
docker exec -it ticketing-postgres psql -U postgres -d ticketing
```

psql 프롬프트에서:
```sql
-- 테이블 목록
\dt

-- 사용자 조회
SELECT * FROM users;

-- 이벤트 조회
SELECT * FROM events;

-- 종료
\q
```

### Python으로 확인

```bash
cd backend
source venv/bin/activate
python -c "from app.db.database import engine; from sqlalchemy import text; with engine.connect() as conn: result = conn.execute(text('SELECT COUNT(*) FROM users')); print('Users:', result.scalar())"
```

## 데이터베이스 정보

- **호스트**: localhost
- **포트**: 5432
- **데이터베이스명**: ticketing
- **사용자명**: postgres
- **비밀번호**: postgres
- **연결 문자열**: `postgresql://postgres:postgres@localhost:5432/ticketing`

## 주의사항

- Docker 컨테이너를 중지하면 데이터는 볼륨에 저장되어 유지됩니다
- 데이터를 완전히 삭제하려면: `docker-compose down -v`
- 프로덕션 환경에서는 비밀번호를 변경하세요

