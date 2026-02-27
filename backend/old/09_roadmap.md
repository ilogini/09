# 백엔드 구현 로드맵 - 멍이랑 (withbowwow)

> 코어 파일: [00_overview.md](./00_overview.md)
> 스택: Python 3.11+ / FastAPI / SQLAlchemy 2.0 / PostgreSQL / Render
> 총 예상 기간: 5~6주 (1인 기준)
> 전제: 프론트엔드(React Native)와 병행 개발, 백엔드 전담

---

## 전체 타임라인

```
Phase 1 (1~2주) ──→ Phase 2 (3주) ──→ Phase 3 (4주) ──→ Phase 4 (5주) ──→ Phase 5 (6주)
   환경 셋업          게이미피케이션        소셜              수익화           안정화
   인증 + DB          뱃지 + 랭킹         피드 + 친구        결제 + 외부API    테스트 + 배포
   산책 CRUD          푸시 알림           초대 + 모임        프리미엄 잠금      모니터링
```

---

## Phase 1: 기반 구축 + MVP 핵심 (1~2주차)

> 앱이 돌아가기 위한 최소 백엔드. 이 단계 끝나면 "산책 기록 + 저장"이 가능해야 한다.

### Week 1: 환경 + 인증 + 핵심 DB

| # | 작업 | 상세 | 산출물 | 참조 |
|---|------|------|--------|------|
| 1-1 | **FastAPI 프로젝트 셋업** | 프로젝트 구조, requirements.txt, Dockerfile, render.yaml | 실행 가능한 FastAPI 앱 | 00_overview.md §3 |
| 1-2 | **SQLAlchemy + Alembic 설정** | database.py, ORM 모델, 마이그레이션 환경 | DB 연결 + 첫 마이그레이션 | 00_overview.md §3 |
| 1-3 | **핵심 테이블 마이그레이션** | `users`, `pets`, `pet_health`, `walks`, `walk_photos` | Alembic 마이그레이션 파일 | 01_database_schema.md §2.1~2.5 |
| 1-4 | **PostGIS 확장 활성화** | PostgreSQL에 PostGIS 설치 + GeoAlchemy2 설정 | 공간 쿼리 가능 | 01_database_schema.md §2.4 |
| 1-5 | **JWT 인증 구현** | python-jose로 JWT 발급/검증, get_current_user 의존성 | 인증 미들웨어 | 02_auth.md §2~4 |
| 1-6 | **카카오 OAuth 연동** | httpx로 카카오 토큰 교환 + 사용자 정보 조회 | POST /auth/kakao | 02_auth.md §1.3 |
| 1-7 | **네이버/Apple 로그인** | 나머지 소셜 로그인 구현 | 3개 소셜 로그인 동작 | 02_auth.md §1.3 |

### Week 2: 산책 데이터 + 저장소

| # | 작업 | 상세 | 산출물 | 참조 |
|---|------|------|--------|------|
| 2-1 | **사용자/반려동물 CRUD API** | GET/POST/PATCH /users, /pets 엔드포인트 | Swagger에서 테스트 가능 | 03_api_routes.md §8 |
| 2-2 | **산책 CRUD API** | POST /walks (시작), POST /walks/{id}/complete (완료), GET /walks | 산책 기록 API | 03_api_routes.md §3 |
| 2-3 | **validate_walk 서비스** | 500m 미만 필터, 시속 15km+ 필터, GPS 스푸핑 감지 | walk_service.py | 03_api_routes.md §2 |
| 2-4 | **R2 스토리지 설정** | Cloudflare R2 버킷 생성, boto3 클라이언트 설정 | storage_service.py | 08_storage.md §1~2 |
| 2-5 | **사진 업로드 API** | POST /upload/pet-profile, /upload/walk-photo + Pillow 리사이즈 | 업로드 엔드포인트 | 08_storage.md §3 |
| 2-6 | **push_tokens 테이블** | 푸시 토큰 저장/업데이트 API | POST /push-tokens | 01_database_schema.md §2.15 |
| 2-7 | **연속일수 계산 함수** | `calculate_streak_days` Stored Procedure 생성 | DB 함수 | 01_database_schema.md §5.1 |

### Phase 1 완료 기준

- [ ] 소셜 로그인 (카카오/네이버/Apple) 동작
- [ ] 반려동물 등록/수정/조회 가능
- [ ] 산책 시작 → GPS 경로 저장 → 산책 완료 플로우 동작
- [ ] 산책 사진 업로드/조회 가능
- [ ] 부정행위 필터링 (500m 미만, 시속 15km+ 제외) 동작
- [ ] Swagger UI (`/docs`)에서 전체 API 테스트 가능

---

## Phase 2: 게이미피케이션 (3주차)

> 뱃지 시스템 + 랭킹 + 푸시 알림. 이 단계 끝나면 "산책하면 뱃지 획득 + 랭킹 반영"이 된다.

| # | 작업 | 상세 | 산출물 | 참조 |
|---|------|------|--------|------|
| 3-1 | **badge_definitions 테이블 + 시드** | 뱃지 정의 테이블 + 45개 뱃지 INSERT | Alembic + 시드 SQL | 01_database_schema.md §2.6, §3 |
| 3-2 | **user_badges 테이블** | 사용자별 뱃지 상태 테이블 | Alembic 마이그레이션 | 01_database_schema.md §2.7 |
| 3-3 | **on_walk_complete 서비스** | 산책 완료 → BackgroundTasks로 뱃지/랭킹/푸시 처리 | walk_service.py | 03_api_routes.md §3 |
| 3-4 | **badge_service.check_progress** | 6개 카테고리별 뱃지 조건 검사 | badge_service.py | 03_api_routes.md §4 |
| 3-5 | **rankings 테이블 + 집계** | 랭킹 테이블 + `refresh_weekly_rankings` Stored Procedure | 테이블 + DB 함수 | 01_database_schema.md §2.8, §5.2 |
| 3-6 | **APScheduler 설정** | 매시간 랭킹 집계, 12시간 친구 추천, 매시간 날씨 캐싱 | scheduler/jobs.py | 03_api_routes.md §5.1 |
| 3-7 | **hall_of_fame 테이블** | 명예의 전당 테이블 + 월간/분기 배치 집계 | 테이블 + Cron | 01_database_schema.md §2.9 |
| 3-8 | **Firebase Admin 초기화 + push_service** | FCM 연동, 푸시 알림 전송 | push_service.py | 05_push_notifications.md §4 |
| 3-9 | **notifications 테이블** | 알림 내역 저장 + 읽음 처리 API | GET/PATCH /notifications | 01_database_schema.md §2.16 |
| 3-10 | **뱃지/랭킹 알림 연결** | on_walk_complete에서 push_service 호출 | 알림 트리거 연결 | 05_push_notifications.md §2 |

### Phase 2 완료 기준

- [ ] 산책 완료 → 뱃지 진행률 자동 업데이트
- [ ] 뱃지 조건 달성 시 자동 획득 (earned 상태)
- [ ] 주간/월간/전체 랭킹 자동 집계
- [ ] 동/구/전국 단위 지역 랭킹 필터
- [ ] 뱃지 획득 시 푸시 알림 수신
- [ ] 랭킹 변동 시 푸시 알림 수신

---

## Phase 3: 소셜 (4주차)

> 팔로우, 피드, 초대, 모임. 이 단계 끝나면 "다른 사용자와 교류"가 가능하다.

| # | 작업 | 상세 | 산출물 | 참조 |
|---|------|------|--------|------|
| 4-1 | **소셜 테이블 마이그레이션** | `follows`, `likes`, `comments`, `blocks`, `reports` | Alembic 마이그레이션 | 01_database_schema.md §2.10~2.12, §2.18~2.19 |
| 4-2 | **팔로우 API** | POST/DELETE /follows/{user_id}, GET /followers, /following | 팔로우 CRUD | 03_api_routes.md §8 |
| 4-3 | **산책 피드 API** | GET /feed — 팔로잉 + 동네 피드 (정렬 알고리즘 적용) | feed_service.py | 03_api_routes.md §7 |
| 4-4 | **좋아요/댓글 API** | POST/DELETE /likes/{walk_id}, POST /comments | 좋아요/댓글 CRUD | 03_api_routes.md §8 |
| 4-5 | **recommend_service** | 친구 추천 알고리즘 (지역40% + 시간25% + 견종20% + 활동량15%) | recommend_service.py | 03_api_routes.md §6 |
| 4-6 | **invitations 테이블 + API** | 산책 초대 생성/수락/거절/만료 | POST/PATCH /invitations | 01_database_schema.md §2.13 |
| 4-7 | **WebSocket: 함께 산책** | 산책 중 실시간 위치 공유 | websocket/walk_together.py | 07_realtime.md §2 |
| 4-8 | **meetups 테이블 + API** | 산책 모임 게시판 CRUD + 참가 신청 | GET/POST /meetups | 01_database_schema.md §2.14 |
| 4-9 | **소셜 푸시 알림** | 팔로우/좋아요/댓글/초대 시 푸시 알림 | push_service 호출 | 05_push_notifications.md §2.5 |
| 4-10 | **차단/신고 기능** | blocks/reports 테이블 + 차단 시 피드/추천에서 제외 | 필터링 로직 | 01_database_schema.md §2.18~2.19 |

### Phase 3 완료 기준

- [ ] 팔로우/언팔로우 동작
- [ ] 소셜 피드에서 팔로잉 사용자 산책 기록 조회
- [ ] 좋아요/댓글 동작
- [ ] 친구 추천 알고리즘 동작
- [ ] 함께 산책 WebSocket 위치 공유
- [ ] 산책 초대/모임 동작
- [ ] 차단/신고 기능 동작

---

## Phase 4: 수익화 + 외부 API (5주차)

> 프리미엄 구독, 결제, 날씨/미세먼지 API. 이 단계 끝나면 "돈을 벌 수 있다".

| # | 작업 | 상세 | 산출물 | 참조 |
|---|------|------|--------|------|
| 5-1 | **subscriptions 테이블** | 구독/결제 이력 테이블 | Alembic 마이그레이션 | 01_database_schema.md §2.17 |
| 5-2 | **iOS IAP 웹훅** | POST /payments/webhook/apple — App Store Notification v2 처리 | payment_service.py | 06_payment.md §3 |
| 5-3 | **Google Play 웹훅** | POST /payments/webhook/google — RTDN 처리 | payment_service.py | 06_payment.md §4 |
| 5-4 | **Toss Payments 연동** | POST /payments/confirm — 결제 승인 + 빌링키 정기결제 | payment_service.py | 06_payment.md §5 |
| 5-5 | **구독 상태 관리** | trial(7일) → active → cancelled → expired + APScheduler Cron | 상태 머신 로직 | 06_payment.md §6 |
| 5-6 | **프리미엄 기능 잠금** | require_premium 의존성으로 프리미엄 전용 API 분기 | dependencies.py | 01_database_schema.md §4 |
| 5-7 | **Redis 설정** | Redis 연결 설정 (Render에서 Redis 추가 또는 Upstash 무료) | config.py | 00_overview.md §8.2 |
| 5-8 | **weather_service** | 기상청 + 에어코리아 API → Redis 캐싱 + 산책 적합도 | weather_service.py | 04_external_apis.md §2~4 |
| 5-9 | **공공데이터 동기화** | 동물병원/반려동물 공원 데이터 주기적 DB 동기화 | APScheduler 작업 | 04_external_apis.md §5 |
| 5-10 | **카카오 로컬 검색 프록시** | 카카오 API 키를 서버에서 관리, 프론트에 프록시 | GET /places/search | 04_external_apis.md §6 |

### Phase 4 완료 기준

- [ ] 프리미엄 구독 결제 가능 (IAP + Toss)
- [ ] 무료체험 7일 → 자동 결제 전환
- [ ] 프리미엄 사용자 기능 분기 동작
- [ ] 홈 화면 날씨/미세먼지 위젯 데이터 제공
- [ ] 산책 적합도 판정 동작
- [ ] 주변 동물병원/공원/카페 데이터 제공

---

## Phase 5: 안정화 + 배포 준비 (6주차)

> 테스트, 모니터링, 성능 최적화, 스토어 심사 준비.

| # | 작업 | 상세 | 산출물 |
|---|------|------|--------|
| 6-1 | **API 에러 핸들링** | 전역 예외 핸들러 + 에러 응답 표준화 | middleware.py |
| 6-2 | **DB 쿼리 최적화** | 느린 쿼리 분석 + 인덱스 튜닝 (EXPLAIN ANALYZE) | 최적화 보고서 |
| 6-3 | **API 보안 검증** | 접근 제어 테스트, JWT 만료 테스트, 입력 유효성 검증 | 보안 체크리스트 |
| 6-4 | **부하 테스트** | locust 또는 k6로 동시 사용자 100명 시뮬레이션 | 성능 보고서 |
| 6-5 | **Render 배포** | render.yaml 작성, GitHub 연동, 자동 배포 설정 | 배포 환경 |
| 6-6 | **모니터링 설정** | Sentry (에러 트래킹), Render Dashboard (리소스 모니터링) | 모니터링 대시보드 |
| 6-7 | **계정 삭제 Cron** | deleted_at + 30일 경과 사용자 완전 삭제 | APScheduler 작업 |
| 6-8 | **구독 만료 Cron** | premium_until 경과 시 자동 무료 전환 | APScheduler 작업 |
| 6-9 | **시즌 뱃지 마감 알림** | 시즌 종료 7일/3일/1일 전 푸시 | APScheduler 작업 |
| 6-10 | **공유 카드 생성** | 산책 완료 시 SNS 공유용 이미지 서버 생성 (Pillow) | 이미지 생성 서비스 |

### Phase 5 완료 기준

- [ ] 모든 API 에러 핸들링 완료
- [ ] 주요 쿼리 응답 시간 200ms 이내
- [ ] 보안 검증 통과
- [ ] Cron Job 모두 정상 동작
- [ ] Sentry 모니터링 연동
- [ ] Render 배포 완료

---

## 구현 기능 전체 체크리스트 (34개)

### 인프라/환경 (3개)
- [ ] FastAPI 프로젝트 셋업 + SQLAlchemy + Alembic
- [ ] Cloudflare R2 버킷 생성 + boto3 연결
- [ ] 환경 변수(.env) 설정 + pydantic-settings

### 인증 (4개)
- [ ] 카카오 OAuth 로그인
- [ ] 네이버 OAuth 로그인
- [ ] Apple Sign in 로그인
- [ ] JWT 발급/갱신/검증 (python-jose)

### 데이터베이스 (5개)
- [ ] 핵심 테이블 마이그레이션 (19개 테이블)
- [ ] 접근 제어 의존성 (get_current_user, require_premium)
- [ ] 인덱스 설정 (PostGIS GIST 포함)
- [ ] Stored Procedures (연속일수, 랭킹 집계, 고유 장소)
- [ ] 뱃지 시드 데이터 45개 INSERT

### API 서비스 (8개)
- [ ] validate_walk (산책 유효성 검증)
- [ ] on_walk_complete (산책 완료 → BackgroundTasks)
- [ ] badge_service.check_progress (뱃지 6카테고리 진행률)
- [ ] ranking_service.calculate (랭킹 APScheduler 집계)
- [ ] recommend_service (친구 추천 알고리즘)
- [ ] push_service.send (FCM/APNs 푸시 전송)
- [ ] weather_service.cache_weather (기상청/에어코리아 + Redis)
- [ ] payment_service.process_webhook (결제 웹훅 처리)

### 외부 API (4개)
- [ ] 기상청 단기예보 API + GPS→격자 변환
- [ ] 에어코리아 미세먼지 API
- [ ] 공공데이터 (동물병원, 반려동물 공원)
- [ ] 카카오 로컬 검색 API

### 푸시 알림 (3개)
- [ ] Firebase Admin 초기화 + 토큰 관리
- [ ] 7가지 알림 유형 구현
- [ ] 빈도 제한 정책 (일 10회, 야간 금지 등)

### 결제 (4개)
- [ ] iOS IAP (App Store Server Notification v2)
- [ ] Google Play Billing (RTDN)
- [ ] Toss Payments (결제 승인 + 빌링키)
- [ ] 구독 상태 머신 (trial → active → cancelled → expired)

### Cron Jobs — APScheduler (3개)
- [ ] 랭킹 집계 (매시간)
- [ ] 날씨 캐싱 (매시간)
- [ ] 계정 삭제/구독 만료 정리 (매일)

---

## 의존 관계 다이어그램

```
Phase 1                    Phase 2                  Phase 3              Phase 4
────────                   ────────                 ────────             ────────
[FastAPI 셋업] ──┐
                 ├→ [핵심 DB] ─┐
[JWT 인증] ─────┘             │
                               ├→ [뱃지 시드] ──→ [badge_service] ─┐
[walks CRUD] ──→ [validate] ──┤                                    │
                               ├→ [rankings] ──→ [APScheduler]     │
[R2 설정] ──→ [사진 API]      │                                    │
                               └→ [push_service] ─────────────────┤
                                                                    │
                                  [follows/likes] ──→ [피드 API] ──┤→ [결제 연동]
                                  [WebSocket] ──→ [함께 산책]       │→ [프리미엄 잠금]
                                  [recommend] ──→ [친구 추천]       │→ [날씨 API]
                                  [invitations] ──→ [산책 초대]     │
                                  [meetups] ──→ [모임 게시판]       │
```

---

*작성일: 2026-02-12*
*버전: 2.0 — FastAPI + PostgreSQL + Render 스택으로 전환*
