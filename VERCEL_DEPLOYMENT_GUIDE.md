# Vercel 프론트엔드 배포 가이드

## 📋 사전 준비

### 1. Vercel 계정
- [Vercel](https://vercel.com) 계정 생성
- GitHub 계정 연결 (선택사항)

### 2. 필요한 것들
- 백엔드 배포 URL (EC2 인스턴스)
- 배포된 스마트 컨트랙트 주소 (테스트넷/메인넷)

---

## 🚀 배포 방법

### 방법 1: Vercel CLI 사용 (권장)

#### Step 1: Vercel CLI 설치

```bash
npm install -g vercel
```

#### Step 2: 로그인

```bash
vercel login
```

#### Step 3: 프로젝트 디렉토리로 이동

```bash
cd frontend
```

#### Step 4: 배포

```bash
# 첫 배포 (대화형 설정)
vercel

# 프로덕션 배포
vercel --prod
```

배포 중 질문:
- **Set up and deploy?** → Yes
- **Which scope?** → 본인 계정 선택
- **Link to existing project?** → No (첫 배포 시)
- **Project name?** → `ticketing-frontend` (원하는 이름)
- **Directory?** → `./` (현재 디렉토리)
- **Override settings?** → No

---

### 방법 2: Vercel 대시보드 사용

#### Step 1: Vercel 대시보드 접속

1. [Vercel Dashboard](https://vercel.com/dashboard) 접속
2. **Add New Project** 클릭

#### Step 2: GitHub 저장소 연결

1. GitHub 저장소 선택
2. **Import** 클릭

#### Step 3: 프로젝트 설정

- **Framework Preset**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Install Command**: `npm install`

#### Step 4: 환경 변수 설정

**Environment Variables** 섹션에서 다음 변수 추가:

```env
VITE_API_URL=https://your-ec2-ip:8000
# 또는 도메인 사용 시
VITE_API_URL=https://api.your-domain.com

VITE_RPC_URL=https://polygon-mumbai-bor.publicnode.com
# 또는 메인넷
VITE_RPC_URL=https://polygon-rpc.com

VITE_CHAIN_ID=80001
# 또는 메인넷: 137

VITE_TICKET_ACCESS_CONTROL_ADDRESS=0x...
VITE_TICKET_NFT_ADDRESS=0x...
VITE_EVENT_MANAGER_ADDRESS=0x...
VITE_MARKETPLACE_ADDRESS=0x...
VITE_REFUND_MANAGER_ADDRESS=0x...
VITE_SMART_WALLET_FACTORY_ADDRESS=0x...
VITE_ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

#### Step 5: 배포

**Deploy** 버튼 클릭

---

## 🔧 환경 변수 설정

### Vercel 대시보드에서 설정

1. 프로젝트 선택
2. **Settings** → **Environment Variables**
3. 각 환경 변수 추가:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://your-ec2-ip:8000`
   - **Environment**: Production, Preview, Development 모두 선택

### Vercel CLI로 설정

```bash
# 환경 변수 추가
vercel env add VITE_API_URL production
# 값 입력: https://your-ec2-ip:8000

# 모든 환경 변수 한 번에 추가
vercel env add VITE_EVENT_MANAGER_ADDRESS production
vercel env add VITE_TICKET_NFT_ADDRESS production
# ... (나머지 변수들)
```

---

## 📝 환경 변수 목록

### 필수 환경 변수

```env
# API
VITE_API_URL=https://your-ec2-ip:8000

# Web3
VITE_RPC_URL=https://polygon-mumbai-bor.publicnode.com
VITE_CHAIN_ID=80001

# Contract Addresses
VITE_TICKET_ACCESS_CONTROL_ADDRESS=0x...
VITE_TICKET_NFT_ADDRESS=0x...
VITE_EVENT_MANAGER_ADDRESS=0x...
VITE_MARKETPLACE_ADDRESS=0x...
VITE_REFUND_MANAGER_ADDRESS=0x...
VITE_SMART_WALLET_FACTORY_ADDRESS=0x...
VITE_ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

---

## 🔄 업데이트 및 재배포

### 코드 업데이트 후

```bash
# Git에 푸시
git add .
git commit -m "Update frontend"
git push origin main

# Vercel이 자동으로 재배포 (GitHub 연동 시)
# 또는 수동 재배포:
vercel --prod
```

### 환경 변수 변경 후

1. Vercel 대시보드에서 환경 변수 수정
2. **Redeploy** 클릭

---

## 🌐 커스텀 도메인 설정

### Step 1: 도메인 추가

1. Vercel 대시보드 → 프로젝트 선택
2. **Settings** → **Domains**
3. 도메인 입력 (예: `ticketing.your-domain.com`)
4. **Add** 클릭

### Step 2: DNS 설정

도메인 제공업체에서 DNS 레코드 추가:

```
Type: CNAME
Name: ticketing (또는 @)
Value: cname.vercel-dns.com
```

### Step 3: SSL 인증서

Vercel이 자동으로 SSL 인증서를 발급합니다.

---

## 🛠️ 빌드 설정

### vercel.json 확인

프로젝트 루트에 `vercel.json` 파일이 있는지 확인:

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite"
}
```

### 빌드 오류 해결

```bash
# 로컬에서 빌드 테스트
cd frontend
npm run build

# 빌드 결과 확인
ls -la dist/
```

---

## 📊 배포 확인

### 배포 상태 확인

1. Vercel 대시보드 → **Deployments**
2. 최신 배포 상태 확인
3. **Visit** 클릭하여 사이트 접속

### 기능 테스트

1. 브라우저에서 배포된 URL 접속
2. 회원가입/로그인 테스트
3. 이벤트 목록 확인
4. 티켓 구매 테스트

---

## 🔒 보안 설정

### CORS 설정 확인

백엔드의 `ALLOWED_ORIGINS`에 Vercel URL 추가:

```env
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:5173
```

### 환경 변수 보안

- 환경 변수는 Vercel 대시보드에서만 관리
- `.env` 파일은 Git에 커밋하지 않기
- 프로덕션과 개발 환경 분리

---

## 🚨 문제 해결

### 빌드 실패

```bash
# 로컬에서 빌드 테스트
npm run build

# 에러 메시지 확인
# Vercel 대시보드 → Deployments → Build Logs 확인
```

### 환경 변수 미적용

1. 환경 변수 설정 확인
2. 재배포 필요 (환경 변수 변경 후)
3. 브라우저 캐시 삭제

### API 연결 오류

1. 백엔드 URL 확인 (`VITE_API_URL`)
2. CORS 설정 확인
3. 백엔드 서버 실행 상태 확인

---

## ✅ 배포 확인 체크리스트

- [ ] Vercel 계정 생성 및 로그인
- [ ] 프로젝트 배포 완료
- [ ] 환경 변수 설정 완료
- [ ] 빌드 성공
- [ ] 사이트 접속 가능
- [ ] API 연결 확인
- [ ] Web3 연결 확인
- [ ] 기본 기능 테스트 완료

---

## 📝 다음 단계

1. **백엔드 CORS 설정**
   - EC2 백엔드의 `ALLOWED_ORIGINS`에 Vercel URL 추가

2. **도메인 연결** (선택사항)
   - 커스텀 도메인 설정

3. **모니터링**
   - Vercel Analytics 설정

4. **성능 최적화**
   - 이미지 최적화
   - 코드 스플리팅 확인

