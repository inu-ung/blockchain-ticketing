# EC2 데이터베이스 연결 오류 해결

## 🔴 문제

```
connection to server at "localhost" (::1), port 5432 failed: Connection refused
```

**원인**: DATABASE_URL이 `localhost`를 사용하고 있음

## ✅ 해결 방법

### Docker Compose에서는 서비스 이름 사용!

Docker Compose 네트워크에서는 `localhost` 대신 **서비스 이름**을 사용해야 합니다.

---

## 📝 .env 파일 수정

### 1. EC2에서 .env 파일 열기

```bash
cd ~/backend
nano .env
```

### 2. DATABASE_URL 수정

**현재 (잘못된 형식):**
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/ticketing
```

**수정 (올바른 형식):**
```env
DATABASE_URL=postgresql://postgres:password@postgres:5432/ticketing
                                                    ^^^^^^^^
                                                    서비스 이름!
```

**중요**: `localhost` → `postgres` (docker-compose.prod.yml의 서비스 이름)

---

## 🔧 전체 .env 파일 예시

```env
# Database (Docker 서비스 이름 사용!)
DATABASE_URL=postgresql://postgres:your-password@postgres:5432/ticketing
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-strong-password
POSTGRES_DB=ticketing

# JWT
SECRET_KEY=your-secret-key-here

# Web3 (Amoy 테스트넷)
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
POLYGON_MAINNET_RPC_URL=https://polygon-rpc.com
PRIVATE_KEY=your-private-key

# Contract Addresses
TICKET_ACCESS_CONTROL_ADDRESS=0x...
TICKET_NFT_ADDRESS=0x...
EVENT_MANAGER_ADDRESS=0x...
MARKETPLACE_ADDRESS=0x...
REFUND_MANAGER_ADDRESS=0x...
SMART_WALLET_FACTORY_ADDRESS=0x...
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789

# IPFS
PINATA_API_KEY=your-key
PINATA_SECRET_KEY=your-secret

# CORS
ALLOWED_ORIGINS=http://localhost:5173
```

---

## 🚀 수정 후 재시작

### 방법 1: 백엔드만 재시작

```bash
docker-compose -f docker-compose.prod.yml restart backend
```

### 방법 2: 완전 재시작

```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### 방법 3: 로그 확인

```bash
docker-compose -f docker-compose.prod.yml logs -f backend
```

---

## ✅ 확인

### 1. 컨테이너 상태

```bash
docker-compose -f docker-compose.prod.yml ps
```

모든 컨테이너가 "Up" 상태여야 함

### 2. 헬스 체크

```bash
curl http://localhost:8000/health
```

응답: `{"status":"healthy"}`

### 3. 데이터베이스 연결 확인

```bash
docker exec -it ticketing-backend python -c "from app.db.database import engine; print('DB Connected!' if engine.connect() else 'Failed')"
```

---

## 🔍 추가 문제 해결

### Web3 연결 오류도 함께 발생

로그에 다음도 보임:
```
Web3 connection failed to http://127.0.0.1:8545
```

**해결**: `.env` 파일에 RPC URL 설정

```env
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
```

또는

```env
POLYGON_MUMBAI_RPC_URL=https://polygon-mumbai-bor.publicnode.com
```

---

## 📝 요약

1. ✅ `.env` 파일에서 `DATABASE_URL` 수정
   - `localhost` → `postgres` (서비스 이름)
2. ✅ RPC URL 설정 확인
3. ✅ 컨테이너 재시작
4. ✅ 로그 확인

---

## 🎯 완료!

이제 백엔드가 정상적으로 실행될 것입니다!

