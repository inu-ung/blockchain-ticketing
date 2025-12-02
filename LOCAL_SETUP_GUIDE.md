# 로컬 환경 설정 가이드

로컬 Hardhat 네트워크에서 전체 시스템을 실행하는 방법

## 📋 목차
1. [사전 준비](#사전-준비)
2. [Hardhat 노드 실행](#hardhat-노드-실행)
3. [컨트랙트 배포](#컨트랙트-배포)
4. [백엔드 설정](#백엔드-설정)
5. [프론트엔드 설정](#프론트엔드-설정)
6. [서비스 실행](#서비스-실행)
7. [테스트](#테스트)

---

## 사전 준비

### 필요한 것들
- ✅ Node.js 18+
- ✅ Python 3.11+
- ✅ PostgreSQL 15+ (또는 Docker)
- ✅ npm 또는 yarn

### 디렉토리 구조 확인
```
BC/
├── contracts/          # 스마트 컨트랙트
├── backend/           # FastAPI 백엔드
├── frontend/          # React 프론트엔드
└── docker-compose.yml # PostgreSQL
```

---

## Hardhat 노드 실행

### 1. Hardhat 노드 시작

**터미널 1:**
```bash
cd contracts
npx hardhat node
```

성공 메시지:
```
Started HTTP and WebSocket server on http://127.0.0.1:8545/
```

**중요:** 이 터미널은 계속 실행 상태로 유지해야 합니다.

### 2. Hardhat 계정 확인

Hardhat 노드가 시작되면 20개의 테스트 계정이 생성됩니다:
- 첫 번째 계정: 서비스 계정 (백엔드에서 사용)
- 나머지 계정: 테스트용

각 계정에는 10,000 ETH가 있습니다.

---

## 컨트랙트 배포

### 1. 배포 스크립트 실행

**터미널 2:**
```bash
cd contracts
npm run deploy:all
# 또는
npx hardhat run scripts/deploy_all.js --network localhost
```

### 2. 배포 확인

배포가 완료되면 `deployments/localhost.json` 파일에 주소가 저장됩니다:

```bash
cat deployments/localhost.json
```

출력 예시:
```json
{
  "network": "localhost",
  "deployer": "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266",
  "entryPoint": "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789",
  "contracts": {
    "TicketAccessControl": "0x...",
    "TicketNFT": "0x...",
    "EventManager": "0x...",
    "TicketMarketplace": "0x...",
    "RefundManager": "0x...",
    "SmartWallet": "0x...",
    "SmartWalletFactory": "0x..."
  }
}
```

### 3. 배포 재개 (필요시)

만약 배포가 중간에 실패했다면:

```bash
npm run deploy:amoy:resume
# 로컬에서는 deploy_resume.js를 localhost용으로 수정 필요
```

---

## 백엔드 설정

### 1. 환경 변수 설정

`backend/.env` 파일을 생성/수정:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ticketing

# JWT
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Web3 (로컬 Hardhat)
POLYGON_MUMBAI_RPC_URL=http://127.0.0.1:8545
PRIVATE_KEY=ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
# ↑ Hardhat 첫 번째 계정의 개인키 (기본값)

# Contract Addresses (deployments/localhost.json에서 복사)
TICKET_ACCESS_CONTROL_ADDRESS=0x...
TICKET_NFT_ADDRESS=0x...
EVENT_MANAGER_ADDRESS=0x...
MARKETPLACE_ADDRESS=0x...
REFUND_MANAGER_ADDRESS=0x...

# Account Abstraction
SMART_WALLET_FACTORY_ADDRESS=0x...
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789

# IPFS (선택사항, Mock 모드 사용 가능)
PINATA_API_KEY=
PINATA_SECRET_KEY=

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 2. Hardhat 첫 번째 계정 개인키 확인

Hardhat 노드를 실행하면 첫 번째 계정의 개인키가 출력됩니다:
```
Account #0: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000 ETH)
Private Key: 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
```

이 개인키를 `PRIVATE_KEY`에 설정하세요.

### 3. 데이터베이스 설정

**PostgreSQL 실행:**
```bash
docker-compose up -d
```

**데이터베이스 확인:**
```bash
docker exec -it ticketing-postgres psql -U postgres -d ticketing
```

### 4. 백엔드 서버 실행

**터미널 3:**
```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn main:app --reload
```

성공 메시지:
```
Uvicorn running on http://127.0.0.1:8000
```

**헬스 체크:**
```bash
curl http://localhost:8000/health
# 응답: {"status":"healthy"}
```

---

## 프론트엔드 설정

### 1. 환경 변수 설정

`frontend/.env` 파일을 생성/수정:

```env
# API
VITE_API_URL=http://localhost:8000

# Web3 (로컬 Hardhat)
VITE_RPC_URL=http://127.0.0.1:8545
VITE_CHAIN_ID=1337

# Contract Addresses (deployments/localhost.json에서 복사)
VITE_TICKET_ACCESS_CONTROL_ADDRESS=0x...
VITE_TICKET_NFT_ADDRESS=0x...
VITE_EVENT_MANAGER_ADDRESS=0x...
VITE_MARKETPLACE_ADDRESS=0x...
VITE_REFUND_MANAGER_ADDRESS=0x...

# Account Abstraction
VITE_SMART_WALLET_FACTORY_ADDRESS=0x...
VITE_ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

### 2. 프론트엔드 서버 실행

**터미널 4:**
```bash
cd frontend
npm run dev
```

성공 메시지:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## 서비스 실행

### 전체 서비스 실행 순서

1. **터미널 1: Hardhat 노드**
   ```bash
   cd contracts
   npx hardhat node
   ```

2. **터미널 2: 컨트랙트 배포** (한 번만)
   ```bash
   cd contracts
   npm run deploy:all
   ```

3. **터미널 3: 백엔드 서버**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload
   ```

4. **터미널 4: 프론트엔드 서버**
   ```bash
   cd frontend
   npm run dev
   ```

5. **터미널 5: PostgreSQL** (Docker 사용 시)
   ```bash
   docker-compose up -d
   ```

### 서비스 확인

- **Hardhat 노드**: http://127.0.0.1:8545
- **백엔드 API**: http://localhost:8000
- **프론트엔드**: http://localhost:5173
- **API 문서**: http://localhost:8000/docs

---

## 테스트

### 1. 기본 기능 테스트

브라우저에서 http://localhost:5173 접속:

1. **회원가입/로그인**
   - 회원가입 페이지에서 계정 생성
   - 로그인 후 Smart Wallet 자동 연결 확인

2. **이벤트 생성** (주최자 계정)
   - 이벤트 생성 페이지 접속
   - 이벤트 정보 입력 및 생성
   - 관리자 계정으로 승인

3. **티켓 구매** (구매자 계정)
   - 이벤트 목록에서 이벤트 선택
   - 티켓 구매 버튼 클릭
   - 구매 완료 확인

4. **재판매**
   - 내 티켓 페이지에서 재판매 등록
   - 마켓플레이스에서 재판매 티켓 확인
   - 다른 계정으로 재판매 구매

5. **환불**
   - 환불 요청
   - 주최자 계정으로 환불 승인

### 2. 통합 테스트 실행

**터미널 6:**
```bash
cd backend
source venv/bin/activate
python test_integration.py
```

### 3. API 테스트

```bash
# 헬스 체크
curl http://localhost:8000/health

# 이벤트 목록
curl http://localhost:8000/api/v1/events

# 사용자 등록
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

---

## 문제 해결

### 1. Hardhat 노드 연결 실패

**문제:** 백엔드에서 Hardhat 노드에 연결할 수 없음

**해결:**
- Hardhat 노드가 실행 중인지 확인
- `POLYGON_MUMBAI_RPC_URL=http://127.0.0.1:8545` 확인
- 포트 8545가 사용 중인지 확인

### 2. 컨트랙트 주소 오류

**문제:** 컨트랙트 주소를 찾을 수 없음

**해결:**
- `deployments/localhost.json` 파일 확인
- 백엔드/프론트엔드 `.env` 파일에 주소 설정 확인
- 컨트랙트 재배포

### 3. 데이터베이스 연결 실패

**문제:** PostgreSQL 연결 오류

**해결:**
- Docker 컨테이너 실행 확인: `docker ps`
- 데이터베이스 URL 확인: `DATABASE_URL`
- PostgreSQL 재시작: `docker-compose restart`

### 4. 프론트엔드 연결 오류

**문제:** 프론트엔드에서 백엔드 API 호출 실패

**해결:**
- `VITE_API_URL=http://localhost:8000` 확인
- 백엔드 서버 실행 확인
- CORS 설정 확인

---

## 유용한 명령어

### Hardhat 노드 재시작
```bash
# 기존 노드 종료 후 재시작
npx hardhat node --reset
```

### 배포 정보 확인
```bash
cat contracts/deployments/localhost.json
```

### 로그 확인
```bash
# 백엔드 로그
tail -f backend/logs/app.log

# Hardhat 노드 로그
# 터미널에서 직접 확인
```

### 데이터베이스 초기화
```bash
docker-compose down -v
docker-compose up -d
```

---

## 다음 단계

로컬 환경이 정상적으로 작동하면:

1. ✅ 기능 테스트 완료
2. ✅ 통합 테스트 실행
3. ✅ 버그 수정
4. ✅ 성능 최적화
5. ✅ 테스트넷 배포 준비

---

## 참고 자료

- [전체 기능 테스트 가이드](./FULL_FEATURE_TEST_GUIDE.md)
- [프론트엔드 테스트 가이드](./FRONTEND_TEST_STEP_BY_STEP.md)
- [Smart Wallet 테스트 가이드](./SMART_WALLET_TEST_GUIDE.md)
- [통합 테스트 가이드](./backend/TESTING_GUIDE.md)

