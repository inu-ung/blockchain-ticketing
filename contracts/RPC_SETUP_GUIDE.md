# RPC 설정 가이드

Polygon Mumbai 테스트넷 배포를 위한 RPC 엔드포인트 설정 방법

## 문제 해결

연결 타임아웃이나 연결 오류가 발생하는 경우, 더 안정적인 RPC 제공자를 사용하세요.

## 추천 RPC 제공자

### 1. Alchemy (가장 안정적, 무료)

**장점:**
- 매우 안정적
- 무료 티어 제공 (월 300M 요청)
- 빠른 응답 속도

**설정 방법:**

1. **Alchemy 계정 생성**
   - https://www.alchemy.com/ 접속
   - "Sign Up" 클릭하여 계정 생성

2. **앱 생성**
   - 대시보드에서 "Create App" 클릭
   - App Name: `Ticket System` (임의)
   - Chain: `Polygon`
   - Network: `Polygon Mumbai`
   - "Create App" 클릭

3. **API 키 복사**
   - 생성된 앱 클릭
   - "View Key" 버튼 클릭
   - HTTP URL 복사 (예: `https://polygon-mumbai.g.alchemy.com/v2/xxxxxxxxxxxxx`)

4. **.env 파일 업데이트**
   ```env
   POLYGON_MUMBAI_RPC_URL=https://polygon-mumbai.g.alchemy.com/v2/YOUR-API-KEY
   ```

### 2. Infura (안정적, 무료)

**장점:**
- 안정적
- 무료 티어 제공
- 널리 사용됨

**설정 방법:**

1. **Infura 계정 생성**
   - https://infura.io/ 접속
   - "Get Started" 클릭하여 계정 생성

2. **프로젝트 생성**
   - 대시보드에서 "Create New Key" 클릭
   - Key Name: `Ticket System` (임의)
   - Network: `Polygon Mumbai` 선택
   - "Create" 클릭

3. **API 키 복사**
   - 생성된 프로젝트에서 "Endpoint" URL 복사
   - 예: `https://polygon-mumbai.infura.io/v3/xxxxxxxxxxxxx`

4. **.env 파일 업데이트**
   ```env
   POLYGON_MUMBAI_RPC_URL=https://polygon-mumbai.infura.io/v3/YOUR-PROJECT-ID
   ```

### 3. QuickNode (무료, API 키 불필요)

**장점:**
- 무료
- API 키 불필요
- 빠른 설정

**설정 방법:**

1. **.env 파일 업데이트**
   ```env
   POLYGON_MUMBAI_RPC_URL=https://polygon-mumbai.gateway.tenderly.co
   ```

   또는 QuickNode 엔드포인트:
   ```env
   POLYGON_MUMBAI_RPC_URL=https://rpc.ankr.com/polygon_mumbai
   ```

## 현재 사용 가능한 무료 RPC (API 키 불필요)

다음 RPC URL들을 시도해볼 수 있습니다:

```env
# Option 1: Chainstack
POLYGON_MUMBAI_RPC_URL=https://matic-mumbai.chainstacklabs.com

# Option 2: Ankr
POLYGON_MUMBAI_RPC_URL=https://rpc.ankr.com/polygon_mumbai

# Option 3: Public RPC
POLYGON_MUMBAI_RPC_URL=https://rpc-mumbai.maticvigil.com
```

## RPC 연결 테스트

RPC가 작동하는지 테스트하려면:

```bash
curl -X POST -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}' \
  YOUR_RPC_URL
```

정상 응답 예시:
```json
{"jsonrpc":"2.0","id":1,"result":"0x123456"}
```

## 문제 해결

### 연결 타임아웃

1. **인터넷 연결 확인**
   ```bash
   ping google.com
   ```

2. **방화벽 확인**
   - 방화벽이 RPC 연결을 차단하는지 확인
   - 회사/학교 네트워크인 경우 관리자에게 문의

3. **VPN 확인**
   - VPN 사용 중이면 해제 후 재시도
   - 일부 VPN은 RPC 연결을 차단할 수 있음

4. **다른 RPC 제공자 시도**
   - Alchemy 또는 Infura 사용 (더 안정적)

### DNS 오류

1. **DNS 서버 변경**
   - Google DNS: `8.8.8.8`, `8.8.4.4`
   - Cloudflare DNS: `1.1.1.1`, `1.0.0.1`

2. **다른 RPC URL 시도**

## 권장 사항

**프로덕션 환경:**
- Alchemy 또는 Infura 사용 (안정성 중요)

**개발/테스트 환경:**
- 무료 RPC 사용 가능
- 문제 발생 시 Alchemy/Infura로 전환

## .env 파일 예시

```env
# RPC URL (Alchemy 권장)
POLYGON_MUMBAI_RPC_URL=https://polygon-mumbai.g.alchemy.com/v2/YOUR-API-KEY

# 또는 Infura
# POLYGON_MUMBAI_RPC_URL=https://polygon-mumbai.infura.io/v3/YOUR-PROJECT-ID

# 배포 계정 개인키
PRIVATE_KEY=your-private-key-here

# Polygonscan API 키 (컨트랙트 검증용, 선택사항)
POLYGONSCAN_API_KEY=your-api-key

# EntryPoint 주소 (ERC-4337 표준)
ENTRY_POINT_ADDRESS=0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789
```

