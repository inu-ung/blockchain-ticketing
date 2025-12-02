# 발표 키워드 및 설명 문장

## 핵심 키워드

### 1. User Registration / Login
**키워드**: `user register`, `user login`, `authentication`

**설명 문장**:
- "사용자는 이메일과 비밀번호로 간단하게 회원가입할 수 있습니다"
- "JWT 토큰 기반 인증으로 안전한 로그인을 제공합니다"
- "소셜 로그인(Google) 지원으로 사용자 편의성을 높였습니다"

**관련 용어**: JWT, OAuth2, Password Hash, Session Management

---

### 2. Smart Wallet Creation
**키워드**: `smart wallet`, `account abstraction`, `wallet creation`, `ERC-4337`

**설명 문장**:
- "ERC-4337 Account Abstraction을 통해 사용자 친화적인 Smart Wallet을 자동 생성합니다"
- "CREATE2 방식을 사용하여 배포 전에도 주소를 예측할 수 있습니다"
- "Proxy 패턴으로 가스비를 절약하면서도 업그레이드 가능한 지갑을 제공합니다"
- "사용자는 복잡한 지갑 설정 없이도 블록체인 티켓을 구매할 수 있습니다"

**관련 용어**: CREATE2, Proxy Pattern, Deterministic Address, Factory Pattern, EntryPoint

---

### 3. Event Creation
**키워드**: `event create`, `organizer`, `event management`, `IPFS metadata`

**설명 문장**:
- "주최자는 이벤트 정보를 입력하여 티켓 판매를 시작할 수 있습니다"
- "IPFS에 메타데이터를 저장하여 블록체인 가스비를 절약합니다"
- "이벤트는 관리자 승인 후 판매가 시작됩니다"
- "판매 기간, 티켓 수량, 가격 등을 세밀하게 설정할 수 있습니다"

**관련 용어**: IPFS, Pinata, Metadata, Event Approval, On-chain Registration

---

### 4. Event Approval
**키워드**: `event approve`, `admin`, `event status`, `moderation`

**설명 문장**:
- "관리자는 이벤트를 검토하고 승인하여 품질을 관리합니다"
- "승인된 이벤트만 티켓 판매가 가능합니다"
- "블록체인에 승인 상태가 기록되어 투명하게 관리됩니다"

**관련 용어**: Access Control, Role-based Permission, Event Status

---

### 5. User Buy Ticket
**키워드**: `user buy ticket`, `ticket purchase`, `NFT mint`, `user operation`

**설명 문장**:
- "사용자는 Account Abstraction을 통해 복잡한 지갑 설정 없이 티켓을 구매할 수 있습니다"
- "ERC-721 NFT 표준으로 티켓을 발행하여 위조가 불가능합니다"
- "UserOperation을 통해 Smart Wallet이 사용자를 대신하여 트랜잭션을 실행합니다"
- "구매 즉시 NFT 티켓이 발행되고 소유권이 블록체인에 기록됩니다"
- "중복 구매 방지, 판매 기간 검증 등 스마트 컨트랙트에서 자동으로 검증합니다"

**관련 용어**: ERC-721, NFT Minting, UserOperation, EntryPoint, Smart Wallet Execute, TicketSold Event

---

### 6. Ticket Resale
**키워드**: `ticket resale`, `marketplace`, `secondary market`, `NFT transfer`

**설명 문장**:
- "구매한 티켓을 마켓플레이스에 재판매할 수 있습니다"
- "원가의 최대 200%까지 가격을 설정할 수 있어 공정한 거래를 보장합니다"
- "플랫폼 수수료(5%)가 자동으로 분배됩니다"
- "NFT 소유권이 블록체인에서 안전하게 이전됩니다"

**관련 용어**: Marketplace, Price Cap, Platform Fee, NFT Transfer, Safe Transfer

---

### 7. Resale Purchase
**키워드**: `buy resale`, `secondary purchase`, `NFT ownership transfer`

**설명 문장**:
- "마켓플레이스에서 재판매 중인 티켓을 구매할 수 있습니다"
- "구매 시 NFT 소유권이 즉시 이전됩니다"
- "판매자에게 자동으로 지불이 이루어집니다"

**관련 용어**: Ownership Transfer, Automatic Payment, Marketplace Transaction

---

### 8. Refund Request
**키워드**: `refund request`, `ticket refund`, `refund policy`

**설명 문장**:
- "이벤트 취소나 개인 사정으로 티켓을 사용할 수 없을 때 환불을 요청할 수 있습니다"
- "환불 요청은 관리자나 주최자의 승인을 받아 처리됩니다"
- "환불 정책에 따라 자동으로 검증됩니다"

**관련 용어**: Refund Policy, Refund Approval, Ticket Status

---

### 9. Refund Processing
**키워드**: `refund process`, `NFT burn`, `refund payment`

**설명 문장**:
- "승인된 환불은 스마트 컨트랙트에서 자동으로 처리됩니다"
- "NFT 티켓이 소각되고 환불 금액이 구매자에게 전송됩니다"
- "모든 환불 내역이 블록체인에 기록되어 투명하게 관리됩니다"

**관련 용어**: NFT Burn, Automatic Refund, Refund Transaction

---

### 10. IPFS Integration
**키워드**: `IPFS`, `metadata storage`, `decentralized storage`, `Pinata`

**설명 문장**:
- "이벤트와 티켓의 상세 정보를 IPFS에 저장하여 가스비를 절약합니다"
- "분산 저장소를 사용하여 메타데이터의 영구 보존을 보장합니다"
- "블록체인에는 IPFS 해시만 저장하여 효율적인 구조를 구현했습니다"

**관련 용어**: IPFS Hash, Decentralized Storage, Gas Optimization, Metadata URI

---

### 11. Blockchain Integration
**키워드**: `blockchain`, `Polygon`, `smart contract`, `on-chain`

**설명 문장**:
- "Polygon 네트워크를 사용하여 저렴한 가스비와 빠른 트랜잭션을 제공합니다"
- "모든 티켓 거래가 블록체인에 기록되어 투명하고 검증 가능합니다"
- "스마트 컨트랙트로 자동화된 거래 처리를 구현했습니다"

**관련 용어**: Polygon Network, Smart Contract, On-chain Record, Transaction Verification

---

### 12. Database Management
**키워드**: `database`, `PostgreSQL`, `off-chain storage`, `data synchronization`

**설명 문장**:
- "PostgreSQL 데이터베이스로 빠른 조회 성능을 제공합니다"
- "블록체인과 데이터베이스의 이중 저장 구조로 효율성을 극대화했습니다"
- "온체인과 오프체인 데이터를 동기화하여 일관성을 유지합니다"

**관련 용어**: Data Synchronization, Off-chain Storage, Fast Query, Dual Storage

---

## 기술 키워드

### Account Abstraction
**키워드**: `account abstraction`, `ERC-4337`, `user operation`, `entry point`

**설명 문장**:
- "ERC-4337 표준을 구현하여 사용자 경험을 혁신했습니다"
- "UserOperation을 통해 복잡한 트랜잭션을 단순화했습니다"
- "EntryPoint를 통한 표준화된 검증 및 실행 프로세스"

**관련 용어**: UserOperation, EntryPoint, Bundler, Paymaster, Signature Verification

---

### Smart Contract Architecture
**키워드**: `smart contract`, `modular design`, `access control`, `reentrancy guard`

**설명 문장**:
- "모듈화된 컨트랙트 구조로 유지보수성과 확장성을 확보했습니다"
- "OpenZeppelin 라이브러리를 활용한 보안 강화"
- "Reentrancy 방지, Access Control 등 다양한 보안 패턴 적용"

**관련 용어**: Modular Design, Access Control, Reentrancy Guard, OpenZeppelin, Security Patterns

---

### NFT Standard
**키워드**: `ERC-721`, `NFT`, `token ID`, `token URI`

**설명 문장**:
- "ERC-721 표준을 준수하여 표준 호환성을 보장합니다"
- "각 티켓은 고유한 tokenId를 가진 NFT로 발행됩니다"
- "IPFS URI를 통해 메타데이터를 연결합니다"

**관련 용어**: ERC-721 Standard, Token ID, Token URI, NFT Minting, NFT Burning

---

## 추가 추천 키워드

### Security
- `security`, `reentrancy protection`, `access control`, `signature verification`
- "다층 보안 구조로 사용자 자산을 보호합니다"

### Scalability
- `scalability`, `gas optimization`, `batch processing`, `layer 2`
- "Polygon L2를 활용하여 확장 가능한 인프라를 구축했습니다"

### User Experience
- `user experience`, `walletless`, `seamless`, `one-click purchase`
- "지갑 없이도 원클릭으로 티켓을 구매할 수 있습니다"

### Transparency
- `transparency`, `immutable record`, `verifiable`, `audit trail`
- "모든 거래가 블록체인에 기록되어 투명하게 관리됩니다"

### Automation
- `automation`, `smart contract execution`, `automatic payment`, `self-executing`
- "스마트 컨트랙트로 자동화된 거래 처리를 구현했습니다"

---

## 키워드 조합 예시

### 발표 슬라이드 제목용
- "User Buy Ticket with Account Abstraction"
- "Smart Wallet Creation for Seamless Experience"
- "NFT Ticket Minting on Polygon Blockchain"
- "Decentralized Marketplace for Ticket Resale"
- "IPFS-based Metadata Storage"

### 기술 설명용
- "ERC-4337 Account Abstraction Implementation"
- "Modular Smart Contract Architecture"
- "Dual Storage: Blockchain + Database"
- "Gas-optimized NFT Minting Process"
- "Automated Refund Processing via Smart Contract"

---

## 발표 시 강조할 핵심 문장

1. **"사용자는 복잡한 지갑 설정 없이도 원클릭으로 티켓을 구매할 수 있습니다"**
   - Account Abstraction의 핵심 가치

2. **"모든 티켓 거래가 블록체인에 기록되어 위조가 불가능하고 투명하게 관리됩니다"**
   - 블록체인의 핵심 가치

3. **"ERC-4337 표준을 구현하여 사용자 경험을 혁신했습니다"**
   - 기술적 혁신

4. **"IPFS와 블록체인의 조합으로 가스비를 절약하면서도 상세한 정보를 저장합니다"**
   - 최적화 전략

5. **"모듈화된 스마트 컨트랙트 구조로 유지보수성과 확장성을 확보했습니다"**
   - 아키텍처 설계

