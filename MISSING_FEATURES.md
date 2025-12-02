# 미구현 기능 목록

## 🔴 완전히 미구현

### 1. Google OAuth 로그인
**위치**: `backend/app/api/v1/auth.py:53-60`
```python
@router.post("/google")
async def google_login():
    """Google 소셜 로그인 (구현 예정)"""
    # TODO: Google OAuth 구현
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google login not implemented yet"
    )
```

**상태**: 완전히 미구현 (501 에러 반환)

---

### 2. 긴급 환불 로직
**위치**: `backend/app/api/v1/admin.py:78-86`
```python
@router.post("/refunds/emergency")
async def emergency_refund(...):
    """긴급 환불 (관리자만)"""
    # TODO: 긴급 환불 로직 구현
    return {"message": "Emergency refund processed", "ticket_id": ticket_id}
```

**상태**: 스텁만 있음, 실제 로직 없음

---

## 🟡 부분 구현 (TODO 주석 있음)

### 3. Account Abstraction 지갑 생성 로직
**위치**: `backend/app/api/v1/auth.py:96-97`
```python
# TODO: Account Abstraction 지갑 생성 로직
# current_user.smart_wallet_address = generate_smart_wallet(...)
```

**상태**: 
- `/wallet/create` 엔드포인트는 구현됨
- 하지만 `/wallet/connect`에서 지갑 생성 로직이 주석 처리됨

---

### 4. 사용자 Private Key 안전 관리
**위치**: `backend/app/api/v1/user_operations.py:127`
```python
# TODO: 사용자의 private key를 안전하게 관리해야 함
# 현재는 서비스 계정의 private key 사용 (테스트용)
```

**상태**: 
- 현재는 서비스 계정의 private key 사용
- 사용자별 private key 관리 로직 없음
- 보안 개선 필요

---

## 🟢 구현됨 (검증 필요)

### 5. Web3 서비스
**위치**: `backend/app/services/web3_service.py`
- ✅ 이벤트 생성/승인
- ✅ 티켓 구매
- ✅ 재판매 등록/구매
- ✅ 환불 요청/처리

**상태**: 구현 완료, 테스트 필요

---

### 6. IPFS 서비스
**위치**: `backend/app/services/ipfs_service.py`
- ✅ JSON 업로드
- ✅ 파일 업로드
- ✅ 데이터 조회

**상태**: 구현 완료, Pinata API 키 설정 필요

---

### 7. Account Abstraction 서비스
**위치**: `backend/app/services/aa_service.py`
- ✅ Smart Wallet 주소 생성
- ✅ UserOperation 생성
- ✅ UserOperation 서명
- ✅ Bundler 연동
- ✅ Paymaster 연동

**상태**: 구현 완료, 테스트 필요

---

## 📋 우선순위별 구현 계획

### 우선순위 1: 보안 개선
1. **사용자 Private Key 안전 관리**
   - 사용자별 키 관리 시스템
   - 암호화 저장
   - 또는 사용자 서명을 프론트엔드에서 처리

### 우선순위 2: 기능 완성
2. **긴급 환불 로직 구현**
   - RefundManager의 `emergencyRefund` 호출
   - 이벤트 취소 시 자동 환불

### 우선순위 3: 선택적 기능
3. **Google OAuth 로그인**
   - OAuth 2.0 플로우 구현
   - Google 계정 연동

---

## 🔍 확인 방법

어떤 기능이 구현되지 않았는지 확인하려면:

```bash
# TODO 주석 검색
grep -r "TODO" backend/app/

# FIXME 주석 검색
grep -r "FIXME" backend/app/

# NotImplementedError 검색
grep -r "NotImplementedError" backend/app/
```

---

## 💡 다음 단계

어떤 기능부터 구현할까요?

1. **긴급 환불 로직** (가장 간단)
2. **사용자 Private Key 관리** (보안 중요)
3. **Google OAuth** (선택적)

