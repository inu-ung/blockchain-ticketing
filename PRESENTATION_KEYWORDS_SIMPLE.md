# 발표 자료용 간단 키워드

## 4단계별 핵심 키워드

### 1단계: User (사용자)
**키워드**:
- `회원가입/로그인`
- `Smart Wallet 자동 생성`
- `Account Abstraction (ERC-4337)`
- `CREATE2 (Deterministic Address)`

**간단 버전**:
- Smart Wallet 자동 생성
- Account Abstraction
- CREATE2

---

### 2단계: Event Organizer (주최자)
**키워드**:
- `이벤트 정보 입력`
- `메타데이터 JSON 생성`
- `IPFS 업로드`
- `EventManager 등록`
- `eventId 발급`
- `관리자 승인`

**간단 버전**:
- IPFS 메타데이터
- EventManager 등록
- 관리자 승인

---

### 3단계: Buy Ticket (티켓 구매)
**키워드**:
- `UserOperation 생성`
- `Paymaster 검증`
- `가스비 스폰서`
- `UserOperation 서명`
- `백엔드 자동 처리`

**간단 버전**:
- UserOperation 생성
- Paymaster 검증
- 가스비 스폰서

---

### 4단계: Ticketing (티켓 발행)
**키워드**:
- `EntryPoint 검증`
- `Smart Wallet 실행`
- `EventManager.purchaseTicket`
- `TicketNFT.mintTicket`
- `NFT 발행`
- `주최자 자동 지불`

**간단 버전**:
- EntryPoint 실행
- EventManager → TicketNFT
- NFT 발행 + 자동 지불

---

## 슬라이드별 키워드 제안

### 슬라이드 1: User 단계
```
회원가입/로그인
    ↓
Smart Wallet 자동 생성
(Account Abstraction)
    ↓
CREATE2 Deterministic Address
```

### 슬라이드 2: Event Organizer 단계
```
이벤트 정보 입력
    ↓
IPFS 메타데이터 업로드
    ↓
EventManager 등록
    ↓
관리자 승인
```

### 슬라이드 3: Buy Ticket 단계
```
구매 요청
    ↓
UserOperation 생성
    ↓
Paymaster 검증 (가스비 스폰서)
    ↓
UserOperation 서명
```

### 슬라이드 4: Ticketing 단계
```
EntryPoint 검증
    ↓
Smart Wallet → EventManager
    ↓
EventManager → TicketNFT
    ↓
NFT 발행 + 주최자 지불
```

---

## 한 줄 요약 키워드

### 각 단계별
1. **User**: `Smart Wallet 자동 생성 (ERC-4337)`
2. **Event Organizer**: `IPFS + EventManager 등록`
3. **Buy Ticket**: `UserOperation + Paymaster`
4. **Ticketing**: `EntryPoint → EventManager → TicketNFT`

---

## 기술 키워드 (참고용)

### 핵심 기술
- `ERC-721 NFT`
- `ERC-4337 Account Abstraction`
- `IPFS`
- `Polygon`

### 주요 컴포넌트
- `Smart Wallet`
- `EntryPoint`
- `EventManager`
- `TicketNFT`
- `Paymaster`
- `Bundler`

---

## 발표 시 강조할 키워드

### 사용자 경험
- **"지갑 설치 불필요"**
- **"원클릭 구매"**
- **"자동 가스비 처리"**

### 기술적 우수성
- **"ERC-4337 표준 준수"**
- **"블록체인 투명성"**
- **"위조 불가능"**

### 자동화
- **"스마트 컨트랙트 자동 실행"**
- **"자동 지불 분배"**
- **"자동 검증"**

