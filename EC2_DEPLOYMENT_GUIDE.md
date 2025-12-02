# EC2 + Docker 백엔드 배포 가이드

## 📋 사전 준비

### 1. AWS 계정 및 EC2 인스턴스
- AWS 계정 생성
- EC2 인스턴스 생성 (Ubuntu 22.04 LTS 권장)
- 보안 그룹 설정 (포트 8000, 22 열기)

### 2. 필요한 것들
- EC2 인스턴스 IP 주소
- SSH 키 페어
- 도메인 (선택사항)

---

## 🚀 배포 단계

### Step 1: EC2 인스턴스 접속

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### Step 2: Docker 및 Docker Compose 설치

```bash
# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Docker 그룹에 사용자 추가
sudo usermod -aG docker ubuntu

# 재로그인 또는 다음 명령 실행
newgrp docker

# 설치 확인
docker --version
docker-compose --version
```

### Step 3: 프로젝트 클론

```bash
# Git 설치
sudo apt-get update
sudo apt-get install -y git

# 프로젝트 클론
git clone https://github.com/your-username/your-repo.git
cd your-repo/backend
```

### Step 4: 환경 변수 설정

```bash
# .env 파일 생성
nano .env
```

`.env` 파일 내용:

```env
# Database
DATABASE_URL=postgresql://postgres:your-password@postgres:5432/ticketing
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-strong-password
POSTGRES_DB=ticketing

# JWT
SECRET_KEY=your-very-secret-key-here-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Web3
POLYGON_MUMBAI_RPC_URL=https://polygon-mumbai-bor.publicnode.com
POLYGON_MAINNET_RPC_URL=https://polygon-rpc.com
PRIVATE_KEY=your-private-key-here

# Contract Addresses (테스트넷/메인넷 배포 주소)
TICKET_ACCESS_CONTROL_ADDRESS=0x...
TICKET_NFT_ADDRESS=0x...
EVENT_MANAGER_ADDRESS=0x...
MARKETPLACE_ADDRESS=0x...
REFUND_MANAGER_ADDRESS=0x...
SMART_WALLET_FACTORY_ADDRESS=0x...
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789

# IPFS
PINATA_API_KEY=your-pinata-api-key
PINATA_SECRET_KEY=your-pinata-secret-key

# Account Abstraction
BUNDLER_URL=https://bundler-url
PAYMASTER_URL=https://paymaster-url

# CORS (프론트엔드 URL)
ALLOWED_ORIGINS=https://your-frontend.vercel.app,http://localhost:5173
```

### Step 5: Docker 이미지 빌드 및 실행

```bash
# Docker Compose로 빌드 및 실행
docker-compose -f docker-compose.prod.yml up -d --build

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f

# 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps
```

### Step 6: 헬스 체크

```bash
# 로컬에서 테스트
curl http://your-ec2-ip:8000/health

# 응답: {"status":"healthy"}
```

---

## 🔧 추가 설정

### Nginx 리버스 프록시 (선택사항)

```bash
# Nginx 설치
sudo apt-get install -y nginx

# Nginx 설정 파일 생성
sudo nano /etc/nginx/sites-available/ticketing-backend
```

Nginx 설정:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/ticketing-backend /etc/nginx/sites-enabled/

# Nginx 재시작
sudo nginx -t
sudo systemctl restart nginx
```

### SSL 인증서 (Let's Encrypt)

```bash
# Certbot 설치
sudo apt-get install -y certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot --nginx -d your-domain.com

# 자동 갱신 설정
sudo certbot renew --dry-run
```

---

## 🔄 업데이트 및 재배포

### 코드 업데이트 후 재배포

```bash
# 프로젝트 디렉토리로 이동
cd ~/your-repo/backend

# 최신 코드 가져오기
git pull origin main

# Docker 이미지 재빌드 및 재시작
docker-compose -f docker-compose.prod.yml up -d --build

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f backend
```

---

## 🛠️ 유용한 명령어

### 컨테이너 관리

```bash
# 컨테이너 시작
docker-compose -f docker-compose.prod.yml start

# 컨테이너 중지
docker-compose -f docker-compose.prod.yml stop

# 컨테이너 재시작
docker-compose -f docker-compose.prod.yml restart

# 컨테이너 삭제 (데이터는 유지)
docker-compose -f docker-compose.prod.yml down

# 컨테이너 및 볼륨 삭제 (데이터도 삭제)
docker-compose -f docker-compose.prod.yml down -v
```

### 로그 확인

```bash
# 모든 로그
docker-compose -f docker-compose.prod.yml logs

# 백엔드 로그만
docker-compose -f docker-compose.prod.yml logs backend

# 실시간 로그
docker-compose -f docker-compose.prod.yml logs -f backend
```

### 데이터베이스 접속

```bash
# PostgreSQL 컨테이너 접속
docker exec -it ticketing-postgres psql -U postgres -d ticketing
```

---

## 🔒 보안 설정

### 1. 방화벽 설정 (UFW)

```bash
# UFW 활성화
sudo ufw enable

# SSH 허용
sudo ufw allow 22/tcp

# HTTP/HTTPS 허용
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 백엔드 포트 (Nginx 사용 시 불필요)
# sudo ufw allow 8000/tcp

# 상태 확인
sudo ufw status
```

### 2. 환경 변수 보안

- `.env` 파일은 절대 Git에 커밋하지 않기
- AWS Secrets Manager 또는 환경 변수 사용
- PRIVATE_KEY는 안전하게 관리

---

## 📊 모니터링

### 시스템 리소스 확인

```bash
# Docker 컨테이너 리소스 사용량
docker stats

# 디스크 사용량
df -h

# 메모리 사용량
free -h
```

---

## 🚨 문제 해결

### 백엔드가 시작되지 않을 때

```bash
# 로그 확인
docker-compose -f docker-compose.prod.yml logs backend

# 컨테이너 재시작
docker-compose -f docker-compose.prod.yml restart backend
```

### 데이터베이스 연결 오류

```bash
# PostgreSQL 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps postgres

# PostgreSQL 로그 확인
docker-compose -f docker-compose.prod.yml logs postgres
```

### 포트 충돌

```bash
# 포트 사용 중인 프로세스 확인
sudo lsof -i :8000

# 프로세스 종료
sudo kill -9 <PID>
```

---

## ✅ 배포 확인 체크리스트

- [ ] EC2 인스턴스 생성 및 접속 가능
- [ ] Docker 및 Docker Compose 설치 완료
- [ ] 프로젝트 클론 완료
- [ ] 환경 변수 설정 완료
- [ ] Docker 이미지 빌드 성공
- [ ] 컨테이너 실행 중
- [ ] 헬스 체크 성공 (`/health` 엔드포인트)
- [ ] 데이터베이스 연결 확인
- [ ] CORS 설정 확인
- [ ] 보안 그룹 설정 확인

---

## 📝 다음 단계

1. **프론트엔드 배포** (Vercel)
   - 프론트엔드의 `VITE_API_URL`을 EC2 백엔드 URL로 설정
   - Vercel에 배포

2. **도메인 연결** (선택사항)
   - Route 53 또는 다른 DNS 서비스 사용
   - EC2 인스턴스에 도메인 연결

3. **모니터링 설정**
   - CloudWatch 또는 다른 모니터링 도구 설정

