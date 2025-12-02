# EC2 배포 문제 해결 가이드

## 🔍 헬스 체크 실패 시 확인 사항

### 1. 로그 확인

```bash
# 백엔드 로그 확인
docker-compose -f docker-compose.prod.yml logs backend

# 최근 50줄만 보기
docker-compose -f docker-compose.prod.yml logs --tail=50 backend

# 실시간 로그 보기
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 2. 컨테이너 상태 확인

```bash
# 모든 컨테이너 상태
docker-compose -f docker-compose.prod.yml ps

# Docker 컨테이너 전체 확인
docker ps -a
```

### 3. 일반적인 문제 및 해결

#### 문제 1: 컨테이너가 시작되지 않음

**확인:**
```bash
docker-compose -f docker-compose.prod.yml ps
```

**해결:**
```bash
# 로그 확인
docker-compose -f docker-compose.prod.yml logs backend

# 컨테이너 재시작
docker-compose -f docker-compose.prod.yml restart backend
```

#### 문제 2: 데이터베이스 연결 오류

**확인:**
```bash
# PostgreSQL 컨테이너 상태
docker-compose -f docker-compose.prod.yml ps postgres

# PostgreSQL 로그
docker-compose -f docker-compose.prod.yml logs postgres
```

**해결:**
```bash
# .env 파일의 DATABASE_URL 확인
cat .env | grep DATABASE_URL

# 올바른 형식: postgresql://postgres:password@postgres:5432/ticketing
```

#### 문제 3: 포트 충돌

**확인:**
```bash
sudo lsof -i :8000
```

**해결:**
```bash
# 프로세스 종료
sudo kill -9 <PID>

# 또는 docker-compose 재시작
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

#### 문제 4: 환경 변수 누락

**확인:**
```bash
# .env 파일 확인
cat .env

# 필수 환경 변수 확인
grep -E "DATABASE_URL|SECRET_KEY|PRIVATE_KEY" .env
```

**해결:**
- `.env` 파일에 필수 환경 변수가 모두 있는지 확인
- 값이 비어있지 않은지 확인

#### 문제 5: Docker 이미지 빌드 실패

**확인:**
```bash
# 빌드 로그 확인
docker-compose -f docker-compose.prod.yml build --no-cache

# 에러 메시지 확인
```

**해결:**
```bash
# 캐시 없이 재빌드
docker-compose -f docker-compose.prod.yml build --no-cache

# 다시 시작
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🔧 단계별 디버깅

### Step 1: 컨테이너 상태 확인

```bash
docker-compose -f docker-compose.prod.yml ps
```

**정상 상태:**
```
NAME                  STATUS
ticketing-backend    Up X seconds
ticketing-postgres   Up X seconds
```

**문제 상태:**
```
NAME                  STATUS
ticketing-backend    Exit 1
ticketing-postgres   Up X seconds
```

### Step 2: 로그 확인

```bash
# 백엔드 로그
docker-compose -f docker-compose.prod.yml logs backend

# PostgreSQL 로그
docker-compose -f docker-compose.prod.yml logs postgres
```

### Step 3: 컨테이너 내부 접속

```bash
# 백엔드 컨테이너 접속
docker exec -it ticketing-backend /bin/bash

# 환경 변수 확인
env | grep -E "DATABASE|SECRET|PRIVATE"

# Python 확인
python --version
```

### Step 4: 수동 실행 테스트

```bash
# 컨테이너 내부에서
docker exec -it ticketing-backend /bin/bash

# 수동으로 서버 실행
cd /app
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## 🚨 자주 발생하는 에러

### 에러 1: "Connection refused" (데이터베이스)

**원인**: PostgreSQL 컨테이너가 시작되지 않음

**해결:**
```bash
# PostgreSQL 재시작
docker-compose -f docker-compose.prod.yml restart postgres

# 연결 확인
docker exec -it ticketing-postgres psql -U postgres -c "SELECT 1;"
```

### 에러 2: "ModuleNotFoundError"

**원인**: requirements.txt 패키지 설치 실패

**해결:**
```bash
# 이미지 재빌드
docker-compose -f docker-compose.prod.yml build --no-cache backend

# 재시작
docker-compose -f docker-compose.prod.yml up -d backend
```

### 에러 3: "Address already in use"

**원인**: 포트 8000이 이미 사용 중

**해결:**
```bash
# 포트 사용 확인
sudo lsof -i :8000

# 프로세스 종료
sudo kill -9 <PID>
```

### 에러 4: "Invalid DATABASE_URL"

**원인**: DATABASE_URL 형식 오류

**확인:**
```bash
cat .env | grep DATABASE_URL
```

**올바른 형식:**
```
DATABASE_URL=postgresql://postgres:password@postgres:5432/ticketing
```

---

## ✅ 정상 작동 확인

### 1. 컨테이너 실행 확인

```bash
docker-compose -f docker-compose.prod.yml ps
```

모든 컨테이너가 "Up" 상태여야 합니다.

### 2. 로그 확인

```bash
docker-compose -f docker-compose.prod.yml logs backend | tail -20
```

에러 메시지가 없어야 합니다.

### 3. 헬스 체크

```bash
# 로컬에서
curl http://localhost:8000/health

# 외부에서 (EC2 퍼블릭 IP)
curl http://your-ec2-ip:8000/health
```

응답: `{"status":"healthy"}`

---

## 📝 체크리스트

- [ ] Docker 및 Docker Compose 설치 확인
- [ ] .env 파일 존재 및 내용 확인
- [ ] DATABASE_URL 형식 확인
- [ ] SECRET_KEY 설정 확인
- [ ] 컨테이너 상태 확인
- [ ] 로그에서 에러 메시지 확인
- [ ] 포트 충돌 확인
- [ ] 네트워크 연결 확인

---

## 🔄 완전 재시작

문제가 계속되면 완전히 재시작:

```bash
# 모든 컨테이너 중지 및 제거
docker-compose -f docker-compose.prod.yml down

# 볼륨도 삭제하려면 (데이터 삭제됨!)
docker-compose -f docker-compose.prod.yml down -v

# 재빌드 및 시작
docker-compose -f docker-compose.prod.yml up -d --build

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f
```

