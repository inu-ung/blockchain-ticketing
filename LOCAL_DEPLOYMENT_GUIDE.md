# 로컬 네트워크 배포 가이드

## 🎯 로컬 배포의 장점

- ✅ **가스비 무료** - 실제 자금 불필요
- ✅ **즉시 배포** - 네트워크 연결 불필요
- ✅ **빠른 테스트** - 즉시 결과 확인
- ✅ **반복 테스트** - 언제든지 재배포 가능

---

## 📋 배포 방법

### 방법 1: Hardhat Node 사용 (권장)

#### Step 1: Hardhat Node 실행

**새 터미널 창**에서 실행:

```bash
cd contracts
npx hardhat node
```

출력 예시:
```
Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545/

Accounts
========
Account #0: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 (10000 ETH)
Account #1: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8 (10000 ETH)
...
```

#### Step 2: 배포 실행

**다른 터미널**에서 실행:

```bash
cd contracts
npx hardhat run scripts/deploy_all.js --network localhost
```

또는:

```bash
npm run deploy:all -- --network localhost
```

#### Step 3: 배포 결과 확인

배포 정보는 `deployments/localhost.json`에 저장됩니다.

---

### 방법 2: Hardhat 네트워크 사용 (기본)

Hardhat Node 없이도 배포 가능:

```bash
cd contracts
npx hardhat run scripts/deploy_all.js
```

기본적으로 Hardhat 네트워크를 사용합니다.

---

## 🔧 배포 스크립트

### 전체 컨트랙트 배포

```bash
# Hardhat Node 사용
npx hardhat run scripts/deploy_all.js --network localhost

# Hardhat 네트워크 사용 (기본)
npx hardhat run scripts/deploy_all.js
```

### 개별 컨트랙트 배포

```bash
npx hardhat run scripts/deploy.js --network localhost
```

---

## ✅ 배포 확인

### 1. 콘솔 출력 확인

배포 성공 시:

```
🎉 배포 완료!
============================================================
Network: localhost
Deployer: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266

📋 Contract Addresses:
  TicketAccessControl: 0x...
  TicketNFT: 0x...
  EventManager: 0x...
  TicketMarketplace: 0x...
  RefundManager: 0x...
  SmartWallet: 0x...
  SmartWalletFactory: 0x...

💾 Deployment info saved to: deployments/localhost.json
```

### 2. 배포 정보 파일 확인

```bash
cat contracts/deployments/localhost.json
```

### 3. Hardhat Console로 테스트

```bash
npx hardhat console --network localhost
```

```javascript
// 컨트랙트 인스턴스 가져오기
const EventManager = await ethers.getContractFactory("EventManager");
const deployment = require("./deployments/localhost.json");
const eventManager = await EventManager.attach(deployment.contracts.EventManager);

// 컨트랙트 테스트
const currentEventId = await eventManager.getCurrentEventId();
console.log("Current Event ID:", currentEventId.toString());
```

---

## 🔄 백엔드/프론트엔드 설정

### 백엔드 환경 변수

`backend/.env` 파일에 추가:

```env
# Local Hardhat Network
WEB3_PROVIDER_URL=http://127.0.0.1:8545
EVENT_MANAGER_ADDRESS=0x...  # deployments/localhost.json에서 확인
TICKET_NFT_ADDRESS=0x...
TICKET_MARKETPLACE_ADDRESS=0x...
REFUND_MANAGER_ADDRESS=0x...
SMART_WALLET_FACTORY_ADDRESS=0x...
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
CHAIN_ID=1337
```

### 프론트엔드 환경 변수

`frontend/.env` 파일에 추가:

```env
# Local Hardhat Network
VITE_WEB3_PROVIDER_URL=http://127.0.0.1:8545
VITE_EVENT_MANAGER_ADDRESS=0x...
VITE_TICKET_NFT_ADDRESS=0x...
VITE_TICKET_MARKETPLACE_ADDRESS=0x...
VITE_REFUND_MANAGER_ADDRESS=0x...
VITE_SMART_WALLET_FACTORY_ADDRESS=0x...
VITE_ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
VITE_CHAIN_ID=1337
```

---

## 🛠️ 트러블슈팅

### "Cannot connect to the network localhost"

**원인**: Hardhat Node가 실행되지 않음

**해결**:
1. 새 터미널에서 `npx hardhat node` 실행
2. 노드가 실행 중인지 확인 (포트 8545)
3. 배포 명령어 다시 실행

### "Account balance is 0"

**원인**: Hardhat Node의 계정 잔액 부족

**해결**:
- Hardhat Node는 기본적으로 각 계정에 10000 ETH를 제공
- 노드를 재시작하면 잔액이 리셋됨

### 배포 실패

**해결**:
1. Hardhat Node 재시작
2. 배포 스크립트 다시 실행
3. 에러 메시지 확인

---

## 📊 배포 비교

| 항목 | 로컬 네트워크 | Amoy 테스트넷 | Polygon 메인넷 |
|------|--------------|--------------|----------------|
| 가스비 | 무료 | 테스트 MATIC 필요 | 실제 MATIC 필요 |
| 배포 속도 | 즉시 | 10-30초/컨트랙트 | 10-30초/컨트랙트 |
| 네트워크 연결 | 불필요 | 필요 | 필요 |
| 영구성 | 노드 종료 시 삭제 | 영구 | 영구 |
| 테스트 목적 | 개발/디버깅 | 통합 테스트 | 프로덕션 |

---

## 💡 유용한 팁

### 1. Hardhat Node 옵션

```bash
# 특정 계정 수 지정
npx hardhat node --accounts 20

# 특정 포트 사용
npx hardhat node --port 8546
```

### 2. 배포 정보 백업

```bash
# 배포 정보 복사
cp deployments/localhost.json ~/backup/localhost-$(date +%Y%m%d).json
```

### 3. 스냅샷 사용

Hardhat Node는 스냅샷 기능을 지원하여 상태를 저장/복원할 수 있습니다.

---

## 🔗 관련 문서

- **로컬 설정 가이드**: `LOCAL_SETUP_GUIDE.md`
- **테스트넷 배포**: `AMOY_DEPLOYMENT_GUIDE.md`
- **메인넷 배포**: `POLYGON_MAINNET_DEPLOYMENT.md`

