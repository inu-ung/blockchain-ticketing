# 환경 변수 업데이트 필요

## ❌ 문제 발견

현재 설정된 컨트랙트 주소가 **이전 배포 주소**입니다. 최신 배포 주소로 업데이트가 필요합니다.

---

## 📋 최신 배포 주소 (2025-12-02 배포)

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

## 🔧 백엔드 환경 변수 업데이트

`backend/.env` 파일을 다음과 같이 수정하세요:

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

---

## 🎨 프론트엔드 환경 변수 업데이트

`frontend/.env` 파일을 다음과 같이 수정하세요:

```env
# API
VITE_API_URL=http://localhost:8000

# Web3 (로컬 Hardhat)
VITE_RPC_URL=http://127.0.0.1:8545
VITE_CHAIN_ID=1337

# Contract Addresses (최신 배포 주소)
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

## ⚠️ 중요 사항

1. **프론트엔드 재시작 필요**: `.env` 파일 수정 후 프론트엔드 서버를 재시작해야 합니다.
   ```bash
   # Ctrl+C로 중지 후
   cd frontend
   npm run dev
   ```

2. **백엔드 재시작 필요**: `.env` 파일 수정 후 백엔드 서버를 재시작해야 합니다.
   ```bash
   # Ctrl+C로 중지 후
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload
   ```

3. **주소 확인**: 항상 `contracts/deployments/localhost.json` 파일에서 최신 주소를 확인하세요.

---

## ✅ 업데이트 후 확인

### 백엔드 확인
```bash
cd backend
source venv/bin/activate
python -c "from app.core.config import settings; print('EventManager:', settings.EVENT_MANAGER_ADDRESS)"
```

### 프론트엔드 확인
브라우저 콘솔에서:
```javascript
console.log(import.meta.env.VITE_EVENT_MANAGER_ADDRESS)
```

---

## 📝 변경 사항 요약

| 컨트랙트 | 이전 주소 | 최신 주소 |
|---------|----------|----------|
| EventManager | 0x9fE4...fa6e0 | 0x6101...AD788 |
| TicketNFT | 0xe7f1...0512 | 0x8A79...FdC318 |
| SmartWalletFactory | 0x0963...ceBef | 0x9A67...CB607508 |

