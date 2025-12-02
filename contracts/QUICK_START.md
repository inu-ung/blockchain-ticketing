# 빠른 시작 가이드 - 테스트넷 배포

## 5분 안에 테스트넷 배포하기

### 1단계: 환경 변수 설정 (1분)

`contracts` 디렉토리에 `.env` 파일 생성:

```bash
cd contracts
cat > .env << EOF
POLYGON_MUMBAI_RPC_URL=https://rpc-mumbai.maticvigil.com
PRIVATE_KEY=your-private-key-here
POLYGONSCAN_API_KEY=your-api-key-here
EOF
```

**개인키 가져오기:**
- MetaMask → 설정 → 보안 및 개인정보 보호 → 계정 내보내기
- `0x` 접두사는 포함하거나 제외해도 됩니다

### 2단계: 테스트 MATIC 받기 (2분)

1. https://faucet.polygon.technology/ 접속
2. 지갑 주소 입력 (MetaMask에서 복사)
3. 캡차 완료 후 "Submit" 클릭
4. 0.1-1 MATIC이 지급됩니다 (몇 분 소요)

**다른 Faucet 옵션:**
- Alchemy: https://www.alchemy.com/faucets/polygon-mumbai
- QuickNode: https://faucet.quicknode.com/polygon/mumbai

### 3단계: 배포 실행 (2분)

```bash
npm run deploy:mumbai
```

배포가 완료되면 다음과 같은 출력이 표시됩니다:

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
```

### 4단계: 배포 확인

1. **Polygonscan에서 확인**
   - https://mumbai.polygonscan.com 접속
   - 컨트랙트 주소 검색
   - 트랜잭션 내역 확인

2. **배포 정보 확인**
   ```bash
   cat deployments/mumbai.json
   ```

### 5단계: 컨트랙트 검증 (선택사항)

```bash
npm run verify:mumbai
```

---

## 문제 해결

### 가스비 부족
- Faucet에서 더 많은 MATIC 받기
- 최소 0.5 MATIC 권장

### 네트워크 연결 오류
- RPC URL 확인
- 다른 RPC 제공자로 변경 시도

### 자세한 가이드
- 전체 가이드: [TESTNET_DEPLOYMENT.md](./TESTNET_DEPLOYMENT.md)

---

## 다음 단계

배포 완료 후:
1. ✅ 백엔드 `.env`에 컨트랙트 주소 추가
2. ✅ 프론트엔드 `.env`에 컨트랙트 주소 추가
3. ✅ 통합 테스트 실행

