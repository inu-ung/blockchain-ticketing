# 블록체인 티켓팅 시스템

Polygon 블록체인 기반 NFT 티켓팅 플랫폼 (ERC-4337 Account Abstraction)

## 🎯 프로젝트 개요

Account Abstraction을 활용한 사용자 친화적인 NFT 티켓팅 시스템입니다. 사용자는 MetaMask 없이도 카드 결제만으로 티켓을 구매할 수 있으며, 가스비는 Paymaster가 자동으로 처리합니다.

## 🏗️ 프로젝트 구조

```
BC/
├── contracts/          # 스마트 컨트랙트 (Hardhat)
│   ├── contracts/      # Solidity 컨트랙트 (2개)
│   └── scripts/       # 배포 스크립트
├── backend/            # FastAPI 백엔드
│   ├── app/
│   │   ├── api/       # API 엔드포인트
│   │   ├── services/  # 비즈니스 로직
│   │   └── models/    # 데이터베이스 모델
│   └── main.py
└── frontend/           # React 프론트엔드
    └── src/
```

## 🛠️ 기술 스택

### 블록체인
- **네트워크**: Polygon (Amoy 테스트넷, Mainnet)
- **표준**: ERC-721 (NFT), ERC-4337 (Account Abstraction)
- **개발 도구**: Hardhat, Solidity 0.8.20+

### 백엔드
- **프레임워크**: FastAPI
- **데이터베이스**: PostgreSQL
- **블록체인 연동**: Web3.py
- **IPFS**: Pinata

### 프론트엔드
- **프레임워크**: React + TypeScript
- **스타일링**: Tailwind CSS
- **상태 관리**: Zustand
- **HTTP 클라이언트**: Axios

## 📦 스마트 컨트랙트 (2개)

### 1. TicketNFT
- ERC-721 기반 NFT 티켓 발행
- 티켓 소각 (환불 시)
- 메타데이터 URI 관리

### 2. SmartWalletFactory
- Account Abstraction 기반 Smart Wallet 생성
- CREATE2를 사용한 Deterministic 주소 생성
- SmartWallet 구현 컨트랙트 포함

**백엔드에서 처리:**
- 이벤트 관리 (EventManager 로직)
- 역할 관리 (AccessControl)
- 재판매 마켓플레이스
- 환불 처리

## 🚀 빠른 시작

### 1. 스마트 컨트랙트 배포

```bash
cd contracts
npm install --legacy-peer-deps

# 로컬 네트워크 (가스비 무료)
npm run node  # 터미널 1
npm run deploy:local  # 터미널 2

# 테스트넷 배포
npm run deploy:amoy

# 하나씩 배포
npm run deploy:ticket-nft --network amoy
npm run deploy:factory --network amoy
```

**환경 변수 설정** (`contracts/.env`):
```env
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
PRIVATE_KEY=your-private-key
POLYGONSCAN_API_KEY=your-api-key
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

### 2. 백엔드 실행

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# PostgreSQL 데이터베이스 생성
createdb ticketing_db

# 환경 변수 설정 (.env 파일)
DATABASE_URL=postgresql://user:password@localhost:5432/ticketing_db
SECRET_KEY=your-secret-key
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
PRIVATE_KEY=your-private-key
TICKET_NFT_ADDRESS=0x...
SMART_WALLET_FACTORY_ADDRESS=0x...
PINATA_API_KEY=your-pinata-api-key
PINATA_SECRET_KEY=your-pinata-secret-key

# 서버 실행
uvicorn main:app --reload
```

### 3. 프론트엔드 실행

```bash
cd frontend
npm install
npm run dev
```

**환경 변수 설정** (`frontend/.env`):
```env
VITE_API_URL=http://localhost:8000
VITE_TICKET_NFT_ADDRESS=0x...
VITE_SMART_WALLET_FACTORY_ADDRESS=0x...
VITE_ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

## ✨ 주요 기능

### 사용자
- ✅ 회원가입/로그인 (이메일, 비밀번호)
- ✅ Smart Wallet 자동 생성 (Account Abstraction)
- ✅ 카드 결제로 티켓 구매 (MetaMask 불필요)
- ✅ 내 티켓 조회 및 환불 요청
- ✅ 티켓 재판매

### 주최자
- ✅ 이벤트 생성 및 관리
- ✅ IPFS 메타데이터 업로드
- ✅ 티켓 판매 현황 조회

### 관리자
- ✅ 이벤트 승인/거부
- ✅ 환불 처리
- ✅ 긴급 환불 처리

## 🔐 Account Abstraction 특징

1. **지갑 없이 사용**: MetaMask 불필요, 카드 결제만으로 사용
2. **가스비 무료**: Paymaster가 자동으로 가스비 스폰서
3. **자동 지갑 생성**: 회원가입 시 Smart Wallet 자동 생성
4. **Deterministic 주소**: CREATE2로 일관된 주소 보장

## 📊 배포 정보

### 로컬 네트워크
- RPC: `http://localhost:8545`
- Chain ID: `1337`
- 가스비: 무료

### Polygon Amoy 테스트넷
- RPC: `https://rpc-amoy.polygon.technology`
- Chain ID: `80002`
- Explorer: https://amoy.polygonscan.com

### 배포된 컨트랙트
배포 후 `contracts/deployments/{network}.json` 파일에서 주소 확인

## 🔗 API 문서

백엔드 실행 후:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📝 환경 변수

### 백엔드 (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/ticketing_db
SECRET_KEY=your-secret-key
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
PRIVATE_KEY=your-private-key
TICKET_NFT_ADDRESS=0x...
SMART_WALLET_FACTORY_ADDRESS=0x...
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
PINATA_API_KEY=your-pinata-api-key
PINATA_SECRET_KEY=your-pinata-secret-key
```

### 프론트엔드 (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_TICKET_NFT_ADDRESS=0x...
VITE_SMART_WALLET_FACTORY_ADDRESS=0x...
VITE_ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

## 🧪 테스트

```bash
# 스마트 컨트랙트 테스트
cd contracts
npm test

# 백엔드 테스트
cd backend
pytest
```

## 📦 배포

### 백엔드 (EC2 + Docker)
```bash
cd backend
docker-compose -f docker-compose.prod.yml up -d
```

### 프론트엔드 (Vercel)
Vercel에 연결하면 자동 배포됩니다.

## 📄 라이선스

MIT
