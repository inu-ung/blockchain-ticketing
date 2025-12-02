# RPC 연결 문제 해결 가이드

## 문제 상황
여러 RPC URL을 시도했지만 연결이 안 되는 경우

## 해결 방법

### 방법 1: Alchemy RPC 사용 (권장)

1. **Alchemy 계정 생성** (무료)
   - https://www.alchemy.com/ 접속
   - 무료 계정 생성

2. **앱 생성**
   - Dashboard → Create App
   - Network: Polygon Mumbai
   - 이름 입력 후 생성

3. **API Key 복사**
   - 생성된 앱 클릭
   - "View Key" 클릭
   - HTTP URL 복사

4. **.env 파일 수정**
   ```
   POLYGON_MUMBAI_RPC_URL=https://polygon-mumbai.g.alchemy.com/v2/YOUR-API-KEY
   ```

### 방법 2: Infura RPC 사용

1. **Infura 계정 생성** (무료)
   - https://infura.io/ 접속
   - 무료 계정 생성

2. **프로젝트 생성**
   - Dashboard → Create New Key
   - Network: Polygon PoS
   - Endpoints: Polygon Mumbai 선택

3. **API Key 복사**
   - 생성된 Endpoint URL 복사

4. **.env 파일 수정**
   ```
   POLYGON_MUMBAI_RPC_URL=https://polygon-mumbai.infura.io/v3/YOUR-PROJECT-ID
   ```

### 방법 3: 로컬 네트워크에서 먼저 테스트

RPC 문제를 우회하고 로컬에서 먼저 테스트:

```bash
# 터미널 1: 로컬 네트워크 실행
npx hardhat node

# 터미널 2: 로컬에 배포
npm run deploy
```

### 방법 4: Public RPC 목록 시도

다음 RPC들을 하나씩 시도:

```env
# 옵션 1
POLYGON_MUMBAI_RPC_URL=https://rpc.ankr.com/polygon_mumbai

# 옵션 2  
POLYGON_MUMBAI_RPC_URL=https://matic-mumbai.chainstacklabs.com

# 옵션 3
POLYGON_MUMBAI_RPC_URL=https://polygon-mumbai-bor.publicnode.com

# 옵션 4
POLYGON_MUMBAI_RPC_URL=https://mumbai.rpc.thirdweb.com
```

## 추천 순서

1. **Alchemy 사용** (가장 안정적)
2. **로컬에서 먼저 테스트** (RPC 문제 우회)
3. **다른 Public RPC 시도**

