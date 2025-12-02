# Smart Wallet 테스트 가이드

## 사전 준비

### 1. 서비스 실행 확인

**터미널 1: Hardhat 노드**
```bash
cd contracts
npx hardhat node
```

**터미널 2: 백엔드 서버**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

**터미널 3: 프론트엔드 서버**
```bash
cd frontend
npm run dev
```

### 2. 컨트랙트 배포 확인

Smart Wallet이 배포되어 있는지 확인:
```bash
cd contracts
cat deployments/localhost.json | grep SmartWallet
```

배포되지 않았다면:
```bash
cd contracts
npx hardhat run scripts/deploy_smart_wallet.js --network localhost
```

## 테스트 방법

### 방법 1: 프론트엔드에서 테스트 (추천)

1. **브라우저 접속**
   - http://localhost:5173

2. **회원가입/로그인**
   - 회원가입 또는 로그인
   - 이메일/비밀번호로 로그인

3. **지갑 연결**
   - 로그인 후 상단에 "지갑 연결" 버튼이 보임
   - 클릭하면 Smart Wallet이 자동으로 생성됨
   - Smart Wallet 주소가 표시됨

4. **확인 사항**
   - Smart Wallet 주소가 표시되는지
   - 잔액이 표시되는지 (0 ETH일 수 있음)
   - 네트워크 정보가 표시되는지

### 방법 2: API로 직접 테스트

#### 1. 사용자 등록
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "role": "buyer"
  }'
```

응답에서 `id`를 복사하세요.

#### 2. 로그인
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123"
  }'
```

응답에서 `access_token`을 복사하세요.

#### 3. Smart Wallet 생성
```bash
TOKEN="여기에_받은_토큰_입력"

curl -X POST http://localhost:8000/api/v1/auth/wallet/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN"
```

응답 예시:
```json
{
  "message": "Smart wallet created successfully",
  "smart_wallet_address": "0x..."
}
```

#### 4. Smart Wallet 주소 확인
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

응답에서 `smart_wallet_address` 확인

### 방법 3: Swagger UI에서 테스트

1. **브라우저 접속**
   - http://localhost:8000/docs

2. **인증**
   - `/api/v1/auth/register`로 회원가입
   - `/api/v1/auth/login`으로 로그인
   - 상단 "Authorize" 버튼 클릭
   - 받은 토큰 입력 (형식: `Bearer <토큰>`)

3. **Smart Wallet 생성**
   - `/api/v1/auth/wallet/create` 엔드포인트 찾기
   - "Try it out" 클릭
   - "Execute" 클릭
   - 응답에서 `smart_wallet_address` 확인

4. **사용자 정보 확인**
   - `/api/v1/auth/me` 엔드포인트
   - "Execute" 클릭
   - `smart_wallet_address` 확인

## 확인 사항

### ✅ 정상 동작 시
- Smart Wallet 주소가 생성됨
- 같은 사용자로 다시 호출해도 같은 주소 반환
- DB에 `smart_wallet_address` 저장됨

### ❌ 문제 발생 시

**문제 1: "SmartWalletFactory address not configured"**
- 해결: `backend/.env` 파일에 `SMART_WALLET_FACTORY_ADDRESS` 추가
- 값: `0x09635F643e140090A9A8Dcd712eD6285858ceBef`

**문제 2: "Web3 not connected"**
- 해결: Hardhat 노드가 실행 중인지 확인
- 포트 8545 확인

**문제 3: "Transaction failed"**
- 해결: Hardhat 노드에 이더가 있는지 확인
- 컨트랙트가 배포되어 있는지 확인

## 체크리스트

- [ ] Hardhat 노드 실행 중
- [ ] 백엔드 서버 실행 중
- [ ] 프론트엔드 서버 실행 중
- [ ] Smart Wallet 컨트랙트 배포됨
- [ ] `.env` 파일에 Factory 주소 설정됨
- [ ] 사용자 등록/로그인 성공
- [ ] Smart Wallet 주소 생성 성공
- [ ] 같은 주소가 반환되는지 확인 (CREATE2)

## 다음 단계

Smart Wallet이 정상적으로 생성되면:
1. 실제 트랜잭션 테스트 (티켓 구매 등)
2. UserOperation 생성 테스트
3. Bundler 연동 테스트

