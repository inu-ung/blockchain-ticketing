# 블록체인 티켓팅 시스템 아키텍처

## 📋 목차
1. [시스템 개요](#시스템-개요)
2. [기술 스택](#기술-스택)
3. [시스템 아키텍처](#시스템-아키텍처)
4. [스마트 컨트랙트 구조](#스마트-컨트랙트-구조)
5. [데이터베이스 스키마](#데이터베이스-스키마)
6. [API 설계](#api-설계)
7. [프론트엔드 구조](#프론트엔드-구조)
8. [Account Abstraction 구현](#account-abstraction-구현)
9. [IPFS 통합](#ipfs-통합)
10. [보안 고려사항](#보안-고려사항)
11. [배포 전략](#배포-전략)

---

## 시스템 개요

### 목적
블록체인 기반 티켓팅 시스템으로 위조 방지, 투명한 재판매 추적, 스마트 컨트랙트 기반 자동화된 환불/취소를 제공합니다.

### 주요 기능
- ✅ 이벤트 생성 및 관리 (주최자)
- ✅ NFT 티켓 발행 및 판매
- ✅ 티켓 구매 (고정가)
- ✅ 2차 시장 재판매
- ✅ 환불 및 취소 처리
- ✅ KYC (간단한 이메일 인증)
- ✅ Account Abstraction 기반 자동 지갑 연결
- ✅ IPFS 기반 메타데이터 저장

### 사용자 역할
1. **관리자**: 시스템 전체 관리, 이벤트 승인, 긴급 환불
2. **주최자**: 이벤트 생성, 티켓 가격 설정, 환불 정책 설정
3. **구매자**: 티켓 구매, 재판매, 환불 요청

---

## 기술 스택

### 블록체인
- **네트워크**: Polygon (Mumbai 테스트넷 → Polygon Mainnet)
- **스마트 컨트랙트 언어**: Solidity (^0.8.20)
- **개발 프레임워크**: Hardhat
- **NFT 표준**: ERC-721
- **Account Abstraction**: ERC-4337

### 백엔드
- **프레임워크**: FastAPI (Python 3.11+)
- **데이터베이스**: PostgreSQL 15+
- **ORM**: SQLAlchemy
- **인증**: JWT + OAuth2 (Google)
- **IPFS 클라이언트**: Pinata SDK

### 프론트엔드
- **프레임워크**: React 18+ (TypeScript)
- **상태 관리**: Zustand / Redux Toolkit
- **UI 라이브러리**: Tailwind CSS + shadcn/ui
- **Web3 라이브러리**: ethers.js / viem
- **Account Abstraction**: @account-abstraction/sdk

### 인프라
- **IPFS**: Pinata
- **Account Abstraction Bundler**: Alchemy / Stackup
- **Paymaster**: 자체 구현 또는 Pimlico
- **배포**: Docker + Docker Compose

---

## 시스템 아키텍처

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  - 사용자 인터페이스                                         │
│  - 지갑 연결 (Account Abstraction)                          │
│  - 이벤트 브라우징/검색                                      │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS/REST API
┌────────────────────▼────────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Auth Service │  │ Event Service│  │ Ticket Service│     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ IPFS Service │  │ Web3 Service │  │ Payment Service│    │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└──────┬──────────┬──────────────┬──────────────┬────────────┘
       │          │              │              │
       │          │              │              │
┌──────▼──────┐ ┌─▼──────────┐ ┌─▼──────────┐ ┌─▼──────────┐
│ PostgreSQL  │ │   IPFS     │ │  Polygon   │ │  Bundler   │
│  Database   │ │  (Pinata)  │ │ Blockchain │ │  (ERC-4337)│
└─────────────┘ └────────────┘ └────────────┘ └────────────┘
```

### 데이터 흐름

1. **이벤트 생성**
   - 주최자가 이벤트 정보 입력
   - 백엔드가 메타데이터를 IPFS에 업로드
   - 스마트 컨트랙트에 이벤트 등록 (IPFS 해시 포함)
   - 관리자 승인 대기

2. **티켓 구매**
   - 사용자가 티켓 선택
   - Account Abstraction으로 자동 지갑 생성/연결
   - 스마트 컨트랙트 호출 (Paymaster가 가스비 부담)
   - NFT 티켓 발행
   - DB에 거래 기록 저장

3. **재판매**
   - 사용자가 재판매 등록
   - 스마트 컨트랙트에 마켓플레이스 등록
   - 구매자가 구매 시 수수료 자동 분배
   - DB에 재판매 기록 업데이트

---

## 스마트 컨트랙트 구조

### 컨트랙트 모듈화

```
contracts/
├── TicketNFT.sol              # ERC-721 티켓 NFT
├── EventManager.sol           # 이벤트 관리
├── TicketMarketplace.sol      # 2차 시장 재판매
├── RefundManager.sol          # 환불 관리
├── AccessControl.sol           # 권한 관리 (관리자/주최자)
└── interfaces/
    ├── ITicketNFT.sol
    ├── IEventManager.sol
    └── IMarketplace.sol
```

### 주요 컨트랙트

#### 1. TicketNFT.sol (ERC-721)
- 티켓 NFT 발행
- 티켓 소유권 관리
- 티켓 메타데이터 (IPFS 해시)

#### 2. EventManager.sol
- 이벤트 생성/수정/삭제
- 이벤트 승인 (관리자)
- 티켓 가격 설정
- 티켓 수량 관리

#### 3. TicketMarketplace.sol
- 재판매 등록
- 재판매 구매
- 수수료 자동 분배 (5-10%)
- 가격 상한선 검증 (200%)

#### 4. RefundManager.sol
- 환불 요청 처리
- 환불 정책 검증
- 자동 환불 실행

#### 5. AccessControl.sol
- 관리자 권한 관리
- 주최자 권한 관리
- 역할 기반 접근 제어

### 스마트 컨트랙트 주요 함수

```solidity
// EventManager.sol
function createEvent(
    string memory ipfsHash,
    uint256 price,
    uint256 maxTickets,
    uint256 startTime,
    uint256 endTime
) external returns (uint256 eventId);

function approveEvent(uint256 eventId) external onlyAdmin;
function updateEventPrice(uint256 eventId, uint256 newPrice) external onlyEventOwner;

// TicketNFT.sol
function mintTicket(
    address to,
    uint256 eventId,
    string memory tokenURI
) external returns (uint256 tokenId);

// TicketMarketplace.sol
function listTicketForResale(
    uint256 tokenId,
    uint256 price
) external;

function buyResaleTicket(uint256 tokenId) external payable;

// RefundManager.sol
function requestRefund(uint256 tokenId) external;
function processRefund(uint256 tokenId) external;
```

---

## 데이터베이스 스키마

### PostgreSQL 테이블 구조

```sql
-- 사용자 테이블
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    wallet_address VARCHAR(42) UNIQUE,
    smart_wallet_address VARCHAR(42), -- Account Abstraction 지갑
    role VARCHAR(20) DEFAULT 'buyer', -- admin, organizer, buyer
    kyc_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 이벤트 테이블
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id_onchain BIGINT, -- 스마트 컨트랙트의 eventId
    organizer_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    ipfs_hash VARCHAR(255), -- IPFS 메타데이터 해시
    price_wei BIGINT NOT NULL, -- 티켓 가격 (wei)
    max_tickets INTEGER NOT NULL,
    sold_tickets INTEGER DEFAULT 0,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    event_date TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, active, cancelled, ended
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 티켓 테이블
CREATE TABLE tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    token_id BIGINT UNIQUE NOT NULL, -- NFT tokenId
    event_id UUID REFERENCES events(id),
    owner_address VARCHAR(42) NOT NULL,
    ipfs_hash VARCHAR(255), -- 티켓 메타데이터 IPFS 해시
    status VARCHAR(20) DEFAULT 'active', -- active, refunded, transferred, cancelled
    purchase_price_wei BIGINT,
    purchase_tx_hash VARCHAR(66),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 재판매 테이블
CREATE TABLE resales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID REFERENCES tickets(id),
    token_id BIGINT NOT NULL,
    seller_address VARCHAR(42) NOT NULL,
    price_wei BIGINT NOT NULL,
    status VARCHAR(20) DEFAULT 'listed', -- listed, sold, cancelled
    created_at TIMESTAMP DEFAULT NOW(),
    sold_at TIMESTAMP,
    sale_tx_hash VARCHAR(66)
);

-- 거래 내역 테이블
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tx_hash VARCHAR(66) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),
    ticket_id UUID REFERENCES tickets(id),
    event_id UUID REFERENCES events(id),
    transaction_type VARCHAR(20) NOT NULL, -- purchase, resale, refund
    amount_wei BIGINT,
    gas_fee_wei BIGINT,
    status VARCHAR(20) DEFAULT 'pending', -- pending, confirmed, failed
    block_number BIGINT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 환불 요청 테이블
CREATE TABLE refund_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID REFERENCES tickets(id),
    user_id UUID REFERENCES users(id),
    reason TEXT,
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected, processed
    refund_amount_wei BIGINT,
    refund_tx_hash VARCHAR(66),
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);
```

---

## API 설계

### 인증 API

```
POST   /api/auth/register              # 회원가입
POST   /api/auth/login                 # 로그인 (이메일/비밀번호)
POST   /api/auth/google                # Google 소셜 로그인
POST   /api/auth/logout                # 로그아웃
GET    /api/auth/me                    # 현재 사용자 정보
POST   /api/auth/wallet/connect        # 지갑 연결 (Account Abstraction)
```

### 이벤트 API

```
GET    /api/events                     # 이벤트 목록 (검색/필터링)
GET    /api/events/:id                 # 이벤트 상세
POST   /api/events                     # 이벤트 생성 (주최자)
PUT    /api/events/:id                 # 이벤트 수정 (주최자)
DELETE /api/events/:id                 # 이벤트 삭제 (주최자)
POST   /api/events/:id/approve         # 이벤트 승인 (관리자)
POST   /api/events/:id/cancel          # 이벤트 취소 (주최자/관리자)
```

### 티켓 API

```
GET    /api/tickets                    # 내 티켓 목록
GET    /api/tickets/:id                # 티켓 상세
POST   /api/tickets/purchase           # 티켓 구매
GET    /api/tickets/:id/metadata       # 티켓 메타데이터 (IPFS)
```

### 재판매 API

```
GET    /api/resales                    # 재판매 목록
GET    /api/resales/:id                # 재판매 상세
POST   /api/resales                    # 재판매 등록
POST   /api/resales/:id/buy            # 재판매 구매
DELETE /api/resales/:id                # 재판매 취소
```

### 환불 API

```
POST   /api/refunds/request            # 환불 요청
GET    /api/refunds                    # 환불 요청 목록
GET    /api/refunds/:id                # 환불 요청 상세
POST   /api/refunds/:id/approve        # 환불 승인 (관리자/주최자)
POST   /api/refunds/:id/reject         # 환불 거부
```

### 관리자 API

```
GET    /api/admin/events/pending       # 승인 대기 이벤트
GET    /api/admin/stats                # 시스템 통계
POST   /api/admin/users/:id/role       # 사용자 역할 변경
POST   /api/admin/refunds/emergency   # 긴급 환불
```

---

## 프론트엔드 구조

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/                    # 공통 컴포넌트
│   │   ├── events/                    # 이벤트 관련
│   │   ├── tickets/                   # 티켓 관련
│   │   ├── marketplace/               # 재판매 마켓플레이스
│   │   └── admin/                     # 관리자 페이지
│   ├── pages/
│   │   ├── Home.tsx
│   │   ├── Events.tsx
│   │   ├── EventDetail.tsx
│   │   ├── MyTickets.tsx
│   │   ├── Marketplace.tsx
│   │   ├── CreateEvent.tsx
│   │   └── Admin.tsx
│   ├── hooks/
│   │   ├── useWeb3.ts                 # Web3 연결
│   │   ├── useAccountAbstraction.ts   # Account Abstraction
│   │   ├── useEvents.ts
│   │   └── useTickets.ts
│   ├── services/
│   │   ├── api.ts                     # API 클라이언트
│   │   ├── web3.ts                    # Web3 서비스
│   │   └── ipfs.ts                    # IPFS 서비스
│   ├── store/
│   │   ├── authStore.ts               # 인증 상태
│   │   ├── eventStore.ts
│   │   └── ticketStore.ts
│   └── utils/
│       ├── constants.ts               # 컨트랙트 주소 등
│       └── helpers.ts
```

---

## Account Abstraction 구현

### 구조

```
User (소셜 로그인)
    ↓
Backend (FastAPI)
    ├── 사용자 인증 (JWT)
    ├── Smart Wallet 생성/관리
    └── UserOperation 생성
    ↓
Bundler (Alchemy/Stackup)
    ├── UserOperation 검증
    ├── 가스비 계산
    └── 트랜잭션 번들링
    ↓
Paymaster (자체 구현)
    ├── 가스비 지불 (핵심 기능만)
    └── 정책 검증
    ↓
EntryPoint (ERC-4337)
    └── 트랜잭션 실행
    ↓
Polygon Blockchain
```

### 구현 세부사항

1. **Smart Wallet 생성**
   - 사용자 로그인 시 백엔드에서 Smart Wallet 주소 생성
   - Deterministic 주소 생성 (CREATE2 사용)
   - 사용자별 고유 Smart Wallet

2. **UserOperation 생성**
   - 프론트엔드에서 트랜잭션 요청
   - 백엔드가 UserOperation 생성
   - 서명은 백엔드에서 관리 (보안 고려 필요)

3. **Paymaster 정책**
   - 티켓 구매: 서비스 부담
   - 재판매 구매: 사용자 부담
   - 환불: 서비스 부담
   - 재판매 등록: 사용자 부담

### 보안 고려사항
- Smart Wallet 서명 키는 암호화하여 저장
- 하드웨어 지갑 또는 AWS KMS 사용 고려
- Rate limiting 및 트랜잭션 검증

---

## IPFS 통합

### Pinata 사용

1. **이벤트 메타데이터 구조**
```json
{
  "name": "콘서트 이름",
  "description": "이벤트 설명",
  "image": "ipfs://Qm...", // 이벤트 이미지
  "attributes": [
    {
      "trait_type": "Date",
      "value": "2024-12-25"
    },
    {
      "trait_type": "Venue",
      "value": "올림픽공원"
    }
  ]
}
```

2. **티켓 메타데이터 구조**
```json
{
  "name": "Ticket #123",
  "description": "콘서트 티켓",
  "image": "ipfs://Qm...", // 티켓 이미지
  "attributes": [
    {
      "trait_type": "Event",
      "value": "이벤트 ID"
    },
    {
      "trait_type": "Seat",
      "value": "A-12"
    }
  ]
}
```

3. **업로드 프로세스**
   - 백엔드에서 Pinata API 사용
   - 메타데이터 JSON 생성
   - IPFS에 업로드
   - 해시를 스마트 컨트랙트에 저장

---

## 보안 고려사항

### 스마트 컨트랙트
- Reentrancy 방지
- Access Control 검증
- Integer overflow 방지 (Solidity 0.8+)
- 이벤트 로깅
- 외부 감사 권장

### 백엔드
- JWT 토큰 검증
- Rate limiting
- SQL Injection 방지 (ORM 사용)
- CORS 설정
- 환경 변수 관리 (.env)

### 프론트엔드
- XSS 방지
- CSRF 토큰
- 입력 검증
- 민감 정보 노출 방지

### Account Abstraction
- Smart Wallet 키 관리
- UserOperation 검증
- Paymaster 정책 엄격히 적용

---

## 배포 전략

### 개발 환경
- 로컬 Hardhat 네트워크
- 로컬 PostgreSQL
- Pinata 테스트 계정

### 테스트넷 배포
1. **스마트 컨트랙트**
   - Hardhat로 Polygon Mumbai 테스트넷 배포
   - 컨트랙트 주소 저장

2. **백엔드**
   - Docker 컨테이너로 배포
   - 환경 변수 설정

3. **프론트엔드**
   - Vercel / Netlify 배포
   - 환경 변수 설정

### 메인넷 배포
- 스마트 컨트랙트 외부 감사 필수
- 점진적 롤아웃
- 모니터링 시스템 구축

---

## 다음 단계

1. 프로젝트 초기 설정
2. 스마트 컨트랙트 개발
3. 백엔드 API 개발
4. 프론트엔드 개발
5. 통합 테스트
6. 테스트넷 배포
7. 보안 감사
8. 메인넷 배포

---

## 참고 자료

- [ERC-721 표준](https://eips.ethereum.org/EIPS/eip-721)
- [ERC-4337 (Account Abstraction)](https://eips.ethereum.org/EIPS/eip-4337)
- [Polygon 문서](https://docs.polygon.technology/)
- [Hardhat 문서](https://hardhat.org/docs)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Pinata 문서](https://docs.pinata.cloud/)

