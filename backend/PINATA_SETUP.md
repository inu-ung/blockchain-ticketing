# Pinata API 키 설정 가이드

## 📍 파일 위치

**`backend/.env`** 파일에 입력하세요.

## 🔑 입력 방법

### 1. 파일 열기

```bash
cd backend
# 텍스트 에디터로 .env 파일 열기
```

또는 IDE에서 `backend/.env` 파일을 직접 열기

### 2. API 키 입력

`.env` 파일에서 다음 두 줄을 찾아서:

```env
PINATA_API_KEY=your_pinata_api_key_here
PINATA_SECRET_KEY=your_pinata_secret_key_here
```

실제 API 키로 교체:

```env
PINATA_API_KEY=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
PINATA_SECRET_KEY=xyz789uvw012rst345qop678nml901kji234hgf567edc890ba
```

### 3. 저장 및 확인

- 파일 저장
- 따옴표 없이 입력 (큰따옴표, 작은따옴표 모두 불필요)
- 공백 없이 입력

## ✅ 설정 확인

### 방법 1: 서버 재시작 후 테스트

```bash
# 서버 재시작
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

다른 터미널에서:
```bash
curl http://localhost:8000/api/v1/ipfs/test
```

응답:
```json
{
  "status": "success",
  "message": "IPFS connection successful",
  "configured": true
}
```

### 방법 2: Python으로 직접 확인

```bash
cd backend
source venv/bin/activate
python -c "from app.services.ipfs_service import ipfs_service; print(f'Configured: {ipfs_service.is_configured}')"
```

출력: `Configured: True` ✅

## ⚠️ 주의사항

1. **`.env` 파일은 절대 Git에 커밋하지 마세요!**
   - `.gitignore`에 이미 포함되어 있어야 합니다
   - API 키가 공개되면 보안 위험

2. **파일 경로 확인**
   - 반드시 `backend/.env` 파일에 입력
   - `backend/.env.example` 같은 다른 파일이 아닌지 확인

3. **형식 확인**
   - `PINATA_API_KEY=키값` (등호 앞뒤 공백 없음)
   - 따옴표 불필요
   - 한 줄에 하나씩

## 🐛 문제 해결

### "Configured: False"가 나오는 경우

1. `.env` 파일이 `backend/` 디렉토리에 있는지 확인
2. 파일 이름이 정확히 `.env`인지 확인 (`.env.txt` 아님)
3. API 키 값에 공백이나 특수문자가 없는지 확인
4. 서버를 재시작했는지 확인

### "Connection failed"가 나오는 경우

1. API 키가 올바른지 확인
2. Pinata 대시보드에서 키가 활성화되어 있는지 확인
3. 인터넷 연결 확인

## 📝 예시 파일

```env
# Pinata IPFS API Keys
PINATA_API_KEY=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
PINATA_SECRET_KEY=xyz789uvw012rst345qop678nml901kji234hgf567edc890ba

# 다른 설정들...
DATABASE_URL=sqlite:///./ticketing.db
SECRET_KEY=your-secret-key-here
```

## 🎯 완료!

API 키를 입력하고 서버를 재시작하면:
- ✅ Mock 모드에서 실제 IPFS 모드로 전환
- ✅ 실제 IPFS에 데이터 업로드
- ✅ 업로드된 데이터 조회 가능

