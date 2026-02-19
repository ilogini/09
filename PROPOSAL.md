# 🐾 멍이랑 (withbowwow) 앱 기획서

> 반려동물과 함께하는 산책을 게이미피케이션으로 즐겁게!
> "나이키 런 클럽"처럼 산책을 기록하고, 다른 보호자들과 경쟁하세요.

---

## 1. 프로젝트 개요

### 1.1 배경

- 국내 반려동물 양육 가구 약 600만 (2025년 기준)
- 매일 반복되는 산책을 "게임"으로 전환하여 동기부여
- 반려동물 산책 전용 트래킹 앱의 국내 시장 부재
- Nike Run Club의 검증된 소셜 경쟁 모델을 반려동물 산책에 적용

### 1.2 핵심 컨셉

| 키워드 | 설명 |
|--------|------|
| **Track** | GPS 기반 산책 경로, 거리, 시간 실시간 기록 |
| **Compete** | 소셜 리더보드, 통합 뱃지 시스템 (Apple Fitness/Pikmin 스타일) |
| **Connect** | 동네 산책 친구 찾기, 산책 코스 공유 |

### 1.3 타겟 사용자

| 페르소나 | 연령 | 특징 |
|---------|------|------|
| 🐕 열혈 산책러 | 20-30대 | 매일 1시간 이상 산책, 기록 좋아함 |
| 🐾 건강 챙기미 | 30-40대 | 반려동물 건강관리 관심, 데이터 중시 |
| 🏆 경쟁 러버 | 20-30대 | 랭킹, 뱃지 수집에 동기부여되는 유형 |

---

## 2. 수익 모델

### 2.1 광고 수익

| 광고 유형 | 위치 | 예상 단가 |
|----------|------|----------|
| 카카오 AdFit 배너 | 홈 피드 사이사이 | CPM 1,000~3,000원 |
| 네이티브 광고 | 산책 완료 화면 | CPC 100~300원 |
| 리워드 광고 | 포인트 충전 시 | 건당 50~200원 |
| 지도 내 스폰서 핀 | 산책 지도 위 | 월정액 B2B |

### 2.2 프리미엄 구독 (월 3,900원)

| 무료 | 프리미엄 |
|------|---------|
| 기본 산책 기록 | 상세 통계 & 리포트 |
| 주간 리더보드 | 실시간 리더보드 + 지역별 |
| 기본 뱃지만 | 프리미엄 전용 뱃지 + 무제한 |
| 광고 노출 | 광고 제거 |
| - | 커스텀 산책 코스 생성 |
| - | 반려동물 건강 리포트 |

### 2.3 인앱 결제

| 아이템 | 가격 | 설명 |
|--------|------|------|
| 프로필 뱃지 팩 | 1,000원 | 특별 뱃지 5종 |
| 산책 테마 | 2,000원 | 지도 테마 변경 |
| 펫 의상 | 500~1,500원 | 프로필 펫 꾸미기 |

### 2.4 결제 연동

```
PG사: 토스페이먼츠 (Toss Payments)
- 카드 결제, 카카오페이, 네이버페이
- 앱 내 결제: iOS IAP / Google Play Billing
- 정기결제(빌링키) 지원
```

---

## 3. 앱 화면 구조

> 각 화면의 세부 콘텐츠 구성, 배치 이유, UX 설계 의도는 `reference/` 폴더의 개별 기획문서를 참조합니다.
> HTML 목업은 `prototype/` 폴더에서 확인할 수 있습니다.

### 3.1 탭 네비게이션 (하단 5탭)

| 탭 | 화면명 | 핵심 기능 | 상세 기획 | 목업 |
|---|---|---|---|---|
| Tab 1 | 🏠 홈 | 날씨, 주간 요약, 최근 산책, 진행 중 뱃지, 주변 추천 코스 | [reference/메인페이지.md](reference/메인페이지.md) | [prototype/멍이랑_메인페이지_시안.html](prototype/멍이랑_메인페이지_시안.html) |
| Tab 2 | 👥 소셜 | 산책 친구 추천, 피드, 초대, 모임 게시판 | [reference/탭2_소셜.md](reference/탭2_소셜.md) | [prototype/소셜.html](prototype/소셜.html) |
| Tab 3 | 🐾 산책 | GPS 트래킹, 실시간 지도, 타이머, 완료 요약 | [reference/탭3_산책.md](reference/탭3_산책.md) | 메인페이지 내 오버레이 |
| Tab 4 | 🗺️ 지도 | 주변 반려동물 친화 장소 탐색 (상점, 공원, 동물병원, 약국, 카페) | [reference/탭4_지도.md](reference/탭4_지도.md) | [prototype/지도탭.html](prototype/지도탭.html) |
| Tab 5 | 👤 마이페이지 | 펫 프로필, 산책기록, 통합 뱃지 컬렉션, 설정 | [reference/탭5_마이페이지.md](reference/탭5_마이페이지.md) | [prototype/마이페이지.html](prototype/마이페이지.html) |

### 3.2 추가 스크린 (탭 외 푸시 네비게이션)

| 스크린 | 진입 경로 | 핵심 기능 | 상세 기획 | 목업 |
|---|---|---|---|---|
| 🏅 뱃지 컬렉션 | 홈/마이페이지 → 전체보기 | 6개 카테고리 뱃지 그리드, 진행률, 획득 현황 | [reference/추가_뱃지컬렉션.md](reference/추가_뱃지컬렉션.md) | [prototype/뱃지.html](prototype/뱃지.html) |
| 🗺️ 지도 | 홈 → 지도보기 | 전체 지도, 장소 핀, 산책 코스, 바텀시트 | [reference/추가_지도.md](reference/추가_지도.md) | [prototype/지도.html](prototype/지도.html) |
| 📊 산책 상세 | 마이페이지 → 기록 선택 | 경로 지도, 통계, 속도 그래프, 사진, 공유 | [reference/추가_산책상세.md](reference/추가_산책상세.md) | [prototype/산책상세.html](prototype/산책상세.html) |
| 🔔 알림 | 헤더 → 벨 아이콘 | 뱃지 획득/진행, 리더보드 변동, 리마인더, 소셜 | [reference/추가_알림.md](reference/추가_알림.md) | [prototype/알림.html](prototype/알림.html) |
| 💎 프리미엄 | 홈/마이페이지 → 배너 | 혜택 비교, 가격 플랜, 결제 | [reference/추가_프리미엄.md](reference/추가_프리미엄.md) | [prototype/프리미엄.html](prototype/프리미엄.html) |
| 🔐 온보딩 | 앱 최초 실행 | 소개 슬라이드, 소셜 로그인, 펫 등록, 권한 요청 | [reference/추가_온보딩.md](reference/추가_온보딩.md) | [prototype/온보딩.html](prototype/온보딩.html) |
| ⚙️ 설정 | 헤더 → 톱니 아이콘 | 알림 설정, 구독 관리, 계정 설정, 앱 정보, 로그아웃 | [reference/추가_설정.md](reference/추가_설정.md) | [prototype/설정.html](prototype/설정.html) |

**총 스크린 수**: 메인 탭 5개 + 서브 스크린 7개 = **12개 스크린**

> **프라이버시 정책**: 견주의 개인정보(사진, 성별, 나이)는 수집/노출하지 않습니다.
> 소셜 기능에서는 **반려동물 정보만** 표시하여 안전한 반려동물 중심의 경험을 제공합니다.

---

## 4. 핵심 기능 정의

### 4.1 산책 트래킹 (MVP 핵심)

| 기능 | 우선순위 | 설명 |
|------|---------|------|
| GPS 실시간 경로 기록 | ✅ 필수 | 네이티브 GPS + 백그라운드 트래킹 |
| 거리/시간/칼로리 측정 | ✅ 필수 | Haversine 공식으로 거리 계산 |
| 지도 위 경로 표시 | ✅ 필수 | 네이버/카카오맵 Polyline |
| 산책 중 사진 촬영 | ⭐ 선택 | 네이티브 카메라 연동, 경로 위 사진 핀 |
| 산책 일시정지/재개 | ✅ 필수 | 상태 관리 |
| 산책 완료 요약 카드 | ✅ 필수 | 공유 가능한 결과 카드 (인스타/카카오톡) |
| 백그라운드 트래킹 | ✅ 필수 | 앱이 백그라운드일 때도 GPS 기록 유지 |
| 오프라인 기록 | ⭐ 선택 | 네트워크 없이도 로컬 저장 후 동기화 |

### 4.2 소셜 & 경쟁 (NRC 스타일)

소셜 탭은 4개의 서브 탭으로 구성됩니다: **피드 / 챌린지 / 클럽 / 가이드산책**

| 기능 | 우선순위 | 설명 |
|------|---------|------|
| 소셜 피드 | ✅ 필수 | 친구 산책 기록 타임라인, 이모지 리액션(👏🔥❤️👍🐶) + 응원하기 |
| 주간 리더보드 | ✅ 필수 | 친구 주간 거리 순위 (피드 탭 내) |
| 친구 챌린지 | ✅ 필수 | 친구 간 거리 대결, 1:1 및 그룹 챌린지 |
| 산책 클럽 | ⭐ 선택 | NRC Run Club 스타일 그룹 커뮤니티 |
| 가이드 산책 | ⭐ 선택 | 큐레이션 코스, 가이드 음성 산책 |
| 통합 뱃지 시스템 | ✅ 필수 | 거리/연속/탐험/시간/스페셜/시즌 뱃지 |
| 팔로잉/피드 | ⭐ 선택 | 다른 사용자 산책 기록 보기 |
| 산책 초대 | ⭐ 선택 | 함께 산책 기능 |

### 4.3 반려동물 관리

| 기능 | 우선순위 | 설명 |
|------|---------|------|
| 펫 프로필 등록 | ✅ 필수 | 이름, 종, 나이, 사진 |
| 산책별 펫 선택 | ✅ 필수 | 멀티펫 지원 |
| 펫 산책 통계 | ⭐ 선택 | 펫별 누적 거리/시간 |
| 건강 기록 | 💡 향후 | 체중, 접종, 병원 방문 |

### 4.4 지도 & 공공데이터

| 기능 | 우선순위 | API |
|------|---------|-----|
| 산책 경로 지도 표시 | ✅ 필수 | 네이버 지도 / 카카오맵 |
| 주변 동물병원 | ✅ 필수 | 공공데이터: 동물병원 현황 |
| 날씨 정보 | ✅ 필수 | 기상청 단기예보 API |
| 반려동물 공원 | ⭐ 선택 | 공공데이터: 반려동물 놀이터 |
| 반려동물 동반 카페 | ⭐ 선택 | 카카오 로컬 API 검색 |

### 4.5 네이티브 앱 전용 기능

| 기능 | 우선순위 | 설명 |
|------|---------|------|
| 푸시 알림 | ✅ 필수 | 산책 리마인더, 뱃지 획득/진행 알림, 리더보드 변동 |
| 백그라운드 GPS | ✅ 필수 | 화면 꺼져도 산책 기록 지속 |
| 위젯 (iOS/Android) | ⭐ 선택 | 홈 화면에서 바로 산책 시작 |
| Apple Watch / WearOS | 💡 향후 | 워치에서 산책 트래킹 |
| 딥 링크 | ⭐ 선택 | 뱃지 공유 링크, 산책 결과 공유 |
| 카메라 네이티브 연동 | ✅ 필수 | 산책 중 사진 촬영 |
| 햅틱 피드백 | ⭐ 선택 | 1km 달성, 배지 획득 시 진동 |

---

## 5. 기술 스택

### 5.1 프론트엔드 (모바일 앱)

```
Framework:    React Native (Expo SDK 52)
Navigation:   React Navigation v7 (Tab + Stack)
UI Library:   React Native Paper / NativeWind (Tailwind)
State:        Zustand (경량 상태관리)
Maps:         react-native-naver-map 또는 react-native-maps
Charts:       react-native-chart-kit (산책 통계 그래프)
Camera:       expo-camera
Location:     expo-location (foreground + background)
Notifications: expo-notifications + FCM/APNs
Storage:      expo-secure-store (토큰), AsyncStorage (캐시)
```

### 5.2 백엔드

```
API:          Supabase (PostgreSQL + Auth + Realtime + Edge Functions)
Auth:         Supabase Auth (카카오, 네이버, Apple 로그인)
Database:     Supabase (PostgreSQL + PostGIS)
Storage:      Supabase Storage (사진 업로드)
Payment:      Toss Payments SDK + iOS IAP + Google Play Billing
Push:         Firebase Cloud Messaging (Android) + APNs (iOS)
```

### 5.3 외부 API

| API | 용도 | 비용 |
|-----|------|------|
| 네이버 지도 API | 산책 경로 표시, 장소 검색 | 무료 (일 200,000건) |
| 카카오맵 API | 지도 대안, 로컬 검색 | 무료 (일 300,000건) |
| 기상청 단기예보 | 산책 전 날씨 확인 | 무료 (공공데이터) |
| 동물병원 현황 | 주변 병원 표시 | 무료 (공공데이터) |
| 네이티브 GPS | 위치 추적 (foreground + background) | 무료 (OS 내장) |
| 카카오 AdFit | 배너 광고 | 수익 (CPC/CPM) |
| Toss Payments | 결제 처리 | 수수료 3.3% |

### 5.4 인프라

```
Backend:      Supabase (managed)
App Store:    Apple App Store + Google Play Store
CI/CD:        EAS Build + EAS Submit (Expo)
OTA Update:   EAS Update (코드 푸시)
Monitoring:   Sentry (React Native)
Analytics:    Firebase Analytics / Amplitude
```

---

## 6. 데이터 모델 (주요 테이블)

```sql
-- 사용자
users (
  id, email, nickname,
  region, premium_until, created_at
)

-- 반려동물
pets (
  id, user_id, name, species, breed,
  age, weight, photo_url
)

-- 산책 기록
walks (
  id, user_id, pet_id,
  started_at, ended_at,
  distance_m, duration_sec,
  calories,
  route_geojson, -- GPS 경로 데이터
  photos, weather
)

-- 챌린지
challenges (
  id, title, description, type,
  goal_distance, goal_days,
  start_date, end_date
)

-- 리더보드 (주간/월간 집계)
leaderboards (
  id, user_id, period_type, period_key,
  total_distance, total_time, walk_count,
  rank, region
)

-- 뱃지
badges (
  id, user_id, badge_type,
  earned_at
)

-- 푸시 알림 토큰
push_tokens (
  id, user_id, platform,
  token, created_at
)

-- 등급 (산책 등급 시스템)
user_grades (
  user_id,          -- FK → users.id
  current_level,    -- 1-10
  total_distance_km,-- decimal
  level_up_at       -- timestamp
)

-- 칭호 (업적 칭호 시스템)
user_titles (
  user_id,          -- FK → users.id
  title_id,         -- string (e.g. 'early_bird', 'marathoner')
  earned_at,        -- timestamp
  is_active         -- boolean (현재 표시 중인 칭호)
)
```

---

## 7. 화면별 상세 설계

### 7.1 홈 화면 [Tab 1]

```
┌──────────────────────────┐
│  🐾 멍이랑    [🔔] [⚙️]   │  ← 앱 헤더 (알림 + 설정)
├──────────────────────────┤
│  오늘의 날씨: ☀️ 12°C     │  ← 날씨 위젯
│  산책하기 좋은 날이에요!   │
├──────────────────────────┤
│  ┌──────────────────┐    │
│  │  이번 주 산책      │    │  ← 주간 요약 카드
│  │  12.5km  3회      │    │
│  │  ████████░░ 70%   │    │  ← 주간 목표 진행률
│  └──────────────────┘    │
├──────────────────────────┤
│  🏅 진행 중 뱃지           │  ← 뱃지
│  ┌────┐ ┌────┐ ┌────┐   │
│  │주50 │ │7일 │ │공원│   │
│  │km  │ │연속│ │5곳 │   │
│  └────┘ └────┘ └────┘   │
├──────────────────────────┤
│  📍 주변 추천 코스         │  ← 추천 코스
│  • 한강공원 코스 (3.2km)  │
│  • 보라매공원 (2.1km)     │
├──────────────────────────┤
│  [🏠] [👥] [🐾] [🗺️] [👤] │  ← 하단 탭 바
└──────────────────────────┘
```

### 7.2 산책 화면 [Tab 3 - 전체화면 오버레이]

```
┌──────────────────────────┐
│         산책 중            │
├──────────────────────────┤
│                          │
│   ┌──────────────────┐   │
│   │                  │   │
│   │   [네이버/카카오  │   │  ← 실시간 지도
│   │     지도 표시]    │   │     GPS 경로 그리기
│   │                  │   │     (백그라운드 유지)
│   │    ···경로···    │   │
│   │                  │   │
│   └──────────────────┘   │
│                          │
│   ⏱️ 00:32:15            │  ← 타이머
│                          │
│   📏 2.34 km              │  ← 거리
│                          │
│   🔥 128 kcal   🐕 초코  │  ← 칼로리 / 반려동물
│                          │
│   ┌──────┐  ┌──────┐    │
│   │ ⏸ 일시│  │ ■ 종료│    │  ← 컨트롤 버튼
│   │  정지 │  │      │    │
│   └──────┘  └──────┘    │
│                          │
└──────────────────────────┘
```

### 7.3 산책 완료 결과 카드

```
┌──────────────────────────┐
│     🎉 산책 완료!         │
├──────────────────────────┤
│                          │
│   ┌──────────────────┐   │
│   │  [경로 지도 축소] │   │
│   └──────────────────┘   │
│                          │
│   📏 거리    2.34 km     │
│   ⏱️ 시간    32분 15초   │
│   🔥 칼로리   128 kcal   │
│                          │
│   🐕 초코와 함께한 산책!  │
│                          │
│   ┌─────────────────┐    │
│   │  📸 사진 추가     │    │
│   └─────────────────┘    │
│                          │
│   [카카오톡 공유] [저장]   │
│                          │
│   ────── 광고 ──────     │  ← 네이티브 광고 영역
│                          │
└──────────────────────────┘
```

---

## 8. API 연동 상세

### 8.1 GPS 트래킹 (네이티브)

```javascript
// expo-location 활용
import * as Location from 'expo-location';

// 포그라운드 + 백그라운드 위치 권한
const { status: fg } = await Location.requestForegroundPermissionsAsync();
const { status: bg } = await Location.requestBackgroundPermissionsAsync();

// 백그라운드 위치 추적 (앱이 백그라운드여도 동작)
await Location.startLocationUpdatesAsync('walk-tracking', {
  accuracy: Location.Accuracy.BestForNavigation,
  distanceInterval: 5,        // 5m마다 업데이트
  deferredUpdatesInterval: 3000,
  showsBackgroundLocationIndicator: true,
  foregroundService: {
    notificationTitle: '멍이랑 - 산책 중',
    notificationBody: '산책을 기록하고 있습니다 🐾',
  },
});
```

### 8.2 네이버 지도 연동

```javascript
// react-native-naver-map 사용 예시
<NaverMapView
  center={{ latitude: 37.5665, longitude: 126.978, zoom: 16 }}
  showsMyLocationButton={true}
>
  <Path
    coordinates={walkRoute}
    color="#10B981"
    width={5}
  />
  <Marker coordinate={currentPosition} />
</NaverMapView>
```

### 8.3 기상청 API

```
엔드포인트: http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0
요청: 초단기실황조회 (getUltraSrtNcst)
응답: 기온(T1H), 습도(REH), 강수형태(PTY)
활용: 홈 화면 날씨 위젯, 산책 추천 알림
```

### 8.4 카카오 AdFit 광고

```javascript
// React Native 네이티브 모듈 연동
import { KakaoAdFitBanner } from 'react-native-kakao-adfit';

<KakaoAdFitBanner
  adId="DAN-xxxxx"
  width={320}
  height={100}
/>
```

### 8.5 푸시 알림

```javascript
// expo-notifications 활용
import * as Notifications from 'expo-notifications';

// 산책 리마인더 로컬 알림
await Notifications.scheduleNotificationAsync({
  content: {
    title: '🐾 산책 시간이에요!',
    body: '초코가 산책을 기다리고 있어요',
  },
  trigger: { hour: 18, minute: 0, repeats: true },
});
```

---

## 9. 통합 뱃지 시스템 (Apple Fitness / Pikmin Bloom 스타일)

> 기존 "배지 컬렉션"과 "챌린지"를 하나의 뱃지 시스템으로 통합.
> 상세 기획: [reference/추가_뱃지컬렉션.md](reference/추가_뱃지컬렉션.md), [reference/탭5_마이페이지.md](reference/탭5_마이페이지.md)

### 9.1 뱃지 카테고리 (6개)

| 배지 | 조건 | 아이콘 |
|------|------|--------|
| 첫 산책 | 첫 산책 기록 | 🐾 |
| 10km 클럽 | 누적 10km | 🥉 |
| 50km 클럽 | 누적 50km | 🥈 |
| 100km 클럽 | 누적 100km | 🥇 |
| 7일 연속 | 7일 연속 산책 | 🔥 |
| 30일 연속 | 30일 연속 산책 | 💎 |
| 얼리버드 | 오전 6시 전 산책 | 🌅 |
| 올빼미 | 밤 10시 후 산책 | 🦉 |
| 마라토너 | 1회 산책 10km+ | 🏃 |
| 탐험가 | 10개 다른 코스 | 🧭 |

### 9.2 뱃지 목표 예시

| 뱃지명 | 카테고리 | 조건 | 상태 |
|--------|---------|------|------|
| 50km 마라토너 | 🏃 거리 | 누적 50km | 진행중 (38/50km) |
| 7일 연속 | 🔥 연속 | 7일 연속 산책 | 진행중 (5/7일) |
| 동네 탐험가 | 🧭 탐험 | 5곳 다른 장소 | 진행중 (3/5곳) |
| 겨울왕국 | 🏆 시즌 | 12~2월 30km | 시즌 한정 |

---

## 10. NRC (Nike Run Club) 벤치마킹

멍이랑은 Nike Run Club의 UX/UI 패턴을 반려동물 산책에 특화하여 적용합니다.

### 참고 요소
| NRC 기능 | 멍이랑 적용 |
|---------|-----------|
| 소셜 피드 + 리액션 | 소셜 탭: 이모지 리액션(👏🔥❤️👍🐶) + 응원하기 |
| 주간 리더보드 | 소셜 탭: 친구 주간 거리 순위 (랭킹 탭 대체) |
| 챌린지 | 소셜 탭: 친구 간 거리 대결 |
| Run Club | 소셜 탭: 산책 클럽 (그룹 커뮤니티) |
| Guided Runs | 소셜 탭: 가이드 산책 (큐레이션 코스) |
| 미니멀 트래킹 UI | 산책 화면: 그레이스케일 지도, 조작 불가, 자동 추적 |
| 러닝 레벨 | 마이페이지: 산책 등급 시스템 (10단계) |
| 업적 칭호 | 마이페이지: 칭호 시스템 (닉네임 옆 표시) |

---

## 11. 산책 등급 시스템

누적 산책 거리(km)에 따른 10단계 등급 시스템.

| Lv | 등급명 | 필요 km | 아이콘 |
|----|--------|---------|--------|
| 1 | 첫걸음 | 0 | 🐣 |
| 2 | 산책 견습생 | 10 | 🥾 |
| 3 | 동네 산책러 | 50 | 🐕 |
| 4 | 산책 매니아 | 100 | 🏃 |
| 5 | 산책 전문가 | 250 | ⭐ |
| 6 | 산책 달인 | 500 | 🌟 |
| 7 | 산책 영웅 | 1,000 | 💪 |
| 8 | 산책 전설 | 2,000 | 🔥 |
| 9 | 산책 챔피언 | 5,000 | 👑 |
| 10 | 산책의 신 | 10,000 | 💎 |

- 마이페이지 프로필 아래에 등급 카드 표시
- 프로그레스바 + 다음 등급까지 남은 거리

---

## 12. 칭호 시스템

특정 업적 달성 시 획득하는 표시 칭호. 닉네임 왼쪽에 표시됨.

| 칭호 | 아이콘 | 획득 조건 |
|------|--------|----------|
| 얼리버드 | 🌅 | 새벽 산책(오전 6시 이전) 10회 |
| 올빼미 | 🦉 | 야간 산책(오후 9시 이후) 10회 |
| 마라토너 | 🏃 | 누적 42.195km 달성 |
| 탐험가 | 🧭 | 서로 다른 10개 장소 방문 |
| 연속왕 | 🔥 | 7일 연속 산책 달성 |
| 사진왕 | 📸 | 산책 중 사진 50장 촬영 |
| 소셜스타 | ⭐ | 받은 좋아요 100개 |
| 동네챔피언 | 👑 | 주간 리더보드 1위 달성 |
| 비바람워커 | 🌧️ | 비/눈 오는 날 산책 5회 |
| 원년멤버 | 🏅 | 서비스 초기(출시 후 30일 이내) 가입 |

- 마이페이지에서 활성 칭호 선택 가능
- 표시 형식: "🏃 마라토너 초코아빠"

---

## 13. MVP 개발 로드맵

### Phase 1: MVP (5주)

| 주차 | 작업 |
|------|------|
| 1주 | 프로젝트 셋업 (Expo), 인증(카카오/네이버/Apple 로그인), DB 설계 |
| 2주 | 산책 트래킹 (GPS foreground + background + 지도), 기록 저장 |
| 3주 | 지도 탭 (주변 장소 탐색), 펫 프로필, 주간 통계 |
| 4주 | 푸시 알림, 오프라인 저장, 앱 안정화 |
| 5주 | 광고 연동, TestFlight/내부 테스트, 스토어 심사 준비 |

### Phase 2: 소셜 (3주)

- 팔로잉/팔로워
- 산책 피드
- 통합 뱃지 시스템

### Phase 3: 수익화 (2주)

- 프리미엄 구독 (iOS IAP / Google Play Billing)
- 인앱 결제
- 광고 최적화

### Phase 4: 확장 (지속)

- Apple Watch / WearOS 연동
- 홈 화면 위젯
- 건강 기록 기능

---

## 14. KPI 목표

| 지표 | 1개월 | 3개월 | 6개월 |
|------|-------|-------|-------|
| MAU | 500 | 3,000 | 10,000 |
| DAU | 100 | 800 | 3,000 |
| 일평균 산책 | 200건 | 1,500건 | 5,000건 |
| 프리미엄 전환율 | - | 3% | 5% |
| 월 광고 수익 | 5만원 | 30만원 | 100만원 |
| 월 구독 수익 | - | 35만원 | 195만원 |
| 앱 스토어 평점 | 4.0+ | 4.3+ | 4.5+ |
| 앱 다운로드 | 1,000 | 5,000 | 20,000 |

---

*작성일: 2026-02-11*
*버전: 1.0*
