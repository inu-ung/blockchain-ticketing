# Account Abstraction 상세 설명

## 1. 실제 Smart Wallet 컨트랙트 배포 (ERC-4337)

### 현재 상태
- ✅ Smart Wallet 주소 생성 (임시 해시 기반)
- ❌ 실제 Smart Wallet 컨트랙트 없음
- ❌ 사용자가 트랜잭션을 실행할 수 없음

### 문제점
현재는 주소만 생성하고 실제 컨트랙트가 없어서:
- 트랜잭션을 보낼 수 없음
- UserOperation을 실행할 수 없음
- 단순히 주소만 있는 상태

### 해결 방법: Smart Wallet 컨트랙트 배포

#### 1-1. Smart Wallet 컨트랙트란?
ERC-4337 표준에 따라 사용자 대신 트랜잭션을 실행하는 스마트 컨트랙트입니다.

**특징:**
- 사용자가 직접 지갑을 설치할 필요 없음
- 서비스가 가스비를 부담할 수 있음 (Paymaster)
- 복잡한 로직 실행 가능 (다중 서명, 시간 잠금 등)

#### 1-2. 구현 방법

**옵션 A: SimpleAccount 사용 (가장 간단)**
```solidity
// OpenZeppelin의 SimpleAccount 사용
// 이미 검증된 컨트랙트, 바로 사용 가능
```

**옵션 B: 직접 구현**
```solidity
// ERC-4337 표준에 맞춰 직접 구현
// 더 많은 커스터마이징 가능
```

#### 1-3. 배포 과정

1. **Smart Wallet Factory 컨트랙트 배포**
   - CREATE2를 사용하여 Deterministic 주소 생성
   - 사용자별 고유 주소 보장

2. **EntryPoint 컨트랙트 확인**
   - ERC-4337 표준 EntryPoint 사용
   - 이미 배포된 주소: `0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789`

3. **사용자별 Smart Wallet 생성**
   - 사용자 로그인 시 Factory에서 생성
   - 또는 첫 트랜잭션 시 자동 생성

#### 1-4. 코드 예시

```python
# backend/app/services/aa_service.py

def deploy_smart_wallet(self, user_id: str) -> str:
    """
    Smart Wallet 배포
    
    Returns:
        Smart Wallet 주소
    """
    # 1. Factory 컨트랙트 인스턴스
    factory = self.w3.eth.contract(
        address=self.factory_address,
        abi=factory_abi
    )
    
    # 2. CREATE2로 주소 계산
    salt = self.generate_salt(user_id)
    wallet_address = factory.functions.getAddress(
        owner_address,  # 사용자 주소 또는 서비스 계정
        salt
    ).call()
    
    # 3. 아직 배포되지 않았다면 배포
    if self.w3.eth.get_code(wallet_address) == b'':
        tx_hash = factory.functions.createAccount(
            owner_address,
            salt
        ).transact({
            'from': self.service_account,
            'gas': 1000000
        })
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return wallet_address
```

---

## 4. 프론트엔드에서 UserOperation 사용

### 현재 상태
- ✅ UserOperation 생성 API 있음
- ✅ 백엔드에서 UserOperation 생성 가능
- ❌ 프론트엔드에서 실제로 사용하는 로직 없음

### 문제점
- 티켓 구매, 재판매 등에서 여전히 일반 트랜잭션 사용
- UserOperation을 통한 트랜잭션 실행이 없음

### 해결 방법: 프론트엔드에서 UserOperation 사용

#### 4-1. UserOperation이란?
일반 트랜잭션 대신 사용하는 ERC-4337의 트랜잭션 형식입니다.

**차이점:**
- 일반 트랜잭션: 사용자가 직접 서명하고 전송
- UserOperation: Bundler가 여러 개를 모아서 실행 (가스비 절약)

#### 4-2. 사용 흐름

```
1. 사용자가 티켓 구매 버튼 클릭
   ↓
2. 프론트엔드: UserOperation 생성 요청
   POST /api/v1/user-operations/create
   {
     "target": "0x...EventManager",
     "data": "0x...purchaseTicket(...)",
     "value": 1000000000000000000
   }
   ↓
3. 백엔드: UserOperation 생성 및 반환
   {
     "user_operation": {...},
     "message": "Signature required"
   }
   ↓
4. 프론트엔드: 서명 (또는 백엔드에서 자동 서명)
   ↓
5. 프론트엔드: UserOperation 전송
   POST /api/v1/user-operations/send
   {
     "user_operation": {...},
     "signature": "0x..."
   }
   ↓
6. 백엔드: Bundler로 전송
   ↓
7. Bundler: EntryPoint를 통해 실행
   ↓
8. 완료!
```

#### 4-3. 프론트엔드 구현 예시

```typescript
// frontend/src/services/userOperation.ts

import apiClient from './api';
import { ethers } from 'ethers';

/**
 * 티켓 구매를 위한 UserOperation 생성 및 전송
 */
export async function purchaseTicketWithAA(
  eventManagerAddress: string,
  eventId: number,
  tokenUri: string,
  price: bigint
): Promise<string> {
  // 1. 컨트랙트 호출 데이터 생성
  const eventManager = new ethers.Interface([
    "function purchaseTicket(uint256 eventId, string memory tokenURI) external payable"
  ]);
  
  const callData = eventManager.encodeFunctionData(
    "purchaseTicket",
    [eventId, tokenUri]
  );
  
  // 2. UserOperation 생성
  const createResponse = await apiClient.post('/user-operations/create', {
    target: eventManagerAddress,
    data: callData,
    value: price.toString()
  });
  
  const userOp = createResponse.data.user_operation;
  
  // 3. 서명 (백엔드에서 자동 처리하거나 프론트엔드에서 처리)
  // TODO: 실제 서명 로직
  
  // 4. UserOperation 전송
  const sendResponse = await apiClient.post('/user-operations/send', {
    user_operation: userOp,
    signature: "0x..." // 서명
  });
  
  return sendResponse.data.user_operation_hash;
}
```

#### 4-4. 실제 사용 예시

**티켓 구매 페이지에서:**
```typescript
// frontend/src/pages/EventDetail.tsx

import { purchaseTicketWithAA } from '../services/userOperation';

const handlePurchase = async () => {
  try {
    // UserOperation을 통한 티켓 구매
    const opHash = await purchaseTicketWithAA(
      EVENT_MANAGER_ADDRESS,
      eventId,
      tokenUri,
      BigInt(event.price_wei)
    );
    
    console.log('Ticket purchased!', opHash);
    // 성공 메시지 표시
  } catch (error) {
    console.error('Purchase failed:', error);
  }
};
```

---

## 요약

### 1번: Smart Wallet 컨트랙트 배포
**목적:** 실제로 트랜잭션을 실행할 수 있는 Smart Wallet 생성

**필요한 것:**
- Smart Wallet Factory 컨트랙트
- EntryPoint 컨트랙트 (이미 배포됨)
- 배포 로직

**결과:**
- 사용자가 실제로 트랜잭션을 보낼 수 있음
- UserOperation이 실행됨

### 4번: 프론트엔드에서 UserOperation 사용
**목적:** 티켓 구매, 재판매 등에서 UserOperation 사용

**필요한 것:**
- UserOperation 생성 함수
- 서명 로직
- 전송 로직

**결과:**
- 사용자가 지갑 설치 없이 트랜잭션 실행
- 서비스가 가스비 부담 가능 (Paymaster)

---

## 구현 우선순위

1. **Smart Wallet 컨트랙트 배포** (1번)
   - 먼저 해야 함
   - 없으면 UserOperation을 실행할 수 없음

2. **프론트엔드 UserOperation 사용** (4번)
   - 1번 완료 후 진행
   - 실제 기능에서 사용

3. **Bundler/Paymaster 연동**
   - 1번, 4번 완료 후 진행
   - 프로덕션 배포 시 필요

