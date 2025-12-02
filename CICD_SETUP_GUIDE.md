# CI/CD 설정 가이드

## 📋 설정 단계

### 1단계: GitHub Secrets 설정

GitHub Repository → **Settings** → **Secrets and variables** → **Actions**로 이동

#### 필수 Secrets 추가

1. **DEPLOYER_PRIVATE_KEY**
   - 배포자 지갑의 개인키
   - `0x`로 시작하는 64자리 16진수
   - ⚠️ **절대 공개하지 마세요!**

2. **POLYGON_AMOY_RPC_URL**
   - Polygon Amoy 테스트넷 RPC URL
   - 예: `https://rpc-amoy.polygon.technology`
   - 또는 Alchemy/Infura URL

3. **POLYGON_MAINNET_RPC_URL**
   - Polygon 메인넷 RPC URL
   - 예: `https://polygon-rpc.com`
   - 또는 Alchemy/Infura URL

4. **ENTRY_POINT_ADDRESS**
   - ERC-4337 표준 EntryPoint 주소
   - 기본값: `0x5FF137D4b0FDCD49DcA30c7CF57E578a026d2789`

5. **POLYGONSCAN_API_KEY**
   - Polygonscan API Key (컨트랙트 검증용)
   - https://polygonscan.com/apis 에서 발급

#### Secrets 추가 방법

```
1. GitHub Repository 접속
2. Settings 클릭
3. 왼쪽 메뉴에서 "Secrets and variables" → "Actions" 클릭
4. "New repository secret" 클릭
5. Name과 Value 입력
6. "Add secret" 클릭
```

---

### 2단계: GitHub에 코드 푸시

```bash
# 현재 변경사항 커밋
git add .
git commit -m "Add CI/CD automation"

# GitHub에 푸시
git push origin develop  # 테스트넷 배포
# 또는
git push origin main     # 메인넷 배포
```

---

### 3단계: GitHub Actions 확인

1. GitHub Repository → **Actions** 탭 클릭
2. 워크플로우 실행 확인
3. 각 단계별 로그 확인

---

## 🚀 자동 배포 트리거

### 자동 실행

- **develop 브랜치에 Push** → Polygon Amoy (테스트넷) 배포
- **main 브랜치에 Push** → Polygon Mainnet 배포
- **Pull Request 생성** → 테스트만 실행 (배포 안 함)

### 수동 실행

1. GitHub Repository → **Actions** 탭
2. 왼쪽에서 **"Deploy Smart Contracts"** 선택
3. **"Run workflow"** 클릭
4. 네트워크 선택 (amoy/polygon)
5. **"Run workflow"** 버튼 클릭

---

## 📝 배포 프로세스 확인

### GitHub Actions에서 확인할 수 있는 단계

1. ✅ **Checkout code** - 코드 체크아웃
2. ✅ **Setup Node.js** - Node.js 환경 설정
3. ✅ **Install dependencies** - 의존성 설치
4. ✅ **Run tests** - 테스트 실행
5. ✅ **Compile contracts** - 컨트랙트 컴파일
6. ✅ **Deploy to network** - 네트워크에 배포
7. ✅ **Verify contracts** - Polygonscan 검증
8. ✅ **Upload deployment artifacts** - 배포 정보 저장

---

## 🔍 배포 결과 확인

### 1. GitHub Actions 로그

```
Actions 탭 → 최근 워크플로우 실행 클릭
→ 각 단계별 로그 확인
```

### 2. 배포 정보 파일

배포 완료 후 **Artifacts**에서 다운로드:
- `deployment-amoy-{commit-hash}.json`
- `deployment-summary-amoy.md`

### 3. Polygonscan 확인

배포된 컨트랙트 주소로 검색:
- Amoy: https://amoy.polygonscan.com/
- Mainnet: https://polygonscan.com/

---

## ⚙️ 로컬에서 테스트

### CI/CD 워크플로우 테스트 (로컬)

```bash
cd contracts

# 테스트 실행
npm test

# 컴파일
npm run compile

# 수동 배포 (테스트)
npm run deploy:amoy
```

---

## 🛠️ 트러블슈팅

### 배포 실패 시

#### 1. Secrets 확인
- 모든 필수 Secrets가 설정되었는지 확인
- Secrets 이름이 정확한지 확인 (대소문자 구분)

#### 2. 잔액 확인
- 배포자 계정에 충분한 MATIC/ETH가 있는지 확인
- 테스트넷: https://faucet.polygon.technology/

#### 3. RPC 연결 확인
- RPC URL이 올바른지 확인
- 네트워크 상태 확인

#### 4. 로그 확인
- GitHub Actions 로그에서 정확한 오류 메시지 확인
- 각 단계별 실패 지점 확인

---

## 📊 배포 전략

### 브랜치별 배포

```
develop 브랜치
  ↓ Push
  → 자동 배포 → Polygon Amoy (테스트넷)
  
main 브랜치
  ↓ Push
  → 자동 배포 → Polygon Mainnet
```

### Pull Request

```
feature/* 브랜치
  ↓ Pull Request 생성
  → 테스트만 실행 (배포 안 함)
  → 모든 테스트 통과 확인 후 Merge
```

---

## ✅ 설정 체크리스트

배포 전 확인사항:

- [ ] GitHub Secrets 모두 설정 완료
  - [ ] DEPLOYER_PRIVATE_KEY
  - [ ] POLYGON_AMOY_RPC_URL
  - [ ] POLYGON_MAINNET_RPC_URL
  - [ ] ENTRY_POINT_ADDRESS
  - [ ] POLYGONSCAN_API_KEY
- [ ] 배포자 계정에 충분한 잔액
- [ ] 로컬에서 테스트 통과
- [ ] 코드가 GitHub에 푸시됨

---

## 🎯 빠른 시작

### 1. Secrets 설정 (5분)

```
GitHub → Settings → Secrets → Actions
→ 5개 Secrets 추가
```

### 2. 코드 푸시 (1분)

```bash
git push origin develop
```

### 3. 배포 확인 (2분)

```
GitHub → Actions 탭
→ 워크플로우 실행 확인
→ 배포 완료 대기
```

### 4. 결과 확인 (1분)

```
Artifacts에서 배포 정보 다운로드
Polygonscan에서 컨트랙트 확인
```

**총 소요 시간: 약 10분**

---

## 📞 추가 도움말

### 자세한 내용

- 자동 배포 상세: `AUTOMATED_DEPLOYMENT.md`
- 배포 옵션: `DEPLOYMENT_OPTIONS.md`
- 테스트넷 배포: `TESTNET_DEPLOYMENT_GUIDE.md`

### 문제 발생 시

1. GitHub Actions 로그 확인
2. 로컬에서 동일한 명령어 실행하여 오류 재현
3. Secrets 및 환경 변수 재확인

