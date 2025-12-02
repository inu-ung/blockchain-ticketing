#!/bin/bash

# 백엔드 배포 스크립트 (EC2용)

set -e

echo "=========================================="
echo "백엔드 배포 시작"
echo "=========================================="

# 환경 변수 파일 확인
if [ ! -f .env ]; then
    echo "❌ .env 파일이 없습니다!"
    echo "EC2_DEPLOYMENT_GUIDE.md를 참고하여 .env 파일을 생성하세요."
    exit 1
fi

echo "✅ .env 파일 확인 완료"

# Docker 및 Docker Compose 설치 확인
if ! command -v docker &> /dev/null; then
    echo "❌ Docker가 설치되지 않았습니다."
    echo "EC2_DEPLOYMENT_GUIDE.md의 Step 2를 참고하여 Docker를 설치하세요."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose가 설치되지 않았습니다."
    echo "EC2_DEPLOYMENT_GUIDE.md의 Step 2를 참고하여 Docker Compose를 설치하세요."
    exit 1
fi

echo "✅ Docker 및 Docker Compose 확인 완료"

# 기존 컨테이너 중지 및 제거
echo ""
echo "기존 컨테이너 정리 중..."
docker-compose -f docker-compose.prod.yml down || true

# Docker 이미지 빌드
echo ""
echo "Docker 이미지 빌드 중..."
docker-compose -f docker-compose.prod.yml build

# 컨테이너 시작
echo ""
echo "컨테이너 시작 중..."
docker-compose -f docker-compose.prod.yml up -d

# 헬스 체크
echo ""
echo "헬스 체크 중..."
sleep 5

for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ 백엔드 서버가 정상적으로 실행 중입니다!"
        echo ""
        echo "=========================================="
        echo "배포 완료!"
        echo "=========================================="
        echo "백엔드 URL: http://localhost:8000"
        echo "API 문서: http://localhost:8000/docs"
        echo "헬스 체크: http://localhost:8000/health"
        echo ""
        echo "로그 확인: docker-compose -f docker-compose.prod.yml logs -f"
        echo "=========================================="
        exit 0
    fi
    echo "대기 중... ($i/30)"
    sleep 2
done

echo "❌ 헬스 체크 실패"
echo "로그 확인: docker-compose -f docker-compose.prod.yml logs backend"
exit 1

