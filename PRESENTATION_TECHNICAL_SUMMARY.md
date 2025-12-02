# 블록체인 티켓팅 시스템 - 기술 발표 자료

## 📋 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [전체 아키텍처](#전체-아키텍처)
3. [스마트 컨트랙트 구조 및 로직](#스마트-컨트랙트-구조-및-로직)
4. [Account Abstraction (ERC-4337) 구현](#account-abstraction-erc-4337-구현)
5. [배포 자동화](#배포-자동화)
6. [주요 기능 구현](#주요-기능-구현)
7. [기술 스택](#기술-스택)
8. [데이터 흐름](#데이터-흐름)

---

## 프로젝트 개요

### 목적
블록체인 기반 NFT 티켓팅 시스템으로 위조 방지, 투명한 재판매 추적, 스마트 컨트랙트 기반 자동화된 환불/취소를 제공합니다.

### 핵심 기술
- **ERC-721 NFT**: 티켓을 고유한 NFT로 발행
- **ERC-4337 Account Abstraction**: 사용자 친화적인 지갑 경험
- **IPFS**: 분산 메타데이터 저장
- **Polygon**: 저렴한 가스비와 빠른 트랜잭션

---

## 전체 아키텍처

### 시스템 구성도

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + TypeScript)              │
│  - 사용자 인터페이스 (Tailwind CSS)                          │
│  - Account Abstraction 지갑 연결                             │
│  - 이벤트 브라우징/검색                                      │
│  - 티켓 구매/재판매/환불                                     │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS/REST API
┌────────────────────▼────────────────────────────────────────┐
│                    Backend (FastAPI)                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Auth Service │  │ Event Service│  │ Ticket Service│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ IPFS Service │  │ Web3 Service │  │ AA Service   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────┬──────────┬──────────────┬──────────────┬────────────┘
       │          │              │              │
       │          │              │              │
┌──────▼──────┐ ┌─▼──────────┐ ┌─▼──────────┐ ┌─▼──────────┐
│ PostgreSQL  │ │   IPFS     │ │  Polygon   │ │  EntryPoint │
│  Database   │ │  (Pinata)  │ │ Blockchain │ │  (ERC-4337) │
└─────────────┘ └────────────┘ └────────────┘ └────────────┘
```

### 계층별 역할

#### 1. 프론트엔드 계층
- **React 18 + TypeScript**: 타입 안정성과 컴포넌트 기반 개발
- **Zustand**: 경량 상태 관리
- **React Query**: 서버 상태 관리 및 캐싱
- **ethers.js**: Web3 상호작용

#### 2. 백엔드 계층
- **FastAPI**: 비동기 고성능 API 서버
- **SQLAlchemy**: ORM을 통한 데이터베이스 추상화
- **JWT + OAuth2**: 인증 및 권한 관리
- **Web3.py**: 블록체인 상호작용

#### 3. 블록체인 계층
- **Polygon**: L2 스케일링 솔루션
- **ERC-721**: NFT 표준
- **ERC-4337**: Account Abstraction 표준

#### 4. 스토리지 계층
- **PostgreSQL**: 관계형 데이터베이스
- **IPFS (Pinata)**: 분산 메타데이터 저장

---

## 스마트 컨트랙트 구조 및 로직

### 컨트랙트 모듈화

```
contracts/
├── TicketNFT.sol              # ERC-721 티켓 NFT
├── EventManager.sol           # 이벤트 관리
├── TicketMarketplace.sol      # 2차 시장 재판매
├── RefundManager.sol          # 환불 관리
├── TicketAccessControl.sol    # 권한 관리
├── SmartWallet.sol            # ERC-4337 Smart Wallet
└── SmartWalletFactory.sol     # Smart Wallet Factory
```

### 주요 컨트랙트 상세

#### 1. TicketNFT.sol (ERC-721)

**역할**: 티켓을 NFT로 발행하고 소유권 관리

**핵심 로직**:
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

**보안 기능**:
- `onlyRole(MINTER_ROLE)`: EventManager만 발행 가능
- `nonReentrant`: 재진입 공격 방지
- `_safeMint`: 안전한 NFT 전송

#### 2. EventManager.sol

**역할**: 이벤트 생성, 승인, 티켓 판매 관리

**핵심 로직**:
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
    (bool success, ) = eventData.organizer.call{value: msg.value}("");
    require(success, "EventManager: payment failed");
    
    emit TicketSold(eventId, tokenId, msg.sender, eventData.price);
    return tokenId;
}
```

**주요 기능**:
- 이벤트 승인 시스템 (관리자만 승인 가능)
- 판매 기간 검증
- 티켓 수량 관리
- 자동 결제 처리

#### 3. TicketMarketplace.sol

**역할**: 2차 시장 재판매 플랫폼

**핵심 로직**:
```solidity
function listTicketForResale(
    uint256 tokenId,
    uint256 price
) external nonReentrant {
    require(
        ticketNFT.ownerOf(tokenId) == msg.sender,
        "TicketMarketplace: not ticket owner"
    );
    require(price > 0, "TicketMarketplace: price must be greater than 0");
    require(!listings[tokenId].active, "TicketMarketplace: already listed");
    
    // 가격 상한선 검증 (원가의 200%까지)
    uint256 eventId = ticketNFT.tokenToEvent(tokenId);
    uint256 originalPrice = eventManager.getEventPrice(eventId);
    uint256 maxPrice = (originalPrice * maxPriceMultiplier) / PRICE_DENOMINATOR;
    require(price <= maxPrice, "TicketMarketplace: price exceeds maximum");
    
    listings[tokenId] = Listing({
        tokenId: tokenId,
        seller: msg.sender,
        price: price,
        active: true,
        listedAt: block.timestamp
    });
    
    emit TicketListed(tokenId, msg.sender, price);
}

function buyResaleTicket(uint256 tokenId) external payable nonReentrant {
    Listing storage listing = listings[tokenId];
    require(listing.active, "TicketMarketplace: ticket not listed");
    require(msg.value >= listing.price, "TicketMarketplace: insufficient payment");
    
    // 수수료 계산
    uint256 fee = (listing.price * platformFee) / FEE_DENOMINATOR;
    uint256 sellerAmount = listing.price - fee;
    
    // NFT 전송
    ticketNFT.safeTransferFrom(listing.seller, msg.sender, tokenId);
    
    // 판매자에게 지불
    (bool success1, ) = listing.seller.call{value: sellerAmount}("");
    require(success1, "TicketMarketplace: payment to seller failed");
    
    // 수수료 수령자에게 지불
    (bool success2, ) = feeRecipient.call{value: fee}("");
    require(success2, "TicketMarketplace: fee payment failed");
    
    listing.active = false;
    
    emit TicketSold(tokenId, listing.seller, msg.sender, listing.price, fee);
}
```

**주요 기능**:
- 가격 상한선 검증 (원가의 200%까지)
- 자동 수수료 분배 (5-10%)
- 안전한 NFT 전송

#### 4. SmartWallet.sol (ERC-4337)

**역할**: 사용자 대신 트랜잭션을 실행하는 스마트 컨트랙트 지갑

**핵심 로직**:
```solidity
function validateUserOp(
    UserOperation calldata userOp,
    bytes32 userOpHash,
    uint256 missingFunds
) external returns (uint256 validationData) {
    require(msg.sender == entryPoint, "SmartWallet: only EntryPoint");
    
    // 서명 검증
    bytes32 hash = userOpHash.toEthSignedMessageHash();
    address signer = ECDSA.recover(hash, userOp.signature);
    require(signer == owner, "SmartWallet: invalid signature");
    
    // Nonce 검증 (재사용 공격 방지)
    require(userOp.nonce == nonce, "SmartWallet: invalid nonce");
    nonce++;
    
    return 0; // 검증 성공
}

function execute(
    address target,
    uint256 value,
    bytes calldata data
) external {
    require(msg.sender == entryPoint, "SmartWallet: only EntryPoint");
    
    (bool success, ) = target.call{value: value}(data);
    require(success, "SmartWallet: execution failed");
    
    emit Executed(target, value, data);
}
```

**주요 기능**:
- EntryPoint를 통한 트랜잭션 실행
- 서명 검증
- Nonce 관리 (재사용 공격 방지)
- UUPS 업그레이드 패턴 지원

#### 5. SmartWalletFactory.sol

**역할**: Deterministic Smart Wallet 주소 생성 및 배포

**핵심 로직**:
```solidity
function getAddress(address owner, uint256 salt) 
    public view returns (address walletAddress) 
{
    bytes memory bytecode = abi.encodePacked(
        type(ERC1967Proxy).creationCode,
        abi.encode(
            walletImplementation,
            abi.encodeCall(SmartWallet.initialize, (owner))
        )
    );
    
    bytes32 hash = keccak256(
        abi.encodePacked(
            bytes1(0xff),
            address(this),
            salt,
            keccak256(bytecode)
        )
    );
    
    walletAddress = address(uint160(uint256(hash)));
}

function createWallet(address owner, uint256 salt) 
    external returns (address walletAddress) 
{
    // 이미 배포된 경우 기존 주소 반환
    if (wallets[owner] != address(0)) {
        return wallets[owner];
    }
    
    walletAddress = getAddress(owner, salt);
    
    // Proxy 배포 (CREATE2)
    bytes memory bytecode = abi.encodePacked(
        type(ERC1967Proxy).creationCode,
        abi.encode(
            walletImplementation,
            abi.encodeCall(SmartWallet.initialize, (owner))
        )
    );
    
    assembly {
        walletAddress := create2(0, add(bytecode, 0x20), mload(bytecode), salt)
    }
    
    wallets[owner] = walletAddress;
    emit WalletCreated(owner, walletAddress);
}
```

**주요 기능**:
- **CREATE2**: Deterministic 주소 생성
- **Proxy 패턴**: 가스비 절약
- 배포 전 주소 예측 가능

---

## Account Abstraction (ERC-4337) 구현

### ERC-4337 개요

**목적**: 사용자가 EOA(Externally Owned Account) 없이도 스마트 컨트랙트 지갑을 사용할 수 있도록 함

**핵심 구성요소**:
1. **Smart Wallet**: 사용자의 스마트 컨트랙트 지갑
2. **EntryPoint**: UserOperation을 검증하고 실행하는 표준 컨트랙트
3. **Bundler**: UserOperation을 번들링하여 블록체인에 제출
4. **Paymaster**: 가스비를 대신 지불하는 컨트랙트

### 구현 아키텍처

```
User (소셜 로그인)
    ↓
Backend (FastAPI)
    ├── 사용자 인증 (JWT)
    ├── Smart Wallet 생성/관리 (Factory 사용)
    └── UserOperation 생성
    ↓
Bundler (로컬 테스트: 직접 EntryPoint 호출)
    ├── UserOperation 검증
    ├── 가스비 계산
    └── 트랜잭션 번들링
    ↓
EntryPoint (ERC-4337 표준)
    ├── validateUserOp 호출
    └── execute 호출
    ↓
Smart Wallet
    └── 실제 컨트랙트 호출
    ↓
Polygon Blockchain
```

### 백엔드 구현 (aa_service.py)

#### 1. Smart Wallet 생성

```python
def generate_smart_wallet_address(
    self,
    user_id: str,
    owner_address: Optional[str] = None,
    salt: Optional[int] = None
) -> str:
    """
    Deterministic Smart Wallet 주소 생성 및 배포 (CREATE2)
    """
    # Factory 컨트랙트 인스턴스
    factory = self._get_contract(factory_address, "SmartWalletFactory")
    
    # 주소 계산 (배포 전에도 주소 예측 가능)
    calculated_address = factory.functions.getAddress(
        owner_address,
        salt
    ).call()
    
    # 이미 배포되어 있는지 확인
    code = self.w3.eth.get_code(calculated_address)
    if code != b'':
        return calculated_address
    
    # 배포
    function = factory.functions.createWallet(owner_address, salt)
    tx_hash = self._send_transaction(function)
    
    return calculated_address
```

#### 2. UserOperation 생성

```python
def create_user_operation(
    self,
    sender: str,
    target: str,
    data: bytes,
    value: int = 0,
    nonce: Optional[int] = None,
    ...
) -> Dict[str, Any]:
    """
    ERC-4337 표준 UserOperation 생성
    """
    # Nonce 조회 (EntryPoint에서)
    if nonce is None:
        entry_point = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.entry_point_address),
            abi=entry_point_abi
        )
        nonce = entry_point.functions.getNonce(sender, 0).call()
    
    # 가스비 조회
    fee_history = self.w3.eth.fee_history(1, "latest")
    base_fee = fee_history["baseFeePerGas"][0]
    max_priority_fee_per_gas = self.w3.to_wei(2, "gwei")
    max_fee_per_gas = base_fee + max_priority_fee_per_gas
    
    # UserOperation 구조
    user_operation = {
        "sender": sender,
        "nonce": nonce,
        "initCode": b"",
        "callData": data,
        "callGasLimit": call_gas_limit,
        "verificationGasLimit": verification_gas_limit,
        "preVerificationGas": pre_verification_gas,
        "maxFeePerGas": max_fee_per_gas,
        "maxPriorityFeePerGas": max_priority_fee_per_gas,
        "paymasterAndData": paymaster_and_data,
        "signature": b""
    }
    
    return user_operation
```

#### 3. UserOperation 해시 계산 및 서명

```python
def _get_user_operation_hash(
    self,
    user_operation: Dict[str, Any]
) -> bytes:
    """
    ERC-4337 표준에 따른 UserOperation 해시 계산
    """
    # EntryPoint에서 getUserOpHash 호출 시도
    try:
        entry_point = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.entry_point_address),
            abi=entry_point_abi
        )
        user_op_hash = entry_point.functions.getUserOpHash(user_op_tuple).call()
        return user_op_hash
    except Exception:
        # 수동 계산 (EntryPoint가 없는 경우)
        encoded = abi_encode(
            ['address', 'uint256', 'bytes', 'bytes', ...],
            [user_operation["sender"], user_operation["nonce"], ...]
        )
        user_op_hash = Web3.keccak(encoded)
        return user_op_hash

def sign_user_operation(
    self,
    user_operation: Dict[str, Any],
    private_key: str
) -> Dict[str, Any]:
    """
    UserOperation 서명 (EIP-191)
    """
    # UserOperation 해시 계산
    user_op_hash = self._get_user_operation_hash(user_operation)
    
    # Ethereum 서명 메시지 해시로 변환
    message_hash = encode_defunct(primitive=user_op_hash)
    
    # 서명
    account = Account.from_key(private_key)
    signed_message = account.sign_message(message_hash)
    signature = signed_message.signature
    
    # UserOperation에 서명 추가
    user_operation["signature"] = signature
    
    return user_operation
```

#### 4. UserOperation 전송

```python
def send_user_operation(
    self,
    user_operation: Dict[str, Any]
) -> str:
    """
    UserOperation을 Bundler로 전송 또는 직접 EntryPoint 호출
    """
    if not self.bundler_url:
        # 로컬 테스트: 직접 EntryPoint 호출
        return self._send_user_operation_direct(user_operation)
    
    # Bundler API 호출
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_sendUserOperation",
        "params": [user_op_rpc, self.entry_point_address]
    }
    
    response = requests.post(self.bundler_url, json=payload)
    result = response.json()
    return result.get("result")
```

### 티켓 구매 통합

```python
# EventManager.purchaseTicket 함수 호출 데이터 인코딩
contract = web3_service._get_contract(settings.EVENT_MANAGER_ADDRESS, "EventManager")
function = contract.functions.purchaseTicket(event.event_id_onchain, token_uri)
call_data = function.build_transaction({'from': smart_wallet_address, 'value': event.price_wei})['data']

# UserOperation 생성
user_operation = aa_service.create_user_operation(
    sender=current_user.smart_wallet_address,
    target=settings.EVENT_MANAGER_ADDRESS,
    data=call_data,
    value=event.price_wei
)

# 서명
signed_user_op = aa_service.sign_user_operation(
    user_operation,
    private_key=settings.PRIVATE_KEY
)

# 전송
tx_hash = aa_service.send_user_operation(signed_user_op)
```

---

## 배포 자동화

### 배포 스크립트 (deploy_all.js)

**기능**: 모든 컨트랙트를 순서대로 배포하고 권한 설정

**배포 순서**:
1. TicketAccessControl
2. TicketNFT
3. EventManager
4. TicketMarketplace
5. RefundManager
6. SmartWallet (구현)
7. SmartWalletFactory
8. 권한 설정 (MINTER_ROLE, BURNER_ROLE)

**핵심 로직**:
```javascript
async function main() {
  const [deployer] = await hre.ethers.getSigners();
  
  // 1. AccessControl 배포
  const accessControl = await TicketAccessControl.deploy(deployer.address);
  contracts.TicketAccessControl = await accessControl.getAddress();
  
  // 2. TicketNFT 배포
  const ticketNFT = await TicketNFT.deploy(contracts.TicketAccessControl);
  contracts.TicketNFT = await ticketNFT.getAddress();
  
  // 3. EventManager 배포
  const eventManager = await EventManager.deploy(
    contracts.TicketAccessControl,
    contracts.TicketNFT
  );
  contracts.EventManager = await eventManager.getAddress();
  
  // ... 나머지 컨트랙트 배포
  
  // 8. 권한 설정
  const MINTER_ROLE = await ticketNFT.MINTER_ROLE();
  await ticketNFT.grantRole(MINTER_ROLE, contracts.EventManager);
  
  // 배포 정보 저장
  const deploymentInfo = {
    network: networkName,
    deployer: deployer.address,
    entryPoint: ENTRY_POINT_ADDRESS,
    contracts: contracts,
    timestamp: new Date().toISOString(),
  };
  
  fs.writeFileSync(
    path.join(deploymentDir, `${networkName}.json`),
    JSON.stringify(deploymentInfo, null, 2)
  );
}
```

**배포 정보 저장**:
- `deployments/{network}.json` 파일에 모든 컨트랙트 주소 저장
- 네트워크별로 분리 관리
- 타임스탬프 포함

**재개 배포 스크립트 (deploy_resume.js)**:
- 이미 배포된 컨트랙트는 스킵
- 가스비 절약
- 부분 배포 실패 시 재개 가능

---

## 주요 기능 구현

### 1. 티켓 구매 플로우

```
1. 사용자가 이벤트 선택
   ↓
2. 백엔드에서 검증
   - 이벤트 승인 여부
   - 판매 기간 확인
   - 티켓 수량 확인
   - 중복 구매 방지
   ↓
3. 티켓 메타데이터 생성 및 IPFS 업로드
   ↓
4. Smart Wallet 주소 확인/생성
   ↓
5. UserOperation 생성
   - EventManager.purchaseTicket 호출 데이터 인코딩
   - 가스비 계산
   - Nonce 조회
   ↓
6. UserOperation 서명
   - EIP-191 표준
   - Owner private key로 서명
   ↓
7. UserOperation 전송
   - Bundler 또는 직접 EntryPoint 호출
   ↓
8. 트랜잭션 완료 후 tokenId 추출
   - Transaction receipt 로그 분석
   - TicketSold 이벤트에서 tokenId 추출
   ↓
9. 데이터베이스에 티켓 저장
```

### 2. 재판매 플로우

```
1. 사용자가 보유 티켓 선택
   ↓
2. 재판매 가격 입력 (원가의 200%까지)
   ↓
3. 백엔드에서 검증
   - 티켓 소유자 확인
   - 가격 상한선 검증
   - 중복 등록 방지
   ↓
4. 온체인 재판매 등록
   - TicketMarketplace.listTicketForResale 호출
   ↓
5. 데이터베이스에 재판매 정보 저장
```

### 3. 환불 플로우

```
1. 사용자가 환불 요청
   ↓
2. 백엔드에서 환불 정책 확인
   - 이벤트 취소 여부
   - 환불 기한 확인
   ↓
3. 관리자/주최자 승인
   ↓
4. 온체인 환불 처리
   - RefundManager.processRefund 호출
   - TicketNFT.burnTicket 호출
   - 환불 금액 전송
   ↓
5. 데이터베이스 업데이트
```

---

## 기술 스택

### 블록체인
- **네트워크**: Polygon (로컬 Hardhat → Amoy 테스트넷)
- **스마트 컨트랙트 언어**: Solidity ^0.8.20
- **개발 프레임워크**: Hardhat
- **NFT 표준**: ERC-721
- **Account Abstraction**: ERC-4337

### 백엔드
- **프레임워크**: FastAPI (Python 3.11+)
- **데이터베이스**: PostgreSQL 15+
- **ORM**: SQLAlchemy
- **인증**: JWT + OAuth2 (Google)
- **Web3 라이브러리**: Web3.py
- **IPFS 클라이언트**: Pinata SDK

### 프론트엔드
- **프레임워크**: React 18+ (TypeScript)
- **상태 관리**: Zustand
- **서버 상태**: React Query
- **UI 라이브러리**: Tailwind CSS
- **Web3 라이브러리**: ethers.js

### 인프라
- **IPFS**: Pinata
- **로컬 개발**: Hardhat Node, Docker Compose
- **배포**: Hardhat Scripts

---

## 데이터 흐름

### 이벤트 생성 플로우

```
주최자 → 프론트엔드
    ↓
백엔드 API (/api/events)
    ├── 이벤트 메타데이터 생성
    ├── IPFS 업로드 (Pinata)
    └── 스마트 컨트랙트 호출 (EventManager.createEvent)
    ↓
블록체인 (이벤트 등록)
    ↓
데이터베이스 저장
    ↓
관리자 승인 대기
```

### 티켓 구매 플로우

```
구매자 → 프론트엔드
    ↓
백엔드 API (/api/tickets/purchase)
    ├── 이벤트 검증
    ├── 티켓 메타데이터 생성 및 IPFS 업로드
    ├── Smart Wallet 주소 확인/생성
    ├── UserOperation 생성
    ├── UserOperation 서명
    └── UserOperation 전송 (EntryPoint)
    ↓
EntryPoint
    ├── validateUserOp (Smart Wallet)
    └── execute (EventManager.purchaseTicket)
    ↓
EventManager
    ├── 검증 (승인, 기간, 수량, 가격)
    ├── TicketNFT.mintTicket 호출
    ├── 주최자에게 지불
    └── TicketSold 이벤트 발생
    ↓
백엔드
    ├── Transaction receipt 분석
    ├── tokenId 추출
    └── 데이터베이스 저장
```

### 재판매 플로우

```
판매자 → 프론트엔드
    ↓
백엔드 API (/api/resales)
    ├── 티켓 소유자 확인
    ├── 가격 상한선 검증
    └── 스마트 컨트랙트 호출 (TicketMarketplace.listTicketForResale)
    ↓
블록체인 (재판매 등록)
    ↓
데이터베이스 저장
    ↓
구매자 → 프론트엔드
    ↓
백엔드 API (/api/resales/{id}/buy)
    ├── 재판매 정보 확인
    └── 스마트 컨트랙트 호출 (TicketMarketplace.buyResaleTicket)
    ↓
TicketMarketplace
    ├── NFT 전송 (TicketNFT.safeTransferFrom)
    ├── 판매자에게 지불
    └── 수수료 수령자에게 지불
```

---

## 보안 고려사항

### 스마트 컨트랙트
- ✅ **Reentrancy 방지**: `nonReentrant` 모디파이어
- ✅ **Access Control**: OpenZeppelin `AccessControl` 사용
- ✅ **Integer Overflow 방지**: Solidity 0.8+ 자동 체크
- ✅ **이벤트 로깅**: 모든 중요한 상태 변경 기록

### 백엔드
- ✅ **JWT 토큰 검증**: 모든 API 엔드포인트
- ✅ **SQL Injection 방지**: SQLAlchemy ORM 사용
- ✅ **CORS 설정**: 허용된 Origin만 접근
- ✅ **환경 변수 관리**: `.env` 파일 사용

### Account Abstraction
- ✅ **서명 검증**: ECDSA 서명 검증
- ✅ **Nonce 관리**: 재사용 공격 방지
- ✅ **EntryPoint 검증**: EntryPoint에서만 호출 가능

---

## 성능 최적화

### 가스비 최적화
- **Proxy 패턴**: Smart Wallet 구현 재사용
- **CREATE2**: Deterministic 주소 생성으로 배포 전 주소 예측
- **이벤트 로깅**: 효율적인 이벤트 구조

### 데이터베이스 최적화
- **인덱스**: 자주 조회되는 필드에 인덱스 설정
- **쿼리 최적화**: N+1 쿼리 방지

### 프론트엔드 최적화
- **React Query**: 서버 상태 캐싱
- **코드 스플리팅**: 라우트별 코드 분할

---

## 테스트 환경

### 로컬 개발 환경
- **Hardhat Node**: 로컬 블록체인
- **PostgreSQL**: Docker Compose로 실행
- **백엔드**: FastAPI (localhost:8000)
- **프론트엔드**: Vite Dev Server (localhost:5173)

### 테스트넷 배포
- **Polygon Amoy**: 테스트넷
- **컨트랙트 주소**: `deployments/amoy.json`
- **환경 변수**: 네트워크별 분리

---

## 향후 개선 사항

1. **Paymaster 구현**: 가스비 스폰서 기능 완성
2. **Bundler 통합**: 실제 Bundler 서비스 연동
3. **보안 감사**: 스마트 컨트랙트 외부 감사
4. **모니터링**: 트랜잭션 모니터링 시스템
5. **로드 밸런싱**: 백엔드 서버 확장

---

## 결론

이 프로젝트는 다음과 같은 기술적 성과를 달성했습니다:

1. **ERC-4337 Account Abstraction 구현**: 사용자 친화적인 지갑 경험
2. **모듈화된 스마트 컨트랙트**: 유지보수성과 확장성
3. **자동화된 배포**: 배포 스크립트로 일관성 있는 배포
4. **IPFS 통합**: 분산 메타데이터 저장
5. **보안 강화**: 다양한 보안 패턴 적용

이러한 기술적 기반 위에 안정적이고 확장 가능한 블록체인 티켓팅 시스템을 구축했습니다.

