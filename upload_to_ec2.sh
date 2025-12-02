#!/bin/bash

# EC2로 백엔드 업로드 스크립트

# 설정 (실제 값으로 변경하세요)
KEY_FILE="mykey.pem"
EC2_IP="43.201.98.14"
EC2_USER="ubuntu"

# 현재 디렉토리 확인
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "EC2로 백엔드 업로드"
echo "=========================================="
echo "키 파일: $KEY_FILE"
echo "EC2 주소: $EC2_USER@$EC2_IP"
echo "현재 디렉토리: $SCRIPT_DIR"
echo ""

# 키 파일 확인
if [ ! -f "$KEY_FILE" ]; then
    echo "❌ 키 파일을 찾을 수 없습니다: $KEY_FILE"
    echo ""
    echo "키 파일 위치를 확인하세요:"
    echo "  find ~ -name '*.pem' -type f"
    echo ""
    echo "또는 키 파일의 전체 경로를 사용하세요:"
    echo "  scp -i /전체/경로/키파일.pem backend.tar.gz $EC2_USER@$EC2_IP:~/"
    exit 1
fi

# 키 파일 권한 확인
chmod 400 "$KEY_FILE" 2>/dev/null

# backend.tar.gz 파일 확인
if [ ! -f "backend.tar.gz" ]; then
    echo "❌ backend.tar.gz 파일을 찾을 수 없습니다"
    echo ""
    echo "백엔드 디렉토리를 압축하세요:"
    echo "  cd ~/blockchain/BC"
    echo "  tar -czf backend.tar.gz backend/"
    exit 1
fi

echo "✅ 파일 확인 완료"
echo "📦 업로드 시작..."
echo ""

# 업로드 실행
scp -i "$KEY_FILE" backend.tar.gz "$EC2_USER@$EC2_IP:~/"

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ 업로드 완료!"
    echo "=========================================="
    echo ""
    echo "다음 단계 (EC2 인스턴스에서 실행):"
    echo "  ssh -i $KEY_FILE $EC2_USER@$EC2_IP"
    echo "  tar -xzf backend.tar.gz"
    echo "  cd backend"
    echo "  nano .env  # 환경 변수 설정"
    echo "  ./deploy.sh  # 배포 실행"
    echo "=========================================="
else
    echo ""
    echo "❌ 업로드 실패"
    echo "키 파일과 EC2 주소를 확인하세요"
    exit 1
fi

