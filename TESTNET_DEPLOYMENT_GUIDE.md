# 테스트넷 배포 가이드

Polygon Mumbai 테스트넷에 전체 시스템 배포하기

## 📋 목차
1. [사전 준비](#사전-준비)
2. [환경 변수 설정](#환경-변수-설정)
3. [테스트 MATIC 받기](#테스트-matic-받기)
4. [배포 실행](#배포-실행)
5. [배포 확인](#배포-확인)
6. [백엔드/프론트엔드 설정](#백엔드프론트엔드-설정)

---

## 사전 준비

### 1. 필요한 것들
- ✅ MetaMask 또는 다른 Web3 지갑
- ✅ 테스트넷용 지갑 (메인넷과 분리 권장)
- ✅ 지갑 개인키
- ✅ Polygonscan API 키 (컨트랙트 검증용, 선택사항)

### 2. Polygon Mumbai 정보
- **체인 ID**: 80001
- **RPC URL**: https://rpc-mumbai.maticvigil.com
- **Explorer**: https://mumbai.polygonscan.com
- **가스 통화**: MATIC (테스트넷)

---

## 환경 변수 설정

### 1. `.env` 파일 생성

`contracts` 디렉토리에 `.env` 파일을 생성합니다:

```bash
cd contracts
touch .env
```

### 2. 환경 변수 입력

`.env` 파일에 다음 내용을 추가합니다:

```env
# Polygon Mumbai RPC URL
POLYGON_MUMBAI_RPC_URL=https://rpc-mumbai.maticvigil.com

# 배포할 지갑의 개인키 (0x 포함 또는 제외 모두 가능)
PRIVATE_KEY=your-private-key-here

# Polygonscan API 키 (컨트랙트 검증용, 선택사항)
POLYGONSCAN_API_KEY=your-polygonscan-api-key

# EntryPoint 주소 (ERC-4337 표준, 변경 불필요)
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

### 3. 개인키 확인 방법

**MetaMask에서:**
1. MetaMask 열기
2. 설정 → 보안 및 개인정보 보호
3. 계정 내보내기 → 개인키 표시
4. 비밀번호 입력 후 개인키 복사

**⚠️ 보안 주의사항:**
- 개인키는 절대 공유하지 마세요
- `.env` 파일은 `.gitignore`에 포함되어 있는지 확인
- GitHub에 업로드하지 마세요
- 테스트넷용 지갑만 사용하세요

### 4. RPC URL 옵션

**무료 옵션:**
- MaticVigil: `https://rpc-mumbai.maticvigil.com`
- Chainstack: `https://matic-mumbai.chainstacklabs.com`
- Ankr: `https://rpc.ankr.com/polygon_mumbai`

**유료 옵션 (더 안정적):**
- Alchemy: `https://polygon-mumbai.g.alchemy.com/v2/YOUR-API-KEY`
- Infura: `https://polygon-mumbai.infura.io/v3/YOUR-PROJECT-ID`

---

## 테스트 MATIC 받기

배포에는 가스비가 필요합니다. 테스트넷 MATIC을 무료로 받을 수 있습니다.

### 방법 1: Polygon Faucet (권장)

1. **Polygon Faucet 접속**
   - https://faucet.polygon.technology/
   - 또는 https://mumbaifaucet.com/

2. **지갑 주소 입력**
   - MetaMask에서 지갑 주소 복사
   - Faucet에 주소 입력

3. **캡차 완료 및 요청**
   - 캡차를 완료하고 "Submit" 클릭
   - 보통 0.1-1 MATIC이 지급됩니다

4. **대기 시간**
   - 즉시 또는 몇 분 내에 지급됩니다
   - 지갑에서 잔액 확인

### 방법 2: Alchemy Faucet

1. https://www.alchemy.com/faucets/polygon-mumbai 접속
2. Alchemy 계정 생성 (무료)
3. 지갑 주소 입력
4. 매일 최대 0.5 MATIC 받기 가능

### 필요한 MATIC 양

- 컨트랙트 배포: 약 0.01-0.1 MATIC
- 권장: 최소 0.5 MATIC 이상 보유

---

## 배포 실행

### 1. 컴파일 확인

먼저 컨트랙트가 정상적으로 컴파일되는지 확인:

```bash
cd contracts
npm run compile
```

### 2. 배포 스크립트 실행

전체 컨트랙트를 한 번에 배포:

```bash
npx hardhat run scripts/deploy_all.js --network mumbai
```

또는 npm 스크립트 사용:

```bash
npm run deploy:mumbai
```

### 3. 배포 과정

배포가 시작되면 다음과 같은 과정이 진행됩니다:

```
[1/7] TicketAccessControl 배포
[2/7] TicketNFT 배포
[3/7] EventManager 배포
[4/7] TicketMarketplace 배포
[5/7] RefundManager 배포
[6/7] SmartWallet 구현 배포
[7/7] SmartWalletFactory 배포
[8/8] 권한 설정
```

각 단계는 약 10-30초 소요됩니다.

### 4. 배포 결과

성공적으로 배포되면 다음과 같은 출력이 표시됩니다:

```
🎉 배포 완료!
============================================================
Network: mumbai
Deployer: 0xYourAddress...

📋 Contract Addresses:
  TicketAccessControl: 0x...
  TicketNFT: 0x...
  EventManager: 0x...
  TicketMarketplace: 0x...
  RefundManager: 0x...
  SmartWallet: 0x...
  SmartWalletFactory: 0x...
  EntryPoint: 0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789

💾 Deployment info saved to: deployments/mumbai.json
```

### 5. 배포 정보 저장

배포된 컨트랙트 주소는 `deployments/mumbai.json` 파일에 자동으로 저장됩니다.

---

## 배포 확인

### 1. Polygonscan에서 확인

각 컨트랙트 주소를 Polygonscan에서 확인:

1. https://mumbai.polygonscan.com 접속
2. 컨트랙트 주소 검색
3. 트랜잭션 내역 확인
4. 컨트랙트 코드 확인 (검증 전에는 바이트코드만 표시)

### 2. 배포 정보 파일 확인

```bash
cat deployments/mumbai.json
```

### 3. 컨트랙트 상호작용 테스트

Hardhat console을 사용하여 배포된 컨트랙트와 상호작용:

```bash
npx hardhat console --network mumbai
```

```javascript
// 배포 정보 로드
const fs = require("fs");
const deployment = JSON.parse(fs.readFileSync("deployments/mumbai.json", "utf8"));

// 컨트랙트 인스턴스 가져오기
const TicketNFT = await ethers.getContractFactory("TicketNFT");
const ticketNFT = await TicketNFT.attach(deployment.contracts.TicketNFT);

// 함수 호출
const name = await ticketNFT.name();
console.log("Token Name:", name);
```

---

## 백엔드/프론트엔드 설정

### 1. 백엔드 설정 업데이트

배포된 컨트랙트 주소를 `backend/.env` 파일에 추가:

```env
# Polygon Mumbai RPC
POLYGON_MUMBAI_RPC_URL=https://rpc-mumbai.maticvigil.com

# 배포된 컨트랙트 주소
TICKET_ACCESS_CONTROL_ADDRESS=0x...
TICKET_NFT_ADDRESS=0x...
EVENT_MANAGER_ADDRESS=0x...
MARKETPLACE_ADDRESS=0x...
REFUND_MANAGER_ADDRESS=0x...

# Account Abstraction
SMART_WALLET_FACTORY_ADDRESS=0x...
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789

# 서비스 계정 개인키 (배포한 지갑과 동일)
PRIVATE_KEY=your-private-key-here
```

### 2. 프론트엔드 설정 업데이트

프론트엔드 `.env` 파일에도 주소 추가:

```env
VITE_API_URL=http://localhost:8000
VITE_RPC_URL=https://rpc-mumbai.maticvigil.com

# 배포된 컨트랙트 주소
VITE_TICKET_ACCESS_CONTROL_ADDRESS=0x...
VITE_TICKET_NFT_ADDRESS=0x...
VITE_EVENT_MANAGER_ADDRESS=0x...
VITE_MARKETPLACE_ADDRESS=0x...
VITE_REFUND_MANAGER_ADDRESS=0x...

# Account Abstraction
VITE_SMART_WALLET_FACTORY_ADDRESS=0x...
VITE_ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

### 3. 자동 설정 스크립트 (선택사항)

배포 후 자동으로 환경 변수를 업데이트하는 스크립트:

```bash
# contracts/scripts/update_env.sh
#!/bin/bash
DEPLOYMENT_FILE="deployments/mumbai.json"
if [ -f "$DEPLOYMENT_FILE" ]; then
  echo "Updating environment variables..."
  # 백엔드 .env 업데이트
  # 프론트엔드 .env 업데이트
fi
```

---

## 컨트랙트 검증 (선택사항)

컨트랙트를 검증하면 Polygonscan에서 소스 코드를 확인할 수 있습니다.

### 1. Polygonscan API 키 발급

1. https://polygonscan.com/apis 접속
2. 계정 생성 (무료)
3. API 키 생성
4. `.env` 파일에 추가

### 2. 검증 스크립트 실행

```bash
# 개별 컨트랙트 검증
npx hardhat verify --network mumbai \
  <CONTRACT_ADDRESS> \
  <CONSTRUCTOR_ARG1> <CONSTRUCTOR_ARG2> ...

# 예시: TicketNFT 검증
npx hardhat verify --network mumbai \
  0x...TicketNFTAddress... \
  0x...AccessControlAddress...
```

---

## 문제 해결

### 1. 가스비 부족 오류

**오류 메시지:**
```
Error: insufficient funds for gas
```

**해결 방법:**
- Faucet에서 더 많은 MATIC 받기
- 지갑 잔액 확인
- 가스 가격이 높을 때는 잠시 후 재시도

### 2. 네트워크 연결 오류

**오류 메시지:**
```
Error: could not detect network
```

**해결 방법:**
- RPC URL이 올바른지 확인
- 인터넷 연결 확인
- 다른 RPC 제공자로 변경

### 3. 트랜잭션 실패

**오류 메시지:**
```
Error: transaction failed
```

**해결 방법:**
- Polygonscan에서 실패 원인 확인
- 가스 한도 증가
- 컨트랙트 로직 오류 확인

### 4. 권한 오류

**오류 메시지:**
```
Error: AccessControl: account is missing role
```

**해결 방법:**
- 배포 스크립트에서 권한 설정 확인
- 올바른 주소로 권한 부여 확인

---

## 다음 단계

테스트넷 배포가 완료되면:

1. ✅ 컨트랙트 기능 테스트
2. ✅ 프론트엔드와 통합 테스트
3. ✅ 사용자 시나리오 테스트
4. ✅ 보안 감사 (선택사항)
5. ✅ 메인넷 배포 준비

---

## 유용한 리소스

- **Polygon 문서**: https://docs.polygon.technology/
- **Hardhat 문서**: https://hardhat.org/docs
- **Polygonscan**: https://mumbai.polygonscan.com
- **Faucet 목록**: https://faucet.polygon.technology/
- **ERC-4337 표준**: https://eips.ethereum.org/EIPS/eip-4337

---

## 주의사항

⚠️ **중요:**
- 테스트넷은 불안정할 수 있습니다
- 가끔 네트워크 지연이 발생할 수 있습니다
- Faucet이 일시적으로 작동하지 않을 수 있습니다
- 테스트넷 데이터는 주기적으로 리셋될 수 있습니다

✅ **권장사항:**
- 배포 전 로컬에서 충분히 테스트
- 배포 후 즉시 기능 테스트
- 배포 정보를 안전하게 보관
- 백업 계획 수립


