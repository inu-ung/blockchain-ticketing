# Polygon Mumbai 테스트넷 배포 가이드

## 📋 목차
1. [테스트넷 개요](#테스트넷-개요)
2. [사전 준비사항](#사전-준비사항)
3. [환경 변수 설정](#환경-변수-설정)
4. [테스트 MATIC 받기](#테스트-matic-받기)
5. [배포 실행](#배포-실행)
6. [배포 확인](#배포-확인)
7. [컨트랙트 검증](#컨트랙트-검증)
8. [문제 해결](#문제-해결)

---

## 테스트넷 개요

### Polygon Mumbai
- **체인 ID**: 80001
- **RPC URL**: https://rpc-mumbai.maticvigil.com
- **Explorer**: https://mumbai.polygonscan.com
- **가스 통화**: MATIC (테스트넷)
- **블록 시간**: 약 2초

### 왜 테스트넷을 사용하나요?
- 실제 비용 없이 테스트 가능
- 메인넷 배포 전 최종 검증
- 다양한 시나리오 테스트
- 사용자 피드백 수집

---

## 사전 준비사항

### 1. 지갑 준비
- MetaMask 또는 다른 Web3 지갑 설치
- 새 지갑 생성 또는 기존 지갑 사용
- **중요**: 테스트넷용 지갑은 메인넷과 분리하는 것을 권장

### 2. 필요한 정보
- 지갑 개인키 또는 시드 문구
- Polygonscan API 키 (선택사항, 컨트랙트 검증용)

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

# 또는 다른 RPC 제공자 사용 가능:
# POLYGON_MUMBAI_RPC_URL=https://matic-mumbai.chainstacklabs.com
# POLYGON_MUMBAI_RPC_URL=https://rpc.ankr.com/polygon_mumbai

# 배포할 지갑의 개인키 (0x 제외)
PRIVATE_KEY=your-private-key-here-without-0x

# Polygonscan API 키 (컨트랙트 검증용, 선택사항)
POLYGONSCAN_API_KEY=your-polygonscan-api-key

# 네트워크 설정
NETWORK=mumbai
```

### 3. 개인키 확인 방법

**MetaMask에서 개인키 가져오기:**
1. MetaMask 열기
2. 설정 → 보안 및 개인정보 보호
3. 계정 내보내기 → 개인키 표시
4. 비밀번호 입력 후 개인키 복사
5. `0x` 접두사 제거 (또는 그대로 사용해도 됨)

**⚠️ 보안 주의사항:**
- 개인키는 절대 공유하지 마세요
- `.env` 파일은 `.gitignore`에 포함되어 있는지 확인
- GitHub에 업로드하지 마세요
- 테스트넷용 지웟만 사용하세요

### 4. RPC URL 옵션

여러 RPC 제공자가 있습니다:

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

### 방법 3: QuickNode Faucet

1. https://faucet.quicknode.com/polygon/mumbai 접속
2. 지갑 주소 입력
3. 소셜 미디어 인증 (선택사항)
4. MATIC 받기

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

```bash
npx hardhat run scripts/deploy.js --network mumbai
```

### 3. 배포 과정

배포가 시작되면 다음과 같은 과정이 진행됩니다:

```
1. TicketAccessControl 배포
   - 권한 관리 컨트랙트
   - 배포 시간: 약 10-30초

2. TicketNFT 배포
   - ERC-721 NFT 컨트랙트
   - 배포 시간: 약 10-30초

3. EventManager 배포
   - 이벤트 관리 컨트랙트
   - 배포 시간: 약 10-30초

4. TicketMarketplace 배포
   - 재판매 마켓플레이스
   - 배포 시간: 약 10-30초

5. RefundManager 배포
   - 환불 관리 컨트랙트
   - 배포 시간: 약 10-30초

6. 권한 설정
   - MINTER_ROLE 부여
   - BURNER_ROLE 부여
```

### 4. 배포 결과

성공적으로 배포되면 다음과 같은 출력이 표시됩니다:

```
=== Deployment Summary ===
Network: mumbai
Deployer: 0xYourAddress...

Contract Addresses:
TicketAccessControl: 0x...
TicketNFT: 0x...
EventManager: 0x...
TicketMarketplace: 0x...
RefundManager: 0x...

Deployment info saved to deployments/mumbai.json
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
// 컨트랙트 인스턴스 가져오기
const TicketNFT = await ethers.getContractFactory("TicketNFT");
const ticketNFT = await TicketNFT.attach("0x...배포된주소...");

// 함수 호출
const name = await ticketNFT.name();
console.log("Token Name:", name);
```

---

## 컨트랙트 검증

컨트랙트를 검증하면 Polygonscan에서 소스 코드를 확인할 수 있습니다.

### 1. Polygonscan API 키 발급

1. https://polygonscan.com/apis 접속
2. 계정 생성 (무료)
3. API 키 생성
4. `.env` 파일에 추가:
   ```
   POLYGONSCAN_API_KEY=your-api-key-here
   ```

### 2. 개별 컨트랙트 검증

각 컨트랙트를 개별적으로 검증:

```bash
# TicketAccessControl 검증
npx hardhat verify --network mumbai \
  <TICKET_ACCESS_CONTROL_ADDRESS> \
  <ADMIN_ADDRESS>

# TicketNFT 검증
npx hardhat verify --network mumbai \
  <TICKET_NFT_ADDRESS> \
  <ADMIN_ADDRESS>

# EventManager 검증
npx hardhat verify --network mumbai \
  <EVENT_MANAGER_ADDRESS> \
  <ACCESS_CONTROL_ADDRESS> \
  <TICKET_NFT_ADDRESS>

# TicketMarketplace 검증
npx hardhat verify --network mumbai \
  <MARKETPLACE_ADDRESS> \
  <ACCESS_CONTROL_ADDRESS> \
  <TICKET_NFT_ADDRESS> \
  <EVENT_MANAGER_ADDRESS> \
  <FEE_RECIPIENT_ADDRESS>

# RefundManager 검증
npx hardhat verify --network mumbai \
  <REFUND_MANAGER_ADDRESS> \
  <ACCESS_CONTROL_ADDRESS> \
  <TICKET_NFT_ADDRESS> \
  <EVENT_MANAGER_ADDRESS>
```

### 3. 자동 검증 스크립트

검증을 자동화하는 스크립트를 만들 수 있습니다:

```javascript
// scripts/verify.js
const hre = require("hardhat");
const fs = require("fs");

async function main() {
  const deployment = JSON.parse(
    fs.readFileSync("deployments/mumbai.json", "utf8")
  );

  // 각 컨트랙트 검증
  // ...
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
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

### 4. 검증 실패

**오류 메시지:**
```
Error: Contract verification failed
```

**해결 방법:**
- 생성자 인자 순서 확인
- 컴파일러 버전 확인
- 최적화 설정 확인

### 5. 권한 오류

**오류 메시지:**
```
Error: AccessControl: account is missing role
```

**해결 방법:**
- 배포 스크립트에서 권한 설정 확인
- 올바른 주소로 권한 부여 확인

---

## 배포 후 작업

### 1. 백엔드 설정 업데이트

배포된 컨트랙트 주소를 백엔드 `.env` 파일에 추가:

```env
TICKET_ACCESS_CONTROL_ADDRESS=0x...
TICKET_NFT_ADDRESS=0x...
EVENT_MANAGER_ADDRESS=0x...
MARKETPLACE_ADDRESS=0x...
REFUND_MANAGER_ADDRESS=0x...
```

### 2. 프론트엔드 설정 업데이트

프론트엔드 `.env` 파일에도 주소 추가:

```env
VITE_TICKET_ACCESS_CONTROL_ADDRESS=0x...
VITE_TICKET_NFT_ADDRESS=0x...
VITE_EVENT_MANAGER_ADDRESS=0x...
VITE_MARKETPLACE_ADDRESS=0x...
VITE_REFUND_MANAGER_ADDRESS=0x...
```

### 3. 테스트 실행

배포된 컨트랙트에 대해 통합 테스트 실행:

```bash
# 테스트넷에서 테스트 실행 (별도 테스트 파일 필요)
```

---

## 유용한 리소스

- **Polygon 문서**: https://docs.polygon.technology/
- **Hardhat 문서**: https://hardhat.org/docs
- **Polygonscan**: https://mumbai.polygonscan.com
- **Faucet 목록**: https://faucet.polygon.technology/

---

## 다음 단계

테스트넷 배포가 완료되면:

1. ✅ 컨트랙트 기능 테스트
2. ✅ 프론트엔드와 통합 테스트
3. ✅ 사용자 시나리오 테스트
4. ✅ 보안 감사 (선택사항)
5. ✅ 메인넷 배포 준비

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

