# Web3 서비스 구현 계획

## 🎯 목표

백엔드에서 스마트 컨트랙트와 직접 통신하여:
- 이벤트 생성/승인
- 티켓 구매
- 재판매 등록/구매
- 환불 처리

## 📋 현재 상태

### ✅ 준비된 것
1. **스마트 컨트랙트**: 구현 및 테스트 완료
2. **ABI 파일**: `contracts/artifacts/contracts/` 폴더에 있음
3. **배포 정보**: `contracts/deployments/localhost.json` (로컬 네트워크)
4. **컨트랙트 주소**: 로컬 네트워크에 배포됨 (또는 배포 가능)

### ❌ 아직 안 된 것
1. **web3 Python 패키지**: 설치 필요
2. **web3_service.py**: 실제 구현 필요 (현재 주석 처리됨)
3. **컨트랙트 주소 설정**: backend/.env에 추가 필요

## 🔧 구현 계획

### 1단계: 환경 설정

#### 1.1 web3 패키지 설치
```bash
cd backend
source venv/bin/activate
pip install web3
```

#### 1.2 ABI 파일 준비
- `contracts/artifacts/contracts/EventManager.sol/EventManager.json`에서 ABI 추출
- `contracts/artifacts/contracts/TicketNFT.sol/TicketNFT.json`에서 ABI 추출
- `contracts/artifacts/contracts/TicketMarketplace.sol/TicketMarketplace.json`에서 ABI 추출
- `contracts/artifacts/contracts/RefundManager.sol/RefundManager.json`에서 ABI 추출

#### 1.3 컨트랙트 주소 설정
- 로컬 네트워크: `contracts/deployments/localhost.json`에서 주소 가져오기
- 또는 로컬 네트워크에 새로 배포
- `backend/.env`에 컨트랙트 주소 추가

### 2단계: Web3Service 클래스 구현

#### 2.1 초기화
```python
from web3 import Web3
from eth_account import Account

class Web3Service:
    def __init__(self):
        # RPC 연결
        self.w3 = Web3(Web3.HTTPProvider(settings.POLYGON_MUMBAI_RPC_URL))
        # 또는 로컬: Web3(Web3.HTTPProvider("http://localhost:8545"))
        
        # 계정 설정 (서비스 계정)
        self.private_key = settings.PRIVATE_KEY
        self.account = Account.from_key(self.private_key)
        self.address = self.account.address
```

#### 2.2 컨트랙트 인스턴스 생성
```python
def get_contract_instance(self, contract_address: str, abi: list):
    """컨트랙트 인스턴스 가져오기"""
    return self.w3.eth.contract(address=contract_address, abi=abi)
```

#### 2.3 트랜잭션 전송 헬퍼
```python
def send_transaction(self, contract_function, value: int = 0):
    """트랜잭션 전송"""
    # 1. 트랜잭션 빌드
    # 2. 서명
    # 3. 전송
    # 4. 트랜잭션 해시 반환
```

### 3단계: 주요 함수 구현

#### 3.1 이벤트 생성 (`create_event_onchain`)
```python
def create_event_onchain(
    self,
    event_manager_address: str,
    ipfs_hash: str,
    price: int,
    max_tickets: int,
    start_time: int,
    end_time: int,
    event_date: int
) -> str:
    """온체인에 이벤트 생성"""
    # 1. EventManager 컨트랙트 인스턴스 가져오기
    # 2. createEvent 함수 호출
    # 3. 트랜잭션 전송
    # 4. 트랜잭션 해시 반환
```

#### 3.2 이벤트 승인 (`approve_event_onchain`)
```python
def approve_event_onchain(
    self,
    event_manager_address: str,
    event_id: int
) -> str:
    """온체인에서 이벤트 승인"""
    # 1. EventManager 컨트랙트 인스턴스
    # 2. approveEvent 함수 호출
    # 3. 트랜잭션 전송
```

#### 3.3 티켓 구매 (`purchase_ticket_onchain`)
```python
def purchase_ticket_onchain(
    self,
    event_manager_address: str,
    event_id: int,
    token_uri: str,
    value: int,
    buyer_address: str
) -> tuple[str, int]:
    """온체인에서 티켓 구매"""
    # 1. EventManager 컨트랙트 인스턴스
    # 2. purchaseTicket 함수 호출 (value 포함)
    # 3. 트랜잭션 전송
    # 4. 이벤트 로그에서 token_id 추출
    # 5. (tx_hash, token_id) 반환
```

#### 3.4 재판매 등록 (`list_ticket_for_resale`)
```python
def list_ticket_for_resale(
    self,
    marketplace_address: str,
    ticket_nft_address: str,
    token_id: int,
    price: int
) -> str:
    """티켓을 재판매 마켓플레이스에 등록"""
    # 1. TicketNFT 컨트랙트에서 approve
    # 2. TicketMarketplace 컨트랙트에서 listTicketForResale
    # 3. 트랜잭션 전송
```

#### 3.5 재판매 구매 (`buy_resale_ticket`)
```python
def buy_resale_ticket(
    self,
    marketplace_address: str,
    listing_id: int,
    value: int,
    buyer_address: str
) -> str:
    """재판매 티켓 구매"""
    # 1. TicketMarketplace 컨트랙트 인스턴스
    # 2. buyTicket 함수 호출 (value 포함)
    # 3. 트랜잭션 전송
```

#### 3.6 환불 처리 (`process_refund`)
```python
def process_refund(
    self,
    refund_manager_address: str,
    ticket_nft_address: str,
    token_id: int
) -> str:
    """환불 처리 (티켓 소각)"""
    # 1. RefundManager 컨트랙트 인스턴스
    # 2. processRefund 함수 호출
    # 3. 트랜잭션 전송
```

### 4단계: ABI 파일 관리

#### 옵션 A: ABI 파일 직접 복사
- `contracts/artifacts/contracts/*.sol/*.json`에서 ABI 추출
- `backend/app/contracts/` 폴더에 저장

#### 옵션 B: 런타임에 ABI 로드
- 배포 정보 파일에서 ABI 읽기
- 또는 하드코딩 (개발용)

### 5단계: 백엔드 API 연동

#### 5.1 이벤트 생성 API 수정
```python
# app/api/v1/events.py
@router.post("")
async def create_event(...):
    # ... 기존 코드 ...
    
    # 온체인에 이벤트 생성
    event_id_onchain = web3_service.create_event_onchain(
        event_manager_address=settings.EVENT_MANAGER_ADDRESS,
        ipfs_hash=ipfs_hash,
        price=event_create.price_wei,
        max_tickets=event_create.max_tickets,
        start_time=int(event_create.start_time.timestamp()),
        end_time=int(event_create.end_time.timestamp()),
        event_date=int(event_create.event_date.timestamp())
    )
    
    db_event.event_id_onchain = event_id_onchain
    db.commit()
```

#### 5.2 티켓 구매 API 수정
```python
# app/api/v1/tickets.py
@router.post("/purchase")
async def purchase_ticket(...):
    # ... 기존 코드 ...
    
    # 온체인에서 티켓 구매
    tx_hash, token_id = web3_service.purchase_ticket_onchain(
        event_manager_address=settings.EVENT_MANAGER_ADDRESS,
        event_id=event.event_id_onchain,
        token_uri=token_uri,
        value=event.price_wei,
        buyer_address=current_user.wallet_address
    )
    
    db_ticket.token_id = token_id
    db_ticket.purchase_tx_hash = tx_hash
```

## 🔍 필요한 정보

### 컨트랙트 함수 시그니처

#### EventManager
- `createEvent(ipfsHash, price, maxTickets, startTime, endTime, eventDate) → uint256`
- `approveEvent(eventId)`
- `purchaseTicket(eventId, tokenURI) payable → uint256`

#### TicketMarketplace
- `listTicketForResale(tokenId, price) → uint256`
- `buyTicket(listingId) payable`

#### RefundManager
- `processRefund(tokenId)`

## ⚠️ 주의사항

1. **가스비**: 모든 트랜잭션에 가스비 필요
2. **서비스 계정**: 백엔드가 사용할 계정 필요 (PRIVATE_KEY)
3. **에러 처리**: 트랜잭션 실패 시 롤백 처리
4. **이벤트 로그**: 트랜잭션 결과 확인용

## 🚀 구현 순서

1. **환경 설정** (10분)
   - web3 설치
   - ABI 파일 준비
   - 컨트랙트 주소 설정

2. **기본 구조** (20분)
   - Web3Service 초기화
   - 컨트랙트 인스턴스 생성
   - 트랜잭션 전송 헬퍼

3. **핵심 함수** (1시간)
   - 이벤트 생성
   - 티켓 구매
   - 재판매 등록/구매
   - 환불 처리

4. **API 연동** (30분)
   - 백엔드 API에 Web3 호출 추가
   - 에러 처리

5. **테스트** (30분)
   - 로컬 네트워크에서 테스트
   - 전체 플로우 확인

## 📝 예상 결과

구현 완료 후:
- ✅ 이벤트 생성 시 온체인에 자동 저장
- ✅ 티켓 구매 시 실제 NFT 발행
- ✅ 재판매 시 블록체인에 기록
- ✅ 환불 시 NFT 소각

## ❓ 질문

1. **로컬 네트워크 사용할까요?**
   - Hardhat 로컬 노드 실행 중이면 바로 사용 가능
   - 아니면 새로 배포 필요

2. **서비스 계정은 어떻게 할까요?**
   - 백엔드가 사용할 계정 필요
   - 로컬: Hardhat 기본 계정 사용 가능
   - 테스트넷: 별도 계정 필요

3. **에러 처리는 어떻게 할까요?**
   - 트랜잭션 실패 시 DB 롤백
   - 사용자에게 명확한 에러 메시지

