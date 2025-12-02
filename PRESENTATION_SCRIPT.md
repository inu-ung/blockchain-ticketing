# 발표 스크립트 - 티켓팅 프로세스 설명

## 수정된 버전

저희 프로젝트의 전체 티켓팅 프로세스는 크게 네 단계로 구성됩니다.

**첫 번째는 사용자 단계(User) 입니다.**

사용자는 간단한 회원가입과 로그인만 하면 자동으로 Smart Wallet이 생성되어, 별도의 메타마스크 설치 없이도 온체인 거래를 수행할 수 있습니다. 이 과정은 Account Abstraction 기반으로 동작하며, CREATE2 방식을 사용하여 사용자별로 고유한 Smart Wallet 주소가 결정적으로 생성됩니다.

**두 번째는 주최자 단계(Event Organizer) 입니다.**

주최자는 콘서트나 전시 같은 이벤트 정보를 입력하고, 해당 정보는 메타데이터 JSON으로 생성된 뒤 IPFS에 업로드됩니다. 이후 EventManager 스마트 컨트랙트에 이벤트가 등록되고, eventId가 발급됩니다. 이벤트는 관리자의 승인을 받아야 판매가 시작됩니다.

**세 번째는 티켓 구매 단계(Buy Ticket) 입니다.**

사용자가 구매 버튼을 누르면, Smart Wallet이 실행할 UserOperation이 생성되고, Paymaster가 트랜잭션을 검증하여 필요한 가스비를 대신 지불합니다. 그 다음 백엔드에서 UserOperation이 자동으로 서명됩니다.

**마지막은 티켓 발행 단계(Ticketing) 입니다.**

UserOperation은 EntryPoint 컨트랙트에서 검증되고 실행됩니다. EntryPoint는 Smart Wallet과 Paymaster를 검증한 후, Smart Wallet이 EventManager 컨트랙트의 purchaseTicket 함수를 호출합니다. EventManager는 이벤트 상태를 검증하고, TicketNFT 컨트랙트의 mintTicket 함수를 호출하여 NFT 티켓을 발행합니다. 동시에 구매자가 지불한 금액이 주최자에게 자동으로 전송됩니다. 최종적으로 사용자의 Smart Wallet 주소로 NFT 티켓이 발행됩니다.

이러한 구조를 통해 사용자는 지갑 설치 없이도 편하게 티켓을 구매할 수 있으며, 모든 데이터는 블록체인에 투명하게 기록되고 위변조가 불가능합니다.

---

## 주요 수정 사항

### 1. User 단계
- ✅ "CREATE2 방식을 사용하여 사용자별로 고유한 Smart Wallet 주소가 결정적으로 생성됩니다" 추가

### 2. Event Organizer 단계
- ✅ "이벤트는 관리자의 승인을 받아야 판매가 시작됩니다" 추가

### 3. Buy Ticket 단계
- ✅ 순서 수정: "Paymaster 검증 → UserOperation 서명" (원래는 서명 후 검증으로 보였음)

### 4. Ticketing 단계 (가장 중요)
- ❌ 기존: "Smart Wallet은 TicketNFT 컨트랙트의 mint 함수를 호출합니다"
- ✅ 수정: "Smart Wallet이 EventManager 컨트랙트의 purchaseTicket 함수를 호출합니다. EventManager는 이벤트 상태를 검증하고, TicketNFT 컨트랙트의 mintTicket 함수를 호출하여 NFT 티켓을 발행합니다."
- ✅ 추가: "동시에 구매자가 지불한 금액이 주최자에게 자동으로 전송됩니다"
- ✅ 수정: "사용자의 Smart Wallet 주소로 NFT 티켓이 발행됩니다" (일반 지갑 주소가 아님)

---

## 간단 버전 (핵심만)

저희 프로젝트의 전체 티켓팅 프로세스는 크게 네 단계로 구성됩니다.

**첫 번째는 사용자 단계입니다.** 사용자는 간단한 회원가입과 로그인만 하면 Account Abstraction 기반으로 Smart Wallet이 자동 생성되어, 별도의 메타마스크 설치 없이도 온체인 거래를 수행할 수 있습니다.

**두 번째는 주최자 단계입니다.** 주최자는 이벤트 정보를 입력하고, 메타데이터를 IPFS에 업로드한 후 EventManager 스마트 컨트랙트에 이벤트를 등록합니다. 관리자 승인 후 판매가 시작됩니다.

**세 번째는 티켓 구매 단계입니다.** 사용자가 구매 버튼을 누르면 UserOperation이 생성되고, Paymaster가 가스비를 대신 지불하며, 백엔드에서 자동으로 서명됩니다.

**마지막은 티켓 발행 단계입니다.** EntryPoint에서 Smart Wallet과 Paymaster를 검증한 후, Smart Wallet이 EventManager의 purchaseTicket 함수를 호출합니다. EventManager는 이벤트를 검증하고 TicketNFT의 mintTicket 함수를 호출하여 NFT 티켓을 발행하며, 주최자에게 자동으로 지불합니다.

이러한 구조를 통해 사용자는 지갑 설치 없이도 편하게 티켓을 구매할 수 있으며, 모든 데이터는 블록체인에 투명하게 기록되고 위변조가 불가능합니다.

