# 프론트엔드 기술 명세 - 멍이랑 (withbowwow)

> 백엔드 코어 파일: [../backend/00_overview.md](../backend/00_overview.md)
> 프론트엔드 담당자 참고용 기술 스펙

---

## 1. 기술 스택

| 항목 | 선택 | 버전 | 비고 |
|------|------|------|------|
| **Framework** | React Native | 0.76+ | Expo 관리형 |
| **Toolchain** | Expo SDK | 52 | Managed Workflow |
| **Language** | TypeScript | 5.x | Strict mode |
| **Navigation** | React Navigation | v7 | Bottom Tabs + Stack |
| **State** | Zustand | 5.x | 경량 전역 상태 관리 |
| **Styling** | NativeWind | v4 | Tailwind CSS for RN |
| **HTTP Client** | axios 또는 fetch | - | FastAPI Swagger 기반 |
| **Map** | react-native-maps | - | Google Maps (Android) + Apple Maps (iOS) |
| **Location** | expo-location | - | GPS 추적 |
| **Camera** | expo-image-picker | - | 사진 촬영/선택 |
| **Push** | expo-notifications | - | FCM + APNs |
| **Secure Storage** | expo-secure-store | - | JWT 토큰 저장 |
| **Animation** | react-native-reanimated | v3 | 뱃지 획득 애니메이션 등 |

---

## 2. 프로젝트 구조

```
app/
├── (tabs)/                    # Bottom Tab Navigator
│   ├── home.tsx               # 탭1: 홈 (오늘의 산책, 날씨)
│   ├── social.tsx             # 탭2: 소셜 (피드, 초대, 모임)
│   ├── walk.tsx               # 탭3: 산책 (GPS 추적, 지도)
│   ├── ranking.tsx            # 탭4: 랭킹
│   └── mypage.tsx             # 탭5: 마이페이지
│
├── auth/                      # 인증 스크린
│   ├── login.tsx
│   └── onboarding.tsx
│
├── walk/                      # 산책 관련 스크린
│   ├── tracking.tsx           # 산책 중 GPS 추적
│   ├── complete.tsx           # 산책 완료 리포트
│   └── detail.tsx             # 산책 상세
│
├── badge/                     # 뱃지 스크린
│   ├── list.tsx
│   └── detail.tsx
│
├── components/                # 재사용 컴포넌트
│   ├── ui/                    # 기본 UI (Button, Card, Modal)
│   ├── walk/                  # 산책 관련 컴포넌트
│   ├── badge/                 # 뱃지 카드, 진행률 바
│   └── social/                # 피드 카드, 댓글
│
├── hooks/                     # 커스텀 훅
│   ├── useAuth.ts
│   ├── useWalk.ts
│   ├── useLocation.ts
│   └── usePushNotification.ts
│
├── stores/                    # Zustand 스토어
│   ├── authStore.ts
│   ├── walkStore.ts
│   └── settingsStore.ts
│
├── services/                  # API 호출
│   ├── api.ts                 # axios 인스턴스 (baseURL, 인터셉터)
│   ├── authApi.ts
│   ├── walkApi.ts
│   ├── badgeApi.ts
│   ├── rankingApi.ts
│   ├── socialApi.ts
│   └── weatherApi.ts
│
├── utils/                     # 유틸리티
│   ├── geo.ts                 # GPS 거리 계산
│   ├── format.ts              # 날짜/숫자 포맷
│   └── constants.ts
│
└── types/                     # TypeScript 타입 정의
    ├── user.ts
    ├── pet.ts
    ├── walk.ts
    ├── badge.ts
    └── api.ts
```

---

## 3. 백엔드 연동

### 3.1 API Base URL

```typescript
// services/api.ts
const api = axios.create({
  baseURL: process.env.EXPO_PUBLIC_API_URL,  // https://withbowwow-api.onrender.com
  timeout: 10000,
});

// JWT 인터셉터
api.interceptors.request.use((config) => {
  const token = await SecureStore.getItemAsync('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 401 시 토큰 갱신
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const newTokens = await refreshToken();
      // 재시도
    }
    return Promise.reject(error);
  }
);
```

### 3.2 API 문서 참조

백엔드 Swagger UI에서 전체 API 명세 확인:
```
GET {API_BASE_URL}/docs
```

### 3.3 주요 API 엔드포인트

| 기능 | Method | Path | 설명 |
|------|--------|------|------|
| 로그인 | POST | /auth/kakao | 카카오 로그인 |
| 토큰 갱신 | POST | /auth/refresh | 리프레시 토큰 |
| 내 프로필 | GET | /users/me | 사용자 정보 |
| 반려동물 | GET/POST | /pets | CRUD |
| 산책 시작 | POST | /walks | 산책 생성 |
| 산책 완료 | POST | /walks/{id}/complete | 산책 완료 처리 |
| 뱃지 목록 | GET | /badges | 진행률 포함 |
| 랭킹 | GET | /rankings | 기간/지역 필터 |
| 피드 | GET | /feed | 소셜 피드 |
| 날씨 | GET | /weather | 날씨/미세먼지 |
| 파일 업로드 | POST | /upload/image | 사진 업로드 |

---

## 4. 주요 기능별 구현 포인트

### 4.1 산책 GPS 추적

```
expo-location으로 백그라운드 GPS 추적:
- 위치 업데이트 간격: 5초
- 정확도: High Accuracy
- 백그라운드 추적: expo-task-manager 사용
- 경로: GeoJSON LineString으로 저장
- 배터리 최적화: 거리 변화 없으면 업데이트 스킵
```

### 4.2 소셜 로그인 (클라이언트)

```
카카오/네이버: expo-auth-session 또는 react-native-kakao-login 등 SDK
Apple: expo-apple-authentication

플로우:
1. 클라이언트에서 SDK로 authorization_code 획득
2. code를 서버 POST /auth/{provider}로 전송
3. 서버에서 토큰 교환 + JWT 반환
4. JWT를 expo-secure-store에 저장
```

### 4.3 푸시 알림

```
expo-notifications 사용:
1. 앱 시작 시 권한 요청 → 토큰 발급
2. POST /push-tokens로 서버에 토큰 등록
3. 산책 리마인더: 로컬 알림 (expo-notifications 스케줄링)
4. 서버 푸시: FCM/APNs → 딥링크 처리
```

### 4.4 함께 산책 WebSocket

```
산책 초대 수락 후:
1. WebSocket 연결: ws://{API_URL}/ws/walk-together/{invitation_id}?token={jwt}
2. 5초 간격으로 내 위치 전송: {"lat": 37.5, "lng": 127.0, "timestamp": ...}
3. 상대방 위치 수신 → 지도에 마커 표시
4. 산책 종료 시 WebSocket 해제
```

---

## 5. 디자인 시스템

### 5.1 컬러 팔레트

| 용도 | 색상 | Hex |
|------|------|-----|
| Primary | 따뜻한 오렌지 | #FF6B35 |
| Secondary | 하늘색 | #4ECDC4 |
| Background | 밝은 크림 | #FFF8F0 |
| Text Primary | 짙은 갈색 | #2D1B0E |
| Success | 초록 | #10B981 |
| Warning | 노랑 | #F59E0B |
| Error | 빨강 | #EF4444 |

### 5.2 타이포그래피

| 용도 | 폰트 | 크기 |
|------|------|------|
| 제목 | Pretendard Bold | 24px |
| 소제목 | Pretendard SemiBold | 18px |
| 본문 | Pretendard Regular | 16px |
| 캡션 | Pretendard Regular | 14px |
| 숫자 (통계) | Pretendard Bold | 32px |

---

## 6. 화면 구성 (5개 탭)

| 탭 | 화면 | 핵심 기능 |
|----|------|----------|
| **홈** | 대시보드 | 오늘의 산책 현황, 주간 목표 진행률, 날씨/미세먼지, 최근 뱃지 |
| **소셜** | 피드 | 팔로잉 산책 기록, 좋아요/댓글, 산책 초대, 모임 게시판 |
| **산책** | 시작 버튼 | GPS 추적, 실시간 거리/시간/칼로리, 사진 촬영, 산책 완료 리포트 |
| **랭킹** | 리더보드 | 주간/월간/전체 랭킹, 동/구/전국 필터, 명예의 전당 |
| **마이** | 프로필 | 반려동물 관리, 산책 통계, 뱃지 컬렉션, 설정, 프리미엄 |

---

## 7. 환경 변수 (프론트)

```
EXPO_PUBLIC_API_URL=https://withbowwow-api.onrender.com
EXPO_PUBLIC_KAKAO_APP_KEY=
EXPO_PUBLIC_NAVER_CLIENT_ID=
EXPO_PUBLIC_GOOGLE_MAPS_KEY=
```

---

*작성일: 2026-02-12*
*버전: 1.0*
