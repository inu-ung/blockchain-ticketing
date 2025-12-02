# EC2 인스턴스 생성 가이드

## 📋 사전 준비

### 1. AWS 계정
- AWS 계정이 필요합니다
- https://aws.amazon.com 에서 계정 생성 (무료 티어 사용 가능)

### 2. 예상 비용
- **t2.micro**: 무료 티어 (월 750시간)
- **t3.small**: 약 $15/월
- **t3.medium**: 약 $30/월

---

## 🚀 EC2 인스턴스 생성 단계

### Step 1: AWS 콘솔 접속

1. https://console.aws.amazon.com 접속
2. 로그인
3. **EC2** 서비스 검색 및 클릭

---

### Step 2: 인스턴스 시작

1. **"인스턴스 시작"** 버튼 클릭

---

### Step 3: 이름 및 태그

**이름**: `ticketing-backend` (원하는 이름)

---

### Step 4: 애플리케이션 및 OS 이미지 선택

**Amazon Machine Image (AMI)** 선택:

**권장: Ubuntu Server 22.04 LTS**
- 검색: `ubuntu`
- 선택: `Ubuntu Server 22.04 LTS (HVM), SSD Volume Type`
- 아키텍처: `64-bit (x86)`

---

### Step 5: 인스턴스 유형 선택

**권장: t3.micro 또는 t3.small**

- **t3.micro** (무료 티어)
  - vCPU: 2
  - 메모리: 1 GB
  - 네트워크 성능: 최대 5 Gbps
  - ✅ 무료 티어 사용 가능

- **t3.small** (더 나은 성능)
  - vCPU: 2
  - 메모리: 2 GB
  - 네트워크 성능: 최대 5 Gbps
  - 💰 약 $15/월

---

### Step 6: 키 페어 생성/선택

**새 키 페어 생성** (처음인 경우):

1. **키 페어 이름**: `ticketing-backend-key`
2. **키 페어 유형**: `RSA`
3. **프라이빗 키 파일 형식**: `.pem` (OpenSSH)
4. **"키 페어 생성"** 클릭
5. **자동으로 다운로드됨** - 안전한 곳에 보관!

⚠️ **중요**: 키 파일을 잃어버리면 인스턴스에 접속할 수 없습니다!

---

### Step 7: 네트워크 설정

**보안 그룹 설정**:

1. **"보안 그룹 생성"** 선택
2. **보안 그룹 이름**: `ticketing-backend-sg`
3. **설명**: `Backend server security group`

**인바운드 규칙 추가**:

| 유형 | 프로토콜 | 포트 범위 | 소스 |
|------|---------|----------|------|
| SSH | TCP | 22 | 내 IP (또는 0.0.0.0/0) |
| HTTP | TCP | 80 | 0.0.0.0/0 |
| HTTPS | TCP | 443 | 0.0.0.0/0 |
| Custom TCP | TCP | 8000 | 0.0.0.0/0 |

**설명**:
- **SSH (22)**: 서버 접속용
- **HTTP (80)**: Nginx 리버스 프록시용 (선택사항)
- **HTTPS (443)**: SSL 인증서용 (선택사항)
- **8000**: 백엔드 API 포트

---

### Step 8: 스토리지 구성

**볼륨 크기**: 20 GB (기본값, 필요시 조정)

**볼륨 유형**: gp3 (SSD)

---

### Step 9: 고급 세부 정보 (선택사항)

**사용자 데이터** (선택사항 - 자동 설정):

```bash
#!/bin/bash
apt-get update
apt-get install -y docker.io docker-compose
usermod -aG docker ubuntu
systemctl enable docker
systemctl start docker
```

---

### Step 10: 인스턴스 시작

1. **"인스턴스 시작"** 버튼 클릭
2. 인스턴스 생성 완료 대기 (1-2분)

---

## 🔑 키 파일 권한 설정 (Mac/Linux)

다운로드한 키 파일의 권한 설정:

```bash
chmod 400 ticketing-backend-key.pem
```

---

## 📡 인스턴스 접속

### 1. 퍼블릭 IP 확인

1. EC2 대시보드에서 인스턴스 선택
2. **퍼블릭 IPv4 주소** 복사 (예: `54.123.45.67`)

### 2. SSH 접속

```bash
ssh -i ticketing-backend-key.pem ubuntu@your-public-ip
```

**예시**:
```bash
ssh -i ticketing-backend-key.pem ubuntu@54.123.45.67
```

### 3. 첫 접속 시 확인

다음과 같은 메시지가 나오면 `yes` 입력:
```
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
```

---

## ✅ 접속 확인

접속 성공 시 다음과 같은 프롬프트가 표시됩니다:

```
Welcome to Ubuntu 22.04.3 LTS (GNU/Linux ...)
...
ubuntu@ip-xxx-xxx-xxx-xxx:~$
```

---

## 🔧 초기 설정

### 1. 시스템 업데이트

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### 2. Docker 설치

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

### 3. Git 설치

```bash
sudo apt-get install -y git
```

---

## 📝 다음 단계

EC2 인스턴스가 준비되었으니:

1. ✅ **프로젝트 클론**
   ```bash
   git clone https://github.com/your-username/your-repo.git
   cd your-repo/backend
   ```

2. ✅ **환경 변수 설정**
   - `.env` 파일 생성 및 설정

3. ✅ **배포 실행**
   ```bash
   ./deploy.sh
   ```

자세한 내용은 `EC2_DEPLOYMENT_GUIDE.md` 참고

---

## 💰 비용 최적화

### 무료 티어 활용

- **t2.micro** 인스턴스 사용
- 월 750시간 무료
- 12개월 동안 무료

### 비용 절감 팁

1. **사용하지 않을 때 중지**
   - EC2 대시보드에서 인스턴스 중지
   - 중지된 인스턴스는 스토리지 비용만 발생

2. **스팟 인스턴스 사용** (고급)
   - 최대 90% 할인
   - 중단될 수 있음

3. **리전 선택**
   - 가장 가까운 리전 선택 (서울: ap-northeast-2)

---

## 🚨 보안 주의사항

### 1. 키 파일 보안

- 키 파일을 절대 공유하지 마세요
- Git에 커밋하지 마세요
- 안전한 곳에 백업 보관

### 2. 보안 그룹

- SSH 포트(22)는 가능하면 내 IP만 허용
- 프로덕션에서는 불필요한 포트 닫기

### 3. 방화벽 (UFW)

인스턴스 내부에서도 방화벽 설정:

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw enable
```

---

## 🔍 문제 해결

### SSH 접속 실패

**문제**: "Permission denied (publickey)"

**해결**:
1. 키 파일 경로 확인
2. 키 파일 권한 확인: `chmod 400 key.pem`
3. 사용자 이름 확인: `ubuntu` (Ubuntu AMI의 경우)

### 연결 시간 초과

**해결**:
1. 보안 그룹에서 SSH 포트(22) 열려있는지 확인
2. 인스턴스가 실행 중인지 확인
3. 퍼블릭 IP 주소 확인

---

## 📚 참고 자료

- **AWS EC2 문서**: https://docs.aws.amazon.com/ec2/
- **EC2 배포 가이드**: `EC2_DEPLOYMENT_GUIDE.md`
- **백엔드 배포 가이드**: `BACKEND_DEPLOYMENT_QUICK_START.md`

