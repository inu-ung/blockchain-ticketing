# 프론트엔드/백엔드 배포 가이드

## 🤔 배포가 필요한가요?

### 현재 상황
- ✅ **스마트 컨트랙트**: 로컬 Hardhat 노드에 배포됨
- ✅ **백엔드**: 로컬에서 실행 중 (`localhost:8000`)
- ✅ **프론트엔드**: 로컬에서 실행 중 (`localhost:5173`)

### 배포가 필요한 경우

#### 1. **로컬 개발/테스트만 하는 경우** ❌ 배포 불필요
- 현재 상태로 충분합니다
- 로컬에서 모든 기능 테스트 가능
- 개발 중에는 배포할 필요 없음

#### 2. **다른 사람과 공유/테스트하는 경우** ✅ 배포 필요
- 친구나 팀원이 접근할 수 있도록
- 데모나 포트폴리오로 보여주기
- 실제 사용자 테스트

#### 3. **실제 서비스로 운영하는 경우** ✅ 배포 필수
- 프로덕션 환경 구축
- 안정적인 서비스 제공
- 도메인 연결 및 SSL 인증서

---

## 📊 배포 옵션 비교

### 옵션 1: 로컬 환경 유지 (현재 상태)

**장점:**
- ✅ 설정이 간단함
- ✅ 무료
- ✅ 빠른 개발/테스트
- ✅ 디버깅이 쉬움

**단점:**
- ❌ 다른 사람이 접근 불가
- ❌ 컴퓨터를 끄면 서비스 중단
- ❌ 실제 사용자 테스트 불가

**적합한 경우:**
- 개발 중
- 개인 프로젝트
- 로컬 테스트만 필요

---

### 옵션 2: 테스트넷 배포 (블록체인만)

**장점:**
- ✅ 실제 블록체인에서 테스트
- ✅ 실제 가스비 경험
- ✅ 테스트넷 토큰 사용

**단점:**
- ❌ 프론트/백엔드는 여전히 로컬
- ❌ 다른 사람 접근 불가

**적합한 경우:**
- 블록체인 기능만 테스트
- 스마트 컨트랙트 검증

---

### 옵션 3: 클라우드 배포 (전체 배포)

**장점:**
- ✅ 24/7 서비스 가능
- ✅ 다른 사람 접근 가능
- ✅ 실제 사용자 테스트 가능
- ✅ 포트폴리오로 활용 가능

**단점:**
- ❌ 비용 발생 가능 (일부 무료 플랜 있음)
- ❌ 설정이 복잡할 수 있음
- ❌ 환경 변수 관리 필요

**적합한 경우:**
- 데모/포트폴리오
- 실제 사용자 테스트
- 프로덕션 서비스

---

## 🚀 배포 방법 (옵션 3 선택 시)

### 백엔드 배포 옵션

#### 1. **Railway** (추천 - 간단함)
```bash
# Railway CLI 설치
npm i -g @railway/cli

# 로그인
railway login

# 프로젝트 초기화
cd backend
railway init

# 환경 변수 설정 (Railway 대시보드에서)
# - DATABASE_URL (Railway가 자동 생성)
# - SECRET_KEY
# - PRIVATE_KEY
# - Contract Addresses
# 등등...

# 배포
railway up
```

**비용:** 무료 플랜 있음 (월 $5 크레딧)

#### 2. **Render**
```bash
# Render 대시보드에서:
# 1. New Web Service
# 2. GitHub 저장소 연결
# 3. 환경 변수 설정
# 4. Build Command: pip install -r requirements.txt
# 5. Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**비용:** 무료 플랜 있음 (15분 후 슬립 모드)

#### 3. **AWS EC2 / DigitalOcean**
- 더 많은 제어권 필요
- 서버 관리 필요
- 비용: 월 $5-10

#### 4. **Fly.io**
```bash
# Fly CLI 설치
curl -L https://fly.io/install.sh | sh

# 로그인
fly auth login

# 앱 생성
cd backend
fly launch

# 환경 변수 설정
fly secrets set DATABASE_URL=...
fly secrets set SECRET_KEY=...

# 배포
fly deploy
```

**비용:** 무료 플랜 있음

---

### 프론트엔드 배포 옵션

#### 1. **Vercel** (추천 - 가장 간단)
```bash
# Vercel CLI 설치
npm i -g vercel

# 배포
cd frontend
vercel

# 환경 변수 설정 (Vercel 대시보드에서)
# - VITE_API_URL (백엔드 URL)
# - VITE_RPC_URL
# - Contract Addresses
# 등등...
```

**비용:** 완전 무료 (개인 프로젝트)

#### 2. **Netlify**
```bash
# Netlify CLI 설치
npm i -g netlify-cli

# 배포
cd frontend
npm run build
netlify deploy --prod
```

**비용:** 완전 무료

#### 3. **GitHub Pages**
```bash
# vite.config.ts 수정 필요
# build 후 gh-pages 브랜치에 배포
```

**비용:** 완전 무료

---

## 📝 배포 전 체크리스트

### 백엔드
- [ ] 환경 변수 설정 (`.env` → 클라우드 환경 변수)
- [ ] 데이터베이스 설정 (PostgreSQL)
- [ ] CORS 설정 (프론트엔드 URL 추가)
- [ ] SECRET_KEY 변경 (프로덕션용)
- [ ] PRIVATE_KEY 보안 관리

### 프론트엔드
- [ ] 환경 변수 설정 (`VITE_*`)
- [ ] API URL 변경 (백엔드 배포 URL)
- [ ] RPC URL 변경 (테스트넷/메인넷)
- [ ] Contract Addresses 업데이트

### 공통
- [ ] 스마트 컨트랙트 테스트넷/메인넷 배포
- [ ] 도메인 설정 (선택사항)
- [ ] SSL 인증서 (자동 설정됨)

---

## 🎯 추천 배포 조합

### 개발/테스트용
```
백엔드: Railway (무료 플랜)
프론트엔드: Vercel (무료)
데이터베이스: Railway PostgreSQL (무료)
블록체인: Polygon Amoy 테스트넷
```

### 프로덕션용
```
백엔드: Railway / Fly.io (유료 플랜)
프론트엔드: Vercel (무료)
데이터베이스: Railway PostgreSQL (유료)
블록체인: Polygon Mainnet
```

---

## ⚠️ 주의사항

### 보안
1. **SECRET_KEY**: 반드시 강력한 랜덤 문자열 사용
2. **PRIVATE_KEY**: 절대 코드에 하드코딩하지 말 것
3. **환경 변수**: 클라우드 플랫폼의 환경 변수 기능 사용

### 비용
- 무료 플랜도 있지만 제한이 있을 수 있음
- 데이터베이스 사용량 모니터링
- 트래픽 제한 확인

### 데이터베이스
- 로컬 PostgreSQL → 클라우드 PostgreSQL로 마이그레이션 필요
- 데이터 백업 계획

---

## 🚀 빠른 시작 (Vercel + Railway)

### 1. 백엔드 배포 (Railway)
```bash
cd backend
railway login
railway init
# 환경 변수 설정 후
railway up
```

### 2. 프론트엔드 배포 (Vercel)
```bash
cd frontend
vercel
# 환경 변수 설정 후
vercel --prod
```

### 3. 환경 변수 업데이트
- 프론트엔드의 `VITE_API_URL`을 Railway 백엔드 URL로 변경
- 재배포

---

## 💡 결론

### 지금 당장 배포가 필요한가요?
- **아니요** - 로컬 개발/테스트만 한다면 현재 상태로 충분합니다
- **네** - 다른 사람과 공유하거나 데모가 필요하다면 배포하세요

### 배포 시기
1. **개발 완료 후**: 모든 기능이 작동하는지 확인
2. **테스트 완료 후**: 로컬에서 충분히 테스트
3. **포트폴리오/데모**: 보여줄 준비가 되었을 때

---

## 📚 추가 자료

- [Railway 문서](https://docs.railway.app/)
- [Vercel 문서](https://vercel.com/docs)
- [Render 문서](https://render.com/docs)
- [Fly.io 문서](https://fly.io/docs)

