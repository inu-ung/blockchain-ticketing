# 백엔드 배포 빠른 시작 가이드

## 📋 배포 방법 선택

### 방법 1: EC2에 직접 배포 (권장)

EC2 인스턴스가 준비되어 있다면:

1. **EC2 인스턴스 접속**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

2. **프로젝트 클론**
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo/backend
   ```

3. **환경 변수 설정**
   ```bash
   cp .env.production.example .env
   nano .env  # 실제 값으로 수정
   ```

4. **배포 실행**
   ```bash
   ./deploy.sh
   ```

자세한 내용은 `EC2_DEPLOYMENT_GUIDE.md` 참고

---

### 방법 2: 로컬에서 Docker 테스트

EC2 배포 전 로컬에서 먼저 테스트:

```bash
cd backend

# 환경 변수 설정
cp .env.production.example .env
# .env 파일 편집하여 실제 값 입력

# Docker 이미지 빌드 및 실행
docker-compose -f docker-compose.prod.yml up -d --build

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f

# 헬스 체크
curl http://localhost:8000/health
```

---

## 🔧 필수 환경 변수 설정

### 1. 데이터베이스

```env
DATABASE_URL=postgresql://postgres:password@postgres:5432/ticketing
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-strong-password
POSTGRES_DB=ticketing
```

### 2. JWT 시크릿 키

```env
SECRET_KEY=your-very-secret-key-here
```

**생성 방법:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Web3 설정

```env
# Amoy 테스트넷 사용 시
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
PRIVATE_KEY=your-private-key

# 또는 메인넷
POLYGON_MAINNET_RPC_URL=https://polygon-rpc.com
PRIVATE_KEY=your-private-key
```

### 4. 컨트랙트 주소

테스트넷/메인넷에 배포된 컨트랙트 주소:

```env
TICKET_ACCESS_CONTROL_ADDRESS=0x...
TICKET_NFT_ADDRESS=0x...
EVENT_MANAGER_ADDRESS=0x...
MARKETPLACE_ADDRESS=0x...
REFUND_MANAGER_ADDRESS=0x...
SMART_WALLET_FACTORY_ADDRESS=0x...
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

### 5. CORS 설정

프론트엔드 URL (Vercel 배포 후 업데이트):

```env
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
```

---

## ✅ 배포 확인

### 1. 헬스 체크

```bash
curl http://your-ec2-ip:8000/health
```

응답:
```json
{"status":"healthy"}
```

### 2. API 문서

브라우저에서 접속:
```
http://your-ec2-ip:8000/docs
```

### 3. 로그 확인

```bash
docker-compose -f docker-compose.prod.yml logs -f backend
```

---

## 🚨 문제 해결

### 포트가 이미 사용 중

```bash
# 포트 사용 중인 프로세스 확인
sudo lsof -i :8000

# 프로세스 종료
sudo kill -9 <PID>
```

### 데이터베이스 연결 오류

```bash
# PostgreSQL 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps postgres

# PostgreSQL 로그 확인
docker-compose -f docker-compose.prod.yml logs postgres
```

### 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker-compose -f docker-compose.prod.yml logs backend

# 컨테이너 재시작
docker-compose -f docker-compose.prod.yml restart backend
```

---

## 📝 다음 단계

1. ✅ 백엔드 배포 완료
2. ⏳ 프론트엔드 배포 (Vercel)
3. ⏳ 환경 변수 연결 확인
4. ⏳ 전체 시스템 테스트

---

## 🔗 관련 문서

- **EC2 배포 가이드**: `EC2_DEPLOYMENT_GUIDE.md`
- **프로덕션 배포 가이드**: `PRODUCTION_DEPLOYMENT_GUIDE.md`

