# 시스템 아키텍처 - 주요 플로우

## 1. 회원가입/로그인

```
User → React (입력)
React → Backend API (POST /api/auth/register)
Backend → PostgreSQL (사용자 저장)
PostgreSQL → Backend (응답)
Backend → React (JWT 토큰)
React → User (로그인 완료)
```

## 2. Smart Wallet 생성

```
User → React (지갑 생성 요청)
React → Backend API (POST /api/auth/wallet/create)
Backend → SmartWalletFactory (주소 계산)
SmartWalletFactory → Backend (주소 반환)
Backend → SmartWalletFactory (배포 트랜잭션)
SmartWalletFactory → Blockchain (Smart Wallet 배포)
Blockchain → Backend (트랜잭션 완료)
Backend → PostgreSQL (주소 저장)
PostgreSQL → Backend (응답)
Backend → React (Smart Wallet 주소)
React → User (생성 완료)
```

## 3. 이벤트 생성 (주최자)

```
User → React (이벤트 정보 입력)
React → Backend API (POST /api/events)
Backend → IPFS/Pinata (메타데이터 업로드)
IPFS/Pinata → Backend (IPFS 해시)
Backend → PostgreSQL (이벤트 저장)
PostgreSQL → Backend (응답)
Backend → EventManager Contract (createEvent 호출)
EventManager → Blockchain (이벤트 등록)
Blockchain → Backend (이벤트 ID)
Backend → PostgreSQL (onchain ID 업데이트)
PostgreSQL → Backend (응답)
Backend → React (이벤트 생성 완료)
React → User (생성 완료)
```

## 4. 이벤트 승인 (관리자)

```
User → React (승인 버튼 클릭)
React → Backend API (POST /api/events/{id}/approve)
Backend → EventManager Contract (approveEvent 호출)
EventManager → Blockchain (승인 상태 변경)
Blockchain → Backend (트랜잭션 완료)
Backend → PostgreSQL (상태 업데이트)
PostgreSQL → Backend (응답)
Backend → React (승인 완료)
React → User (승인 완료)
```

## 5. 티켓 구매

```
User → React (구매 버튼 클릭)
React → Backend API (POST /api/tickets/purchase)
Backend → PostgreSQL (이벤트 검증)
PostgreSQL → Backend (이벤트 정보)
Backend → IPFS/Pinata (티켓 메타데이터 업로드)
IPFS/Pinata → Backend (IPFS 해시)
Backend → AA Service (UserOperation 생성)
AA Service → EntryPoint (Nonce 조회)
EntryPoint → Backend (Nonce 반환)
Backend → AA Service (UserOperation 서명)
AA Service → EntryPoint (UserOperation 전송)
EntryPoint → Smart Wallet (validateUserOp)
Smart Wallet → EntryPoint (검증 완료)
EntryPoint → Smart Wallet (execute)
Smart Wallet → EventManager (purchaseTicket 호출)
EventManager → TicketNFT (mintTicket)
TicketNFT → Blockchain (NFT 발행)
EventManager → Blockchain (주최자에게 지불)
Blockchain → Backend (트랜잭션 완료)
Backend → PostgreSQL (티켓 저장)
PostgreSQL → Backend (응답)
Backend → React (구매 완료)
React → User (구매 완료)
```

## 6. 재판매 등록

```
User → React (재판매 등록 버튼)
React → Backend API (POST /api/resales)
Backend → PostgreSQL (티켓 소유자 확인)
PostgreSQL → Backend (티켓 정보)
Backend → EventManager (원가 조회)
EventManager → Backend (원가 반환)
Backend → TicketMarketplace (listTicketForResale 호출)
TicketMarketplace → Blockchain (재판매 등록)
Blockchain → Backend (트랜잭션 완료)
Backend → PostgreSQL (재판매 정보 저장)
PostgreSQL → Backend (응답)
Backend → React (등록 완료)
React → User (등록 완료)
```

## 7. 재판매 구매

```
User → React (구매 버튼 클릭)
React → Backend API (POST /api/resales/{id}/buy)
Backend → PostgreSQL (재판매 정보 조회)
PostgreSQL → Backend (재판매 정보)
Backend → TicketMarketplace (buyResaleTicket 호출)
TicketMarketplace → TicketNFT (safeTransferFrom)
TicketNFT → Blockchain (NFT 소유권 이전)
TicketMarketplace → Blockchain (판매자에게 지불)
TicketMarketplace → Blockchain (수수료 수령자에게 지불)
Blockchain → Backend (트랜잭션 완료)
Backend → PostgreSQL (재판매 상태 업데이트)
PostgreSQL → Backend (응답)
Backend → React (구매 완료)
React → User (구매 완료)
```

## 8. 환불 요청

```
User → React (환불 요청 버튼)
React → Backend API (POST /api/refunds/request)
Backend → PostgreSQL (환불 요청 저장)
PostgreSQL → Backend (응답)
Backend → React (요청 완료)
React → User (요청 완료)
```

## 9. 환불 처리 (관리자/주최자)

```
User → React (환불 승인 버튼)
React → Backend API (POST /api/refunds/{id}/approve)
Backend → RefundManager (processRefund 호출)
RefundManager → TicketNFT (burnTicket)
TicketNFT → Blockchain (NFT 소각)
RefundManager → Blockchain (환불 금액 전송)
Blockchain → Backend (트랜잭션 완료)
Backend → PostgreSQL (환불 상태 업데이트)
PostgreSQL → Backend (응답)
Backend → React (처리 완료)
React → User (처리 완료)
```

## 10. 이벤트 목록 조회

```
User → React (이벤트 목록 페이지)
React → Backend API (GET /api/events)
Backend → PostgreSQL (이벤트 조회)
PostgreSQL → Backend (이벤트 목록)
Backend → React (이벤트 목록)
React → User (화면 표시)
```

## 11. 내 티켓 조회

```
User → React (내 티켓 페이지)
React → Backend API (GET /api/tickets)
Backend → PostgreSQL (티켓 조회)
PostgreSQL → Backend (티켓 목록)
Backend → React (티켓 목록)
React → User (화면 표시)
```

## 12. 재판매 목록 조회

```
User → React (마켓플레이스 페이지)
React → Backend API (GET /api/resales)
Backend → PostgreSQL (재판매 목록 조회)
PostgreSQL → Backend (재판매 목록)
Backend → React (재판매 목록)
React → User (화면 표시)
```

---

## 주요 컴포넌트

- **User**: 사용자
- **React**: 프론트엔드 (React + TypeScript)
- **Backend API**: FastAPI 백엔드
- **PostgreSQL**: 데이터베이스
- **IPFS/Pinata**: 메타데이터 저장
- **AA Service**: Account Abstraction 서비스
- **EntryPoint**: ERC-4337 EntryPoint
- **Smart Wallet**: 사용자 Smart Wallet
- **EventManager**: 이벤트 관리 컨트랙트
- **TicketNFT**: 티켓 NFT 컨트랙트
- **TicketMarketplace**: 재판매 마켓플레이스 컨트랙트
- **RefundManager**: 환불 관리 컨트랙트
- **Blockchain**: Polygon 블록체인
- **SmartWalletFactory**: Smart Wallet Factory 컨트랙트

