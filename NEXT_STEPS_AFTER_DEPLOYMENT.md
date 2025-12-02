# 배포 후 다음 단계 가이드

## ✅ 현재 완료된 작업

1. ✅ **로컬 네트워크 배포 완료**
   - Hardhat Node 실행 중
   - 모든 스마트 컨트랙트 배포 완료
   - 배포 주소: `contracts/deployments/localhost.json`

2. ✅ **프론트엔드 서버 실행 중**
   - 포트: 5173
   - URL: http://localhost:5173

---

## 🔄 다음 단계

### 1단계: 환경 변수 설정 (필수)

#### 백엔드 환경 변수 설정

`backend/.env` 파일에 다음 내용을 추가/수정:

```env
# Web3 (로컬 Hardhat)
POLYGON_MUMBAI_RPC_URL=http://127.0.0.1:8545
PRIVATE_KEY=ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

# Contract Addresses (최신 배포 주소)
TICKET_ACCESS_CONTROL_ADDRESS=0x2279B7A0a67DB372996a5FaB50D91eAA73d2eBe6
TICKET_NFT_ADDRESS=0x8A791620dd6260079BF849Dc5567aDC3F2FdC318
EVENT_MANAGER_ADDRESS=0x610178dA211FEF7D417bC0e6FeD39F05609AD788
MARKETPLACE_ADDRESS=0xB7f8BC63BbcaD18155201308C8f3540b07f84F5e
REFUND_MANAGER_ADDRESS=0xA51c1fc2f0D1a1b8494Ed1FE312d7C3a78Ed91C0

# Account Abstraction
SMART_WALLET_FACTORY_ADDRESS=0x9A676e781A523b5d0C0e43731313A708CB607508
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

#### 프론트엔드 환경 변수 설정

`frontend/.env` 파일에 다음 내용을 추가/수정:

```env
# API
VITE_API_URL=http://localhost:8000

# Web3 (로컬 Hardhat)
VITE_RPC_URL=http://127.0.0.1:8545
VITE_CHAIN_ID=1337

# Contract Addresses
VITE_TICKET_ACCESS_CONTROL_ADDRESS=0x2279B7A0a67DB372996a5FaB50D91eAA73d2eBe6
VITE_TICKET_NFT_ADDRESS=0x8A791620dd6260079BF849Dc5567aDC3F2FdC318
VITE_EVENT_MANAGER_ADDRESS=0x610178dA211FEF7D417bC0e6FeD39F05609AD788
VITE_MARKETPLACE_ADDRESS=0xB7f8BC63BbcaD18155201308C8f3540b07f84F5e
VITE_REFUND_MANAGER_ADDRESS=0xA51c1fc2f0D1a1b8494Ed1FE312d7C3a78Ed91C0

# Account Abstraction
VITE_SMART_WALLET_FACTORY_ADDRESS=0x9A676e781A523b5d0C0e43731313A708CB607508
VITE_ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

---

### 2단계: 백엔드 서버 실행

**새 터미널에서:**

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
uvicorn main:app --reload
```

**확인:**
- http://localhost:8000/health 접속
- `{"status":"healthy"}` 응답 확인

---

### 3단계: PostgreSQL 데이터베이스 확인

```bash
# Docker로 PostgreSQL 실행
docker-compose up -d

# 데이터베이스 확인
docker exec -it ticketing-postgres psql -U postgres -d ticketing -c "\dt"
```

---

### 4단계: 전체 시스템 테스트

#### 테스트 시나리오 1: 회원가입 및 로그인

1. 브라우저에서 http://localhost:5173 접속
2. 회원가입:
   - 이메일: `organizer@test.com`
   - 비밀번호: `test123`
3. 로그인 확인
4. Smart Wallet 자동 생성 확인

#### 테스트 시나리오 2: 이벤트 생성

1. 주최자 계정으로 로그인
2. "이벤트 생성" 메뉴 클릭
3. 이벤트 정보 입력 및 생성
4. 이벤트가 DB에 저장되는지 확인

#### 테스트 시나리오 3: 티켓 구매

1. 구매자 계정 생성 (`buyer@test.com`)
2. 이벤트 목록에서 이벤트 선택
3. 티켓 구매 버튼 클릭
4. Smart Wallet을 통한 구매 확인
5. NFT 티켓 발행 확인

---

### 5단계: 통합 테스트 실행 (선택사항)

```bash
cd backend
source venv/bin/activate
python test_integration.py
```

---

## 🎯 우선순위별 체크리스트

### 필수 작업 (지금 해야 할 것)

- [ ] **백엔드 환경 변수 설정** (`backend/.env`)
- [ ] **프론트엔드 환경 변수 설정** (`frontend/.env`)
- [ ] **백엔드 서버 실행**
- [ ] **PostgreSQL 데이터베이스 실행**
- [ ] **기본 기능 테스트** (회원가입, 로그인)

### 다음 단계 (기능 테스트 후)

- [ ] **이벤트 생성 테스트**
- [ ] **티켓 구매 테스트**
- [ ] **재판매 기능 테스트**
- [ ] **환불 기능 테스트**

### 배포 옵션 (선택사항)

- [ ] **테스트넷 배포** (Amoy)
- [ ] **메인넷 배포** (Polygon)

---

## 🚨 문제 해결

### 백엔드 서버가 시작되지 않을 때

1. 환경 변수 확인: `backend/.env` 파일 존재 여부
2. 가상환경 활성화 확인: `source venv/bin/activate`
3. 의존성 설치 확인: `pip install -r requirements.txt`
4. 포트 충돌 확인: 다른 프로세스가 8000 포트 사용 중인지

### 프론트엔드가 컨트랙트를 찾지 못할 때

1. 환경 변수 확인: `frontend/.env` 파일 존재 여부
2. `VITE_` 접두사 확인: 모든 환경 변수는 `VITE_`로 시작해야 함
3. 서버 재시작: 환경 변수 변경 후 `npm run dev` 재시작

### Smart Wallet 생성 실패

1. Hardhat Node 실행 확인: `ps aux | grep "hardhat node"`
2. RPC URL 확인: `http://127.0.0.1:8545`
3. 백엔드 로그 확인: 에러 메시지 확인

---

## 📚 참고 문서

- **환경 변수 설정**: `DEPLOYMENT_ENV_SETUP.md`
- **전체 기능 테스트**: `FULL_FEATURE_TEST_GUIDE.md`
- **로컬 설정 가이드**: `LOCAL_SETUP_GUIDE.md`
- **테스트넷 배포**: `AMOY_DEPLOYMENT_GUIDE.md`

---

## 💡 빠른 시작 명령어

```bash
# 1. 환경 변수 설정 (수동으로 .env 파일 편집)

# 2. 백엔드 서버 실행
cd backend && source venv/bin/activate && uvicorn main:app --reload

# 3. PostgreSQL 실행
docker-compose up -d

# 4. 프론트엔드 확인 (이미 실행 중)
# 브라우저에서 http://localhost:5173 접속
```

