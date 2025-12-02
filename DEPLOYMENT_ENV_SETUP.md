# 배포 완료 - 환경 변수 설정 가이드

## 배포된 컨트랙트 주소 (localhost)

```
TicketAccessControl: 0x2279B7A0a67DB372996a5FaB50D91eAA73d2eBe6
TicketNFT: 0x8A791620dd6260079BF849Dc5567aDC3F2FdC318
EventManager: 0x610178dA211FEF7D417bC0e6FeD39F05609AD788
TicketMarketplace: 0xB7f8BC63BbcaD18155201308C8f3540b07f84F5e
RefundManager: 0xA51c1fc2f0D1a1b8494Ed1FE312d7C3a78Ed91C0
SmartWallet: 0x0DCd1Bf9A1b36cE34237eEaFef220932846BCD82
SmartWalletFactory: 0x9A676e781A523b5d0C0e43731313A708CB607508
EntryPoint: 0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

---

## 백엔드 환경 변수 설정

`backend/.env` 파일에 다음 내용을 추가/수정하세요:

```env
# Web3 (로컬 Hardhat)
POLYGON_MUMBAI_RPC_URL=http://127.0.0.1:8545
PRIVATE_KEY=ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

# Contract Addresses
TICKET_ACCESS_CONTROL_ADDRESS=0x2279B7A0a67DB372996a5FaB50D91eAA73d2eBe6
TICKET_NFT_ADDRESS=0x8A791620dd6260079BF849Dc5567aDC3F2FdC318
EVENT_MANAGER_ADDRESS=0x610178dA211FEF7D417bC0e6FeD39F05609AD788
MARKETPLACE_ADDRESS=0xB7f8BC63BbcaD18155201308C8f3540b07f84F5e
REFUND_MANAGER_ADDRESS=0xA51c1fc2f0D1a1b8494Ed1FE312d7C3a78Ed91C0

# Account Abstraction
SMART_WALLET_FACTORY_ADDRESS=0x9A676e781A523b5d0C0e43731313A708CB607508
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

---

## 프론트엔드 환경 변수 설정

`frontend/.env` 파일에 다음 내용을 추가/수정하세요:

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

## 다음 단계

1. ✅ **로컬 배포 완료** - Hardhat Node에서 컨트랙트 배포됨
2. ⏳ **백엔드 환경 변수 설정** - 위의 주소들을 `backend/.env`에 추가
3. ⏳ **프론트엔드 환경 변수 설정** - 위의 주소들을 `frontend/.env`에 추가
4. ⏳ **서비스 실행** - 백엔드와 프론트엔드 서버 시작

---

## 서비스 실행 방법

### 1. Hardhat Node (이미 실행 중)
```bash
# 백그라운드에서 실행 중
# 종료하려면: pkill -f "hardhat node"
```

### 2. 백엔드 서버
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### 3. 프론트엔드 서버
```bash
cd frontend
npm run dev
```

---

## 배포 정보 확인

배포 정보는 `contracts/deployments/localhost.json`에 저장되어 있습니다.

```bash
cat contracts/deployments/localhost.json
```

