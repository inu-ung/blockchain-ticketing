# 헬스 체크 실패 문제 해결

## 🔍 즉시 확인할 사항

### 1. 컨테이너가 실제로 실행 중인지 확인

```bash
# 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps

# Docker 컨테이너 전체 확인
docker ps -a
```

**예상 결과:**
- `ticketing-backend` 컨테이너가 "Up" 상태여야 함
- "Exit" 상태라면 문제 있음

---

### 2. 백엔드 로그 확인 (가장 중요!)

```bash
# 전체 로그
docker-compose -f docker-compose.prod.yml logs backend

# 최근 100줄
docker-compose -f docker-compose.prod.yml logs --tail=100 backend

# 실시간 로그
docker-compose -f docker-compose.prod.yml logs -f backend
```

**확인할 에러:**
- 데이터베이스 연결 오류
- 모듈 import 오류
- 포트 바인딩 오류
- 환경 변수 누락

---

### 3. 수동 헬스 체크

```bash
# 컨테이너 내부에서 직접 확인
docker exec -it ticketing-backend curl http://localhost:8000/health

# 또는 컨테이너 IP 확인
docker inspect ticketing-backend | grep IPAddress
```

---

## 🚨 일반적인 원인 및 해결

### 원인 1: 데이터베이스 연결 실패

**증상:**
- 로그에 "Connection refused" 또는 "database" 관련 오류

**확인:**
```bash
# PostgreSQL 컨테이너 확인
docker-compose -f docker-compose.prod.yml ps postgres

# PostgreSQL 로그
docker-compose -f docker-compose.prod.yml logs postgres
```

**해결:**
```bash
# .env 파일의 DATABASE_URL 확인
cat .env | grep DATABASE_URL

# 올바른 형식: postgresql://postgres:password@postgres:5432/ticketing
# 잘못된 형식: sqlite:///./ticketing.db
```

---

### 원인 2: 컨테이너가 시작되지 않음

**확인:**
```bash
docker-compose -f docker-compose.prod.yml ps
```

**해결:**
```bash
# 컨테이너 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 로그 확인
docker-compose -f docker-compose.prod.yml logs backend
```

---

### 원인 3: 포트 바인딩 실패

**확인:**
```bash
# 포트 사용 확인
sudo lsof -i :8000

# 네트워크 확인
docker network ls
docker network inspect backend_ticketing-network
```

**해결:**
```bash
# 포트를 사용하는 프로세스 종료
sudo kill -9 <PID>

# 완전 재시작
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

---

### 원인 4: 애플리케이션 시작 실패

**확인:**
```bash
# 컨테이너 내부 접속
docker exec -it ticketing-backend /bin/bash

# 수동 실행
cd /app
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

**에러 메시지 확인**

---

### 원인 5: 환경 변수 문제

**확인:**
```bash
# 컨테이너 내부 환경 변수 확인
docker exec -it ticketing-backend env | grep -E "DATABASE|SECRET|PRIVATE"

# .env 파일 확인
cat .env
```

**해결:**
- 필수 환경 변수가 모두 설정되어 있는지 확인
- 값이 비어있지 않은지 확인

---

## 🔧 단계별 디버깅

### Step 1: 컨테이너 상태 확인

```bash
docker-compose -f docker-compose.prod.yml ps
```

### Step 2: 로그 확인

```bash
docker-compose -f docker-compose.prod.yml logs backend
```

### Step 3: 수동 테스트

```bash
# 컨테이너 내부 접속
docker exec -it ticketing-backend /bin/bash

# Python 확인
python --version

# 의존성 확인
pip list | grep fastapi

# 수동 실행
cd /app
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🚀 빠른 해결 방법

### 방법 1: 완전 재시작

```bash
# 모든 컨테이너 중지
docker-compose -f docker-compose.prod.yml down

# 재빌드 및 시작
docker-compose -f docker-compose.prod.yml up -d --build

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 방법 2: 로그 기반 해결

```bash
# 로그 확인
docker-compose -f docker-compose.prod.yml logs backend | tail -50

# 에러 메시지에 따라 해결
```

---

## 📝 체크리스트

- [ ] 컨테이너가 "Up" 상태인가?
- [ ] PostgreSQL 컨테이너가 실행 중인가?
- [ ] 로그에 에러 메시지가 있는가?
- [ ] DATABASE_URL이 올바른가?
- [ ] 포트 8000이 사용 가능한가?
- [ ] 환경 변수가 모두 설정되어 있는가?

---

## 💡 다음 단계

1. **로그 확인**: `docker-compose -f docker-compose.prod.yml logs backend`
2. **에러 메시지 확인**
3. **에러 메시지를 알려주시면 정확한 해결 방법 제시**

