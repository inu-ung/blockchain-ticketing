# IPFS Mock 모드 설명

## 🤔 Mock 모드란?

**Mock 모드**는 Pinata API 키가 없을 때 사용되는 **가짜 모드**입니다.

### 작동 방식

1. **API 키가 없을 때**:
   - 실제 IPFS에 업로드하지 않음
   - 가짜 해시 (`QmMockHash123456789`) 반환
   - 개발/테스트 목적으로 사용

2. **API 키가 있을 때**:
   - 실제 Pinata를 통해 IPFS에 업로드
   - 실제 IPFS 해시 반환
   - 프로덕션 환경에서 사용

## 📝 코드 동작

```python
# IPFS 서비스 코드
def upload_json(self, data: dict):
    if not self.is_configured:  # API 키가 없으면
        logger.warning("Pinata API keys not configured. Using mock hash.")
        return "QmMockHash123456789"  # 가짜 해시 반환
    
    # 실제 Pinata API 호출
    response = requests.post(url, json=payload, headers=headers)
    return response.json().get("IpfsHash")  # 실제 해시 반환
```

## ⚠️ Mock 모드의 한계

### ✅ 작동하는 것
- 업로드 함수 호출 시 에러 없이 해시 반환
- 개발/테스트 환경에서 코드 흐름 확인 가능
- API 키 없이도 백엔드 서버 실행 가능

### ❌ 작동하지 않는 것
- **실제 IPFS 저장소에 데이터가 저장되지 않음**
- Mock 해시로는 데이터를 조회할 수 없음
- 실제 NFT 메타데이터가 블록체인에 연결되지 않음

## 🔍 실제 테스트 결과

```bash
# Mock 모드에서 업로드
업로드 결과: QmMockHash123456789  # 가짜 해시

# Mock 해시로 조회 시도
조회 결과: None  # 실제 IPFS에 없으므로 조회 실패
```

## 💡 언제 사용하나요?

### Mock 모드 사용 (API 키 없음)
- ✅ 로컬 개발 환경
- ✅ 빠른 프로토타이핑
- ✅ API 구조 테스트
- ✅ 프론트엔드 개발

### 실제 IPFS 사용 (API 키 필요)
- ✅ 프로덕션 환경
- ✅ 실제 NFT 발행
- ✅ 메타데이터 영구 저장
- ✅ 블록체인과 연동

## 🚀 실제 IPFS 사용하려면?

### 1. Pinata 계정 생성
https://pinata.cloud

### 2. API 키 발급
- 대시보드 → Developer → API Keys
- New Key 생성

### 3. 환경 변수 설정
```bash
# backend/.env
PINATA_API_KEY=your_api_key_here
PINATA_SECRET_KEY=your_secret_key_here
```

### 4. 서버 재시작
```bash
# 서버 재시작 후
# is_configured = True로 변경됨
# 실제 IPFS 업로드 시작
```

## 📊 비교표

| 항목 | Mock 모드 | 실제 IPFS |
|------|----------|----------|
| API 키 필요 | ❌ | ✅ |
| 실제 저장 | ❌ | ✅ |
| 데이터 조회 | ❌ | ✅ |
| 개발용 | ✅ | ❌ |
| 프로덕션용 | ❌ | ✅ |
| 비용 | 무료 | 무료 (제한 있음) |

## 🎯 결론

**Mock 모드**는:
- 개발 중에는 편리하지만
- 실제로는 데이터가 저장되지 않습니다
- 프로덕션에서는 반드시 Pinata API 키가 필요합니다

**현재 상태**: Mock 모드로 작동 중 (API 키 없음)
**권장 사항**: 개발이 완료되면 Pinata API 키 설정 권장

