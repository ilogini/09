# 멍이랑 (withbowwow) 백엔드 설계 문서

> 이 파일은 백엔드 기획의 **코어 파일**입니다.
> 전체 구조를 파악한 뒤, 필요한 상세 내용은 각 참조 파일을 확인하세요.

---

## 1. 기술 스택 추천

### 1.1 왜 Supabase + TypeScript인가

| 항목 | 선택 | 이유 |
|------|------|------|
| **Backend Platform** | Supabase | PostgreSQL 기반 BaaS, Auth/Realtime/Storage/Edge Functions 통합 |
| **Database** | PostgreSQL 15+ (Supabase 관리형) | PostGIS 확장으로 GPS/GeoJSON 네이티브 지원, 강력한 집계 쿼리 |
| **Server-side Language** | TypeScript (Deno) | Supabase Edge Functions 기본 런타임, React Native와 언어 통일 |
| **Auth** | Supabase Auth | 카카오/네이버/Apple 소셜 로그인 내장 지원 |
| **Realtime** | Supabase Realtime | WebSocket 기반, 테이블 변경 실시간 브로드캐스트 |
| **Storage** | Supabase Storage | S3 호환, 이미지 리사이즈 변환 지원 |
| **Push** | Firebase Cloud Messaging (FCM) + APNs | 크로스 플랫폼 푸시, Expo Notifications 연동 |
| **Payment** | Toss Payments SDK + IAP | 국내 PG 최적, iOS/Android 인앱결제 필수 |

### 1.2 기술 스택 선정 근거

#### DB: PostgreSQL + PostGIS

- GPS 경로 데이터(GeoJSON)를 `geometry` 타입으로 네이티브 저장/쿼리
- `ST_Distance`, `ST_DWithin` 등 공간 함수로 "내 주변 500m 동물병원" 같은 쿼리 가능
- `RANK() OVER()` 윈도우 함수로 랭킹 집계 효율적
- JSON/JSONB 타입으로 유연한 메타데이터 저장 (날씨 정보, 뱃지 조건 등)
- Row Level Security(RLS)로 데이터 접근 제어

#### 언어: TypeScript (Deno Runtime)

- React Native(프론트)와 동일 언어 → 풀스택 코드 공유 가능
- Supabase Edge Functions는 Deno 런타임 사용
- 타입 안전성으로 뱃지 조건, 랭킹 계산 등 비즈니스 로직 오류 최소화
- npm 생태계 활용 (Toss Payments SDK, FCM SDK 등)

#### 왜 별도 서버가 아닌 Supabase인가

| 비교 | Supabase (선택) | Express/NestJS 자체 서버 |
|------|----------------|------------------------|
| 인증 | 내장 (소셜 로그인 포함) | Passport.js 등 직접 구현 |
| DB | 관리형 PostgreSQL | 직접 프로비저닝/관리 |
| Realtime | 내장 WebSocket | Socket.io 등 직접 구현 |
| Storage | 내장 (S3 호환) | Multer + S3 직접 연동 |
| 배포 | Edge Functions (서버리스) | EC2/ECS 직접 운영 |
| 비용 | Free tier → Pro $25/월 | EC2 + RDS 최소 $50~/월 |
| 확장성 | 자동 스케일링 | 직접 로드밸런서 구성 |
| MVP 속도 | 빠름 (1~2주 핵심 기능) | 느림 (3~4주 예상) |

**결론**: MVP 단계에서는 Supabase가 개발 속도, 비용, 운영 부담 모두 우위. 사용자 10만+ 규모에서 성능 이슈 발생 시 자체 서버 마이그레이션 고려.

---

## 2. 아키텍처 개요

```
┌─────────────────────────────────────────────────────┐
│                    React Native App                  │
│               (Expo SDK 52 + TypeScript)             │
└──────────┬──────────┬──────────┬──────────┬─────────┘
           │          │          │          │
     Supabase     Supabase   Supabase    FCM/APNs
      Auth        Client     Realtime     Push
           │          │          │          │
┌──────────▼──────────▼──────────▼──────────▼─────────┐
│                     Supabase                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │   Auth    │  │ Realtime │  │  Edge Functions   │  │
│  │ (소셜로그인)│  │(WebSocket)│  │ (비즈니스 로직)    │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │ PostgreSQL│  │ Storage  │  │   PostGIS 확장    │  │
│  │ (메인 DB) │  │ (사진)   │  │ (GPS/GeoJSON)    │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────┘
           │              │              │
    ┌──────▼──────┐ ┌────▼────┐ ┌──────▼──────┐
    │ External API │ │  Toss   │ │  FCM/APNs   │
    │ 기상청/에어코리아│ │Payments │ │  Push 서버  │
    │ 공공데이터/카카오│ │  SDK    │ │             │
    └─────────────┘ └─────────┘ └─────────────┘
```

---

## 3. 백엔드 핵심 도메인

| # | 도메인 | 상세 문서 | 핵심 내용 |
|---|--------|----------|----------|
| 1 | **데이터베이스 스키마** | [01_database_schema.md](./01_database_schema.md) | 전체 테이블 정의, 관계, 인덱스, RLS 정책 |
| 2 | **인증 시스템** | [02_auth.md](./02_auth.md) | 카카오/네이버/Apple 소셜 로그인, 토큰 관리, 온보딩 플로우 |
| 3 | **Edge Functions (비즈니스 로직)** | [03_edge_functions.md](./03_edge_functions.md) | 뱃지 진행률, 랭킹 집계, 친구 추천, 산책 유효성 검증 |
| 4 | **외부 API 연동** | [04_external_apis.md](./04_external_apis.md) | 기상청, 에어코리아, 공공데이터, 카카오 로컬 API |
| 5 | **푸시 알림** | [05_push_notifications.md](./05_push_notifications.md) | FCM/APNs 전략, 7가지 알림 유형, 빈도 제한 |
| 6 | **결제 시스템** | [06_payment.md](./06_payment.md) | Toss Payments, iOS IAP, Google Play Billing, 구독 관리 |
| 7 | **실시간 기능** | [07_realtime.md](./07_realtime.md) | Supabase Realtime 구독, 피드/랭킹/초대 실시간 업데이트 |
| 8 | **파일 저장소** | [08_storage.md](./08_storage.md) | 프로필 사진, 산책 사진, 공유 카드 이미지 관리 |

---

## 4. 데이터 모델 요약

### 4.1 핵심 테이블 (12개)

```
users ──┬── pets ──── pet_health
        │
        ├── walks (route_geojson, photos)
        │     └── walk_photos
        │
        ├── user_badges ──── badge_definitions
        │
        ├── rankings
        │     └── hall_of_fame
        │
        ├── follows
        ├── likes / comments
        ├── invitations / meetups
        │
        ├── push_tokens
        ├── notifications
        │
        └── subscriptions (결제/구독)
```

### 4.2 테이블별 역할 요약

| 테이블 | 역할 | 주요 연관 기능 |
|--------|------|---------------|
| `users` | 사용자 계정 (닉네임, 지역, 프리미엄 상태) | 모든 기능 |
| `pets` | 반려동물 프로필 (이름, 견종, 나이, 체중) | 산책, 소셜, 마이페이지 |
| `pet_health` | 건강 기록 (체중 변화, 접종, 병원 방문) | 마이페이지 |
| `walks` | 산책 기록 (경로 GeoJSON, 거리, 시간, 칼로리) | 핵심 데이터 |
| `walk_photos` | 산책 중 촬영 사진 (GPS 좌표 + 파일 URL) | 산책, 소셜 피드 |
| `badge_definitions` | 뱃지 정의 (47개, 6카테고리) | 뱃지 시스템 |
| `user_badges` | 사용자별 뱃지 상태 (locked/in_progress/earned) | 뱃지 시스템 |
| `rankings` | 기간별 랭킹 집계 (주간/월간/전체) | 랭킹 탭 |
| `follows` | 팔로우 관계 | 소셜 탭 |
| `likes` / `comments` | 산책 피드 인터랙션 | 소셜 탭 |
| `invitations` | 산책 초대 | 소셜 탭 |
| `meetups` | 산책 모임 게시판 | 소셜 탭 |
| `push_tokens` | FCM/APNs 토큰 | 푸시 알림 |
| `notifications` | 알림 내역 | 알림 스크린 |
| `subscriptions` | 구독/결제 이력 | 결제 시스템 |

> 전체 스키마 정의(CREATE TABLE, 인덱스, RLS)는 [01_database_schema.md](./01_database_schema.md) 참조

---

## 5. Edge Functions 목록

| 함수명 | 트리거 | 역할 |
|--------|--------|------|
| `on-walk-complete` | 산책 완료 시 | 뱃지 진행률 업데이트, 랭킹 재계산, 연속일수 계산 |
| `calculate-rankings` | 1시간마다 (Cron) | 주간/월간/전체 랭킹 집계 |
| `recommend-friends` | 12시간마다 (Cron) | 친구 추천 알고리즘 실행 |
| `check-badge-progress` | `on-walk-complete` 내부 호출 | 6개 카테고리 뱃지 조건 검사 |
| `send-push` | 이벤트 발생 시 | FCM/APNs 푸시 알림 전송 |
| `validate-walk` | 산책 저장 전 | 부정행위 필터 (시속 15km+, GPS 스푸핑, 500m 미만) |
| `weather-cache` | 1시간마다 (Cron) | 기상청/에어코리아 API 호출 후 캐싱 |
| `process-payment` | 결제 웹훅 수신 | Toss Payments 결제 확인, 구독 상태 업데이트 |

> 상세 로직은 [03_edge_functions.md](./03_edge_functions.md) 참조

---

## 6. 개발 우선순위 (MVP 기준)

### Phase 1: MVP 핵심 (1~2주차)

| 순서 | 작업 | 관련 문서 |
|------|------|----------|
| 1 | DB 스키마 생성 (users, pets, walks, push_tokens) | 01_database_schema.md |
| 2 | Supabase Auth 설정 (카카오/네이버/Apple) | 02_auth.md |
| 3 | 산책 데이터 CRUD API (Supabase Client) | 01_database_schema.md |
| 4 | `validate-walk` Edge Function | 03_edge_functions.md |
| 5 | Supabase Storage 설정 (사진 업로드) | 08_storage.md |

### Phase 2: 게이미피케이션 (3주차)

| 순서 | 작업 | 관련 문서 |
|------|------|----------|
| 6 | badge_definitions 시드 데이터 (47개 뱃지) | 01_database_schema.md |
| 7 | `on-walk-complete` → 뱃지 진행률 업데이트 | 03_edge_functions.md |
| 8 | `calculate-rankings` 랭킹 집계 | 03_edge_functions.md |
| 9 | 푸시 알림 (산책 리마인더, 뱃지 획득) | 05_push_notifications.md |

### Phase 3: 소셜 (4주차)

| 순서 | 작업 | 관련 문서 |
|------|------|----------|
| 10 | follows, likes, comments 테이블 | 01_database_schema.md |
| 11 | 산책 피드 API + Realtime 구독 | 07_realtime.md |
| 12 | `recommend-friends` 친구 추천 | 03_edge_functions.md |
| 13 | 산책 초대 + 모임 게시판 | 01_database_schema.md |

### Phase 4: 수익화 (5주차)

| 순서 | 작업 | 관련 문서 |
|------|------|----------|
| 14 | Toss Payments 연동 | 06_payment.md |
| 15 | iOS IAP / Google Play Billing | 06_payment.md |
| 16 | 구독 상태 관리 + 프리미엄 기능 잠금 | 06_payment.md |
| 17 | 외부 API 연동 (기상청, 에어코리아) | 04_external_apis.md |

---

## 7. 환경 구성

### 7.1 Supabase 프로젝트 설정

```
프로젝트명: withbowwow
리전: Northeast Asia (ap-northeast-2, 서울 근접)
플랜: Free → Pro 전환 시점: MAU 50,000 또는 DB 500MB 초과 시
```

### 7.2 환경 변수 (.env)

```env
# Supabase
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJI...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJI...

# 소셜 로그인
KAKAO_CLIENT_ID=
KAKAO_CLIENT_SECRET=
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
APPLE_CLIENT_ID=
APPLE_TEAM_ID=
APPLE_KEY_ID=
APPLE_PRIVATE_KEY=

# 외부 API
WEATHER_API_KEY=          # 기상청 공공데이터 포털
AIR_KOREA_API_KEY=        # 에어코리아
PUBLIC_DATA_API_KEY=      # 공공데이터 (동물병원 등)
KAKAO_REST_API_KEY=       # 카카오 로컬 검색

# 푸시 알림
FCM_SERVER_KEY=
APNS_KEY_ID=
APNS_TEAM_ID=

# 결제
TOSS_CLIENT_KEY=
TOSS_SECRET_KEY=
```

---

*작성일: 2026-02-12*
*버전: 1.0*
