# 프로덕션 배포 전체 가이드

## 📋 개요

이 가이드는 다음 구성을 위한 전체 배포 프로세스를 설명합니다:
- **백엔드**: Docker + EC2
- **프론트엔드**: Vercel
- **데이터베이스**: PostgreSQL (Docker 컨테이너)
- **블록체인**: Polygon 테스트넷/메인넷

---

## 🎯 배포 순서

### 1단계: 스마트 컨트랙트 배포

#### 테스트넷 배포 (Amoy)

```bash
cd contracts

# 환경 변수 설정 (contracts/.env)
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
PRIVATE_KEY=your-private-key
POLYGONSCAN_API_KEY=your-api-key

# 배포
npm run deploy:amoy

# 배포 주소 확인
cat deployments/amoy.json
```

#### 메인넷 배포 (Polygon)

```bash
# 환경 변수 설정
POLYGON_MAINNET_RPC_URL=https://polygon-rpc.com
PRIVATE_KEY=your-private-key
POLYGONSCAN_API_KEY=your-api-key

# 배포
npm run deploy:polygon

# 배포 주소 확인
cat deployments/polygon.json
```

---

### 2단계: 백엔드 배포 (EC2 + Docker)

자세한 내용은 `EC2_DEPLOYMENT_GUIDE.md` 참고

#### 요약

1. **EC2 인스턴스 생성**
   - Ubuntu 22.04 LTS
   - 보안 그룹: 포트 22, 80, 443, 8000 열기

2. **Docker 설치**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```

3. **프로젝트 클론**
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo/backend
   ```

4. **환경 변수 설정** (`.env` 파일)
   ```env
   DATABASE_URL=postgresql://postgres:password@postgres:5432/ticketing
   SECRET_KEY=your-secret-key
   POLYGON_MUMBAI_RPC_URL=https://polygon-mumbai-bor.publicnode.com
   PRIVATE_KEY=your-private-key
   EVENT_MANAGER_ADDRESS=0x... # 배포된 주소
   TICKET_NFT_ADDRESS=0x... # 배포된 주소
   # ... (나머지 컨트랙트 주소)
   ALLOWED_ORIGINS=https://your-app.vercel.app
   ```

5. **Docker Compose로 배포**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

6. **헬스 체크**
   ```bash
   curl http://your-ec2-ip:8000/health
   ```

---

### 3단계: 프론트엔드 배포 (Vercel)

자세한 내용은 `VERCEL_DEPLOYMENT_GUIDE.md` 참고

#### 요약

1. **Vercel CLI 설치 및 로그인**
   ```bash
   npm install -g vercel
   vercel login
   ```

2. **프로젝트 디렉토리로 이동**
   ```bash
   cd frontend
   ```

3. **환경 변수 설정** (Vercel 대시보드 또는 CLI)
   ```env
   VITE_API_URL=https://your-ec2-ip:8000
   VITE_RPC_URL=https://polygon-mumbai-bor.publicnode.com
   VITE_CHAIN_ID=80001
   VITE_EVENT_MANAGER_ADDRESS=0x... # 배포된 주소
   VITE_TICKET_NFT_ADDRESS=0x... # 배포된 주소
   # ... (나머지 컨트랙트 주소)
   ```

4. **배포**
   ```bash
   vercel --prod
   ```

---

## 🔗 연결 설정

### 백엔드 CORS 설정

EC2 백엔드의 `.env` 파일:

```env
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:5173
```

### 프론트엔드 API URL

Vercel 환경 변수:

```env
VITE_API_URL=https://your-ec2-ip:8000
# 또는 도메인 사용 시
VITE_API_URL=https://api.your-domain.com
```

---

## 📝 환경 변수 체크리스트

### 백엔드 (EC2)

- [ ] `DATABASE_URL`
- [ ] `SECRET_KEY`
- [ ] `POLYGON_MUMBAI_RPC_URL` 또는 `POLYGON_MAINNET_RPC_URL`
- [ ] `PRIVATE_KEY`
- [ ] `TICKET_ACCESS_CONTROL_ADDRESS`
- [ ] `TICKET_NFT_ADDRESS`
- [ ] `EVENT_MANAGER_ADDRESS`
- [ ] `MARKETPLACE_ADDRESS`
- [ ] `REFUND_MANAGER_ADDRESS`
- [ ] `SMART_WALLET_FACTORY_ADDRESS`
- [ ] `ENTRY_POINT_ADDRESS`
- [ ] `PINATA_API_KEY`
- [ ] `PINATA_SECRET_KEY`
- [ ] `ALLOWED_ORIGINS` (Vercel URL 포함)

### 프론트엔드 (Vercel)

- [ ] `VITE_API_URL` (EC2 백엔드 URL)
- [ ] `VITE_RPC_URL`
- [ ] `VITE_CHAIN_ID`
- [ ] `VITE_TICKET_ACCESS_CONTROL_ADDRESS`
- [ ] `VITE_TICKET_NFT_ADDRESS`
- [ ] `VITE_EVENT_MANAGER_ADDRESS`
- [ ] `VITE_MARKETPLACE_ADDRESS`
- [ ] `VITE_REFUND_MANAGER_ADDRESS`
- [ ] `VITE_SMART_WALLET_FACTORY_ADDRESS`
- [ ] `VITE_ENTRY_POINT_ADDRESS`

---

## ✅ 배포 확인

### 1. 스마트 컨트랙트

```bash
# Polygonscan에서 확인
https://amoy.polygonscan.com/address/YOUR_CONTRACT_ADDRESS
```

### 2. 백엔드

```bash
# 헬스 체크
curl https://your-ec2-ip:8000/health

# API 문서
https://your-ec2-ip:8000/docs
```

### 3. 프론트엔드

- Vercel 배포 URL 접속
- 회원가입/로그인 테스트
- 이벤트 목록 확인
- 티켓 구매 테스트

---

## 🔒 보안 체크리스트

- [ ] `SECRET_KEY` 강력한 랜덤 문자열 사용
- [ ] `PRIVATE_KEY` 안전하게 관리 (환경 변수만 사용)
- [ ] `.env` 파일 Git에 커밋하지 않음
- [ ] CORS 설정 올바르게 구성
- [ ] HTTPS 사용 (SSL 인증서)
- [ ] 방화벽 설정 (필요한 포트만 열기)
- [ ] 데이터베이스 비밀번호 강력하게 설정

---

## 🚨 문제 해결

### 백엔드 연결 오류

1. EC2 보안 그룹 확인 (포트 8000 열려있는지)
2. 백엔드 서버 실행 상태 확인
3. CORS 설정 확인

### 프론트엔드 빌드 오류

1. 로컬에서 빌드 테스트: `npm run build`
2. 환경 변수 확인
3. Vercel 빌드 로그 확인

### API 연결 오류

1. `VITE_API_URL` 확인
2. 백엔드 CORS 설정 확인
3. 네트워크 연결 확인

---

## 📚 관련 문서

- **EC2 배포**: `EC2_DEPLOYMENT_GUIDE.md`
- **Vercel 배포**: `VERCEL_DEPLOYMENT_GUIDE.md`
- **테스트넷 배포**: `AMOY_DEPLOYMENT_GUIDE.md`
- **메인넷 배포**: `POLYGON_MAINNET_DEPLOYMENT.md`

---

## 💡 팁

1. **단계별 배포**: 한 번에 모든 것을 배포하지 말고 단계별로 진행
2. **테스트**: 각 단계마다 테스트 후 다음 단계 진행
3. **백업**: 배포 전 데이터베이스 백업
4. **모니터링**: 배포 후 로그 모니터링
5. **롤백 계획**: 문제 발생 시 롤백 방법 준비

