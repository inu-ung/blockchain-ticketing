# 프론트엔드 배포 다음 단계

## ✅ 현재 상태

- ✅ 백엔드 배포 완료 (EC2)
- ✅ 헬스 체크 성공
- ⏳ 프론트엔드 배포 필요 (Vercel)

---

## 🚀 프론트엔드 배포 방법

### 방법 1: Vercel 배포 (권장)

#### 1단계: Vercel 계정 및 프로젝트 생성

1. https://vercel.com 접속
2. GitHub 계정으로 로그인
3. "New Project" 클릭
4. GitHub 저장소 선택
5. 프로젝트 설정:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

#### 2단계: 환경 변수 설정

Vercel 대시보드 → Settings → Environment Variables에서 추가:

```env
# 백엔드 API URL
VITE_API_URL=http://43.201.98.14:8000

# Polygon RPC URL (Amoy 테스트넷)
VITE_RPC_URL=https://rpc-amoy.polygon.technology

# 스마트 컨트랙트 주소 (테스트넷 배포 후 업데이트)
VITE_TICKET_ACCESS_CONTROL_ADDRESS=0x...
VITE_TICKET_NFT_ADDRESS=0x...
VITE_EVENT_MANAGER_ADDRESS=0x...
VITE_REFUND_MANAGER_ADDRESS=0x...
```

#### 3단계: 배포

1. "Deploy" 클릭
2. 배포 완료 대기
3. 배포된 URL 확인 (예: `https://your-project.vercel.app`)

---

### 방법 2: 로컬에서 빌드 및 테스트

```bash
cd frontend

# 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 의존성 설치
npm install

# 빌드
npm run build

# 프리뷰
npm run preview
```

---

## 🔧 프론트엔드 환경 변수 설정

### 필수 환경 변수

`.env` 파일 또는 Vercel 환경 변수에 설정:

```env
# 백엔드 API URL (EC2 퍼블릭 IP)
VITE_API_URL=http://43.201.98.14:8000

# Polygon RPC URL
VITE_RPC_URL=https://rpc-amoy.polygon.technology

# 스마트 컨트랙트 주소 (테스트넷 배포 후 업데이트)
VITE_TICKET_ACCESS_CONTROL_ADDRESS=
VITE_TICKET_NFT_ADDRESS=
VITE_EVENT_MANAGER_ADDRESS=
VITE_REFUND_MANAGER_ADDRESS=
```

---

## 🔗 백엔드 CORS 설정 업데이트

프론트엔드가 배포되면 백엔드 CORS 설정을 업데이트해야 합니다.

### EC2에서 .env 파일 수정

```bash
nano .env
```

`ALLOWED_ORIGINS` 추가/수정:

```env
# Vercel 배포 URL 추가
ALLOWED_ORIGINS=https://your-project.vercel.app,http://localhost:5173
```

### 백엔드 재시작

```bash
docker-compose -f docker-compose.prod.yml restart backend
```

---

## ✅ 배포 확인

### 1. 프론트엔드 접속

브라우저에서 Vercel 배포 URL 접속

### 2. API 연결 확인

브라우저 개발자 도구 → Network 탭에서 API 요청 확인

### 3. 기능 테스트

- 회원가입/로그인
- 이벤트 목록 조회
- 이벤트 생성 (주최자)
- 티켓 구매
- 환불/재판매

---

## 📝 체크리스트

- [ ] Vercel 계정 생성
- [ ] GitHub 저장소 연결
- [ ] Vercel 프로젝트 생성
- [ ] 환경 변수 설정
- [ ] 배포 실행
- [ ] 백엔드 CORS 설정 업데이트
- [ ] 전체 시스템 테스트

---

## 🎯 다음 단계

1. ✅ 백엔드 배포 완료
2. ⏳ 프론트엔드 배포 (Vercel)
3. ⏳ 환경 변수 연결 확인
4. ⏳ 전체 시스템 테스트

---

## 📚 참고 문서

- **Vercel 배포 가이드**: `VERCEL_DEPLOYMENT_GUIDE.md`
- **프로덕션 배포 가이드**: `PRODUCTION_DEPLOYMENT_GUIDE.md`

