# 프론트엔드 직접 테스트 - 단계별 가이드

## 준비 단계

### 1. 모든 서비스 실행 확인

**터미널 1: Hardhat 노드**
```bash
cd contracts
npx hardhat node
```
✅ "Started HTTP and WebSocket server" 메시지 확인

**터미널 2: 백엔드 서버**
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```
✅ "Uvicorn running on http://127.0.0.1:8000" 메시지 확인

**터미널 3: 프론트엔드 서버**
```bash
cd frontend
npm run dev
```
✅ "Local: http://localhost:5173" 메시지 확인

**터미널 4: PostgreSQL (Docker)**
```bash
docker-compose up -d
```
✅ "Container ticketing-postgres started" 확인

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

---

## 테스트 시나리오

### 시나리오 1: 주최자 계정 생성 및 이벤트 생성

#### 1-1. 회원가입
1. 브라우저에서 http://localhost:5173 접속
2. 우측 상단 "회원가입" 버튼 클릭
3. 회원가입 폼 입력:
   - 이메일: `organizer@test.com`
   - 비밀번호: `test123`
4. "회원가입" 버튼 클릭
5. ✅ "회원가입 성공" 메시지 확인
6. 자동으로 로그인됨

#### 1-2. Smart Wallet 연결 확인
1. 로그인 후 상단에 "지갑 연결 중..." 표시
2. 잠시 후 "연결됨" 상태로 변경
3. Smart Wallet 주소 표시 확인
4. ✅ 예: `0x39bE...aCEB`

#### 1-3. 주최자 권한 부여 (필요시)
현재는 회원가입 시 역할을 선택할 수 없으므로, DB에서 수동으로 변경하거나:
- 관리자 계정으로 역할 변경 API 호출
- 또는 테스트용으로 organizer 역할로 회원가입

**임시 해결책:**
```bash
# PostgreSQL 접속
docker exec -it ticketing-postgres psql -U postgres -d ticketing

# 사용자 역할 변경
UPDATE users SET role = 'organizer' WHERE email = 'organizer@test.com';
```

#### 1-4. 이벤트 생성
1. 상단 메뉴에서 "이벤트 생성" 클릭
   - 또는 http://localhost:5173/create-event 직접 접속
2. 이벤트 정보 입력:
   - **이름**: `Test Concert`
   - **설명**: `Test concert description`
   - **가격**: `100` (MATIC)
   - **최대 티켓 수**: `100`
   - **판매 시작**: 내일 날짜 선택
   - **판매 종료**: 내일 날짜 + 7일
   - **이벤트 날짜**: 내일 날짜 + 30일
3. "이벤트 생성" 버튼 클릭
4. ✅ "이벤트가 생성되었습니다. 관리자 승인을 기다려주세요." 메시지 확인
5. 이벤트 목록 페이지로 이동됨

---

### 시나리오 2: 관리자로 이벤트 승인

#### 2-1. 관리자 계정 생성
1. 우측 상단 "로그아웃" 버튼 클릭
2. "회원가입" 버튼 클릭
3. 회원가입 폼 입력:
   - 이메일: `admin@test.com`
   - 비밀번호: `test123`
4. "회원가입" 버튼 클릭

#### 2-2. 관리자 권한 부여
```bash
# PostgreSQL 접속
docker exec -it ticketing-postgres psql -U postgres -d ticketing

# 사용자 역할 변경
UPDATE users SET role = 'admin' WHERE email = 'admin@test.com';
```

#### 2-3. 관리자 페이지 접속
1. 상단 메뉴에서 "관리자" 클릭
   - 또는 http://localhost:5173/admin 직접 접속
2. 대기 중인 이벤트 목록 확인
3. "승인" 버튼 클릭
4. ✅ 이벤트 상태가 "승인됨"으로 변경 확인

---

### 시나리오 3: 티켓 구매

#### 3-1. 구매자 계정 생성
1. 로그아웃
2. 회원가입:
   - 이메일: `buyer@test.com`
   - 비밀번호: `test123`
3. 로그인 후 Smart Wallet 자동 연결 확인

#### 3-2. 이벤트 목록 확인
1. 상단 메뉴에서 "이벤트" 클릭
   - 또는 http://localhost:5173/events 직접 접속
2. 승인된 이벤트 목록 확인
3. 생성한 "Test Concert" 이벤트 확인

#### 3-3. 이벤트 상세 페이지
1. "Test Concert" 이벤트 클릭
2. 이벤트 상세 정보 확인:
   - 이름, 설명, 가격
   - 판매 기간
   - 이벤트 날짜

#### 3-4. 티켓 구매
1. "티켓 구매" 버튼 클릭
2. ✅ "티켓 구매가 완료되었습니다!" 메시지 확인
3. 자동으로 "내 티켓" 페이지로 이동
4. 구매한 티켓 확인:
   - Token ID
   - 이벤트 이름
   - 구매 가격

---

### 시나리오 4: 재판매 등록 및 구매

#### 4-1. 재판매 등록
1. "내 티켓" 페이지에서 구매한 티켓 확인
2. 재판매 등록 기능이 있다면:
   - "재판매 등록" 버튼 클릭
   - 가격 입력: `150` (MATIC)
   - 등록
3. 재판매 등록 기능이 없다면:
   - API로 직접 호출 (Swagger UI 사용)
   - http://localhost:8000/docs 접속
   - `/api/v1/resales` POST 엔드포인트 사용

#### 4-2. 재판매 마켓플레이스 확인
1. 상단 메뉴에서 "마켓플레이스" 클릭
   - 또는 http://localhost:5173/marketplace 직접 접속
2. 등록된 재판매 티켓 확인:
   - Token ID
   - 가격
   - 판매자 주소

#### 4-3. 다른 구매자로 재판매 구매
1. 로그아웃
2. 새로운 구매자 계정 생성:
   - 이메일: `buyer2@test.com`
   - 비밀번호: `test123`
3. 로그인 및 Smart Wallet 연결
4. 마켓플레이스 접속
5. 재판매 티켓 확인
6. "구매하기" 버튼 클릭
7. ✅ "티켓 구매가 완료되었습니다!" 메시지 확인
8. "내 티켓" 페이지에서 구매한 티켓 확인

---

### 시나리오 5: 환불 요청 및 승인

#### 5-1. 환불 요청
1. 구매자 계정으로 로그인 (`buyer@test.com`)
2. "내 티켓" 페이지 접속
3. 환불 요청 기능이 있다면:
   - "환불 요청" 버튼 클릭
   - 사유 입력: `Test refund`
   - 요청
4. 환불 요청 기능이 없다면:
   - API로 직접 호출 (Swagger UI 사용)
   - http://localhost:8000/docs 접속
   - `/api/v1/refunds/request` POST 엔드포인트 사용

#### 5-2. 주최자로 환불 승인
1. 주최자 계정으로 로그인 (`organizer@test.com`)
2. 환불 요청 목록 확인 (API 또는 관리자 페이지)
3. 환불 승인 기능이 있다면:
   - "승인" 버튼 클릭
4. 환불 승인 기능이 없다면:
   - API로 직접 호출 (Swagger UI 사용)
   - http://localhost:8000/docs 접속
   - `/api/v1/refunds/{refund_id}/approve` POST 엔드포인트 사용
5. ✅ 환불 승인 성공 확인

---

## Swagger UI 사용법 (API 직접 테스트)

### 1. Swagger UI 접속
- http://localhost:8000/docs

### 2. 인증 설정
1. 상단 "Authorize" 버튼 클릭
2. 로그인 API로 토큰 받기:
   - `/api/v1/auth/login` POST
   - 이메일/비밀번호 입력
   - 응답에서 `access_token` 복사
3. "Authorize" 창에 입력:
   - `Bearer <토큰>` 형식으로 입력
   - 예: `Bearer eyJhbGciOiJIUzI1NiIs...`
4. "Authorize" 버튼 클릭

### 3. API 테스트
- 각 엔드포인트에서 "Try it out" 클릭
- 필요한 파라미터 입력
- "Execute" 버튼 클릭
- 응답 확인

---

## 확인 사항 체크리스트

### 각 시나리오 완료 후 확인:
- [ ] 성공 메시지 표시
- [ ] 데이터베이스에 저장 확인
- [ ] 프론트엔드에서 데이터 표시 확인
- [ ] Hardhat 노드 로그에서 트랜잭션 확인

### 데이터베이스 확인 방법:
```bash
# PostgreSQL 접속
docker exec -it ticketing-postgres psql -U postgres -d ticketing

# 테이블 확인
\dt

# 데이터 확인
SELECT * FROM users;
SELECT * FROM events;
SELECT * FROM tickets;
SELECT * FROM resales;
SELECT * FROM refund_requests;
```

---

## 문제 해결

### 문제 1: "지갑 연결" 안 됨
- 해결: 브라우저 콘솔(F12)에서 에러 확인
- Hardhat 노드가 실행 중인지 확인
- 백엔드 서버가 실행 중인지 확인

### 문제 2: "이벤트 생성" 안 됨
- 해결: 주최자 권한 확인
- PostgreSQL에서 역할 확인:
  ```sql
  SELECT email, role FROM users WHERE email = 'organizer@test.com';
  ```

### 문제 3: "티켓 구매" 안 됨
- 해결: 이벤트 승인 상태 확인
- 판매 기간 확인 (현재 시간이 판매 기간 내인지)
- 티켓 수량 확인 (sold_tickets < max_tickets)

### 문제 4: "재판매 구매" 안 됨
- 해결: 다른 사용자로 구매 확인
- 자신의 티켓은 구매할 수 없음

### 문제 5: "환불 요청" 안 됨
- 해결: 환불 기한 확인
- 이벤트 날짜 1일 전까지 가능

---

## 빠른 테스트 요약

1. **회원가입** → 로그인 → Smart Wallet 연결
2. **이벤트 생성** (주최자)
3. **이벤트 승인** (관리자)
4. **티켓 구매** (구매자)
5. **재판매 등록** (구매자)
6. **재판매 구매** (다른 구매자)
7. **환불 요청** (구매자)
8. **환불 승인** (주최자)

각 단계에서 성공 메시지와 데이터 표시를 확인하세요!

