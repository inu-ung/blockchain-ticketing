# GitHub 저장소 생성 및 푸시 가이드

## 📋 사전 준비

- ✅ GitHub 계정
- ✅ Git 설치 확인

---

## 🚀 GitHub 저장소 생성 및 푸시

### 1단계: GitHub에서 저장소 생성

1. **GitHub 접속**
   - https://github.com 접속
   - 로그인

2. **새 저장소 생성**
   - 우측 상단 "+" → "New repository" 클릭
   - 저장소 정보 입력:
     - **Repository name**: `blockchain-ticketing` (원하는 이름)
     - **Description**: `Polygon 기반 NFT 티켓팅 시스템`
     - **Visibility**: Public 또는 Private 선택
     - **Initialize this repository with**: 체크하지 않음 (로컬에서 푸시할 예정)
   - "Create repository" 클릭

3. **저장소 URL 확인**
   - 예: `https://github.com/your-username/blockchain-ticketing.git`

---

### 2단계: 로컬 Git 초기화 및 커밋

#### Git 상태 확인

```bash
cd ~/blockchain/BC
git status
```

#### Git 초기화 (아직 안 되어있다면)

```bash
# Git 초기화
git init

# 기본 브랜치 이름 설정
git branch -M main
```

#### .gitignore 확인

`.gitignore` 파일이 있는지 확인하고, 다음 항목이 포함되어 있는지 확인:

```
# 환경 변수 파일
.env
.env.local
.env.production

# 의존성
node_modules/
__pycache__/
*.pyc
*.pyo

# 빌드 결과
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# 로그
*.log

# OS
.DS_Store
Thumbs.db

# Docker
*.tar.gz

# 키 파일
*.pem
*.key
```

#### 변경사항 추가 및 커밋

```bash
# 모든 파일 추가
git add .

# 커밋
git commit -m "Initial commit: Blockchain Ticketing System"

# 또는 단계별 커밋
git add backend/
git commit -m "Add backend: FastAPI + PostgreSQL + Docker"

git add frontend/
git commit -m "Add frontend: React + Vite + TypeScript"

git add contracts/
git commit -m "Add smart contracts: Solidity + Hardhat"
```

---

### 3단계: GitHub에 푸시

#### 원격 저장소 추가

```bash
# GitHub 저장소 URL 사용 (실제 URL로 변경)
git remote add origin https://github.com/your-username/blockchain-ticketing.git

# 또는 SSH 사용
git remote add origin git@github.com:your-username/blockchain-ticketing.git
```

#### 푸시

```bash
# 메인 브랜치 푸시
git push -u origin main
```

**인증 필요 시:**
- Personal Access Token 사용 (HTTPS)
- 또는 SSH 키 설정 (SSH)

---

## 🔐 GitHub 인증 설정

### 방법 1: Personal Access Token (HTTPS)

1. **토큰 생성**
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - "Generate new token" 클릭
   - 권한 선택: `repo` (전체 저장소 접근)
   - 토큰 생성 및 복사

2. **푸시 시 사용**
   ```bash
   # 사용자 이름: GitHub 사용자 이름
   # 비밀번호: Personal Access Token
   git push -u origin main
   ```

### 방법 2: SSH 키 설정

1. **SSH 키 생성** (아직 없다면)
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```

2. **SSH 키 복사**
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

3. **GitHub에 추가**
   - GitHub → Settings → SSH and GPG keys
   - "New SSH key" 클릭
   - 키 추가

4. **SSH로 원격 저장소 설정**
   ```bash
   git remote set-url origin git@github.com:your-username/blockchain-ticketing.git
   ```

---

## ✅ 확인

### 저장소 확인

```bash
# 원격 저장소 확인
git remote -v

# 브랜치 확인
git branch -a

# 최근 커밋 확인
git log --oneline -5
```

### GitHub에서 확인

- GitHub 저장소 페이지에서 파일들이 보이는지 확인
- 커밋 히스토리 확인

---

## 🚨 주의사항

### .env 파일은 절대 커밋하지 마세요!

```bash
# .gitignore에 포함되어 있는지 확인
cat .gitignore | grep "\.env"

# 이미 커밋된 경우 제거
git rm --cached backend/.env
git rm --cached frontend/.env
git commit -m "Remove .env files from git"
```

### 민감한 정보 확인

다음 파일들이 커밋되지 않았는지 확인:
- `*.pem` (키 파일)
- `.env` (환경 변수)
- `node_modules/` (의존성)
- `dist/` (빌드 결과)

---

## 📝 체크리스트

- [ ] GitHub 저장소 생성
- [ ] 로컬 Git 초기화 (필요시)
- [ ] .gitignore 확인
- [ ] 파일 커밋
- [ ] GitHub 인증 설정
- [ ] 원격 저장소 추가
- [ ] 푸시 완료
- [ ] GitHub에서 확인

---

## 🎯 다음 단계

GitHub 저장소 생성 및 푸시 완료 후:

1. ✅ Vercel 배포 진행
2. ✅ Vercel에서 GitHub 저장소 연결
3. ✅ 자동 배포 설정

---

## 💡 유용한 명령어

```bash
# Git 상태 확인
git status

# 변경사항 확인
git diff

# 커밋 히스토리
git log --oneline

# 원격 저장소 확인
git remote -v

# 브랜치 확인
git branch -a
```

