# Vercel 배포 단계별 가이드

## ✅ 준비 사항

- ✅ GitHub 저장소에 코드 푸시 완료
- ✅ Vercel 계정 (GitHub로 로그인)
- ✅ 백엔드 배포 완료 (EC2: 43.201.98.14:8000)

---

## 🚀 Vercel 배포 단계

### 1단계: Vercel 프로젝트 생성

1. **Vercel 접속**
   - https://vercel.com 접속
   - GitHub 계정으로 로그인

2. **새 프로젝트 생성**
   - 대시보드에서 "Add New..." → "Project" 클릭
   - GitHub 저장소 선택
   - "Import" 클릭

3. **프로젝트 설정**
   ```
   Framework Preset: Vite
   Root Directory: frontend
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

---

### 2단계: 환경 변수 설정

**Settings → Environment Variables**에서 다음 변수 추가:

#### 필수 환경 변수

```env
# 백엔드 API URL
VITE_API_URL=http://43.201.98.14:8000

# Polygon RPC URL (Amoy 테스트넷)
VITE_RPC_URL=https://rpc-amoy.polygon.technology
```

#### 스마트 컨트랙트 주소 (테스트넷 배포 후 업데이트)

```env
VITE_TICKET_ACCESS_CONTROL_ADDRESS=0x...
VITE_TICKET_NFT_ADDRESS=0x...
VITE_EVENT_MANAGER_ADDRESS=0x...
VITE_REFUND_MANAGER_ADDRESS=0x...
```

**중요**: 
- 모든 환경 변수는 **Production**, **Preview**, **Development** 모두에 적용
- 또는 Production만 선택해도 됨

---

### 3단계: 배포 실행

1. **"Deploy" 버튼 클릭**
2. **배포 진행 상황 확인**
   - 빌드 로그 확인
   - 에러 발생 시 로그 확인
3. **배포 완료 대기** (약 1-2분)

---

### 4단계: 배포 확인

1. **배포된 URL 확인**
   - 예: `https://your-project.vercel.app`
2. **브라우저에서 접속**
3. **개발자 도구 → Network 탭에서 API 요청 확인**

---

## 🔧 백엔드 CORS 설정 업데이트

프론트엔드가 배포되면 백엔드 CORS 설정을 업데이트해야 합니다.

### EC2에서 실행

```bash
# .env 파일 편집
nano .env

# ALLOWED_ORIGINS에 Vercel URL 추가
ALLOWED_ORIGINS=https://your-project.vercel.app,http://localhost:5173

# 백엔드 재시작
docker-compose -f docker-compose.prod.yml restart backend
```

---

## ✅ 배포 후 확인 사항

### 1. 프론트엔드 접속
- Vercel 배포 URL에서 정상 로드 확인

### 2. API 연결 확인
- 브라우저 개발자 도구 → Console/Network
- CORS 오류가 없어야 함

### 3. 기능 테스트
- [ ] 회원가입
- [ ] 로그인
- [ ] 이벤트 목록 조회
- [ ] 이벤트 생성 (주최자)
- [ ] 티켓 구매
- [ ] 환불/재판매

---

## 🐛 문제 해결

### CORS 오류 발생 시

**증상**: 브라우저 콘솔에 CORS 오류

**해결**:
1. EC2에서 `.env` 파일 확인
2. `ALLOWED_ORIGINS`에 Vercel URL 추가
3. 백엔드 재시작

### API 연결 실패

**확인 사항**:
1. `VITE_API_URL` 환경 변수가 올바른지 확인
2. 백엔드가 실행 중인지 확인: `curl http://43.201.98.14:8000/health`
3. EC2 보안 그룹에서 포트 8000이 열려있는지 확인

### 빌드 실패

**확인 사항**:
1. Vercel 빌드 로그 확인
2. `package.json`의 빌드 스크립트 확인
3. 의존성 설치 오류 확인

---

## 📝 체크리스트

- [ ] Vercel 계정 생성/로그인
- [ ] GitHub 저장소 연결
- [ ] Vercel 프로젝트 생성
- [ ] 프로젝트 설정 (Root Directory: frontend)
- [ ] 환경 변수 설정
- [ ] 배포 실행
- [ ] 배포 완료 확인
- [ ] 백엔드 CORS 설정 업데이트
- [ ] 전체 시스템 테스트

---

## 🎯 완료!

배포가 완료되면:
1. ✅ 프론트엔드: Vercel URL
2. ✅ 백엔드: http://43.201.98.14:8000
3. ✅ 전체 시스템 연동 완료

---

## 📚 참고

- **Vercel 문서**: https://vercel.com/docs
- **Vite 배포**: https://vitejs.dev/guide/static-deploy.html#vercel

