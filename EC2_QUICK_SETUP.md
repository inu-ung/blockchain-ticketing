# EC2 인스턴스 빠른 생성 가이드

## 🚀 5분 안에 EC2 인스턴스 만들기

### 1단계: AWS 콘솔 접속

1. https://console.aws.amazon.com 접속
2. **EC2** 검색 및 클릭
3. **"인스턴스 시작"** 클릭

---

### 2단계: 기본 설정

**이름**: `ticketing-backend`

**AMI**: `Ubuntu Server 22.04 LTS` 검색 및 선택

**인스턴스 유형**: `t3.micro` (무료 티어) 또는 `t3.small`

**키 페어**: 
- "새 키 페어 생성" 클릭
- 이름: `ticketing-backend-key`
- "키 페어 생성" 클릭
- **다운로드된 .pem 파일 보관!**

---

### 3단계: 네트워크 설정

**보안 그룹** → "보안 그룹 생성"

**인바운드 규칙 추가**:

| 유형 | 포트 | 소스 |
|------|------|------|
| SSH | 22 | 내 IP |
| Custom TCP | 8000 | 0.0.0.0/0 |

---

### 4단계: 시작

**"인스턴스 시작"** 클릭

---

### 5단계: 접속

1. 인스턴스 선택 → **퍼블릭 IPv4 주소** 복사
2. 터미널에서:

```bash
# 키 파일 권한 설정
chmod 400 ticketing-backend-key.pem

# 접속
ssh -i ticketing-backend-key.pem ubuntu@your-public-ip
```

---

## ✅ 완료!

이제 `EC2_DEPLOYMENT_GUIDE.md`를 참고하여 백엔드를 배포하세요!

