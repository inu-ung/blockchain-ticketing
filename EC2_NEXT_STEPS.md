# EC2 인스턴스 다음 단계 가이드

## ✅ 현재 상태

- EC2 인스턴스 생성 완료
- SSH 접속 완료

---

## 🚀 다음 단계

### 1단계: 초기 설정 (Docker 설치)

EC2 인스턴스 터미널에서 다음 명령어 실행:

```bash
# 시스템 업데이트
sudo apt-get update
sudo apt-get upgrade -y

# Docker 설치
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
rm get-docker.sh

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Docker 그룹에 사용자 추가
sudo usermod -aG docker ubuntu
newgrp docker

# Git 설치
sudo apt-get install -y git

# 설치 확인
docker --version
docker-compose --version
git --version
```

**또는 자동 스크립트 사용:**

로컬에서 스크립트를 EC2로 복사:

```bash
# 로컬 터미널에서
scp -i your-key.pem EC2_SETUP_SCRIPT.sh ubuntu@your-ec2-ip:~/

# EC2 인스턴스에서
chmod +x EC2_SETUP_SCRIPT.sh
./EC2_SETUP_SCRIPT.sh
```

---

### 2단계: 프로젝트 클론

#### 방법 1: Git으로 클론 (권장)

```bash
# GitHub 저장소 클론
git clone https://github.com/your-username/your-repo.git
cd your-repo/backend
```

#### 방법 2: SCP로 파일 업로드

로컬에서:

```bash
# 프로젝트 디렉토리 압축
cd /Users/ung/blockchain/BC
tar -czf backend.tar.gz backend/

# EC2로 업로드
scp -i your-key.pem backend.tar.gz ubuntu@your-ec2-ip:~/

# EC2에서 압축 해제
ssh -i your-key.pem ubuntu@your-ec2-ip
tar -xzf backend.tar.gz
cd backend
```

---

### 3단계: 환경 변수 설정

`.env` 파일 생성:

```bash
nano .env
```

다음 내용 입력 (실제 값으로 변경):

```env
# Database
DATABASE_URL=postgresql://postgres:your-strong-password@postgres:5432/ticketing
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-strong-password-here
POSTGRES_DB=ticketing

# JWT
SECRET_KEY=your-very-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Web3 (Amoy 테스트넷)
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
PRIVATE_KEY=your-private-key-here

# Contract Addresses (테스트넷 배포 주소 - 아직 배포 안 했으면 나중에 업데이트)
TICKET_ACCESS_CONTROL_ADDRESS=0x...
TICKET_NFT_ADDRESS=0x...
EVENT_MANAGER_ADDRESS=0x...
MARKETPLACE_ADDRESS=0x...
REFUND_MANAGER_ADDRESS=0x...
SMART_WALLET_FACTORY_ADDRESS=0x...
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789

# IPFS (선택사항)
PINATA_API_KEY=
PINATA_SECRET_KEY=

# Account Abstraction (선택사항)
BUNDLER_URL=
PAYMASTER_URL=

# CORS
ALLOWED_ORIGINS=http://localhost:5173
```

**SECRET_KEY 생성:**

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

### 4단계: 배포 실행

```bash
# 배포 스크립트 실행 권한 부여
chmod +x deploy.sh

# 배포 실행
./deploy.sh
```

**또는 직접 실행:**

```bash
# Docker 이미지 빌드 및 실행
docker-compose -f docker-compose.prod.yml up -d --build

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f
```

---

### 5단계: 배포 확인

#### 헬스 체크

```bash
# EC2 인스턴스 내부에서
curl http://localhost:8000/health

# 로컬 컴퓨터에서 (퍼블릭 IP 사용)
curl http://your-ec2-ip:8000/health
```

응답:
```json
{"status":"healthy"}
```

#### API 문서 확인

브라우저에서:
```
http://your-ec2-ip:8000/docs
```

---

## 🔧 유용한 명령어

### 컨테이너 관리

```bash
# 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps

# 로그 확인
docker-compose -f docker-compose.prod.yml logs -f backend

# 컨테이너 재시작
docker-compose -f docker-compose.prod.yml restart backend

# 컨테이너 중지
docker-compose -f docker-compose.prod.yml stop

# 컨테이너 시작
docker-compose -f docker-compose.prod.yml start
```

### 데이터베이스 접속

```bash
# PostgreSQL 컨테이너 접속
docker exec -it ticketing-postgres psql -U postgres -d ticketing
```

---

## 🚨 문제 해결

### Docker 명령어가 작동하지 않을 때

```bash
# Docker 그룹에 재로그인
newgrp docker

# 또는 재접속
exit
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### 포트가 이미 사용 중

```bash
# 포트 사용 확인
sudo lsof -i :8000

# 프로세스 종료
sudo kill -9 <PID>
```

### 배포 실패

```bash
# 로그 확인
docker-compose -f docker-compose.prod.yml logs backend

# 환경 변수 확인
cat .env
```

---

## 📝 체크리스트

- [ ] Docker 설치 완료
- [ ] Docker Compose 설치 완료
- [ ] Git 설치 완료
- [ ] 프로젝트 클론 완료
- [ ] .env 파일 생성 및 설정 완료
- [ ] 배포 스크립트 실행 완료
- [ ] 헬스 체크 성공
- [ ] API 문서 접속 가능

---

## 🎯 다음 단계

1. ✅ 백엔드 배포 완료
2. ⏳ 프론트엔드 배포 (Vercel)
3. ⏳ 환경 변수 연결 확인
4. ⏳ 전체 시스템 테스트

---

## 📚 참고 문서

- **EC2 배포 가이드**: `EC2_DEPLOYMENT_GUIDE.md`
- **백엔드 배포 가이드**: `BACKEND_DEPLOYMENT_QUICK_START.md`

