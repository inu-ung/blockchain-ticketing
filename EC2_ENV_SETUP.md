# EC2 .env 파일 설정 가이드

## 📝 .env 파일 설정 방법

nano 에디터에서 다음 내용을 입력하세요:

---

## 전체 .env 파일 내용

```env
# Database (PostgreSQL - Docker 컨테이너 사용)
DATABASE_URL=postgresql://postgres:your-strong-password@postgres:5432/ticketing
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-strong-password-here
POSTGRES_DB=ticketing

# JWT
SECRET_KEY=your-very-secret-key-here-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Web3 (Amoy 테스트넷)
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
POLYGON_MAINNET_RPC_URL=https://polygon-rpc.com
PRIVATE_KEY=your-private-key-here

# Contract Addresses (테스트넷 배포 주소 - 나중에 업데이트)
TICKET_ACCESS_CONTROL_ADDRESS=0x...
TICKET_NFT_ADDRESS=0x...
EVENT_MANAGER_ADDRESS=0x...
MARKETPLACE_ADDRESS=0x...
REFUND_MANAGER_ADDRESS=0x...
SMART_WALLET_FACTORY_ADDRESS=0x...
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789

# IPFS (Pinata)
PINATA_API_KEY=c8572d477668830dae7b
PINATA_SECRET_KEY=7adec890b542fc21803d5be9ab3da271dfd4d9f15d9761eb317761566b5c

# Account Abstraction (선택사항)
BUNDLER_URL=
PAYMASTER_URL=

# CORS (프론트엔드 URL - Vercel 배포 후 업데이트)
ALLOWED_ORIGINS=http://localhost:5173
```

---

## 🔧 설정 방법

### 1. nano 에디터 사용법

- **저장**: `Ctrl + O` → Enter
- **종료**: `Ctrl + X`
- **복사/붙여넣기**: 마우스로 선택 후 우클릭

### 2. 필수 항목 수정

#### Database 비밀번호 생성

```bash
# EC2에서 실행
python3 -c "import secrets; print(secrets.token_urlsafe(16))"
```

생성된 비밀번호를 `POSTGRES_PASSWORD`에 사용

#### SECRET_KEY 생성

```bash
# EC2에서 실행
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

생성된 키를 `SECRET_KEY`에 사용

#### PRIVATE_KEY

블록체인 트랜잭션에 사용할 개인키 입력

---

## ⚠️ 중요 사항

1. **DATABASE_URL**: `sqlite:///./ticketing.db` → PostgreSQL로 변경 필요!
2. **POSTGRES_PASSWORD**: 강력한 비밀번호 사용
3. **SECRET_KEY**: 강력한 랜덤 문자열 사용
4. **Contract Addresses**: 테스트넷 배포 완료 후 업데이트

---

## ✅ 저장 및 종료

1. `Ctrl + O` (저장)
2. Enter (파일명 확인)
3. `Ctrl + X` (종료)

---

## 다음 단계

.env 파일 저장 후:

```bash
# 배포 실행
chmod +x deploy.sh
./deploy.sh
```

