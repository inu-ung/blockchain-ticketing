# 빠른 테스트 가이드

## 1단계: 서비스 실행

### 터미널 1: Hardhat 노드
```bash
cd contracts
npx hardhat node
```

### 터미널 2: 백엔드
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### 터미널 3: 프론트엔드
```bash
cd frontend
npm run dev
```

## 2단계: 테스트

### 방법 A: 프론트엔드 (가장 쉬움)
1. 브라우저: http://localhost:5173
2. 회원가입/로그인
3. "지갑 연결" 버튼 클릭
4. Smart Wallet 주소 확인 ✅

### 방법 B: Swagger UI
1. 브라우저: http://localhost:8000/docs
2. `/api/v1/auth/register` - 회원가입
3. `/api/v1/auth/login` - 로그인
4. 상단 "Authorize"에 토큰 입력
5. `/api/v1/auth/wallet/create` - Smart Wallet 생성
6. `/api/v1/auth/me` - 주소 확인 ✅

## 확인
- Smart Wallet 주소가 생성되는가?
- 같은 사용자로 다시 호출해도 같은 주소인가?

