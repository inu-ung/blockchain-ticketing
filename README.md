# 블록체인 티켓팅 시스템

Polygon 블록체인 기반 NFT 티켓팅 플랫폼

## 프로젝트 구조

```
BC/
├── contracts/          # 스마트 컨트랙트 (Hardhat)
├── backend/            # FastAPI 백엔드
├── frontend/           # React 프론트엔드
└── ARCHITECTURE.md     # 아키텍처 문서
```

## 기술 스택

- **블록체인**: Polygon (ERC-721, ERC-4337)
- **스마트 컨트랙트**: Solidity, Hardhat
- **백엔드**: FastAPI, PostgreSQL
- **프론트엔드**: React, TypeScript, Tailwind CSS
- **IPFS**: Pinata

## 시작하기

### 사전 요구사항

- Node.js 18+
- Python 3.11+
- PostgreSQL 15+
- npm 또는 yarn

### 1. 스마트 컨트랙트

```bash
cd contracts
npm install --legacy-peer-deps
npm run compile
npm run deploy  # 로컬 네트워크 배포
```

**환경 변수 설정** (`contracts/.env`):
```
POLYGON_MUMBAI_RPC_URL=https://rpc-mumbai.maticvigil.com
PRIVATE_KEY=your-private-key
POLYGONSCAN_API_KEY=your-api-key
```

### 2. 백엔드

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# PostgreSQL 데이터베이스 생성
createdb ticketing_db

# 환경 변수 설정
cp .env.example .env  # .env 파일을 생성하고 값 입력

# 서버 실행
uvicorn main:app --reload
```

**환경 변수 설정** (`backend/.env`):
```
DATABASE_URL=postgresql://user:password@localhost:5432/ticketing_db
SECRET_KEY=your-secret-key
POLYGON_MUMBAI_RPC_URL=https://rpc-mumbai.maticvigil.com
PRIVATE_KEY=your-private-key
PINATA_API_KEY=your-pinata-api-key
PINATA_SECRET_KEY=your-pinata-secret-key
# 배포된 컨트랙트 주소들...
```

### 3. 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

**환경 변수 설정** (`frontend/.env`):
```
VITE_API_URL=http://localhost:8000
VITE_TICKET_ACCESS_CONTROL_ADDRESS=...
VITE_TICKET_NFT_ADDRESS=...
VITE_EVENT_MANAGER_ADDRESS=...
VITE_MARKETPLACE_ADDRESS=...
VITE_REFUND_MANAGER_ADDRESS=...
```

## 주요 기능

- ✅ 이벤트 생성 및 관리
- ✅ NFT 티켓 발행 및 판매
- ✅ 티켓 구매 (고정가)
- ✅ 2차 시장 재판매
- ✅ 환불 및 취소 처리
- ✅ Account Abstraction 기반 자동 지갑 연결
- ✅ IPFS 기반 메타데이터 저장

## 개발 상태

현재 기본 구조와 스마트 컨트랙트가 완성되었습니다. 다음 단계:
- API 엔드포인트 구현
- 프론트엔드 컴포넌트 구현
- Account Abstraction 통합
- IPFS 통합
- 테스트 작성

## 라이선스

MIT

