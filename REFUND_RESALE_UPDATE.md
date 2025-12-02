# 환불 및 재판매 기능 개선 완료

## ✅ 수정 완료 사항

### 1. 환불 로직 개선

#### 변경 사항
- ✅ **Smart Wallet 지원**: Smart Wallet 주소로도 환불 요청 가능
- ✅ **UserOperation 통합**: Account Abstraction을 사용한 환불 요청
- ✅ **Paymaster 지원**: 환불 요청 시 가스비 스폰서
- ✅ **상태 확인**: 이미 환불된 티켓은 재환불 불가
- ✅ **온체인 처리**: RefundManager 컨트랙트와 연동

#### API 엔드포인트
```
POST /api/v1/refunds/request
- 구매한 티켓 환불 요청
- Smart Wallet 또는 일반 지갑 주소 사용 가능
```

```
POST /api/v1/refunds/{refund_id}/approve
- 주최자/관리자가 환불 승인
- 온체인에서 티켓 소각 및 환불금 지불
```

```
POST /api/v1/admin/refunds/emergency
- 관리자 긴급 환불 (이벤트 취소 시)
- 이벤트 취소된 경우에만 사용 가능
```

---

### 2. 재판매 기능 개선

#### 변경 사항
- ✅ **Smart Wallet 지원**: Smart Wallet 주소로도 재판매 등록 가능
- ✅ **UserOperation 통합**: Account Abstraction을 사용한 재판매 등록
- ✅ **상태 확인**: 환불된 티켓은 재판매 불가
- ✅ **소유자 확인**: Smart Wallet 주소 또는 일반 지갑 주소로 확인
- ✅ **온체인 처리**: TicketMarketplace 컨트랙트와 연동

#### API 엔드포인트
```
POST /api/v1/resales
- 구매한 티켓을 재판매 마켓플레이스에 등록
- 가격은 원가의 200%까지 설정 가능
```

```
POST /api/v1/resales/{resale_id}/buy
- 재판매 티켓 구매
- 티켓 소유권 자동 이전
```

```
DELETE /api/v1/resales/{resale_id}
- 재판매 등록 취소
```

---

### 3. "토큰" 개념 설명

#### 토큰(Token)이란?
**토큰 ID (token_id)**는 블록체인에서 각 티켓을 고유하게 식별하는 번호입니다.

#### 왜 필요한가?
- ✅ **고유성**: 각 티켓마다 고유한 번호
- ✅ **위조 불가능**: 블록체인에 저장되어 변경 불가
- ✅ **소유권 추적**: 각 토큰은 고유한 소유자(지갑 주소)를 가짐
- ✅ **전송 가능**: 다른 사람에게 전송 가능

#### 예시
```
이벤트 A의 첫 번째 티켓 → token_id: 1
이벤트 A의 두 번째 티켓 → token_id: 2
이벤트 B의 첫 번째 티켓 → token_id: 3
```

#### 재판매에서의 사용
```
1. 내가 티켓 구매 → token_id: 5 발행
2. 재판매 등록 → token_id: 5를 마켓플레이스에 등록
3. 다른 사람이 구매 → token_id: 5의 소유권이 구매자로 이전
```

**"토큰"은 티켓의 블록체인상 고유 번호입니다!**

---

## 🔄 작동 흐름

### 환불 흐름
```
1. 사용자: 환불 요청
   POST /api/v1/refunds/request
   ↓
2. 백엔드: UserOperation 생성 및 전송
   - RefundManager.requestRefund() 호출
   - Paymaster로 가스비 스폰서
   ↓
3. 주최자/관리자: 환불 승인
   POST /api/v1/refunds/{refund_id}/approve
   ↓
4. 백엔드: 온체인 환불 처리
   - RefundManager.processRefund() 호출
   - 티켓 소각 (NFT 소각)
   - 환불금 지불
   ↓
5. 완료: 티켓 상태 → "refunded"
```

### 재판매 흐름
```
1. 사용자: 재판매 등록
   POST /api/v1/resales
   - 가격 설정 (원가의 200%까지)
   ↓
2. 백엔드: UserOperation 생성 및 전송
   - TicketNFT.approve() 호출 (마켓플레이스에 권한 부여)
   - TicketMarketplace.listTicketForResale() 호출
   ↓
3. 마켓플레이스: 재판매 등록 완료
   - 온체인에 리스팅 저장
   ↓
4. 구매자: 재판매 티켓 구매
   POST /api/v1/resales/{resale_id}/buy
   ↓
5. 백엔드: 온체인 구매 처리
   - TicketMarketplace.buyResaleTicket() 호출
   - 티켓 소유권 이전
   - 판매자에게 지불
   - 수수료 처리
   ↓
6. 완료: 티켓 소유권 → 구매자로 이전
```

---

## 📝 주요 개선 사항

### 1. Smart Wallet 지원
- 기존: 일반 지갑 주소만 지원
- 개선: Smart Wallet 주소도 지원
- 효과: Account Abstraction 사용 시 일관성 유지

### 2. UserOperation 통합
- 기존: 직접 트랜잭션 전송
- 개선: UserOperation을 통한 트랜잭션 실행
- 효과: Paymaster 지원, 가스비 스폰서 가능

### 3. 상태 관리 개선
- 환불된 티켓은 재판매 불가
- 이미 환불된 티켓은 재환불 불가
- 재판매 구매 후 티켓 상태 업데이트

### 4. 에러 처리 개선
- 명확한 에러 메시지
- 상태 확인 로직 추가
- 온체인 실패 시 DB 상태 유지

---

## 🎯 사용 방법

### 환불 요청
```bash
POST /api/v1/refunds/request
{
  "ticket_id": "티켓 UUID",
  "reason": "환불 사유 (선택사항)"
}
```

### 재판매 등록
```bash
POST /api/v1/resales
{
  "ticket_id": "티켓 UUID",
  "price_wei": 1500000000000000000  # 1.5 MATIC (wei 단위)
}
```

### 재판매 구매
```bash
POST /api/v1/resales/{resale_id}/buy
```

---

## ✅ 테스트 체크리스트

- [ ] 환불 요청 (일반 지갑)
- [ ] 환불 요청 (Smart Wallet)
- [ ] 환불 승인
- [ ] 재판매 등록 (일반 지갑)
- [ ] 재판매 등록 (Smart Wallet)
- [ ] 재판매 구매
- [ ] 환불된 티켓 재판매 불가 확인
- [ ] 긴급 환불 (관리자)

---

## 📚 관련 문서

- **재판매 설명**: `RESALE_EXPLANATION.md`
- **스마트 컨트랙트 로직**: `SMART_CONTRACT_LOGIC.md`
- **워크플로우**: `WORKFLOW_DESCRIPTION.md`

