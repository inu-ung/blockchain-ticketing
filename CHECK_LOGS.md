# 백엔드 서버 로그 확인 가이드

## 빠른 확인 방법

### 1. 백엔드 서버 실행 (터미널 1)
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

### 2. 테스트 실행 (터미널 2)
```bash
cd backend
source venv/bin/activate
python test_user_operation_purchase.py
```

### 3. 로그 확인
- 터미널 1에서 실시간 로그 확인
- 오류 메시지와 스택 트레이스 확인

## 상세 로그 활성화

### 환경 변수 설정
```bash
export LOG_LEVEL=DEBUG
uvicorn main:app --reload --log-level debug
```

### 또는 Python 코드에서
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 주요 로그 위치

1. **콘솔 출력**: 백엔드 서버 실행 터미널
2. **에러 로그**: `logger.error()` 호출 시 콘솔에 표시
3. **INFO 로그**: `logger.info()` 호출 시 콘솔에 표시

## 로그 예시

### 정상 로그
```
INFO:app.services.aa_service:Created UserOperation: sender=0x..., target=0x...
INFO:app.services.aa_service:UserOperation signed by 0x...
```

### 오류 로그
```
ERROR:app.api.v1.tickets:Failed to purchase ticket with UserOperation: ...
Traceback (most recent call last):
  File "...", line ..., in ...
    ...
```

## 문제 해결

1. **Internal Server Error**: 
   - 로그에서 정확한 오류 메시지 확인
   - 스택 트레이스에서 오류 발생 위치 확인

2. **로그가 안 보임**:
   - 백엔드 서버가 실행 중인지 확인
   - 로깅 레벨이 너무 높은지 확인 (INFO 이상)

3. **상세 로그 필요**:
   - `--log-level debug` 옵션 사용
   - 또는 코드에 `logger.debug()` 추가

