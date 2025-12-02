# .env 파일 설정 가이드

로컬에 배포된 컨트랙트 주소를 백엔드와 프론트엔드 .env 파일에 설정하는 방법

## 📋 현재 배포된 컨트랙트 주소 (localhost)

`contracts/deployments/localhost.json` 파일에서 확인한 주소:

```json
{
  "TicketAccessControl": "0x5FbDB2315678afecb367f032d93F642f64180aa3",
  "TicketNFT": "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512",
  "EventManager": "0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0",
  "TicketMarketplace": "0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9",
  "RefundManager": "0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9",
  "SmartWallet": "0x7a2088a1bFc9d81c55368AE168C2C02570cB814F",
  "SmartWalletFactory": "0x09635F643e140090A9A8Dcd712eD6285858ceBef",
  "EntryPoint": "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789"
}
```

---

## 🔧 백엔드 .env 파일 설정

### 파일 위치
`backend/.env`

### 설정해야 할 항목

```env
# Web3 (로컬 Hardhat)
POLYGON_MUMBAI_RPC_URL=http://127.0.0.1:8545
PRIVATE_KEY=ac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
# ↑ Hardhat 첫 번째 계정의 개인키 (기본값)

# Contract Addresses (로컬 배포 주소)
TICKET_ACCESS_CONTROL_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
TICKET_NFT_ADDRESS=0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
EVENT_MANAGER_ADDRESS=0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0
MARKETPLACE_ADDRESS=0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9
REFUND_MANAGER_ADDRESS=0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9

# Account Abstraction
SMART_WALLET_FACTORY_ADDRESS=0x09635F643e140090A9A8Dcd712eD6285858ceBef
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

### 전체 백엔드 .env 예시

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

# Contract Addresses
TICKET_ACCESS_CONTROL_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
TICKET_NFT_ADDRESS=0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
EVENT_MANAGER_ADDRESS=0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0
MARKETPLACE_ADDRESS=0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9
REFUND_MANAGER_ADDRESS=0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9

# Account Abstraction
SMART_WALLET_FACTORY_ADDRESS=0x09635F643e140090A9A8Dcd712eD6285858ceBef
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789

# IPFS (선택사항)
PINATA_API_KEY=
PINATA_SECRET_KEY=

# CORS
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## 🎨 프론트엔드 .env 파일 설정

### 파일 위치
`frontend/.env`

### 파일 생성 (없는 경우)

```bash
cd frontend
touch .env
```

### 설정해야 할 항목

```env
# API
VITE_API_URL=http://localhost:8000

# Web3 (로컬 Hardhat)
VITE_RPC_URL=http://127.0.0.1:8545
VITE_CHAIN_ID=1337

# Contract Addresses (로컬 배포 주소)
VITE_TICKET_ACCESS_CONTROL_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
VITE_TICKET_NFT_ADDRESS=0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
VITE_EVENT_MANAGER_ADDRESS=0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0
VITE_MARKETPLACE_ADDRESS=0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9
VITE_REFUND_MANAGER_ADDRESS=0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9

# Account Abstraction
VITE_SMART_WALLET_FACTORY_ADDRESS=0x09635F643e140090A9A8Dcd712eD6285858ceBef
VITE_ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

**중요:** 프론트엔드에서는 환경 변수 이름 앞에 `VITE_` 접두사가 필요합니다!

---

## 🔍 왜 이 주소들을 설정해야 하나요?

### 백엔드에서
- 스마트 컨트랙트와 상호작용할 때 어떤 주소의 컨트랙트를 사용할지 알아야 합니다
- 예: 티켓 구매 시 `EVENT_MANAGER_ADDRESS`의 컨트랙트를 호출합니다

### 프론트엔드에서
- 사용자에게 컨트랙트 정보를 표시하거나
- 직접 컨트랙트와 상호작용할 때 주소가 필요합니다

---

## ✅ 설정 확인 방법

### 백엔드 확인
```bash
cd backend
python -c "from app.core.config import settings; print(settings.EVENT_MANAGER_ADDRESS)"
```

### 프론트엔드 확인
브라우저 콘솔에서:
```javascript
console.log(import.meta.env.VITE_EVENT_MANAGER_ADDRESS)
```

---

## 📝 주의사항

1. **로컬 배포 주소는 매번 다를 수 있습니다**
   - Hardhat 노드를 재시작하면 주소가 변경될 수 있습니다
   - 배포 후 항상 `deployments/localhost.json`을 확인하세요

2. **환경 변수 이름 확인**
   - 백엔드: `EVENT_MANAGER_ADDRESS`
   - 프론트엔드: `VITE_EVENT_MANAGER_ADDRESS` (VITE_ 접두사 필요!)

3. **프론트엔드 재시작 필요**
   - `.env` 파일을 수정한 후 프론트엔드 서버를 재시작해야 합니다
   ```bash
   # Ctrl+C로 중지 후
   npm run dev
   ```

---

## 🚀 빠른 설정 스크립트

### 백엔드 .env 업데이트
```bash
cd backend
cat >> .env << 'EOF'

# Contract Addresses (로컬)
TICKET_ACCESS_CONTROL_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
TICKET_NFT_ADDRESS=0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
EVENT_MANAGER_ADDRESS=0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0
MARKETPLACE_ADDRESS=0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9
REFUND_MANAGER_ADDRESS=0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9
SMART_WALLET_FACTORY_ADDRESS=0x09635F643e140090A9A8Dcd712eD6285858ceBef
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
EOF
```

### 프론트엔드 .env 생성
```bash
cd frontend
cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000
VITE_RPC_URL=http://127.0.0.1:8545
VITE_CHAIN_ID=1337
VITE_TICKET_ACCESS_CONTROL_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
VITE_TICKET_NFT_ADDRESS=0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512
VITE_EVENT_MANAGER_ADDRESS=0x9fE46736679d2D9a65F0992F2272dE9f3c7fa6e0
VITE_MARKETPLACE_ADDRESS=0xCf7Ed3AccA5a467e9e704C703E8D87F634fB0Fc9
VITE_REFUND_MANAGER_ADDRESS=0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9
VITE_SMART_WALLET_FACTORY_ADDRESS=0x09635F643e140090A9A8Dcd712eD6285858ceBef
VITE_ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
EOF
```

---

## ❓ 문제 해결

### 백엔드에서 컨트랙트를 찾을 수 없다는 오류
- `.env` 파일에 주소가 올바르게 설정되었는지 확인
- Hardhat 노드가 실행 중인지 확인
- 배포가 완료되었는지 확인 (`deployments/localhost.json`)

### 프론트엔드에서 환경 변수가 undefined
- 환경 변수 이름에 `VITE_` 접두사가 있는지 확인
- 프론트엔드 서버를 재시작했는지 확인
- `.env` 파일이 `frontend/` 디렉토리에 있는지 확인

