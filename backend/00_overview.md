# 멍이랑 (withbowwow) 백엔드 설계 문서

> 이 파일은 백엔드 기획의 **코어 파일**입니다.
> 전체 구조를 파악한 뒤, 필요한 상세 내용은 각 참조 파일을 확인하세요.

---

## 1. 기술 스택

### 1.1 스택 구성

| 항목 | 선택 | 이유 |
|------|------|------|
| **Language** | Python 3.11+ | FastAPI 생태계, 데이터 처리 라이브러리 풍부 |
| **Framework** | FastAPI | 비동기 지원, 자동 Swagger 문서, 타입 힌트 기반 검증 |
| **ORM** | SQLAlchemy 2.0 | Python 표준 ORM, async 지원, 성숙한 생태계 |
| **Migration** | Alembic | SQLAlchemy 공식 마이그레이션 도구 |
| **Database** | PostgreSQL 15+ (자체 운영) | PostGIS 확장, 공간 쿼리, 윈도우 함수 |
| **Geo** | GeoAlchemy2 | PostGIS를 SQLAlchemy에서 사용하기 위한 확장 |
| **Auth** | python-jose (JWT) + httpx (OAuth) | 소셜 로그인 직접 구현, JWT 발급/검증 |
| **WebSocket** | FastAPI WebSocket | 함께 산책 실시간 위치 공유 |
| **Scheduler** | APScheduler | 랭킹 집계, 날씨 캐싱 등 주기 작업 (별도 워커 불필요) |
| **Cache** | Redis | 날씨 캐시, 세션, 빈도 제한 |
| **Push** | firebase-admin | FCM/APNs 크로스 플랫폼 푸시 |
| **Payment** | httpx | Toss Payments REST API 호출 |
| **Storage** | Cloudflare R2 (boto3) | S3 호환, 무료 10GB, 이그레스 무료 |
| **Deploy** | Render | 사이드 프로젝트 적합, Free → Starter $7/월 |

### 1.2 기술 스택 선정 근거

#### DB: PostgreSQL + PostGIS (자체 운영)

- GPS 경로 데이터(GeoJSON)를 `geometry` 타입으로 네이티브 저장/쿼리
- `ST_Distance`, `ST_DWithin` 등 공간 함수로 "내 주변 500m 동물병원" 같은 쿼리 가능
- `RANK() OVER()` 윈도우 함수로 랭킹 집계 효율적
- JSON/JSONB 타입으로 유연한 메타데이터 저장 (날씨 정보, 뱃지 조건 등)
- **이미 준비된 PostgreSQL DB를 그대로 활용** → BaaS 종속성 없음

#### 언어: Python + FastAPI

- FastAPI의 자동 Swagger UI(`/docs`)로 프론트엔드 개발자와 API 명세 공유 용이
- Pydantic 기반 요청/응답 검증 → 런타임 에러 최소화
- async/await 네이티브 지원 → WebSocket, 외부 API 호출에 유리
- firebase-admin, boto3, httpx 등 필요한 모든 라이브러리 존재

#### 배포: Render

| 항목 | Free tier | Starter ($7/월) |
|------|-----------|-----------------|
| Web Service | 750시간/월 | 무제한 |
| 자동 배포 | GitHub 연동 | GitHub 연동 |
| 슬립 | 15분 비활동 시 슬립 | 슬립 없음 |
| 대역폭 | 100GB/월 | 100GB/월 |

> MVP는 Free tier로 시작, 사용자 유입 시 Starter로 전환

---

## 2. 아키텍처 개요

```
┌─────────────────────────────────────────────────────┐
│                    React Native App                  │
│               (Expo SDK 52 + TypeScript)             │
└──────────┬──────────┬──────────┬──────────┬─────────┘
           │          │          │          │
       REST API    WebSocket   R2 URL    FCM/APNs
       (HTTPS)    (WSS)       (CDN)      Push
           │          │          │          │
┌──────────▼──────────▼──────────┘          │
│              FastAPI Server                │
│  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │  Router   │  │WebSocket │  │Scheduler│ │
│  │ (API 엔드 │  │(실시간    │  │(APSched │ │
│  │  포인트)   │  │ 위치공유) │  │  uler)  │ │
│  └──────────┘  └──────────┘  └─────────┘ │
│  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │SQLAlchemy│  │  Redis   │  │  boto3  │ │
│  │(ORM+Geo) │  │ (캐시)   │  │ (R2/S3) │ │
│  └────┬─────┘  └──────────┘  └─────────┘ │
└───────┼──────────────────────────────────-┘
        │              │              │
 ┌──────▼──────┐ ┌─────▼─────┐ ┌─────▼──────┐
 │ PostgreSQL  │ │Cloudflare │ │ External   │
 │  + PostGIS  │ │    R2     │ │   APIs     │
 │  (자체 DB)  │ │  (파일)   │ │기상청/에어코리아│
 └─────────────┘ └───────────┘ │카카오/FCM/Toss│
                               └─────────────┘
```

---

## 3. 프로젝트 구조

```
backend/
├── app/
│   ├── main.py                 # FastAPI 앱 진입점
│   ├── config.py               # 환경 변수 설정 (pydantic-settings)
│   ├── database.py             # SQLAlchemy 엔진 + 세션
│   ├── dependencies.py         # 공통 의존성 (get_db, get_current_user)
│   │
│   ├── models/                 # SQLAlchemy ORM 모델
│   │   ├── user.py
│   │   ├── pet.py
│   │   ├── walk.py
│   │   ├── badge.py
│   │   ├── ranking.py
│   │   ├── social.py
│   │   ├── notification.py
│   │   └── subscription.py
│   │
│   ├── schemas/                # Pydantic 요청/응답 스키마
│   │   ├── user.py
│   │   ├── pet.py
│   │   ├── walk.py
│   │   ├── badge.py
│   │   └── ...
│   │
│   ├── routers/                # API 라우터 (엔드포인트)
│   │   ├── auth.py             # 소셜 로그인, 토큰 관리
│   │   ├── users.py            # 사용자 CRUD
│   │   ├── pets.py             # 반려동물 CRUD
│   │   ├── walks.py            # 산책 CRUD + 유효성 검증
│   │   ├── badges.py           # 뱃지 조회
│   │   ├── rankings.py         # 랭킹 조회
│   │   ├── social.py           # 팔로우, 피드, 좋아요, 댓글
│   │   ├── invitations.py      # 산책 초대
│   │   ├── meetups.py          # 산책 모임
│   │   ├── notifications.py    # 알림 조회/읽음
│   │   ├── payments.py         # 결제 웹훅
│   │   ├── weather.py          # 날씨/미세먼지
│   │   └── upload.py           # 파일 업로드
│   │
│   ├── services/               # 비즈니스 로직
│   │   ├── walk_service.py     # 산책 유효성 검증, 완료 처리
│   │   ├── badge_service.py    # 뱃지 진행률 계산
│   │   ├── ranking_service.py  # 랭킹 집계
│   │   ├── push_service.py     # 푸시 알림 전송
│   │   ├── payment_service.py  # 결제 처리
│   │   ├── weather_service.py  # 날씨 API 호출 + 캐싱
│   │   ├── recommend_service.py# 친구 추천
│   │   └── storage_service.py  # R2 파일 업로드
│   │
│   ├── scheduler/              # APScheduler 작업
│   │   ├── jobs.py             # Cron Job 정의
│   │   └── tasks.py            # 실행 태스크
│   │
│   └── websocket/              # WebSocket 핸들러
│       └── walk_together.py    # 함께 산책 위치 공유
│
├── alembic/                    # DB 마이그레이션
│   ├── alembic.ini
│   └── versions/
│
├── requirements.txt
├── Dockerfile
├── render.yaml                 # Render 배포 설정
└── .env
```

---

## 4. 백엔드 핵심 도메인

| # | 도메인 | 상세 문서 | 핵심 내용 |
|---|--------|----------|----------|
| 1 | **데이터베이스 스키마** | [01_database_schema.md](./01_database_schema.md) | 전체 테이블 정의, 관계, 인덱스, Stored Procedures |
| 2 | **인증 시스템** | [02_auth.md](./02_auth.md) | 카카오/네이버/Apple 소셜 로그인, JWT 토큰 관리 |
| 3 | **API 라우트 및 서비스** | [03_api_routes.md](./03_api_routes.md) | 뱃지 진행률, 랭킹 집계, 친구 추천, 산책 유효성 검증 |
| 4 | **외부 API 연동** | [04_external_apis.md](./04_external_apis.md) | 기상청, 에어코리아, 공공데이터, 카카오 로컬 API |
| 5 | **푸시 알림** | [05_push_notifications.md](./05_push_notifications.md) | FCM/APNs 전략, 7가지 알림 유형, 빈도 제한 |
| 6 | **결제 시스템** | [06_payment.md](./06_payment.md) | Toss Payments, iOS IAP, Google Play Billing, 구독 관리 |
| 7 | **실시간 기능** | [07_realtime.md](./07_realtime.md) | FastAPI WebSocket, 함께 산책 위치 공유 |
| 8 | **파일 저장소** | [08_storage.md](./08_storage.md) | Cloudflare R2, 프로필/산책 사진, 공유 카드 |
| 9 | **구현 로드맵** | [09_roadmap.md](./09_roadmap.md) | 5단계 구현 순서, 체크리스트 |

---

## 5. 데이터 모델 요약

### 5.1 핵심 테이블 (19개)

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

### 5.2 테이블별 역할 요약

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

> 전체 스키마 정의(CREATE TABLE, 인덱스)는 [01_database_schema.md](./01_database_schema.md) 참조

---

## 6. API 서비스 모듈 목록

| 모듈 | 트리거 | 역할 |
|------|--------|------|
| `walk_service.validate_walk()` | 산책 저장 전 | 부정행위 필터 (시속 15km+, GPS 스푸핑, 500m 미만) |
| `walk_service.on_walk_complete()` | 산책 완료 시 | 뱃지 진행률 업데이트, 랭킹 재계산, 연속일수 계산 |
| `badge_service.check_progress()` | on_walk_complete 내부 | 6개 카테고리 뱃지 조건 검사 |
| `ranking_service.calculate()` | APScheduler (1시간마다) | 주간/월간/전체 랭킹 집계 |
| `recommend_service.get_recommendations()` | APScheduler (12시간마다) | 친구 추천 알고리즘 실행 |
| `push_service.send()` | 이벤트 발생 시 | FCM/APNs 푸시 알림 전송 |
| `weather_service.cache_weather()` | APScheduler (1시간마다) | 기상청/에어코리아 API 호출 후 캐싱 |
| `payment_service.process_webhook()` | 결제 웹훅 수신 | Toss Payments 결제 확인, 구독 상태 업데이트 |

> 상세 로직은 [03_api_routes.md](./03_api_routes.md) 참조

---

## 7. 개발 우선순위 (MVP 기준)

### Phase 1: MVP 핵심 (1~2주차)

| 순서 | 작업 | 관련 문서 |
|------|------|----------|
| 1 | FastAPI 프로젝트 셋업 + SQLAlchemy + Alembic | 본 문서 §3 |
| 2 | DB 스키마 마이그레이션 (users, pets, walks, push_tokens) | 01_database_schema.md |
| 3 | JWT 인증 + 카카오/네이버/Apple OAuth | 02_auth.md |
| 4 | 산책 데이터 CRUD API | 03_api_routes.md |
| 5 | validate-walk 서비스 | 03_api_routes.md |
| 6 | R2 파일 업로드 설정 | 08_storage.md |

### Phase 2: 게이미피케이션 (3주차)

| 순서 | 작업 | 관련 문서 |
|------|------|----------|
| 7 | badge_definitions 시드 데이터 (47개 뱃지) | 01_database_schema.md |
| 8 | on-walk-complete → 뱃지 진행률 업데이트 | 03_api_routes.md |
| 9 | calculate-rankings APScheduler Job | 03_api_routes.md |
| 10 | 푸시 알림 (산책 리마인더, 뱃지 획득) | 05_push_notifications.md |

### Phase 3: 소셜 (4주차)

| 순서 | 작업 | 관련 문서 |
|------|------|----------|
| 11 | follows, likes, comments API | 03_api_routes.md |
| 12 | 산책 피드 API + 정렬 알고리즘 | 03_api_routes.md |
| 13 | recommend-friends 친구 추천 | 03_api_routes.md |
| 14 | 산책 초대 + 모임 게시판 | 03_api_routes.md |

### Phase 4: 수익화 (5주차)

| 순서 | 작업 | 관련 문서 |
|------|------|----------|
| 15 | Toss Payments 연동 | 06_payment.md |
| 16 | iOS IAP / Google Play Billing | 06_payment.md |
| 17 | 구독 상태 관리 + 프리미엄 기능 잠금 | 06_payment.md |
| 18 | 외부 API 연동 (기상청, 에어코리아) | 04_external_apis.md |

---

## 8. 환경 구성

### 8.1 배포 환경

```
플랫폼: Render
서비스 타입: Web Service (Docker)
리전: Oregon (US West) — 한국 사용자 대상이지만 Render는 미국 리전만 제공
플랜: Free → Starter ($7/월) 전환 시점: 슬립 없는 서비스 필요 시
```

### 8.2 환경 변수 (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/withbowwow

# JWT
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# 소셜 로그인
KAKAO_CLIENT_ID=
KAKAO_CLIENT_SECRET=
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
APPLE_CLIENT_ID=
APPLE_TEAM_ID=
APPLE_KEY_ID=
APPLE_PRIVATE_KEY=

# Redis
REDIS_URL=redis://localhost:6379

# 외부 API
WEATHER_API_KEY=          # 기상청 공공데이터 포털
AIR_KOREA_API_KEY=        # 에어코리아
PUBLIC_DATA_API_KEY=      # 공공데이터 (동물병원 등)
KAKAO_REST_API_KEY=       # 카카오 로컬 검색

# 푸시 알림
FIREBASE_CREDENTIALS_JSON= # Firebase 서비스 계정 JSON (Base64)

# 결제
TOSS_CLIENT_KEY=
TOSS_SECRET_KEY=

# Storage (Cloudflare R2)
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=withbowwow
R2_PUBLIC_URL=https://pub-xxx.r2.dev
```

### 8.3 주요 의존성 (requirements.txt)

```
fastapi>=0.110.0
uvicorn[standard]>=0.27.0
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
alembic>=1.13.0
geoalchemy2>=0.14.0
pydantic>=2.6.0
pydantic-settings>=2.1.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
httpx>=0.27.0
firebase-admin>=6.4.0
apscheduler>=3.10.0
redis>=5.0.0
boto3>=1.34.0
python-multipart>=0.0.9
pillow>=10.2.0
```

---

*작성일: 2026-02-12*
*버전: 2.0 — FastAPI + PostgreSQL + Render 스택으로 전환*
