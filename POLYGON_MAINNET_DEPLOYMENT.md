# Polygon 메인넷 배포 가이드

## ⚠️ 중요 주의사항

**메인넷 배포는 실제 자금이 사용됩니다!**

- 배포 전 **반드시 테스트넷에서 충분히 테스트**하세요
- 외부 보안 감사를 받는 것을 **강력히 권장**합니다
- 배포 전 모든 환경 변수를 **반드시 확인**하세요
- 배포 후에는 **수정이 불가능**합니다

---

## 📋 사전 준비사항

### 1. 테스트넷 배포 완료 확인

메인넷 배포 전에 테스트넷에서 모든 기능이 정상 작동하는지 확인:

```bash
# 테스트넷 배포 및 테스트 완료 확인
```

### 2. 보안 감사 (권장)

- 스마트 컨트랙트 보안 감사 받기
- 코드 리뷰 완료
- 모든 테스트 통과 확인

### 3. 가스비 준비

Polygon 메인넷 배포에 필요한 MATIC:
- 전체 컨트랙트 배포: 약 **0.1 - 0.5 MATIC**
- 권장: 최소 **1 MATIC** 이상 보유

---

## 🔧 환경 설정

### 1. `.env` 파일 설정

`contracts/.env` 파일 생성 또는 수정:

```bash
# 배포자 개인키 (0x로 시작)
PRIVATE_KEY=0x...

# Polygon 메인넷 RPC URL
POLYGON_MAINNET_RPC_URL=https://polygon-rpc.com
# 또는 더 안정적인 RPC 제공자:
# Alchemy: https://polygon-mainnet.g.alchemy.com/v2/YOUR-API-KEY
# Infura: https://polygon-mainnet.infura.io/v3/YOUR-PROJECT-ID

# Polygonscan API Key (컨트랙트 검증용)
POLYGONSCAN_API_KEY=...

# ERC-4337 EntryPoint 주소 (기본값 사용 가능)
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

### 2. RPC 제공자 선택

#### 무료 옵션
- **Polygon 공식**: `https://polygon-rpc.com`
- **Ankr**: `https://rpc.ankr.com/polygon`

#### 유료 옵션 (더 안정적, 권장)
- **Alchemy**: https://www.alchemy.com/
  - 무료 티어: 300M compute units/month
  - URL: `https://polygon-mainnet.g.alchemy.com/v2/YOUR-API-KEY`
  
- **Infura**: https://www.infura.io/
  - 무료 티어: 100k requests/day
  - URL: `https://polygon-mainnet.infura.io/v3/YOUR-PROJECT-ID`

### 3. Polygonscan API Key 발급

1. https://polygonscan.com/ 접속
2. 계정 생성 및 로그인
3. **API-KEYs** 메뉴 클릭
4. **Add** 클릭하여 새 API Key 생성
5. 생성된 API Key를 `.env`에 추가

---

## 🚀 배포 방법

### 방법 1: 수동 배포 (로컬)

#### Step 1: 컴파일 확인

```bash
cd contracts
npm run compile
```

#### Step 2: 테스트 실행 (선택사항)

```bash
npm test
```

#### Step 3: 배포 실행

```bash
# 전체 컨트랙트 배포
npm run deploy:polygon

# 또는 직접 실행
npx hardhat run scripts/deploy_all.js --network polygon
```

#### Step 4: 배포 결과 확인

배포가 성공하면 다음과 같은 출력이 표시됩니다:

```
🎉 배포 완료!
============================================================
Network: polygon
Deployer: 0x...

📋 Contract Addresses:
  TicketAccessControl: 0x...
  TicketNFT: 0x...
  EventManager: 0x...
  TicketMarketplace: 0x...
  RefundManager: 0x...
  SmartWallet: 0x...
  SmartWalletFactory: 0x...
  EntryPoint: 0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789

💾 Deployment info saved to: deployments/polygon.json
```

#### Step 5: 컨트랙트 검증

```bash
npm run verify:polygon

# 또는 직접 실행
npx hardhat run scripts/verify.js --network polygon
```

---

### 방법 2: 자동 배포 (CI/CD)

#### GitHub Actions 사용

1. **GitHub Secrets 설정** (이미 설정했다면 생략)
   - `DEPLOYER_PRIVATE_KEY`
   - `POLYGON_MAINNET_RPC_URL`
   - `POLYGONSCAN_API_KEY`
   - `ENTRY_POINT_ADDRESS`

2. **main 브랜치에 Push**

```bash
git checkout main
git push origin main
```

3. **GitHub Actions에서 확인**
   - Repository → **Actions** 탭
   - 워크플로우 실행 확인
   - 배포 완료 대기

#### 수동 트리거

1. GitHub Repository → **Actions** 탭
2. **"Deploy Smart Contracts"** 선택
3. **"Run workflow"** 클릭
4. Network: **polygon** 선택
5. **"Run workflow"** 버튼 클릭

---

## 📊 배포 순서

자동으로 다음 순서로 배포됩니다:

1. **TicketAccessControl** - 권한 관리 컨트랙트
2. **TicketNFT** - NFT 티켓 컨트랙트
3. **EventManager** - 이벤트 관리 컨트랙트
4. **TicketMarketplace** - 재판매 마켓플레이스
5. **RefundManager** - 환불 관리 컨트랙트
6. **SmartWallet** - ERC-4337 스마트 지갑 (구현)
7. **SmartWalletFactory** - Smart Wallet 팩토리
8. **권한 설정**
   - EventManager에 MINTER_ROLE 부여
   - RefundManager에 BURNER_ROLE 부여

---

## ✅ 배포 후 확인

### 1. Polygonscan에서 확인

각 컨트랙트 주소를 Polygonscan에서 검색:
- https://polygonscan.com/

**확인 사항**:
- ✅ 트랜잭션 내역 확인
- ✅ 컨트랙트 코드 검증 상태 확인
- ✅ 컨트랙트 소스 코드 확인

### 2. 배포 정보 파일 확인

```bash
cat contracts/deployments/polygon.json
```

### 3. 백엔드/프론트엔드 환경 변수 업데이트

#### 백엔드 (`backend/.env`)

```bash
# Polygon Mainnet
WEB3_PROVIDER_URL=https://polygon-rpc.com
EVENT_MANAGER_ADDRESS=0x...
TICKET_NFT_ADDRESS=0x...
TICKET_MARKETPLACE_ADDRESS=0x...
REFUND_MANAGER_ADDRESS=0x...
SMART_WALLET_FACTORY_ADDRESS=0x...
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
CHAIN_ID=137
```

#### 프론트엔드 (`frontend/.env`)

```bash
# Polygon Mainnet
VITE_WEB3_PROVIDER_URL=https://polygon-rpc.com
VITE_EVENT_MANAGER_ADDRESS=0x...
VITE_TICKET_NFT_ADDRESS=0x...
VITE_TICKET_MARKETPLACE_ADDRESS=0x...
VITE_REFUND_MANAGER_ADDRESS=0x...
VITE_SMART_WALLET_FACTORY_ADDRESS=0x...
VITE_ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
VITE_CHAIN_ID=137
```

---

## 🔍 트러블슈팅

### 배포 실패 시

#### 1. 잔액 부족

**증상**: `insufficient funds for gas`

**해결**:
- 배포자 계정에 충분한 MATIC 확인
- 최소 1 MATIC 이상 권장

#### 2. RPC 연결 실패

**증상**: `ECONNREFUSED`, `timeout`

**해결**:
- RPC URL 확인
- 다른 RPC 제공자로 변경 (Alchemy, Infura)
- 네트워크 상태 확인

#### 3. Nonce 오류

**증상**: `nonce too high`

**해결**:
- 지갑에서 최근 트랜잭션 확인
- 잠시 대기 후 재시도

#### 4. 검증 실패

**증상**: `Contract verification failed`

**해결**:
- Polygonscan API Key 확인
- 네트워크와 API Key 일치 확인
- 수동 검증 시도:
  ```bash
  npx hardhat verify --network polygon <CONTRACT_ADDRESS> <CONSTRUCTOR_ARGS>
  ```

---

## 📝 배포 체크리스트

배포 전 확인:

- [ ] 테스트넷에서 모든 기능 테스트 완료
- [ ] 보안 감사 완료 (권장)
- [ ] `.env` 파일에 모든 환경 변수 설정
- [ ] 배포자 계정에 충분한 MATIC (최소 1 MATIC)
- [ ] RPC URL이 올바른지 확인
- [ ] Polygonscan API Key 설정
- [ ] 로컬에서 컴파일 성공 확인
- [ ] 배포 스크립트 테스트 (선택사항)

배포 후 확인:

- [ ] 모든 컨트랙트 배포 성공
- [ ] Polygonscan에서 컨트랙트 확인
- [ ] 컨트랙트 검증 완료
- [ ] 배포 정보 파일 저장 확인
- [ ] 백엔드 환경 변수 업데이트
- [ ] 프론트엔드 환경 변수 업데이트
- [ ] 통합 테스트 실행

---

## 💡 유용한 팁

### 1. 가스비 절약

- 배포는 한 번만 실행 (중복 배포 방지)
- 배포 전 모든 설정 확인

### 2. 배포 정보 백업

```bash
# 배포 정보 파일 복사
cp contracts/deployments/polygon.json ~/backup/
```

### 3. 배포 로그 저장

```bash
# 배포 로그 저장
npm run deploy:polygon 2>&1 | tee deployment.log
```

### 4. 단계별 배포 (선택사항)

전체 배포가 실패할 경우를 대비해 단계별 배포 스크립트 사용 가능

---

## 🔗 관련 링크

- **Polygonscan**: https://polygonscan.com/
- **Polygon 공식 문서**: https://docs.polygon.technology/
- **Alchemy**: https://www.alchemy.com/
- **Infura**: https://www.infura.io/
- **Hardhat 문서**: https://hardhat.org/docs

---

## 📞 지원

배포 중 문제가 발생하면:

1. GitHub Actions 로그 확인
2. Polygonscan에서 트랜잭션 상태 확인
3. 로컬에서 동일한 명령어 실행하여 오류 재현
4. 환경 변수 및 설정 재확인

