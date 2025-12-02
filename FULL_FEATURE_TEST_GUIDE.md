# 전체 기능 테스트 가이드

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
uvicorn main:app --reload
```

**터미널 3: 프론트엔드 서버**
```bash
cd frontend
npm run dev
```

**터미널 4: PostgreSQL (Docker)**
```bash
docker-compose up -d
```

### 2. 컨트랙트 배포 확인

```bash
cd contracts
cat deployments/localhost.json
```

배포되지 않았다면:
```bash
cd contracts
npx hardhat run scripts/deploy.js --network localhost
npx hardhat run scripts/grant_roles.js --network localhost
```

## 테스트 시나리오

### 시나리오 1: 이벤트 생성 및 승인

1. **주최자 계정 생성**
   - 프론트엔드: http://localhost:5173/register
   - 이메일: `organizer@test.com`
   - 비밀번호: `test123`
   - 역할: `organizer` (또는 회원가입 후 관리자가 역할 변경)

2. **로그인**
   - 프론트엔드: http://localhost:5173/login
   - 이메일: `organizer@test.com`
   - 비밀번호: `test123`

3. **Smart Wallet 연결**
   - 로그인 후 자동으로 연결됨
   - 또는 "지갑 연결" 버튼 클릭

4. **이벤트 생성**
   - 프론트엔드: http://localhost:5173/create-event
   - 이벤트 정보 입력:
     - 이름: `Test Concert`
     - 설명: `Test concert description`
     - 가격: `100` (MATIC)
     - 최대 티켓 수: `100`
     - 판매 시작: 미래 날짜
     - 판매 종료: 미래 날짜
     - 이벤트 날짜: 미래 날짜
   - "이벤트 생성" 버튼 클릭
   - ✅ 성공 메시지 확인

5. **관리자 계정으로 이벤트 승인**
   - 관리자 계정 생성/로그인
   - 프론트엔드: http://localhost:5173/admin
   - 대기 중인 이벤트 목록 확인
   - "승인" 버튼 클릭
   - ✅ 이벤트 상태가 "승인됨"으로 변경

### 시나리오 2: 티켓 구매

1. **구매자 계정 생성**
   - 프론트엔드: http://localhost:5173/register
   - 이메일: `buyer@test.com`
   - 비밀번호: `test123`
   - 역할: `buyer`

2. **로그인 및 지갑 연결**
   - 로그인 후 Smart Wallet 자동 연결

3. **이벤트 목록 확인**
   - 프론트엔드: http://localhost:5173/events
   - 승인된 이벤트 확인

4. **이벤트 상세 페이지**
   - 이벤트 클릭
   - 이벤트 정보 확인

5. **티켓 구매**
   - "티켓 구매" 버튼 클릭
   - ✅ 구매 성공 메시지 확인
   - ✅ 내 티켓 페이지에서 확인

### 시나리오 3: 재판매 등록 및 구매

1. **재판매 등록**
   - 프론트엔드: http://localhost:5173/tickets
   - 구매한 티켓 확인
   - "재판매 등록" 버튼 클릭 (있다면)
   - 또는 API로 직접 호출:
     ```bash
     POST /api/v1/resales
     {
       "ticket_id": "티켓_ID",
       "price_wei": 1500000000000000000  # 1.5 MATIC
     }
     ```
   - ✅ 재판매 등록 성공

2. **재판매 마켓플레이스 확인**
   - 프론트엔드: http://localhost:5173/marketplace
   - 등록된 재판매 티켓 확인

3. **다른 구매자로 재판매 구매**
   - 새로운 구매자 계정 생성/로그인
   - 마켓플레이스에서 티켓 확인
   - "구매하기" 버튼 클릭
   - ✅ 구매 성공
   - ✅ 내 티켓에서 확인

### 시나리오 4: 환불 요청 및 승인

1. **환불 요청**
   - 프론트엔드: http://localhost:5173/tickets
   - 티켓 확인
   - "환불 요청" 버튼 클릭 (있다면)
   - 또는 API로 직접 호출:
     ```bash
     POST /api/v1/refunds/request
     {
       "ticket_id": "티켓_ID",
       "reason": "Test refund"
     }
     ```
   - ✅ 환불 요청 성공

2. **주최자로 환불 승인**
   - 주최자 계정으로 로그인
   - 환불 요청 목록 확인
   - "승인" 버튼 클릭
   - ✅ 환불 승인 성공
   - ✅ 티켓 상태가 "환불됨"으로 변경

## 백엔드 통합 테스트

```bash
cd backend
source venv/bin/activate
python test_integration.py
```

## 확인 사항

### ✅ 정상 작동 시
- 모든 API 호출이 성공 (200/201 상태 코드)
- 데이터베이스에 정상 저장
- 온체인 트랜잭션 성공
- 프론트엔드에서 데이터 정상 표시

### ❌ 문제 발생 시

**문제 1: "Wallet not connected"**
- 해결: Smart Wallet 연결 확인
- 프론트엔드에서 "지갑 연결" 버튼 클릭

**문제 2: "Event not approved"**
- 해결: 관리자로 이벤트 승인

**문제 3: "Not in sale period"**
- 해결: 이벤트의 판매 기간 확인
- start_time과 end_time이 현재 시간 이후인지 확인

**문제 4: "Tickets sold out"**
- 해결: 다른 이벤트로 테스트 또는 max_tickets 증가

**문제 5: "Refund deadline has passed"**
- 해결: 이벤트 날짜를 미래로 설정
- 환불 기한은 이벤트 날짜 1일 전까지

## 체크리스트

- [ ] Hardhat 노드 실행 중
- [ ] 백엔드 서버 실행 중
- [ ] 프론트엔드 서버 실행 중
- [ ] PostgreSQL 실행 중
- [ ] 컨트랙트 배포됨
- [ ] 주최자 계정 생성
- [ ] 관리자 계정 생성
- [ ] 구매자 계정 생성
- [ ] 이벤트 생성 성공
- [ ] 이벤트 승인 성공
- [ ] 티켓 구매 성공
- [ ] 재판매 등록 성공
- [ ] 재판매 구매 성공
- [ ] 환불 요청 성공
- [ ] 환불 승인 성공

## 다음 단계

모든 기능이 정상 작동하면:
1. UserOperation 구현
2. Bundler 연동
3. 테스트넷 배포
4. 메인넷 배포

