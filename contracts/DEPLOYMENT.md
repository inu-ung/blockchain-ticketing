# 스마트 컨트랙트 배포 가이드

## 로컬 네트워크 배포

### 1. 로컬 네트워크 실행

```bash
npx hardhat node
```

### 2. 배포 실행

```bash
npm run deploy
# 또는
npx hardhat run scripts/deploy.js --network localhost
```

### 3. 배포된 컨트랙트 주소

배포 후 `deployments/localhost.json` 파일에 주소가 저장됩니다.

## 테스트넷 배포 (Polygon Mumbai)

**📖 자세한 가이드는 [TESTNET_DEPLOYMENT.md](./TESTNET_DEPLOYMENT.md)를 참고하세요.**

### 빠른 시작

1. **환경 변수 설정**
   - `.env` 파일 생성 및 설정 (자세한 내용은 TESTNET_DEPLOYMENT.md 참고)

2. **테스트 MATIC 받기**
   - https://faucet.polygon.technology/ 에서 테스트 MATIC 받기

3. **배포 실행**
   ```bash
   npm run deploy:mumbai
   # 또는
   npx hardhat run scripts/deploy.js --network mumbai
   ```

4. **컨트랙트 검증**
   ```bash
   npm run verify:mumbai
   # 또는
   npx hardhat run scripts/verify.js --network mumbai
   ```

## 메인넷 배포 (Polygon)

### 주의사항

- 메인넷 배포 전 반드시 외부 감사를 받으세요
- 충분한 테스트를 완료하세요
- 배포 전 모든 환경 변수를 확인하세요

### 배포 실행

```bash
npx hardhat run scripts/deploy.js --network polygon
```

## 배포 순서

1. **TicketAccessControl** - 권한 관리 컨트랙트
2. **TicketNFT** - NFT 티켓 컨트랙트
3. **EventManager** - 이벤트 관리 컨트랙트
4. **TicketMarketplace** - 재판매 마켓플레이스
5. **RefundManager** - 환불 관리 컨트랙트

## 권한 설정

배포 후 자동으로 다음 권한이 설정됩니다:

- EventManager에 MINTER_ROLE 부여
- RefundManager에 BURNER_ROLE 부여

## 컨트랙트 검증

### Polygon Mumbai

```bash
npx hardhat verify --network mumbai <CONTRACT_ADDRESS> <CONSTRUCTOR_ARGS>
```

### Polygon Mainnet

```bash
npx hardhat verify --network polygon <CONTRACT_ADDRESS> <CONSTRUCTOR_ARGS>
```

## 테스트

모든 테스트 실행:

```bash
npm run test
```

특정 테스트 파일 실행:

```bash
npx hardhat test test/TicketSystem.test.js
```

## 문제 해결

### 가스비 부족

- 계정에 충분한 MATIC을 보유하고 있는지 확인하세요.

### 배포 실패

- 네트워크 연결 상태를 확인하세요.
- 환경 변수가 올바르게 설정되었는지 확인하세요.
- 컨트랙트 컴파일 오류가 없는지 확인하세요.

