# 자동 배포 시스템 (Automated Deployment)

## 개요

스마트 컨트랙트 배포를 자동화하여 **CI/CD 파이프라인**을 구축했습니다. 코드 변경 시 자동으로 테스트, 컴파일, 배포, 검증이 수행됩니다.

---

## 자동 배포 아키텍처

```
GitHub Repository
    ↓ (Push/PR)
GitHub Actions (CI/CD)
    ├── 테스트 실행
    ├── 컨트랙트 컴파일
    ├── 네트워크 선택 (자동)
    │   ├── main 브랜치 → Polygon Mainnet
    │   └── develop 브랜치 → Polygon Amoy (테스트넷)
    ├── 스마트 컨트랙트 배포
    ├── 컨트랙트 검증 (Polygonscan)
    └── 배포 정보 저장 (Artifacts)
```

---

## 자동 배포 트리거

### 1. 자동 트리거
- **main 브랜치에 Push** → Polygon Mainnet 배포
- **develop 브랜치에 Push** → Polygon Amoy (테스트넷) 배포
- **Pull Request 생성** → 테스트만 실행 (배포 안 함)

### 2. 수동 트리거 (Workflow Dispatch)
- GitHub Actions에서 수동으로 실행 가능
- 네트워크 선택 (amoy/polygon)
- 테스트 건너뛰기 옵션

---

## 배포 프로세스

### Step 1: 코드 체크아웃
```yaml
- Checkout code from GitHub
```

### Step 2: 환경 설정
```yaml
- Setup Node.js 18
- Install npm dependencies
```

### Step 3: 테스트 실행
```bash
npm test
```
- 모든 스마트 컨트랙트 테스트 실행
- 테스트 실패 시 배포 중단

### Step 4: 컨트랙트 컴파일
```bash
npm run compile
```
- Solidity 컨트랙트 컴파일
- 컴파일 오류 시 배포 중단

### Step 5: 네트워크 선택
- **main 브랜치** → `polygon` (메인넷)
- **develop 브랜치** → `amoy` (테스트넷)
- **수동 실행** → 사용자 선택

### Step 6: 스마트 컨트랙트 배포
```bash
npm run deploy:amoy  # 또는 deploy:polygon
```

**배포 순서**:
1. TicketAccessControl
2. TicketNFT
3. EventManager
4. TicketMarketplace
5. RefundManager
6. SmartWallet (구현)
7. SmartWalletFactory
8. 권한 설정 (MINTER_ROLE, BURNER_ROLE)

### Step 7: 컨트랙트 검증
```bash
npm run verify:amoy  # 또는 verify:polygon
```
- Polygonscan에서 컨트랙트 소스 코드 검증
- 검증 실패해도 배포는 성공 (경고만)

### Step 8: 배포 정보 저장
- `deployments/{network}.json` 파일 생성
- GitHub Artifacts로 저장 (90일 보관)

---

## GitHub Secrets 설정

자동 배포를 위해 다음 Secrets를 GitHub에 설정해야 합니다:

### 필수 Secrets

```bash
# 배포자 개인키
DEPLOYER_PRIVATE_KEY=0x...

# RPC URL
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
POLYGON_MAINNET_RPC_URL=https://polygon-rpc.com

# EntryPoint 주소 (ERC-4337)
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789

# Polygonscan API Key (검증용)
POLYGONSCAN_API_KEY=...
```

### Secrets 설정 방법

1. GitHub Repository → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret** 클릭
3. 위의 각 Secret 추가

---

## 배포 스크립트

### 자동 배포 스크립트 (`deploy_auto.js`)

```javascript
// 환경 변수로 제어
NETWORK=amoy npm run deploy:auto
```

**특징**:
- CI/CD 환경 자동 감지
- 배포 정보 JSON 출력
- 에러 발생 시 즉시 중단

### 수동 배포 스크립트 (`deploy_all.js`)

```bash
# 로컬에서 수동 배포
npm run deploy:amoy
npm run deploy:polygon
```

---

## 배포 결과 확인

### 1. GitHub Actions 로그
- **Actions** 탭에서 배포 진행 상황 확인
- 각 단계별 로그 확인 가능

### 2. 배포 정보 파일
```json
{
  "network": "amoy",
  "deployer": "0x...",
  "entryPoint": "0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789",
  "contracts": {
    "TicketAccessControl": "0x...",
    "TicketNFT": "0x...",
    "EventManager": "0x...",
    "TicketMarketplace": "0x...",
    "RefundManager": "0x...",
    "SmartWallet": "0x...",
    "SmartWalletFactory": "0x..."
  },
  "timestamp": "2024-01-01T00:00:00.000Z",
  "commitHash": "abc123...",
  "branch": "develop"
}
```

### 3. GitHub Artifacts
- 배포 완료 후 Artifacts에서 다운로드 가능
- 90일간 보관

### 4. Polygonscan
- 배포된 컨트랙트 주소로 검색
- 검증 완료 시 소스 코드 확인 가능

---

## 배포 전략

### 1. 브랜치 전략
```
main (프로덕션)
  ↓ 자동 배포 → Polygon Mainnet
  
develop (개발)
  ↓ 자동 배포 → Polygon Amoy (테스트넷)
  
feature/* (기능 개발)
  ↓ Pull Request → 테스트만 실행
```

### 2. 롤백 전략
- 배포 실패 시 자동 중단
- 이전 배포 정보는 Artifacts에 보관
- 수동으로 이전 버전 재배포 가능

### 3. 검증 전략
- 배포 후 자동 검증 시도
- 검증 실패해도 배포는 성공 (수동 검증 가능)

---

## 자동 배포의 장점

### 1. **일관성**
- 동일한 프로세스로 반복 배포
- 수동 실수 방지

### 2. **투명성**
- 모든 배포 기록이 GitHub에 저장
- 누가, 언제, 무엇을 배포했는지 추적 가능

### 3. **안전성**
- 배포 전 자동 테스트 실행
- 테스트 실패 시 배포 중단

### 4. **효율성**
- 수동 작업 최소화
- 배포 시간 단축

### 5. **검증 자동화**
- Polygonscan 자동 검증
- 소스 코드 공개 자동화

---

## 수동 배포 (로컬)

자동 배포를 사용하지 않고 로컬에서 수동 배포:

```bash
cd contracts

# 환경 변수 설정
export PRIVATE_KEY=0x...
export POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
export POLYGONSCAN_API_KEY=...

# 배포
npm run deploy:amoy

# 검증
npm run verify:amoy
```

---

## 트러블슈팅

### 배포 실패 시

1. **잔액 부족**
   - 배포자 계정에 충분한 MATIC/ETH 확인
   - 테스트넷: https://faucet.polygon.technology/

2. **RPC 연결 실패**
   - RPC URL 확인
   - 대체 RPC 제공자 사용

3. **검증 실패**
   - Polygonscan API Key 확인
   - 네트워크와 API Key 일치 확인

4. **권한 오류**
   - GitHub Secrets 설정 확인
   - Secrets 이름 정확히 확인

---

## 발표용 요약

### 자동 배포 시스템의 핵심

1. **CI/CD 파이프라인**
   - GitHub Actions 기반
   - 코드 변경 시 자동 배포

2. **네트워크 자동 선택**
   - main → 메인넷
   - develop → 테스트넷

3. **전체 프로세스 자동화**
   - 테스트 → 컴파일 → 배포 → 검증

4. **배포 정보 자동 저장**
   - JSON 파일 생성
   - GitHub Artifacts 보관

5. **안전한 배포**
   - 테스트 실패 시 중단
   - 배포 기록 추적

---

## 다음 단계

배포 후:

1. **백엔드 환경 변수 업데이트**
   ```bash
   # backend/.env
   EVENT_MANAGER_ADDRESS=0x...
   TICKET_NFT_ADDRESS=0x...
   # ...
   ```

2. **프론트엔드 환경 변수 업데이트**
   ```bash
   # frontend/.env
   VITE_EVENT_MANAGER_ADDRESS=0x...
   VITE_TICKET_NFT_ADDRESS=0x...
   # ...
   ```

3. **통합 테스트**
   - 배포된 컨트랙트와 백엔드/프론트엔드 연동 테스트

