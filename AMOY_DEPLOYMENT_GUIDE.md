# Polygon Amoy 테스트넷 배포 가이드

## 📋 빠른 시작

### 1단계: 환경 변수 설정

`contracts/.env` 파일 생성 또는 확인:

```bash
cd contracts
```

`.env` 파일에 다음 내용 추가:

```env
# Polygon Amoy RPC URL
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology

# 배포할 지갑의 개인키 (0x 포함)
PRIVATE_KEY=0x...

# Polygonscan API 키 (컨트랙트 검증용, 선택사항)
POLYGONSCAN_API_KEY=...

# EntryPoint 주소 (ERC-4337 표준, 변경 불필요)
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

### 2단계: 테스트 MATIC 받기

1. **Polygon Faucet 접속**
   - https://faucet.polygon.technology/
   - 또는 https://www.alchemy.com/faucets/polygon-amoy

2. **지갑 주소 입력**
   - MetaMask에서 지갑 주소 복사
   - Faucet에 주소 입력
   - 캡차 완료 후 요청

3. **대기**
   - 보통 0.1-1 MATIC이 지급됩니다
   - 최소 0.5 MATIC 이상 권장

### 3단계: 배포 실행

```bash
cd contracts

# 컴파일 확인
npm run compile

# Amoy 테스트넷 배포
npm run deploy:amoy
```

### 4단계: 배포 확인

```bash
# 컨트랙트 검증 (선택사항)
npm run verify:amoy

# 배포 정보 확인
cat deployments/amoy.json
```

---

## 🔧 상세 설정

### RPC URL 옵션

#### 무료 옵션
- **Polygon 공식**: `https://rpc-amoy.polygon.technology`
- **Ankr**: `https://rpc.ankr.com/polygon_amoy`

#### 유료 옵션 (더 안정적)
- **Alchemy**: `https://polygon-amoy.g.alchemy.com/v2/YOUR-API-KEY`
- **Infura**: `https://polygon-amoy.infura.io/v3/YOUR-PROJECT-ID`

### Polygonscan API Key 발급

1. https://amoy.polygonscan.com/ 접속
2. 계정 생성 및 로그인
3. **API-KEYs** 메뉴 클릭
4. **Add** 클릭하여 새 API Key 생성

---

## 📊 배포 프로세스

배포가 시작되면 다음 순서로 진행됩니다:

```
[1/7] Deploying TicketAccessControl...
[2/7] Deploying TicketNFT...
[3/7] Deploying EventManager...
[4/7] Deploying TicketMarketplace...
[5/7] Deploying RefundManager...
[6/7] Deploying SmartWallet implementation...
[7/7] Deploying SmartWalletFactory...
[8/8] Setting up roles...
  ✅ Granted MINTER_ROLE to EventManager
  ✅ Granted BURNER_ROLE to RefundManager
```

각 단계는 약 10-30초 소요됩니다.

---

## ✅ 배포 성공 확인

### 1. 콘솔 출력 확인

배포 성공 시 다음과 같은 출력이 표시됩니다:

```
🎉 배포 완료!
============================================================
Network: amoy
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

💾 Deployment info saved to: deployments/amoy.json
```

### 2. Polygonscan에서 확인

- https://amoy.polygonscan.com/
- 배포된 컨트랙트 주소로 검색
- 트랜잭션 내역 확인

### 3. 배포 정보 파일 확인

```bash
cat contracts/deployments/amoy.json
```

---

## 🔄 백엔드/프론트엔드 설정

### 백엔드 환경 변수 업데이트

`backend/.env` 파일에 배포된 주소 추가:

```env
# Polygon Amoy Testnet
WEB3_PROVIDER_URL=https://rpc-amoy.polygon.technology
EVENT_MANAGER_ADDRESS=0x...
TICKET_NFT_ADDRESS=0x...
TICKET_MARKETPLACE_ADDRESS=0x...
REFUND_MANAGER_ADDRESS=0x...
SMART_WALLET_FACTORY_ADDRESS=0x...
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
CHAIN_ID=80002
```

### 프론트엔드 환경 변수 업데이트

`frontend/.env` 파일에 배포된 주소 추가:

```env
# Polygon Amoy Testnet
VITE_WEB3_PROVIDER_URL=https://rpc-amoy.polygon.technology
VITE_EVENT_MANAGER_ADDRESS=0x...
VITE_TICKET_NFT_ADDRESS=0x...
VITE_TICKET_MARKETPLACE_ADDRESS=0x...
VITE_REFUND_MANAGER_ADDRESS=0x...
VITE_SMART_WALLET_FACTORY_ADDRESS=0x...
VITE_ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
VITE_CHAIN_ID=80002
```

---

## 🛠️ 트러블슈팅

### 잔액 부족

**증상**: `insufficient funds for gas`

**해결**:
1. Faucet에서 테스트 MATIC 받기
2. 최소 0.5 MATIC 이상 권장

### RPC 연결 실패

**증상**: `ECONNREFUSED`, `timeout`

**해결**:
1. RPC URL 확인
2. 다른 RPC 제공자로 변경
3. 네트워크 상태 확인

### 배포 실패

**증상**: 특정 컨트랙트 배포 실패

**해결**:
1. 배포 재개 스크립트 사용:
   ```bash
   npm run deploy:amoy:resume
   ```
2. 이미 배포된 컨트랙트는 재사용

---

## 📝 체크리스트

배포 전:
- [ ] `.env` 파일에 모든 환경 변수 설정
- [ ] 배포자 계정에 테스트 MATIC 보유 (최소 0.5 MATIC)
- [ ] 로컬에서 컴파일 성공 확인

배포 후:
- [ ] 모든 컨트랙트 배포 성공 확인
- [ ] Polygonscan에서 컨트랙트 확인
- [ ] 배포 정보 파일 저장 확인
- [ ] 백엔드 환경 변수 업데이트
- [ ] 프론트엔드 환경 변수 업데이트

---

## 🔗 유용한 링크

- **Polygon Amoy Explorer**: https://amoy.polygonscan.com/
- **Polygon Faucet**: https://faucet.polygon.technology/
- **Alchemy Faucet**: https://www.alchemy.com/faucets/polygon-amoy
- **Polygon 공식 문서**: https://docs.polygon.technology/

