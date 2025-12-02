#!/bin/bash

# EC2 인스턴스 초기 설정 스크립트
# EC2 인스턴스에 접속한 후 실행하세요

set -e

echo "=========================================="
echo "EC2 인스턴스 초기 설정 시작"
echo "=========================================="

# 1. 시스템 업데이트
echo ""
echo "[1/5] 시스템 업데이트 중..."
sudo apt-get update
sudo apt-get upgrade -y

# 2. Docker 설치
echo ""
echo "[2/5] Docker 설치 중..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
    echo "✅ Docker 설치 완료"
else
    echo "✅ Docker가 이미 설치되어 있습니다"
fi

# 3. Docker Compose 설치
echo ""
echo "[3/5] Docker Compose 설치 중..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose 설치 완료"
else
    echo "✅ Docker Compose가 이미 설치되어 있습니다"
fi

# 4. Docker 그룹에 사용자 추가
echo ""
echo "[4/5] Docker 그룹 설정 중..."
sudo usermod -aG docker ubuntu
echo "✅ Docker 그룹 설정 완료"
echo "⚠️  재로그인하거나 'newgrp docker' 명령을 실행하세요"

# 5. Git 설치
echo ""
echo "[5/5] Git 설치 중..."
if ! command -v git &> /dev/null; then
    sudo apt-get install -y git
    echo "✅ Git 설치 완료"
else
    echo "✅ Git이 이미 설치되어 있습니다"
fi

# 설치 확인
echo ""
echo "=========================================="
echo "설치 확인"
echo "=========================================="
echo "Docker 버전:"
docker --version || echo "⚠️  Docker 그룹에 재로그인 필요: newgrp docker"

echo ""
echo "Docker Compose 버전:"
docker-compose --version

echo ""
echo "Git 버전:"
git --version

echo ""
echo "=========================================="
echo "✅ 초기 설정 완료!"
echo "=========================================="
echo ""
echo "다음 단계:"
echo "1. Docker 그룹 적용: newgrp docker"
echo "2. 프로젝트 클론: git clone <your-repo-url>"
echo "3. backend 디렉토리로 이동: cd <repo>/backend"
echo "4. .env 파일 생성 및 설정"
echo "5. 배포 실행: ./deploy.sh"
echo "=========================================="

