# Smart Wallet 컨트랙트 배포 설명

## 1. Smart Wallet이란?

### 개념
Smart Wallet은 **사용자 대신 트랜잭션을 실행하는 스마트 컨트랙트**입니다.

**일반 지갑 vs Smart Wallet:**
- 일반 지갑: 사용자가 직접 서명하고 트랜잭션 전송
- Smart Wallet: 컨트랙트가 사용자의 서명을 검증하고 트랜잭션 실행

### 장점
1. **지갑 설치 불필요**: 사용자가 MetaMask 등을 설치할 필요 없음
2. **가스비 부담 가능**: 서비스(Paymaster)가 가스비를 지불 가능
3. **복잡한 로직**: 다중 서명, 시간 잠금 등 구현 가능
4. **배치 실행**: 여러 트랜잭션을 묶어서 실행 가능

## 2. 구현된 컨트랙트

### 2-1. SmartWallet.sol

**역할:**
- 사용자 대신 트랜잭션 실행
- 서명 검증
- EntryPoint와 통신

**주요 함수:**
```solidity
// 초기화 (Proxy 배포 시)
function initialize(address _owner)

// 트랜잭션 실행 (EntryPoint에서 호출)
function execute(address target, uint256 value, bytes calldata data)

// UserOperation 검증 (EntryPoint에서 호출)
function validateUserOp(UserOperation calldata userOp, ...)
```

**동작 흐름:**
```
1. 사용자가 UserOperation 생성
   ↓
2. EntryPoint가 validateUserOp 호출
   → 서명 검증
   → Nonce 검증
   ↓
3. EntryPoint가 execute 호출
   → 실제 컨트랙트 호출
   ↓
4. 완료!
```

### 2-2. SmartWalletFactory.sol

**역할:**
- Smart Wallet 생성
- CREATE2로 Deterministic 주소 생성
- Proxy 패턴으로 가스비 절약

**주요 함수:**
```solidity
// 주소 계산 (배포 전에도 가능)
function getAddress(address owner, uint256 salt) returns (address)

// Smart Wallet 생성
function createWallet(address owner, uint256 salt) returns (address)
```

**CREATE2 설명:**
- 같은 `owner`와 `salt`로 항상 같은 주소 생성
- 배포 전에도 주소를 미리 알 수 있음
- 사용자 ID를 salt로 사용하면 사용자별 고유 주소 보장

## 3. 배포 과정

### 3-1. 컨트랙트 배포

```bash
cd contracts
npx hardhat run scripts/deploy_smart_wallet.js --network localhost
```

**배포 순서:**
1. SmartWallet 구현 컨트랙트 배포
2. SmartWalletFactory 배포
3. 배포 정보 저장

### 3-2. 배포 결과

```
SmartWallet: 0x... (구현 컨트랙트)
SmartWalletFactory: 0x... (Factory)
EntryPoint: 0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789 (표준 주소)
```

## 4. 백엔드에서 사용

### 4-1. Smart Wallet 생성

```python
# backend/app/services/aa_service.py

def generate_smart_wallet_address(self, user_id: str) -> str:
    """
    Smart Wallet 주소 생성
    
    Args:
        user_id: 사용자 고유 ID
    
    Returns:
        Smart Wallet 주소
    """
    # 1. Factory 컨트랙트 인스턴스
    factory = self._get_contract(factory_address, "SmartWalletFactory")
    
    # 2. Salt 생성 (사용자 ID 기반)
    salt = int(hashlib.sha256(user_id.encode()).hexdigest()[:16], 16)
    
    # 3. 주소 계산
    wallet_address = factory.functions.getAddress(
        owner_address,  # 서비스 계정 또는 사용자 주소
        salt
    ).call()
    
    # 4. 배포 (아직 배포되지 않은 경우)
    if self.w3.eth.get_code(wallet_address) == b'':
        tx_hash = factory.functions.createWallet(
            owner_address,
            salt
        ).transact({
            'from': self.service_account,
            'gas': 1000000
        })
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
    
    return wallet_address
```

### 4-2. 사용자별 Smart Wallet 생성

```python
# 사용자 로그인 시
POST /api/v1/auth/wallet/create

# 백엔드에서:
1. 사용자 ID로 salt 생성
2. Factory에서 주소 계산
3. 배포되지 않았다면 배포
4. DB에 주소 저장
```

## 5. 동작 원리

### 5-1. 주소 생성

```
사용자 ID: "user-123"
   ↓
Salt 생성: SHA256("user-123") → 0x1234...
   ↓
Factory.getAddress(owner, salt)
   ↓
CREATE2 계산
   ↓
항상 같은 주소: 0xABCD...
```

### 5-2. 트랜잭션 실행

```
사용자: "티켓 구매" 클릭
   ↓
UserOperation 생성
   ↓
서명 (백엔드 또는 프론트엔드)
   ↓
Bundler로 전송
   ↓
EntryPoint가 SmartWallet.validateUserOp 호출
   ↓
EntryPoint가 SmartWallet.execute 호출
   ↓
EventManager.purchaseTicket 실행
   ↓
완료!
```

## 6. Proxy 패턴

### 왜 Proxy를 사용하나?

**문제:**
- Smart Wallet을 직접 배포하면 가스비가 많이 듦
- 각 사용자마다 컨트랙트를 배포해야 함

**해결:**
- Proxy 패턴 사용
- 구현 컨트랙트는 1개만 배포
- 각 사용자는 가벼운 Proxy만 배포
- 가스비 절약!

**구조:**
```
SmartWallet (구현) - 1개만 배포
   ↑
   | (위임)
   |
Proxy (사용자별) - 가벼운 컨트랙트
```

## 7. 다음 단계

1. ✅ Smart Wallet 컨트랙트 배포 완료
2. ✅ Factory 배포 완료
3. ⏳ 백엔드에서 실제 배포 로직 구현
4. ⏳ 프론트엔드에서 UserOperation 사용

## 8. 테스트

```bash
# 배포 확인
npx hardhat run scripts/deploy_smart_wallet.js --network localhost

# 주소 계산 테스트
npx hardhat console --network localhost
> const factory = await ethers.getContractAt("SmartWalletFactory", "0x...")
> await factory.getAddress("0x...", 12345)
```

