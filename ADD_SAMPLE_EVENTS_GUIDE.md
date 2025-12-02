# 샘플 이벤트 데이터 추가 가이드

## 📋 개요

티켓 구입 페이지에 실제 의미 있는 콘서트 데이터를 추가하는 방법입니다.

## 🎯 추가되는 이벤트

1. **BIGBANG 2024 WORLD TOUR - SEOUL**
   - 가격: 150 USDC
   - 일정: 2024년 8월 15일
   - 티켓 수: 5,000매

2. **BLACKPINK BORN PINK WORLD TOUR - SEOUL**
   - 가격: 180 USDC
   - 일정: 2024년 9월 20일
   - 티켓 수: 8,000매

3. **BTS SUGA | Agust D TOUR - SEOUL**
   - 가격: 200 USDC
   - 일정: 2024년 10월 5일
   - 티켓 수: 3,000매

4. **IU 2024 CONCERT - THE GOLDEN HOUR**
   - 가격: 120 USDC
   - 일정: 2024년 11월 10일
   - 티켓 수: 6,000매

5. **NewJeans 2024 FAN MEETING - SEOUL**
   - 가격: 100 USDC
   - 일정: 2024년 12월 25일
   - 티켓 수: 4,000매

---

## 🚀 실행 방법

### 1. 백엔드 가상환경 활성화

```bash
cd backend
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. 샘플 이벤트 추가 스크립트 실행

```bash
python scripts/add_sample_events.py
```

### 3. 결과 확인

성공 시 다음과 같은 출력이 표시됩니다:

```
============================================================
샘플 이벤트 데이터 추가
============================================================
✅ 주최자로 사용: organizer@example.com (ID: ...)
✅ 이벤트 추가: BIGBANG 2024 WORLD TOUR - SEOUL
✅ 이벤트 추가: BLACKPINK BORN PINK WORLD TOUR - SEOUL
✅ 이벤트 추가: BTS SUGA | Agust D TOUR - SEOUL
✅ 이벤트 추가: IU 2024 CONCERT - THE GOLDEN HOUR
✅ 이벤트 추가: NewJeans 2024 FAN MEETING - SEOUL

🎉 총 5개의 샘플 이벤트가 추가되었습니다!
```

---

## 📝 주의사항

1. **주최자 계정 필요**
   - 주최자(organizer) 또는 관리자(admin) 계정이 있어야 합니다
   - 없으면 첫 번째 사용자를 주최자로 사용합니다

2. **중복 방지**
   - 같은 이름의 이벤트가 이미 있으면 건너뜁니다
   - 다시 실행해도 안전합니다

3. **이벤트 상태**
   - 모든 이벤트는 **APPROVED** 상태로 생성됩니다
   - 바로 티켓 구매가 가능합니다

---

## 🔄 이벤트 수정

샘플 이벤트를 수정하려면:

1. `backend/scripts/add_sample_events.py` 파일 열기
2. `SAMPLE_EVENTS` 배열 수정
3. 스크립트 다시 실행

---

## ✅ 확인 방법

1. 프론트엔드에서 **티켓 구입** 페이지 접속
2. 이벤트 목록에 샘플 이벤트들이 표시되는지 확인
3. 각 이벤트 클릭하여 상세 정보 확인

---

## 🎫 다음 단계

샘플 이벤트 추가 후:

1. ✅ 티켓 구매 테스트
2. ✅ 환불 기능 테스트
3. ✅ 재판매 기능 테스트

