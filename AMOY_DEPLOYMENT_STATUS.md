# Amoy 테스트넷 배포 상태

## 현재 상태

### 배포 계정 정보
- **주소**: `0x3871a30CD3B9cDb3d8176CDf6D557a24a2CEA64d`
- **현재 잔액**: 0.043 MATIC
- **필요한 잔액**: 약 0.1-0.2 MATIC

### 배포 진행 상황

✅ **완료된 컨트랙트:**
- TicketAccessControl: `0xC587e94932D70bf43299765f5c9C8cC70AFfb611`

❌ **배포 실패 (가스비 부족):**
- TicketNFT
- EventManager
- TicketMarketplace
- RefundManager
- SmartWallet
- SmartWalletFactory

---

## 다음 단계

### 1. 테스트 MATIC 받기

다음 Faucet 중 하나에서 테스트 MATIC을 받으세요:

1. **Polygon 공식 Faucet**
   - URL: https://faucet.polygon.technology/
   - 주소 입력: `0x3871a30CD3B9cDb3d8176CDf6D557a24a2CEA64d`

2. **Alchemy Faucet**
   - URL: https://www.alchemy.com/faucets/polygon-amoy
   - 주소 입력: `0x3871a30CD3B9cDb3d8176CDf6D557a24a2CEA64d`

3. **QuickNode Faucet**
   - URL: https://faucet.quicknode.com/polygon/amoy
   - 주소 입력: `0x3871a30CD3B9cDb3d8176CDf6D557a24a2CEA64d`

### 2. 잔액 확인

```bash
cd contracts
node -e "const ethers = require('ethers'); const provider = new ethers.JsonRpcProvider('https://rpc-amoy.polygon.technology'); const privateKey = process.env.PRIVATE_KEY || '595da0d85a1d933296ac2876ce788b824b2ff495239f516eaa6ba321d98219fd'; const wallet = new ethers.Wallet(privateKey, provider); wallet.getAddress().then(addr => { console.log('주소:', addr); return provider.getBalance(addr); }).then(balance => console.log('잔액:', ethers.formatEther(balance), 'MATIC'));"
```

### 3. 배포 재개

잔액이 충분해지면 (0.1 MATIC 이상):

```bash
cd contracts
npm run deploy:amoy:resume
```

또는 처음부터 다시 배포:

```bash
cd contracts
npm run deploy:amoy
```

---

## 배포 완료 후

배포가 완료되면 `contracts/deployments/amoy.json` 파일에 모든 컨트랙트 주소가 저장됩니다.

이 주소들을:
1. 백엔드 `.env` 파일에 설정
2. 프론트엔드 `.env` 파일에 설정 (Vercel 환경 변수)
3. EC2 배포 시 사용

---

## 참고

- Amoy 테스트넷 Chain ID: 80002
- RPC URL: https://rpc-amoy.polygon.technology
- Explorer: https://amoy.polygonscan.com

