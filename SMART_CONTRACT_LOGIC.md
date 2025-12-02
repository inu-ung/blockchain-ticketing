# 스마트 컨트랙트 로직 설명

## 전체 컨트랙트 구조

```
TicketAccessControl (권한 관리)
    ↓
TicketNFT (ERC-721 NFT)
    ↓
EventManager (이벤트 관리)
    ↓
TicketMarketplace (재판매)
RefundManager (환불)
SmartWallet (ERC-4337)
SmartWalletFactory (Smart Wallet 생성)
```

---

## 1. TicketAccessControl.sol

### 역할
관리자와 주최자 권한을 관리하는 컨트랙트

### 핵심 로직

#### 역할 정의
```solidity
bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
bytes32 public constant ORGANIZER_ROLE = keccak256("ORGANIZER_ROLE");
```

#### 관리자 추가/제거
- `addAdmin(address)`: 관리자 역할 부여
- `removeAdmin(address)`: 관리자 역할 제거
- 관리자만 호출 가능 (`onlyRole(ADMIN_ROLE)`)

#### 주최자 추가/제거
- `addOrganizer(address)`: 주최자 역할 부여
- `removeOrganizer(address)`: 주최자 역할 제거
- 관리자만 호출 가능

### 보안
- OpenZeppelin `AccessControl` 사용
- 역할 기반 접근 제어 (RBAC)

---

## 2. TicketNFT.sol (ERC-721)

### 역할
티켓을 NFT로 발행하고 소유권 관리

### 핵심 로직

#### 티켓 발행 (mintTicket)
```solidity
function mintTicket(
    address to,
    uint256 eventId,
    string memory tokenURI
) external onlyRole(MINTER_ROLE) nonReentrant returns (uint256)
```

**로직**:
1. `onlyRole(MINTER_ROLE)`: EventManager만 호출 가능
2. `nonReentrant`: 재진입 공격 방지
3. Token ID 생성: `_tokenIdCounter` 사용, 카운터 증가
4. NFT 발행: `_safeMint(to, tokenId)` - ERC-721 표준
5. 메타데이터 설정: `_setTokenURI(tokenId, tokenURI)` - IPFS URI
6. 매핑 저장:
   - `tokenToEvent[tokenId] = eventId` - 토큰과 이벤트 연결
   - `eventTicketCount[eventId]++` - 이벤트별 티켓 수 증가
7. 이벤트 발생: `TicketMinted`

**보안**:
- MINTER_ROLE만 발행 가능
- Reentrancy 방지
- Safe Mint (스마트 컨트랙트 호출 시 검증)

#### 티켓 소각 (burnTicket)
```solidity
function burnTicket(uint256 tokenId) external onlyRole(BURNER_ROLE)
```

**로직**:
1. `onlyRole(BURNER_ROLE)`: RefundManager만 호출 가능
2. 토큰 존재 확인
3. 이벤트 ID 조회
4. NFT 소각: `_burn(tokenId)`
5. 카운터 감소: `eventTicketCount[eventId]--`
6. 이벤트 발생: `TicketBurned`

---

## 3. EventManager.sol

### 역할
이벤트 생성, 승인, 티켓 판매 관리

### 핵심 로직

#### 이벤트 생성 (createEvent)
```solidity
function createEvent(
    string memory ipfsHash,
    uint256 price,
    uint256 maxTickets,
    uint256 startTime,
    uint256 endTime,
    uint256 eventDate
) external returns (uint256)
```

**검증**:
- `onlyRole(ORGANIZER_ROLE)`: 주최자만 호출 가능
- `price > 0`: 가격이 0보다 커야 함
- `maxTickets > 0`: 티켓 수량이 0보다 커야 함
- `startTime < endTime`: 판매 시작 시간 < 종료 시간
- `endTime <= eventDate`: 판매 종료 시간 ≤ 이벤트 날짜

**로직**:
1. Event ID 생성: `_eventIdCounter` 사용
2. Event 구조체 생성 및 저장
3. 주최자별 이벤트 목록에 추가
4. 이벤트 발생: `EventCreated`
5. Event ID 반환

**상태**: `approved: false` (관리자 승인 대기)

#### 이벤트 승인 (approveEvent)
```solidity
function approveEvent(uint256 eventId) external
```

**검증**:
- `onlyRole(ADMIN_ROLE)`: 관리자만 호출 가능
- 이벤트 존재 확인
- 이미 승인되지 않았는지 확인
- 취소되지 않았는지 확인

**로직**:
1. `events[eventId].approved = true`
2. 이벤트 발생: `EventApproved`

#### 티켓 구매 (purchaseTicket)
```solidity
function purchaseTicket(
    uint256 eventId,
    string memory tokenURI
) external payable nonReentrant returns (uint256)
```

**검증** (순서대로):
1. 이벤트 존재 확인
2. `eventData.approved`: 이벤트가 승인되었는지
3. `!eventData.cancelled`: 이벤트가 취소되지 않았는지
4. `block.timestamp >= startTime && <= endTime`: 판매 기간 내인지
5. `soldTickets < maxTickets`: 티켓이 매진되지 않았는지
6. `msg.value >= eventData.price`: 지불 금액이 충분한지

**로직**:
1. **티켓 발행**: `ticketNFT.mintTicket(msg.sender, eventId, tokenURI)`
   - `msg.sender`는 Smart Wallet 주소
   - Token ID 반환
2. **판매 수량 증가**: `eventData.soldTickets++`
3. **주최자에게 지불**: `eventData.organizer.call{value: msg.value}("")`
   - Smart Wallet에서 받은 ETH를 주최자에게 전송
4. **이벤트 발생**: `TicketSold(eventId, tokenId, msg.sender, price)`
5. Token ID 반환

**보안**:
- `nonReentrant`: 재진입 공격 방지
- 모든 검증을 통과해야만 실행
- 실패 시 가스비만 소비, 상태 변경 없음

#### 이벤트 가격 수정 (updateEventPrice)
```solidity
function updateEventPrice(uint256 eventId, uint256 newPrice) external
```

**검증**:
- `onlyOrganizerOrAdmin`: 주최자 또는 관리자만
- `soldTickets == 0`: 티켓이 하나도 팔리지 않았을 때만 수정 가능

**로직**:
1. `events[eventId].price = newPrice`
2. 이벤트 발생: `EventUpdated`

#### 이벤트 취소 (cancelEvent)
```solidity
function cancelEvent(uint256 eventId) external
```

**검증**:
- `onlyOrganizerOrAdmin`: 주최자 또는 관리자만
- 이미 취소되지 않았는지 확인

**로직**:
1. `events[eventId].cancelled = true`
2. 이벤트 발생: `EventCancelled`

---

## 4. TicketMarketplace.sol

### 역할
2차 시장 재판매 마켓플레이스

### 핵심 로직

#### 재판매 등록 (listTicketForResale)
```solidity
function listTicketForResale(uint256 tokenId, uint256 price) external
```

**검증**:
- `ticketNFT.ownerOf(tokenId) == msg.sender`: 티켓 소유자 확인
- `price > 0`: 가격이 0보다 커야 함
- `!listings[tokenId].active`: 이미 등록되지 않았는지

**가격 상한선 검증**:
```solidity
uint256 eventId = ticketNFT.tokenToEvent(tokenId);
EventManager.Event memory eventData = eventManager.getEvent(eventId);
uint256 maxPrice = (eventData.price * maxPriceMultiplier) / PRICE_DENOMINATOR;
require(price <= maxPrice, "TicketMarketplace: price exceeds maximum");
```
- 원가의 200%까지 설정 가능 (기본값)
- `maxPriceMultiplier = 20000` (200%)

**로직**:
1. Listing 구조체 생성 및 저장
2. 판매자별 리스팅 목록에 추가
3. 이벤트 발생: `TicketListed`

#### 재판매 구매 (buyResaleTicket)
```solidity
function buyResaleTicket(uint256 tokenId) external payable
```

**검증**:
- `listings[tokenId].active`: 재판매 등록되어 있는지
- `msg.sender != listing.seller`: 자신의 티켓을 구매하지 않는지
- `msg.value >= listing.price`: 지불 금액이 충분한지

**로직**:
1. **리스팅 비활성화**: `listing.active = false`
2. **수수료 계산**:
   - `fee = (listing.price * platformFee) / FEE_DENOMINATOR` (5%)
   - `sellerAmount = listing.price - fee`
3. **NFT 소유권 이전**: `ticketNFT.safeTransferFrom(seller, buyer, tokenId)`
   - ERC-721 `safeTransferFrom` 사용
   - 안전한 전송 (스마트 컨트랙트 호출 시 검증)
4. **판매자에게 지불**: `sellerAmount` 전송
5. **수수료 수령자에게 지불**: `fee` 전송
6. **초과 지불액 반환**: `msg.value - listing.price` 반환
7. 이벤트 발생: `TicketSold`

**보안**:
- `nonReentrant`: 재진입 공격 방지
- `safeTransferFrom`: 안전한 NFT 전송
- 모든 지불 실패 시 트랜잭션 롤백

---

## 5. RefundManager.sol

### 역할
환불 요청 및 처리 관리

### 핵심 로직

#### 환불 요청 (requestRefund)
```solidity
function requestRefund(uint256 tokenId) external
```

**검증**:
- `ticketNFT.ownerOf(tokenId) == msg.sender`: 티켓 소유자 확인
- `!refundRequests[tokenId].processed`: 이미 처리되지 않았는지

**환불 가능 기간 확인**:
```solidity
require(
    block.timestamp <= eventData.eventDate - refundDeadlineDays,
    "RefundManager: refund deadline passed"
);
```
- 이벤트 시작 7일 전까지만 환불 가능 (기본값)
- `refundDeadlineDays = 7 days`

**이벤트 취소 확인**:
- `!eventData.cancelled`: 이벤트가 취소되지 않았는지
- 취소된 이벤트는 `emergencyRefund` 사용

**로직**:
1. 환불 금액 계산:
   - `refundAmount = eventData.price`
   - 수수료가 있으면 차감
2. RefundRequest 구조체 생성 및 저장
3. 이벤트 발생: `RefundRequested`

**상태**: `processed: false` (주최자/관리자 승인 대기)

#### 환불 처리 (processRefund)
```solidity
function processRefund(uint256 tokenId) external
```

**검증**:
- `onlyOrganizerOrAdmin`: 주최자 또는 관리자만
- `refundRequests[tokenId].requester != address(0)`: 환불 요청이 있는지
- `!request.processed`: 이미 처리되지 않았는지

**로직**:
1. 환불 금액 계산 (수수료 차감)
2. 상태 업데이트: `processed = true`, `processedAt = block.timestamp`
3. **NFT 소각**: `ticketNFT.burnTicket(tokenId)`
4. **환불 지불**: `requester.call{value: refundAmount}("")`
5. 이벤트 발생: `RefundProcessed`

**보안**:
- `nonReentrant`: 재진입 공격 방지
- 주최자/관리자만 승인 가능

#### 긴급 환불 (emergencyRefund)
```solidity
function emergencyRefund(uint256 tokenId) external onlyAdmin
```

**검증**:
- `onlyAdmin`: 관리자만 호출 가능
- `eventData.cancelled`: 이벤트가 취소되었는지

**로직**:
1. NFT 소각
2. 소유자에게 환불 지불
3. 환불 요청 없이도 즉시 처리

---

## 6. SmartWallet.sol (ERC-4337)

### 역할
사용자 대신 트랜잭션을 실행하는 스마트 컨트랙트 지갑

### 핵심 로직

#### 검증 (validateUserOp)
```solidity
function validateUserOp(
    UserOperation calldata userOp,
    bytes32 userOpHash,
    uint256 missingFunds
) external returns (uint256 validationData)
```

**검증**:
- `msg.sender == entryPoint`: EntryPoint에서만 호출 가능
- 서명 검증:
  ```solidity
  bytes32 hash = userOpHash.toEthSignedMessageHash();
  address signer = ECDSA.recover(hash, userOp.signature);
  require(signer == owner, "SmartWallet: invalid signature");
  ```
- Nonce 검증:
  ```solidity
  require(userOp.nonce == nonce, "SmartWallet: invalid nonce");
  nonce++;
  ```

**로직**:
1. UserOperation 해시를 EIP-191 형식으로 변환
2. 서명에서 서명자 주소 복구
3. 서명자가 owner인지 확인
4. Nonce가 올바른지 확인 (재사용 공격 방지)
5. Nonce 증가
6. `return 0` (검증 성공)

#### 실행 (execute)
```solidity
function execute(
    address target,
    uint256 value,
    bytes calldata data
) external
```

**검증**:
- `msg.sender == entryPoint`: EntryPoint에서만 호출 가능

**로직**:
1. `target.call{value: value}(data)`: 컨트랙트 호출
2. 성공 여부 확인
3. 이벤트 발생: `Executed`

**사용 예시**:
- `target = EventManager 주소`
- `value = 티켓 가격`
- `data = purchaseTicket(eventId, tokenURI) 함수 호출 데이터`

---

## 7. SmartWalletFactory.sol

### 역할
Deterministic Smart Wallet 주소 생성 및 배포

### 핵심 로직

#### 주소 계산 (getAddress)
```solidity
function getAddress(address owner, uint256 salt) public view returns (address)
```

**로직** (CREATE2):
1. Proxy 바이트코드 생성
2. CREATE2 해시 계산:
   ```solidity
   bytes32 hash = keccak256(
       abi.encodePacked(
           bytes1(0xff),
           address(this),  // Factory 주소
           salt,            // 사용자별 고유 salt
           keccak256(bytecode)
       )
   );
   ```
3. 주소 변환: `address(uint160(uint256(hash)))`

**특징**:
- 같은 `owner`와 `salt`로 항상 같은 주소 반환
- 배포 전에도 주소 예측 가능

#### Smart Wallet 생성 (createWallet)
```solidity
function createWallet(address owner, uint256 salt) external returns (address)
```

**로직**:
1. 이미 배포된 경우 기존 주소 반환
2. 주소 계산: `getAddress(owner, salt)`
3. 이미 배포되어 있는지 확인 (`extcodesize`)
4. Proxy 배포 (CREATE2):
   ```solidity
   assembly {
       walletAddress := create2(0, add(bytecode, 0x20), mload(bytecode), salt)
   }
   ```
5. 매핑 저장: `wallets[owner] = walletAddress`
6. 이벤트 발생: `WalletCreated`

**특징**:
- Proxy 패턴으로 가스비 절약
- 구현 컨트랙트 재사용

---

## 주요 보안 패턴

### 1. Reentrancy 방지
- `nonReentrant` 모디파이어 사용
- 상태 변경 후 외부 호출

### 2. Access Control
- OpenZeppelin `AccessControl` 사용
- 역할 기반 접근 제어

### 3. Integer Overflow 방지
- Solidity 0.8+ 자동 체크
- SafeMath 불필요

### 4. 이벤트 로깅
- 모든 중요한 상태 변경 기록
- 투명성 및 감사 가능

### 5. Safe Transfer
- `safeTransferFrom` 사용
- 스마트 컨트랙트 호출 시 검증

---

## 컨트랙트 간 상호작용

### 티켓 구매 플로우
```
Smart Wallet
    ↓ execute()
EventManager.purchaseTicket()
    ├── 검증 (승인, 기간, 수량, 가격)
    ├── TicketNFT.mintTicket()
    │   └── NFT 발행
    └── 주최자에게 지불
```

### 재판매 플로우
```
사용자
    ↓ listTicketForResale()
TicketMarketplace
    ├── 가격 상한선 검증
    └── Listing 저장

구매자
    ↓ buyResaleTicket()
TicketMarketplace
    ├── TicketNFT.safeTransferFrom()
    ├── 판매자에게 지불
    └── 수수료 수령자에게 지불
```

### 환불 플로우
```
사용자
    ↓ requestRefund()
RefundManager
    ├── 환불 가능 기간 확인
    └── RefundRequest 저장

주최자/관리자
    ↓ processRefund()
RefundManager
    ├── TicketNFT.burnTicket()
    └── 환불 지불
```

---

## 핵심 설계 원칙

### 1. 모듈화
- 각 컨트랙트가 명확한 역할
- 컨트랙트 간 느슨한 결합

### 2. 권한 분리
- TicketAccessControl로 중앙 관리
- 각 컨트랙트가 필요한 역할만 가짐

### 3. 검증 우선
- 모든 함수에서 검증 먼저 수행
- 검증 실패 시 상태 변경 없음

### 4. 이벤트 기반
- 모든 중요한 상태 변경을 이벤트로 기록
- 오프체인에서 추적 가능

### 5. 가스비 최적화
- Proxy 패턴 사용
- 불필요한 저장소 접근 최소화

