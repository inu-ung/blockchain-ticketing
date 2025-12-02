# 아키텍처 다이어그램 추가 제안

## 현재 포함된 것들 ✅
- Users → Browser
- GitHub → GitHub Actions → EC2
- EC2 (Docker)
  - NGINX (Reverse Proxy)
  - React (Frontend)
  - FastAPI (Backend)
  - PostgreSQL (Database)
- IPFS
- Hardhat

---

## 추가할 만한 것들

### 1. 블록체인 계층 (필수)

#### Polygon 블록체인
- **위치**: FastAPI → Polygon Blockchain
- **역할**: 실제 스마트 컨트랙트가 배포되는 블록체인
- **참고**: Hardhat은 개발 도구, Polygon은 실제 네트워크

#### 스마트 컨트랙트들 (Polygon 위에)
- **EventManager**: 이벤트 관리
- **TicketNFT**: NFT 티켓 발행
- **TicketMarketplace**: 재판매 마켓플레이스
- **RefundManager**: 환불 관리
- **SmartWallet**: 사용자 Smart Wallet
- **SmartWalletFactory**: Smart Wallet 생성
- **EntryPoint**: ERC-4337 표준 EntryPoint

**표시 방법**:
```
Polygon Blockchain
  ├── EventManager
  ├── TicketNFT
  ├── TicketMarketplace
  ├── RefundManager
  ├── SmartWallet
  ├── SmartWalletFactory
  └── EntryPoint (ERC-4337)
```

---

### 2. Account Abstraction 계층 (중요)

#### Bundler
- **위치**: FastAPI → Bundler → EntryPoint
- **역할**: UserOperation을 번들링하여 블록체인에 제출
- **표시**: FastAPI와 EntryPoint 사이

#### Paymaster
- **위치**: FastAPI → Paymaster → EntryPoint
- **역할**: 가스비 스폰서
- **표시**: FastAPI와 EntryPoint 사이 (Bundler 옆)

---

### 3. IPFS 서비스 명시

#### Pinata
- **위치**: FastAPI → Pinata (IPFS)
- **역할**: IPFS 게이트웨이 서비스
- **표시**: IPFS 대신 "IPFS (Pinata)" 또는 별도로 표시

---

### 4. 추가 연결 관계

#### FastAPI → 스마트 컨트랙트
- FastAPI → Polygon Blockchain (스마트 컨트랙트 호출)
- FastAPI → EntryPoint (UserOperation 전송)
- FastAPI → Bundler (UserOperation 전송)
- FastAPI → Paymaster (가스비 스폰서 요청)

#### React → IPFS
- React → IPFS (메타데이터 조회) - 이미 있음 ✅

#### React → Polygon (선택사항)
- React → Polygon Blockchain (직접 조회하는 경우)

---

## 권장 다이어그램 구조

```
Users
  ↓
Browser
  ↓
NGINX (EC2/Docker)
  ├── React (Frontend)
  └── FastAPI (Backend)
      ├── PostgreSQL
      ├── IPFS (Pinata)
      ├── Bundler
      ├── Paymaster
      └── Polygon Blockchain
          ├── EntryPoint
          ├── SmartWalletFactory
          ├── EventManager
          ├── TicketNFT
          ├── TicketMarketplace
          └── RefundManager

GitHub → GitHub Actions → EC2
Hardhat (로컬 개발용)
```

---

## 추가 제안 (선택사항)

### 1. 모니터링/로깅
- **Grafana/Prometheus**: 시스템 모니터링
- **로그 수집**: CloudWatch, ELK Stack 등

### 2. 캐싱
- **Redis**: 세션 관리, 캐싱 (선택사항)

### 3. 메시지 큐
- **RabbitMQ/Celery**: 비동기 작업 처리 (선택사항)

### 4. CDN
- **CloudFront/Cloudflare**: 정적 파일 배포 (선택사항)

---

## 핵심 추가 사항 (필수)

1. **Polygon Blockchain** - 실제 블록체인 네트워크
2. **스마트 컨트랙트들** - EventManager, TicketNFT 등
3. **EntryPoint** - ERC-4337 표준
4. **Bundler** - UserOperation 번들링
5. **Paymaster** - 가스비 스폰서
6. **Pinata** - IPFS 서비스 명시

---

## 간단 버전 (핵심만)

현재 다이어그램에 추가:
- **Polygon Blockchain** (Hardhat 옆 또는 대체)
- **스마트 컨트랙트 박스** (EventManager, TicketNFT 등)
- **EntryPoint** (ERC-4337)
- **Bundler** (FastAPI와 EntryPoint 사이)
- **Paymaster** (FastAPI와 EntryPoint 사이)

