# IPFS 서비스 설정 가이드

## 📋 개요

IPFS 서비스는 Pinata를 통해 구현되어 있습니다. Pinata는 IPFS 데이터를 영구적으로 저장하고 관리하는 서비스입니다.

## 🔧 설정 방법

### 1. Pinata 계정 생성

1. https://pinata.cloud 접속
2. 무료 계정 생성
3. 대시보드에서 API 키 생성

### 2. API 키 발급

1. Pinata 대시보드 → **Developer** → **API Keys**
2. **New Key** 클릭
3. 권한 설정:
   - `pinFileToIPFS`: ✅
   - `pinJSONToIPFS`: ✅
   - `unpin`: ✅ (선택)
4. API Key와 Secret Key 복사

### 3. 환경 변수 설정

`backend/.env` 파일에 추가:

```env
PINATA_API_KEY=your_api_key_here
PINATA_SECRET_KEY=your_secret_key_here
```

또는 `backend/app/core/config.py`에서 직접 설정 (개발용)

## 🧪 테스트

### 1. 연결 테스트

```bash
# API 테스트
curl http://localhost:8000/api/v1/ipfs/test
```

또는 Swagger UI에서:
- http://localhost:8000/docs
- `/api/v1/ipfs/test` 엔드포인트 호출

### 2. 데이터 업로드 테스트

```bash
curl -X POST http://localhost:8000/api/v1/ipfs/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Ticket",
    "description": "Test description",
    "image": "https://example.com/image.png"
  }'
```

### 3. 데이터 조회 테스트

```bash
curl http://localhost:8000/api/v1/ipfs/retrieve/QmYourHashHere
```

## 📝 사용 예시

### 이벤트 생성 시

이벤트를 생성하면 자동으로 IPFS에 메타데이터가 업로드됩니다:

```python
# events.py에서 자동 처리
metadata = {
    "name": event_create.name,
    "description": event_create.description,
    "event_date": event_create.event_date.isoformat(),
}
ipfs_hash = ipfs_service.upload_json(metadata)
```

### 티켓 구매 시

티켓을 구매하면 NFT 메타데이터가 IPFS에 업로드됩니다:

```python
# tickets.py에서 자동 처리
metadata = {
    "name": f"Ticket for {event.name}",
    "description": f"Ticket for event: {event.name}",
    "attributes": [...]
}
ipfs_hash = ipfs_service.upload_json(metadata, pinata_metadata)
```

### 메타데이터 조회

```python
# IPFS에서 메타데이터 가져오기
metadata = ipfs_service.get_json(ipfs_hash)
```

## 🔍 IPFS 게이트웨이

다음 게이트웨이를 통해 IPFS 데이터에 접근할 수 있습니다:

1. **Pinata Gateway**: `https://gateway.pinata.cloud/ipfs/{hash}`
2. **IPFS.io**: `https://ipfs.io/ipfs/{hash}`
3. **Cloudflare**: `https://cloudflare-ipfs.com/ipfs/{hash}`

## ⚠️ 주의사항

1. **API 키 보안**: API 키를 절대 공개 저장소에 올리지 마세요
2. **무료 플랜 제한**: Pinata 무료 플랜은 월 1GB 제한
3. **Mock 모드**: API 키가 없으면 자동으로 Mock 해시 반환 (개발용)

## 🚀 프로덕션 설정

프로덕션 환경에서는:

1. 환경 변수로 API 키 관리
2. IPFS 노드 직접 운영 (선택)
3. 여러 IPFS 게이트웨이 사용
4. 데이터 백업 전략 수립

## 📚 참고 자료

- [Pinata 문서](https://docs.pinata.cloud/)
- [IPFS 문서](https://docs.ipfs.io/)
- [NFT 메타데이터 표준](https://docs.opensea.io/docs/metadata-standards)
