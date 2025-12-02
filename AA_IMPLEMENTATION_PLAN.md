# Account Abstraction 구현 계획

## 현재 상태

- ✅ 아키텍처 설계 완료 (ERC-4337 기반)
- ✅ DB 스키마에 `smart_wallet_address` 필드 존재
- ✅ 백엔드 설정에 `BUNDLER_URL`, `PAYMASTER_URL` 필드 존재
- ❌ Smart Wallet 생성 로직 미구현
- ❌ 프론트엔드 Web3 연결 미구현
- ❌ UserOperation 생성/서명 미구현

## 구현 단계

### 1단계: 기본 Web3 연결 (프론트엔드)
- ethers.js 또는 viem 설치
- Web3 Provider 연결 (로컬 Hardhat 노드)
- 기본 지갑 연결 기능

### 2단계: Account Abstraction 기본 구조
- Smart Wallet 주소 생성 (Deterministic)
- 사용자별 Smart Wallet 관리
- 백엔드에서 Smart Wallet 생성 API

### 3단계: UserOperation 생성 및 서명
- UserOperation 구조 생성
- 서명 로직 구현
- Bundler 연동

### 4단계: Paymaster 연동
- Paymaster 정책 구현
- 가스비 지불 로직
- 핵심 기능만 서비스 부담

## 기술 스택

### 프론트엔드
- **ethers.js v6** 또는 **viem**: Web3 라이브러리
- **@account-abstraction/sdk** (선택): AA SDK (또는 직접 구현)

### 백엔드
- **web3.py**: 이미 설치됨
- **eth-account**: 계정 관리
- **CREATE2**: Deterministic 주소 생성

### 외부 서비스
- **Bundler**: Alchemy, Stackup, 또는 자체 구현
- **Paymaster**: 자체 구현 또는 Pimlico

## 구현 우선순위

1. **프론트엔드 Web3 기본 연결** (지금)
   - ethers.js 설치
   - Provider 연결
   - 기본 지갑 연결 UI

2. **Smart Wallet 생성** (다음)
   - 백엔드에서 Smart Wallet 주소 생성
   - 사용자별 매핑

3. **UserOperation 생성** (그 다음)
   - 트랜잭션을 UserOperation으로 변환
   - 서명 로직

4. **Bundler/Paymaster 연동** (마지막)
   - 외부 서비스 연동
   - 가스비 정책 적용

## 참고 자료

- [ERC-4337 스펙](https://eips.ethereum.org/EIPS/eip-4337)
- [Account Abstraction SDK](https://github.com/account-abstraction)
- [Alchemy AA](https://www.alchemy.com/account-abstraction)
- [Stackup](https://docs.stackup.sh/)

