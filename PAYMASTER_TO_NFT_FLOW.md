# Paymaster 검증 이후 NFT 티켓 발행까지의 워크플로우

## 전체 흐름 개요

```
Paymaster 검증
    ↓
UserOperation 서명
    ↓
EntryPoint로 전송
    ↓
EntryPoint 검증 (Smart Wallet + Paymaster)
    ↓
Smart Wallet 실행
    ↓
EventManager.purchaseTicket 호출
    ↓
TicketNFT.mintTicket 호출
    ↓
NFT 발행 완료
    ↓
백엔드가 tokenId 추출
```

---

## 단계별 상세 설명

### 1단계: Paymaster 검증 완료 후 UserOperation 서명

**위치**: `backend/app/api/v1/tickets.py` (line 290-306)

```python
# Paymaster 데이터 가져오기 (티켓 구매는 스폰서)
paymaster_data = aa_service.get_paymaster_sponsor_data(
    user_operation,
    target=settings.EVENT_MANAGER_ADDRESS
)
user_operation["paymasterAndData"] = paymaster_data

# UserOperation 서명
signed_user_op = aa_service.sign_user_operation(user_operation, private_key)
```

**동작**:
- Paymaster 데이터가 `paymasterAndData` 필드에 포함됨
- UserOperation 해시를 계산하고 서명
- 서명이 `signature` 필드에 추가됨

**결과**: 서명된 UserOperation 완성

---

### 2단계: EntryPoint로 UserOperation 전송

**위치**: `backend/app/services/aa_service.py` (line 387-451)

**경로 A: Bundler 사용 (프로덕션)**
```python
# Bundler API 호출
POST {bundler_url}
{
    "method": "eth_sendUserOperation",
    "params": [user_op_rpc, entry_point_address]
}
```
- Bundler가 UserOperation을 번들링하여 블록체인에 제출
- UserOperation 해시 반환

**경로 B: 직접 EntryPoint 호출 (로컬 테스트)**
```python
# EntryPoint.handleOps 직접 호출
entry_point.functions.handleOps([user_op_tuple], beneficiary)
```
- 서비스 계정이 직접 트랜잭션 전송
- 트랜잭션 해시 반환

**결과**: 트랜잭션이 블록체인에 제출됨

---

### 3단계: EntryPoint 내부 검증 프로세스

**위치**: EntryPoint 컨트랙트 (ERC-4337 표준)

#### 3-1. Paymaster 검증 (있는 경우)

```
EntryPoint.validatePaymasterUserOp(userOp)
    ↓
Paymaster 컨트랙트 호출
    ↓
Paymaster.validatePaymasterUserOp 검증
    - 정책 확인 (티켓 구매는 스폰서 가능)
    - 서명 검증
    - 가스비 지불 가능 여부 확인
    ↓
검증 통과 ✅
```

**동작**:
- `paymasterAndData`가 비어있지 않으면 Paymaster 검증 시작
- Paymaster 컨트랙트의 `validatePaymasterUserOp` 함수 호출
- Paymaster가 가스비를 지불할 수 있는지 확인
- 검증 통과 시 Paymaster가 가스비를 지불할 준비 완료

#### 3-2. Smart Wallet 검증

```
EntryPoint.validateUserOp(userOp)
    ↓
Smart Wallet.validateUserOp 호출
    ↓
서명 검증 (ECDSA.recover)
    ↓
Nonce 검증
    ↓
검증 통과 ✅
```

**위치**: `contracts/contracts/SmartWallet.sol` (line 81-105)

```solidity
function validateUserOp(
    UserOperation calldata userOp,
    bytes32 userOpHash,
    uint256 missingFunds
) external returns (uint256 validationData) {
    // EntryPoint에서만 호출 가능
    require(msg.sender == entryPoint, "SmartWallet: only EntryPoint");
    
    // 서명 검증
    bytes32 hash = userOpHash.toEthSignedMessageHash();
    address signer = ECDSA.recover(hash, userOp.signature);
    require(signer == owner, "SmartWallet: invalid signature");
    
    // Nonce 검증
    require(userOp.nonce == nonce, "SmartWallet: invalid nonce");
    nonce++;
    
    return 0; // 검증 성공
}
```

**동작**:
- UserOperation 해시를 EIP-191 형식으로 변환
- 서명에서 서명자 주소 복구
- 서명자가 Smart Wallet의 owner인지 확인
- Nonce가 올바른지 확인 (재사용 공격 방지)
- 검증 통과 시 nonce 증가

**결과**: Smart Wallet 검증 완료

---

### 4단계: Smart Wallet 실행

**위치**: EntryPoint → Smart Wallet.execute

```
EntryPoint.executeUserOp(userOp)
    ↓
Smart Wallet.execute 호출
    ↓
EventManager.purchaseTicket 실행
```

**위치**: `contracts/contracts/SmartWallet.sol` (line 59-72)

```solidity
function execute(
    address target,
    uint256 value,
    bytes calldata data
) external {
    require(msg.sender == entryPoint, "SmartWallet: only EntryPoint");
    
    // 컨트랙트 호출
    (bool success, ) = target.call{value: value}(data);
    require(success, "SmartWallet: execution failed");
    
    emit Executed(target, value, data);
}
```

**동작**:
- `target`: EventManager 주소
- `value`: 티켓 가격 (wei)
- `data`: `purchaseTicket(eventId, tokenURI)` 함수 호출 데이터
- Smart Wallet이 EventManager를 호출

**결과**: EventManager.purchaseTicket 함수 실행 시작

---

### 5단계: EventManager.purchaseTicket 실행

**위치**: `contracts/contracts/EventManager.sol` (line 177-206)

```solidity
function purchaseTicket(
    uint256 eventId,
    string memory tokenURI
) external payable nonReentrant returns (uint256) {
    Event storage eventData = events[eventId];
    
    // 검증
    require(eventData.approved, "EventManager: event not approved");
    require(!eventData.cancelled, "EventManager: event is cancelled");
    require(
        block.timestamp >= eventData.startTime && 
        block.timestamp <= eventData.endTime,
        "EventManager: not in sale period"
    );
    require(
        eventData.soldTickets < eventData.maxTickets,
        "EventManager: tickets sold out"
    );
    require(msg.value >= eventData.price, "EventManager: insufficient payment");
    
    // 티켓 발행
    uint256 tokenId = ticketNFT.mintTicket(msg.sender, eventId, tokenURI);
    eventData.soldTickets++;
    
    // 주최자에게 지불
    if (msg.value > 0) {
        (bool success, ) = eventData.organizer.call{value: msg.value}("");
        require(success, "EventManager: payment failed");
    }
    
    emit TicketSold(eventId, tokenId, msg.sender, eventData.price);
    return tokenId;
}
```

**동작**:
1. **이벤트 검증**
   - 이벤트가 승인되었는지 확인
   - 이벤트가 취소되지 않았는지 확인
   - 현재 시간이 판매 기간 내인지 확인
   - 티켓이 매진되지 않았는지 확인
   - 지불 금액이 충분한지 확인

2. **티켓 발행**
   - `ticketNFT.mintTicket(msg.sender, eventId, tokenURI)` 호출
   - `msg.sender`는 Smart Wallet 주소 (사용자의 Smart Wallet)

3. **판매 수량 증가**
   - `eventData.soldTickets++`

4. **주최자에게 지불**
   - Smart Wallet에서 받은 ETH를 주최자에게 전송

5. **이벤트 발생**
   - `TicketSold(eventId, tokenId, msg.sender, eventData.price)` 이벤트 발생

**결과**: TicketNFT.mintTicket 호출 및 주최자 지불 완료

---

### 6단계: TicketNFT.mintTicket 실행 (NFT 발행)

**위치**: `contracts/contracts/TicketNFT.sol` (line 47-62)

```solidity
function mintTicket(
    address to,
    uint256 eventId,
    string memory tokenURI
) external onlyRole(MINTER_ROLE) nonReentrant returns (uint256) {
    uint256 tokenId = _tokenIdCounter;
    _tokenIdCounter++;
    
    _safeMint(to, tokenId);
    _setTokenURI(tokenId, tokenURI);
    tokenToEvent[tokenId] = eventId;
    eventTicketCount[eventId]++;
    
    emit TicketMinted(tokenId, eventId, to, tokenURI);
    return tokenId;
}
```

**동작**:
1. **Token ID 생성**
   - `_tokenIdCounter`를 사용하여 고유한 tokenId 생성
   - 카운터 증가

2. **NFT 발행**
   - `_safeMint(to, tokenId)`: ERC-721 표준에 따라 NFT 발행
   - `to`는 Smart Wallet 주소 (사용자의 Smart Wallet)
   - NFT 소유권이 Smart Wallet에 할당됨

3. **메타데이터 설정**
   - `_setTokenURI(tokenId, tokenURI)`: IPFS URI 설정
   - `tokenURI`는 `ipfs://Qm...` 형식

4. **매핑 저장**
   - `tokenToEvent[tokenId] = eventId`: 토큰과 이벤트 연결
   - `eventTicketCount[eventId]++`: 이벤트별 티켓 수 증가

5. **이벤트 발생**
   - `TicketMinted(tokenId, eventId, to, tokenURI)` 이벤트 발생

**결과**: NFT 티켓이 블록체인에 발행되고 Smart Wallet에 할당됨

---

### 7단계: 트랜잭션 완료 및 tokenId 추출

**위치**: `backend/app/api/v1/tickets.py` (line 312-380)

#### 7-1. 트랜잭션 영수증 대기

```python
receipt = web3_service.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
```

**동작**:
- 트랜잭션이 블록에 포함될 때까지 대기
- 최대 120초 대기
- 트랜잭션 상태 확인 (성공/실패)

#### 7-2. TicketSold 이벤트에서 tokenId 추출

```python
# EventManager 컨트랙트에서 발생한 이벤트만 확인
event_manager_address_checksum = Web3.to_checksum_address(settings.EVENT_MANAGER_ADDRESS)
ticket_sold = contract.events.TicketSold()

for log in receipt.logs:
    # EventManager 컨트랙트에서 발생한 로그만 확인
    if log.address.lower() == event_manager_address_checksum.lower():
        decoded = ticket_sold.process_log(log)
        if decoded.args.eventId == event.event_id_onchain:
            token_id = decoded.args.tokenId
            break
```

**동작**:
- 트랜잭션 receipt의 모든 로그 확인
- EventManager 컨트랙트에서 발생한 `TicketSold` 이벤트 찾기
- 이벤트에서 `tokenId` 추출

#### 7-3. Fallback: TicketNFT에서 직접 조회

```python
# token_id를 찾지 못한 경우, TicketNFT에서 직접 조회
ticket_nft = web3_service._get_contract(settings.TICKET_NFT_ADDRESS, "TicketNFT")
total_supply = ticket_nft.functions.totalSupply().call()

# 최근 mint된 token들 확인
for i in range(min(10, total_supply)):
    check_token_id = total_supply - 1 - i
    owner = ticket_nft.functions.ownerOf(check_token_id).call()
    token_to_event = ticket_nft.functions.tokenToEvent(check_token_id).call()
    
    if (owner.lower() == current_user.smart_wallet_address.lower() and 
        token_to_event == event.event_id_onchain):
        token_id = check_token_id
        break
```

**동작**:
- 이벤트에서 tokenId를 찾지 못한 경우
- TicketNFT 컨트랙트에서 최근 mint된 토큰 확인
- 사용자의 Smart Wallet이 소유하고, 해당 이벤트의 토큰인지 확인

#### 7-4. 최종 Fallback: 데이터베이스에서 계산

```python
# 마지막 수단: 데이터베이스에서 최대 token_id + 1 사용
if token_id is None:
    max_token_id = db.query(func.max(Ticket.token_id)).scalar() or 0
    token_id = max_token_id + 1
```

**동작**:
- 모든 방법이 실패한 경우
- 데이터베이스에서 최대 token_id 조회
- +1하여 임시 token_id 사용

---

### 8단계: 데이터베이스에 티켓 저장

**위치**: `backend/app/api/v1/tickets.py` (line 380 이후)

```python
# 데이터베이스에 티켓 저장
db_ticket = Ticket(
    token_id=token_id,
    event_id=event_uuid,
    owner_address=current_user.smart_wallet_address,
    ipfs_hash=ipfs_hash,
    status=TicketStatus.ACTIVE,
    purchase_price_wei=event.price_wei,
    purchase_tx_hash=tx_hash
)
db.add(db_ticket)
db.commit()
```

**동작**:
- 추출한 `token_id`와 함께 티켓 정보 저장
- `owner_address`는 Smart Wallet 주소
- 트랜잭션 해시 저장
- 상태를 `ACTIVE`로 설정

**결과**: 데이터베이스에 티켓 정보 저장 완료

---

## 전체 흐름 요약

```
1. Paymaster 검증 ✅
   → Paymaster 데이터 포함

2. UserOperation 서명 ✅
   → 서명 추가

3. EntryPoint로 전송 ✅
   → 트랜잭션 제출

4. EntryPoint 검증 ✅
   ├─ Paymaster 검증 (가스비 지불 승인)
   └─ Smart Wallet 검증 (서명 + Nonce)

5. Smart Wallet 실행 ✅
   → EventManager.purchaseTicket 호출

6. EventManager 검증 ✅
   → 이벤트 상태, 기간, 수량, 가격 확인

7. TicketNFT.mintTicket ✅
   → NFT 발행 (ERC-721)
   → Smart Wallet에 소유권 할당

8. 주최자에게 지불 ✅
   → ETH 전송

9. 이벤트 발생 ✅
   → TicketSold, TicketMinted

10. 백엔드 tokenId 추출 ✅
    → Transaction receipt 분석
    → 데이터베이스 저장

11. 사용자에게 응답 ✅
    → 구매 완료 알림
```

---

## 핵심 포인트

### 1. Paymaster의 역할
- **검증 단계**: EntryPoint가 Paymaster 검증
- **지불 단계**: Paymaster가 실제 가스비 지불
- **정책**: 티켓 구매는 스폰서, 재판매는 사용자 부담

### 2. Smart Wallet의 역할
- **검증**: 서명 및 Nonce 확인
- **실행**: EventManager 호출
- **소유권**: NFT는 Smart Wallet에 발행됨

### 3. NFT 발행 과정
- **EventManager**: 비즈니스 로직 검증
- **TicketNFT**: 실제 NFT 발행 (ERC-721)
- **소유권**: 사용자의 Smart Wallet 주소에 할당

### 4. 데이터 동기화
- **블록체인**: NFT 소유권, 이벤트 정보
- **데이터베이스**: 빠른 조회를 위한 메타데이터
- **동기화**: 트랜잭션 receipt에서 정보 추출

---

## 보안 검증 포인트

1. **Paymaster 검증**: 정책에 따라 가스비 스폰서 여부 결정
2. **서명 검증**: Smart Wallet owner의 서명 확인
3. **Nonce 검증**: 재사용 공격 방지
4. **이벤트 검증**: 승인, 기간, 수량, 가격 확인
5. **Reentrancy 방지**: `nonReentrant` 모디파이어 사용

이 모든 과정이 블록체인에 기록되어 투명하고 검증 가능합니다.

