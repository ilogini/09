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
PG사: 토스페이먼츠 (Toss Payments) — 백엔드 httpx로 REST API 호출
- 카드 결제, 카카오페이, 네이버페이
- 앱 내 결제: iOS IAP / Google Play Billing
- 정기결제(빌링키) 지원
- 구독 상태: trial(7일) → active → cancelled → expired
```

> 상세 결제 설계: [backend/06_payment.md](backend/06_payment.md)

---

## 3. 앱 화면 구조

> 각 화면의 세부 콘텐츠 구성, 배치 이유, UX 설계 의도는 `reference/` 폴더의 개별 기획문서를 참조합니다.
> HTML 목업은 `prototype/` 폴더에서 확인할 수 있습니다.

### 3.1 탭 네비게이션 (하단 5탭)

| 탭 | 화면명 | 핵심 기능 | 상세 기획 | 목업 |
|---|---|---|---|---|
| Tab 1 | 🏠 홈 | 날씨, 주간 요약, 최근 산책, 진행 중 뱃지, 주변 추천 코스 | [reference/메인페이지.md](reference/메인페이지.md) | [prototype/메인페이지.html](prototype/메인페이지.html) |
| Tab 2 | 👥 소셜 | 친구 리더보드, 챌린지 (2탭 구조) | [reference/탭2_소셜.md](reference/탭2_소셜.md) | [prototype/소셜.html](prototype/소셜.html) |
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
| 🔐 로그인 | 앱 최초 실행 / 로그아웃 후 | 소셜 로그인 (카카오/네이버/Apple/Google) | [reference/추가_로그인.md](reference/추가_로그인.md) | [prototype/로그인.html](prototype/로그인.html) |

**총 스크린 수**: 메인 탭 5개 + 서브 스크린 8개 = **13개 스크린**

> **프라이버시 정책**: 견주의 개인정보(사진, 성별, 나이)는 수집/노출하지 않습니다.
> 소셜 기능에서는 **반려동물 정보만** 표시하여 안전한 반려동물 중심의 경험을 제공합니다.

### 3.3 디자인 시스템

> 전체 디자인 가이드: [design/연주/DESIGN_GUIDE_v2.md](design/연주/DESIGN_GUIDE_v2.md)
> 공통 헤더/푸터 표준: [reference/공통_앱셸.md](reference/공통_앱셸.md)

#### 디자인 컨셉 (DESIGN_GUIDE_v2 기준)

**컨셉**: 시원하고 청량한 맑은 날의 산책 — 라임(Lime Punch) + 아주르(Azure) + 글래스모피즘

| 요소 | 값 |
|------|---|
| 주 컬러 | Lime Punch `#C5D900` / Azure `#0099FF` |
| 배경 | `#F8FCFA` (살짝 민트) |
| 유리 효과 | `backdrop-filter: blur(24px)` 반투명 흰색 |
| 서체 | Pretendard Variable |
| 아이콘 | Lucide Icons (stroke 기반) |
| 라운딩 | XL 28px / LG 24px / MD 20px / SM 14px / XS 10px |

#### 공통 앱 셸 (모든 페이지 고정)

**상단 헤더** — `position: sticky; top: 0; height: 58px`

```
┌──────────────────────────────────────┐
│  🐾 멍이랑                  [🔔] [⚙️]  │  ← 탭 페이지
│  [←]  페이지 제목                      │  ← 서브 페이지
└──────────────────────────────────────┘
```

**하단 네비게이션** — `position: fixed; bottom: 0; height: 76px`

```
┌────────────────────────────────────────┐
│  🏠      👥      🐾      🗺️      👤    │
│  홈    소셜    산책    지도     MY     │
│                 ↑
│            중앙 플로팅 버튼 (54px 원형)
└────────────────────────────────────────┘
```

> 헤더와 하단 네비는 **디자인 변경 금지 영역**입니다.
> 변경이 필요한 경우 [reference/공통_앱셸.md](reference/공통_앱셸.md)를 먼저 업데이트하고 모든 prototype을 일괄 수정하세요.
> 기준(canonical) 파일: `prototype/마이페이지.html`

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

소셜 탭은 2개의 서브 탭으로 구성됩니다: **리더보드 / 챌린지**

| 기능 | 우선순위 | 설명 |
|------|---------|------|
| 친구 리더보드 | ✅ 필수 | 친구 간 일별/주간 거리 비교 (리더보드 탭) |
| 챌린지 | ✅ 필수 | 친구 간 거리 챌린지 + 앱 기본 월간 챌린지 10개 |
| 통합 뱃지 시스템 | ✅ 필수 | 거리/연속/탐험/시간/스페셜/시즌 뱃지 |

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
Framework:    React Native 0.81 (Expo SDK 54)
Language:     TypeScript 5.x (Strict mode)
Navigation:   React Navigation v7 (Bottom Tabs + Native Stack)
Styling:      NativeWind v4.1 (Tailwind CSS for RN)
State:        Zustand 5.x (경량 전역 상태)
Server State: TanStack Query v5 (API 캐싱, 리트라이, 백그라운드 리페치)
Animation:    react-native-reanimated v3 (~3.16.x, NativeWind v4 호환)
HTTP:         axios 1.13.x
Maps:         @mj-studio/react-native-naver-map v2.x (한국 시장 필수)
Location:     expo-location + expo-task-manager (foreground + background GPS)
Camera:       expo-image-picker (사진 촬영/갤러리 선택)
Push:         expo-notifications + FCM/APNs
Storage:      expo-secure-store (JWT 토큰), AsyncStorage (캐시)
Social Login: @react-native-kakao/core, expo-apple-authentication, expo-auth-session
```

> **참고**: Expo Go 미지원 — Development Build 필수 (네이버 지도, 카카오 SDK 등 네이티브 모듈 사용)
> 상세 환경 설정: [frontend/env_setup.md](frontend/env_setup.md)

### 5.2 백엔드

```
Language:     Python 3.11+ (3.12 권장)
Framework:    FastAPI 0.115+ (비동기, 자동 Swagger UI)
ORM:          SQLAlchemy 2.0 (async 지원) + GeoAlchemy2
Migration:    Alembic 1.13+
Database:     PostgreSQL 15+ (자체 운영) + PostGIS 확장
Auth:         python-jose (JWT 발급/검증) + httpx (소셜 OAuth)
WebSocket:    FastAPI WebSocket (함께 산책 위치 공유)
Scheduler:    APScheduler (랭킹 집계, 날씨 캐싱, 계정 정리)
Cache:        Redis 7+ (날씨 캐시, 빈도 제한)
Push:         firebase-admin (FCM/APNs 크로스 플랫폼)
Payment:      httpx (Toss Payments REST API) + iOS IAP + Google Play Billing
Storage:      Cloudflare R2 (S3 호환, boto3) — 무료 10GB, 이그레스 무료
Deploy:       Render (Docker) — Free → Starter $7/월
Validation:   Pydantic v2.6+ (요청/응답 스키마)
Image:        Pillow 10.2+ (서버사이드 리사이징)
```

> 상세 설계: [backend/00_overview.md](backend/00_overview.md)
> 환경 설정: [backend/env_setup.md](backend/env_setup.md)

### 5.3 외부 API

| API | 용도 | 호출 방식 | 비용 |
|-----|------|----------|------|
| 네이버 지도 API | 산책 경로 표시 | 프론트 직접 호출 | 무료 (일 200,000건) |
| 카카오 로컬 API | 반려동물 카페/장소 검색, 역지오코딩 | 백엔드 프록시 | 무료 (일 300,000건) |
| 기상청 단기예보 | 기온, 강수, 하늘 상태 | 백엔드 (Redis 1시간 캐싱) | 무료 (공공데이터) |
| 에어코리아 | 미세먼지 PM10/PM2.5 | 백엔드 (Redis 1시간 캐싱) | 무료 (공공데이터) |
| 동물병원 현황 | 주변 병원 표시 | 백엔드 (DB 24시간 동기화) | 무료 (공공데이터) |
| 반려동물 놀이터 | 반려동물 공원 정보 | 백엔드 (DB 24시간 동기화) | 무료 (공공데이터) |
| 네이티브 GPS | 위치 추적 (foreground + background) | 프론트 직접 | 무료 (OS 내장) |
| 카카오 AdFit | 배너 광고 | 프론트 직접 | 수익 (CPC/CPM) |
| Toss Payments | 결제 처리 | 백엔드 REST API | 수수료 3.3% |
| Firebase | FCM 푸시 알림 | 백엔드 (firebase-admin) | 무료 (Spark) |

> 상세 연동: [backend/04_external_apis.md](backend/04_external_apis.md)

### 5.4 인프라

```
Backend:      Render (Docker) — Free → Starter $7/월
Database:     PostgreSQL 15+ (Render 또는 자체 운영)
Cache:        Redis 7+ (Render Redis 또는 Upstash 무료)
Storage:      Cloudflare R2 (S3 호환, 무료 10GB)
App Store:    Apple App Store + Google Play Store
CI/CD (FE):   EAS Build + EAS Submit (Expo)
CI/CD (BE):   GitHub → Render 자동 배포
OTA Update:   EAS Update (코드 푸시)
Monitoring:   Sentry (React Native + FastAPI)
Analytics:    Firebase Analytics / Amplitude
```

---

## 6. 데이터 모델 (21개 테이블)

> 전체 스키마(CREATE TABLE, 인덱스, Stored Procedures)는 [backend/01_database_schema.md](backend/01_database_schema.md) 참조
> ORM: SQLAlchemy 2.0 + GeoAlchemy2 / 마이그레이션: Alembic

### 6.1 ER 관계 요약

```
users ──┬── pets ──── pet_health
        │
        ├── walks (route_geojson, route_geometry)
        │     └── walk_photos
        │
        ├── user_badges ──── badge_definitions (45개 뱃지)
        │
        ├── rankings
        │     └── hall_of_fame
        │
        ├── follows (self-referencing)
        ├── likes / comments ──── walks
        ├── invitations / meetups ──── meetup_participants
        │
        ├── blocks / reports
        │
        ├── push_tokens / notifications
        └── subscriptions (결제/구독)
```

### 6.2 테이블별 핵심 컬럼

```sql
-- 사용자 (소셜 로그인 기반)
users (
  id UUID, email, nickname,
  provider, provider_id,              -- kakao / naver / apple
  region_sido, region_sigungu, region_dong,  -- 지역 3단계
  is_premium, premium_until,
  weekly_goal_km, notification_settings JSONB,
  hashed_refresh_token,               -- JWT 리프레시 토큰 해시
  deleted_at                          -- 소프트 삭제 (30일 유예)
)

-- 반려동물
pets (
  id UUID, user_id FK, name, species, breed,
  size, birth_date, weight_kg, photo_url,
  is_primary                          -- 대표 반려동물
)

-- 반려동물 건강 기록
pet_health (
  id UUID, pet_id FK, record_type,    -- weight / vaccination / hospital_visit
  record_date, value_numeric, title, memo
)

-- 산책 기록 (핵심 테이블, PostGIS)
walks (
  id UUID, user_id FK, pet_id FK,
  started_at, ended_at, duration_sec, distance_m, calories,
  avg_speed_kmh,
  route_geojson JSONB,                -- GeoJSON LineString
  route_geometry GEOMETRY(LineString, 4326),  -- PostGIS 인덱스
  start_point GEOMETRY(Point, 4326),
  end_point GEOMETRY(Point, 4326),
  weather JSONB,                      -- {"temp": 12, "sky": "맑음", "pm10": 30}
  is_valid, shared_to_feed
)

-- 산책 사진
walk_photos (
  id UUID, walk_id FK,
  photo_url, thumbnail_url,           -- Cloudflare R2 URL
  location GEOMETRY(Point, 4326)
)

-- 뱃지 정의 (45개, 6카테고리)
badge_definitions (
  id UUID, category,                  -- distance/streak/exploration/time/special/season
  name, description, icon,
  condition_type, condition_value, condition_extra JSONB,
  difficulty,                         -- beginner~mythic (7단계)
  season_start, season_end
)

-- 사용자별 뱃지 상태
user_badges (
  id UUID, user_id FK, badge_id FK,
  status,                             -- locked / in_progress / earned
  progress_value, progress_percent,
  earned_at, earned_walk_id FK
)

-- 랭킹 (주간/월간/전체)
rankings (
  id UUID, user_id FK, pet_id FK,
  period_type, period_key,            -- "2026-W07", "2026-02", "alltime"
  total_distance_m, total_duration_sec, walk_count,
  rank, prev_rank,
  region_sigungu, region_dong
)

-- 명예의 전당
hall_of_fame (id UUID, user_id FK, category, period_key, record_value)

-- 소셜
follows (follower_id FK, following_id FK)
likes (user_id FK, walk_id FK)
comments (user_id FK, walk_id FK, content)
invitations (inviter_id FK, invitee_id FK, scheduled_at, location_point, status)
meetups (creator_id FK, title, location_point, scheduled_at, max_participants)
meetup_participants (meetup_id FK, user_id FK)

-- 안전
blocks (blocker_id FK, blocked_id FK)
reports (reporter_id FK, target_type, target_id, reason, status)

-- 시스템
push_tokens (user_id FK, platform, token, is_active)
notifications (user_id FK, type, title, body, data JSONB, is_read)
subscriptions (user_id FK, plan_type, status, payment_provider, current_period_end)
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

```typescript
// expo-location + expo-task-manager 활용
import * as Location from 'expo-location';
import * as TaskManager from 'expo-task-manager';

const WALK_TRACKING_TASK = 'walk-background-tracking';

// 반드시 글로벌 스코프에서 정의 (컴포넌트 밖)
TaskManager.defineTask(WALK_TRACKING_TASK, ({ data, error }) => {
  if (error) return;
  const { locations } = data as { locations: Location.LocationObject[] };
  // Zustand store에 경로 포인트 추가
});

// 산책 시작 시 호출
export async function startWalkTracking() {
  await Location.startLocationUpdatesAsync(WALK_TRACKING_TASK, {
    accuracy: Location.Accuracy.Balanced,    // 배터리 최적화 (~5-8%/시간)
    timeInterval: 10000,                     // 10초마다
    distanceInterval: 10,                    // 10m 이동 시에만 업데이트
    deferredUpdatesInterval: 15000,          // 15초 배치 처리
    showsBackgroundLocationIndicator: true,  // iOS 상단 파란 바
    foregroundService: {                     // Android 알림
      notificationTitle: '멍이랑 - 산책 중',
      notificationBody: '산책을 기록하고 있습니다',
      notificationColor: '#FF6B35',
    },
    pausesUpdatesAutomatically: false,
  });
}
```

> 상세 GPS 최적화: [frontend/env_setup.md](frontend/env_setup.md) §7

### 8.2 네이버 지도 연동

```typescript
// @mj-studio/react-native-naver-map v2.x 사용
import { NaverMapView, NaverMapPath, NaverMapMarker } from '@mj-studio/react-native-naver-map';

<NaverMapView
  center={{ latitude: 37.5665, longitude: 126.978, zoom: 16 }}
  isShowMyLocationButton={true}
>
  <NaverMapPath
    coordinates={walkRoute}
    color="#10B981"
    width={5}
  />
  <NaverMapMarker coordinate={currentPosition} />
</NaverMapView>
```

> New Architecture 필수 (Expo SDK 54 기본 활성화)

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

```typescript
// 클라이언트: expo-notifications (로컬 리마인더)
import * as Notifications from 'expo-notifications';

await Notifications.scheduleNotificationAsync({
  content: {
    title: '산책 시간이에요!',
    body: '초코가 산책을 기다리고 있어요',
  },
  trigger: { hour: 18, minute: 0, repeats: true },
});
```

```python
# 서버: firebase-admin (FCM/APNs 원격 푸시)
from firebase_admin import messaging

message = messaging.Message(
    token=user_push_token,
    notification=messaging.Notification(
        title="새 뱃지를 획득했어요!",
        body="50km 마라토너 뱃지를 달성했어요!",
    ),
    data={"type": "badge_earned", "badge_id": "..."},
)
messaging.send(message)
```

> 7가지 알림 유형, 일일 최대 10회 제한, 야간 금지(22~08시)
> 상세: [backend/05_push_notifications.md](backend/05_push_notifications.md)

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
| 주간 리더보드 | 소셜 탭: 친구 기반 일별/주간 리더보드 (발바닥 캘린더) |
| 챌린지 | 소셜 탭: 친구 챌린지 + 앱 기본 월간 챌린지 10개 |
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

> 프론트엔드(React Native)와 백엔드(FastAPI) 병행 개발 기준
> 백엔드 상세 로드맵: [backend/09_roadmap.md](backend/09_roadmap.md)

### Phase 1: 기반 구축 + MVP 핵심 (1~2주)

| 주차 | 프론트엔드 (Expo SDK 54) | 백엔드 (FastAPI) |
|------|------------------------|-----------------|
| 1주 | Expo 프로젝트 셋업, Development Build 구성, 소셜 로그인 UI | FastAPI + SQLAlchemy + Alembic 셋업, 핵심 DB 마이그레이션, JWT 인증 + 카카오/네이버/Apple OAuth |
| 2주 | 산책 GPS 트래킹 (foreground + background), 네이버 지도 연동 | 산책 CRUD API, validate_walk 서비스, R2 사진 업로드, 연속일수 계산 함수 |

### Phase 2: 게이미피케이션 (3주차)

| 프론트엔드 | 백엔드 |
|-----------|--------|
| 뱃지 컬렉션 UI, 진행률 바, 획득 애니메이션 | badge_definitions 45개 시드, badge_service 6카테고리 진행률, APScheduler 랭킹 집계 |
| 랭킹 화면 (주간/월간, 지역 필터) | rankings 테이블 + refresh_weekly_rankings, hall_of_fame |
| 푸시 알림 연동 (expo-notifications) | Firebase Admin + push_service (7가지 알림, 빈도 제한) |

### Phase 3: 소셜 (4주차)

| 프론트엔드 | 백엔드 |
|-----------|--------|
| 소셜 피드, 팔로우/좋아요/댓글 UI | follows/likes/comments API, 피드 정렬 알고리즘 |
| 산책 초대/모임 화면 | invitations + WebSocket (함께 산책 위치 공유) |
| 친구 추천 UI | recommend_service (지역40% + 시간25% + 견종20% + 활동량15%) |
| 차단/신고 기능 | blocks/reports + 피드/추천 필터링 |

### Phase 4: 수익화 + 외부 API (5주차)

| 프론트엔드 | 백엔드 |
|-----------|--------|
| 프리미엄 가입 화면, 결제 UI | Toss Payments 연동, iOS IAP/Google Play 웹훅, 구독 상태 머신 |
| 날씨/미세먼지 위젯 | weather_service (기상청 + 에어코리아 → Redis 캐싱) |
| 지도 탭 (주변 장소 탐색) | 공공데이터 동기화 (동물병원/공원), 카카오 로컬 검색 프록시 |

### Phase 5: 안정화 + 배포 (6주차)

- 에러 핸들링 표준화, DB 쿼리 최적화, 보안 검증
- Render 배포, Sentry 모니터링 연동
- EAS Build → TestFlight/Google Play 내부 테스트
- Cron Job 동작 확인 (랭킹/날씨/계정 정리)
- 스토어 심사 준비

### Phase 6: 확장 (지속)

- Apple Watch / WearOS 연동
- 홈 화면 위젯
- 건강 기록 기능
- 광고 최적화 (카카오 AdFit)

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
*최종 수정: 2026-02-24 — 디자인 시스템(3.3) 추가, 공통 앱셸 표준화*
*버전: 2.0 — 백엔드 FastAPI 전환, 프론트엔드 Expo SDK 54 업그레이드 반영*
