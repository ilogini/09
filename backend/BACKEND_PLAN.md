# 멍이랑 백엔드 구현 기획서

> 이 문서는 백엔드 구현의 **마스터 플랜**입니다.
> 기존 설계 문서(00~09)는 참고용으로 유지하고, 실제 구현은 이 문서를 기준으로 진행합니다.
> 프로토타입 HTML 페이지를 기준으로 필요한 API를 도출했습니다.

---

## 0. 현재 상태 (2026-02-26 기준)

### 살릴 수 있는 것 (이미 구현됨)

| 기능 | 파일 | 판단 |
|------|------|------|
| FastAPI 서버 구조 | main.py, config.py, database.py | **유지** |
| JWT 인증 + 소셜 로그인 (카카오/네이버/Apple) | routers/auth.py, dependencies.py | **유지** |
| 사용자 조회/수정 | routers/users.py | **유지** |
| 반려동물 CRUD | routers/pets.py, models/pet.py | **유지** |
| 산책 CRUD + 유효성 검증 | routers/walks.py, models/walk.py | **유지** |
| Docker + Alembic 설정 | Dockerfile, alembic/ | **유지** |
| 환경 변수 분리 (.env + Render) | config.py, .env.example | **유지** |

### 재검토 필요

| 항목 | 현재 상태 | 판단 |
|------|----------|--------|
| PostGIS geometry 컬럼 | Walk 모델에 추가됨 | 지도 기능 최우선이므로 **유지** |
| Apple 로그인 | 코드 있음 | iOS 심사 필수이므로 **유지** |
| 테이블 23개 설계 | 문서에만 존재 | Phase별 순차 구현 |

---

## 1. 우선순위 결정 (확정)

### Q1. MVP에서 반드시 있어야 하는 기능은?
- [x] 산책 기록 (GPS 트래킹 + 저장) — **최우선**
- [x] 지도 (주변 장소) — **최우선**
- [x] 소셜 로그인
- [x] 반려동물 등록
- [x] 뱃지 시스템
- [x] 랭킹/리더보드
- [x] 소셜 (팔로우/좋아요/댓글)
- [ ] 결제/프리미엄 — 후순위
- [ ] 푸시 알림 — 후순위

> **핵심**: 산책 트래킹이 작동하는 것이 가장 우선. 지도가 최우선도.

### Q2. 첫 테스트 배포 목표는?
- [x] 내부 테스트 (개발팀만)

### Q3. 프론트엔드 개발자가 당장 필요한 API는?
- 프론트는 디자인 확정 후 개발 시작 예정 → 백엔드 우선 기획

---

## 2. 프로토타입 페이지별 API 분석

> 각 프로토타입 HTML 페이지에서 도출한 필요 API와 구현 상태

### 페이지 1: 로그인 / 온보딩
> `로그인.html`, `온보딩.html`

| 필요 API | 설명 | 구현 상태 | Phase |
|----------|------|----------|-------|
| `POST /auth/kakao` | 카카오 로그인 | **완료** | 1 |
| `POST /auth/naver` | 네이버 로그인 | **완료** | 1 |
| `POST /auth/apple` | Apple 로그인 | **완료** | 1 |
| `POST /auth/refresh` | 토큰 갱신 | **완료** | 1 |
| `POST /auth/logout` | 로그아웃 | **완료** | 1 |
| `GET /auth/onboarding-status` | 온보딩 완료 여부 확인 | **TODO** | 1 |
| `DELETE /users/me` | 회원 탈퇴 (soft delete, 30일 유예) | **TODO** | 1 |

> **참고**: Google 로그인은 `로그인.html`에만 있고 `온보딩.html`에는 없음 → MVP 보류

### 페이지 2: 메인페이지 (홈)
> `메인페이지.html` — 앱의 중심 화면, 기능 집약도 높음

| 필요 API | 설명 | 구현 상태 | Phase |
|----------|------|----------|-------|
| `GET /walks/weekly-summary` | 주간 요약 (총 거리/횟수/시간, 목표 달성률) | **TODO (신규)** | 1 |
| `GET /walks?page=1&size=2` | 최근 산책 2건 | **완료** | 1 |
| `GET /pets` | 산책 시작 시 펫 선택 | **완료** | 1 |
| `POST /walks` | 산책 시작 | **완료** | 1 |
| `POST /walks/{id}/complete` | 산책 완료 | **완료** | 1 |
| `POST /walks/{id}/photos` | 산책 중 사진 촬영 | **TODO** | 1 |
| `GET /weather` | 날씨/미세먼지/산책 추천 | **TODO** | 4 |
| `GET /badges/in-progress` | 진행 중 챌린지 4건 | **TODO** | 2 |
| `GET /places/nearby` | 주변 장소 미니맵 | **TODO** | 4 |
| `GET /notifications/unread-count` | 알림 뱃지 | **TODO** | 4 |
| `GET /subscriptions/me` | 프리미엄 배너 노출 여부 | **TODO** | 4 |

> **GPS 트래킹 자체는 프론트 전용** (watchPosition → route_geojson으로 서버 전송)
> **산책 완료 응답에 뱃지 정보 포함** 필요 (Phase 2에서 `earned_badges` 필드 추가)

### 페이지 3: 산책기록
> `산책기록.html` — 산책 히스토리, 통계

| 필요 API | 설명 | 구현 상태 | Phase |
|----------|------|----------|-------|
| `GET /walks/stats` | 누적 통계 (총 횟수/거리/시간/칼로리) | **TODO (신규)** | 1 |
| `GET /walks?period=weekly` | 기간별 산책 목록 (주/월/년 필터) | **완료** (필터 추가 필요) | 1 |

> 기존 `GET /walks`에 `period` 쿼리 파라미터 추가 필요

### 페이지 4: 산책상세
> `산책상세.html` — 단일 산책 상세 정보

| 필요 API | 설명 | 구현 상태 | Phase |
|----------|------|----------|-------|
| `GET /walks/{id}` | 산책 상세 (경로, 통계, 사진 포함) | **완료** | 1 |

> 경로 지도, 구간별 속도 차트, 사진 갤러리는 프론트에서 `route_geojson` + `photos` 데이터로 렌더링
> 공유(카카오/인스타)는 클라이언트 SDK 사용

### 페이지 5: 지도 (**최우선**)
> `지도.html` — 전체 화면 지도, 장소 검색

| 필요 API | 설명 | 구현 상태 | Phase |
|----------|------|----------|-------|
| `GET /places/nearby` | 주변 장소 (공원/카페/병원/약국) `?lat=&lng=&type=&radius=` | **TODO** | 1* |
| `GET /places/search` | 장소 검색 `?q=keyword` | **TODO (신규)** | 1* |
| `GET /places/{id}` | 장소 상세 | **TODO (신규)** | 1* |

> **사용자 요구: 지도가 최우선도** → 원래 Phase 4이지만 **Phase 1로 승격**
> 외부 API 연동 필요: 카카오맵 API 또는 Google Places API

### 페이지 6: 마이페이지
> `마이페이지.html` — 프로필, 펫, 뱃지, 통계

| 필요 API | 설명 | 구현 상태 | Phase |
|----------|------|----------|-------|
| `GET /users/me` | 프로필 정보 | **완료** | 1 |
| `PATCH /users/me` | 프로필 수정 | **완료** | 1 |
| `GET /pets` | 내 펫 목록 | **완료** | 1 |
| `GET /walks/stats` | 누적 통계 | **TODO (신규)** | 1 |
| `GET /users/me/grade` | 내 등급/레벨 | **TODO** | 2 |
| `GET /badges` | 뱃지 컬렉션 (진행률 포함) | **TODO** | 2 |
| `GET /follows/count` | 팔로잉/팔로워 수 | **TODO (신규)** | 3 |

### 페이지 7: 뱃지
> `뱃지.html` — 뱃지 컬렉션, 6개 카테고리

| 필요 API | 설명 | 구현 상태 | Phase |
|----------|------|----------|-------|
| `GET /badges` | 전체 뱃지 목록 (카테고리별, 진행률 포함) | **TODO** | 2 |
| `GET /badges/{id}` | 뱃지 상세 | **TODO** | 2 |

> 6개 카테고리: 거리, 연속, 탐험, 시간, 특별, 시즌

### 페이지 8: 랭킹
> `랭킹.html` — 주간/월간/전체, 지역별

| 필요 API | 설명 | 구현 상태 | Phase |
|----------|------|----------|-------|
| `GET /rankings/weekly` | 주간 랭킹 `?region=` | **TODO** | 2 |
| `GET /rankings/monthly` | 월간 랭킹 `?region=` | **TODO** | 2 |
| `GET /rankings/all-time` | 전체 랭킹 | **TODO (신규)** | 2 |
| `GET /rankings/me` | 내 현재 순위 | **TODO (신규)** | 2 |
| `GET /rankings/hall-of-fame` | 명예의 전당 | **TODO** | 2 |

> Top 3 포디움 + 4~10위 리스트 + 순위 변동 표시
> 지역 필터(구 단위) 필요

### 페이지 9: 소셜
> `소셜.html` — 3개 탭 (친구, 챌린지, 모임)

**친구 탭**
| 필요 API | 설명 | Phase |
|----------|------|-------|
| `GET /follows/following` | 내 친구 목록 | 3 |
| `GET /follows/followers` | 팔로워 목록 | 3 |
| `POST /follows/{user_id}` | 팔로우 | 3 |
| `DELETE /follows/{user_id}` | 언팔로우 | 3 |
| `GET /users/search` | 사용자 검색 (친구 찾기) | 3 (신규) |

**챌린지 탭**
| 필요 API | 설명 | Phase |
|----------|------|-------|
| `POST /challenges` | 챌린지 생성 | 3 (신규) |
| `GET /challenges` | 챌린지 목록 (월간/친구) | 3 (신규) |
| `GET /challenges/{id}` | 챌린지 상세 (리더보드 포함) | 3 (신규) |
| `POST /challenges/{id}/join` | 챌린지 참가 | 3 (신규) |

**모임 탭** (프로토타입에 UI 있으나 간략)
| 필요 API | 설명 | Phase |
|----------|------|-------|
| `GET /meetups` | 모임 목록 | 3 |
| `POST /meetups` | 모임 생성 | 3 |
| `POST /meetups/{id}/join` | 모임 참가 | 3 |

> **발견**: 프로토타입에 `challenges` 개념이 별도로 존재 (invitation과 다름)
> 챌린지 = 목표 기반 경쟁 (예: "주간 30km 도전"), invitation = 함께 산책 초대

### 페이지 10: 알림
> `알림.html` — 시간별 그룹, 다양한 알림 유형

| 필요 API | 설명 | 구현 상태 | Phase |
|----------|------|----------|-------|
| `GET /notifications` | 알림 목록 (그룹: 오늘/어제/이번주) | **TODO** | 4 |
| `PATCH /notifications/{id}/read` | 알림 읽음 처리 | **TODO** | 4 |
| `PATCH /notifications/read-all` | 모두 읽음 처리 | **TODO (신규)** | 4 |

> 알림 유형: badge, ranking, social, challenge, reminder, season, system

### 페이지 11: 설정
> `설정.html` — 알림 설정, 계정, 앱 정보

| 필요 API | 설명 | 구현 상태 | Phase |
|----------|------|----------|-------|
| `PATCH /users/me` | 알림 설정 저장 (notification_settings JSONB) | **완료** | 1 |
| `POST /auth/logout` | 로그아웃 | **완료** | 1 |
| `GET /subscriptions/me` | 현재 플랜 확인 | **TODO** | 4 |

> 알림 세부 설정: 산책 리마인더(시간 포함), 뱃지 획득, 소셜 알림

### 페이지 12: 프리미엄
> `프리미엄.html` — 구독 플랜, 결제

| 필요 API | 설명 | 구현 상태 | Phase |
|----------|------|----------|-------|
| `POST /payments/subscribe` | 구독 시작 | **TODO** | 4 |
| `GET /subscriptions/me` | 내 구독 상태 | **TODO** | 4 |

> 월간 ₩3,900 / 연간 ₩35,900 (23% 할인)
> 7일 무료 체험

---

## 3. Phase 구성 (확정)

> 프로토타입 분석 결과 반영, 사용자 우선순위 적용

### Phase 1: 핵심 MVP + 지도
> 목표: "로그인 → 펫 등록 → 산책 트래킹 → 결과 확인 → 지도에서 장소 검색"

**인증/계정**
- [x] 소셜 로그인 (카카오/네이버/Apple)
- [x] 토큰 갱신/로그아웃
- [ ] 온보딩 상태 확인 API
- [ ] 회원 탈퇴 (soft delete)

**반려동물**
- [x] CRUD 완료

**산책 (최우선)**
- [x] 산책 시작/완료/목록/상세
- [ ] `GET /walks/weekly-summary` — 주간 요약 (신규)
- [ ] `GET /walks/stats` — 누적 통계 (신규)
- [ ] `GET /walks` 기간 필터 추가 (period 파라미터)
- [ ] `POST /walks/{id}/photos` — 사진 업로드
- [ ] `GET /upload/presigned` — R2 presigned URL

**지도 (최우선 → Phase 4에서 승격)**
- [ ] `GET /places/nearby` — 주변 장소
- [ ] `GET /places/search` — 장소 검색
- [ ] `GET /places/{id}` — 장소 상세
- [ ] 외부 API 연동 (카카오맵 or Google Places)

**마이페이지**
- [x] 내 정보 조회/수정

### Phase 2: 게이미피케이션
> 목표: "산책하면 뭔가 쌓이는 재미"

- [ ] 뱃지 시스템 (45개, 6카테고리)
- [ ] `GET /badges`, `GET /badges/{id}`
- [ ] `GET /badges/in-progress` — 진행 중 뱃지
- [ ] 등급 시스템 (10단계)
- [ ] `GET /grades`, `GET /users/me/grade`
- [ ] 칭호 시스템 (10개)
- [ ] `GET /titles`, `PATCH /users/me/title`
- [ ] 랭킹 (주간/월간/전체, 지역별)
- [ ] `GET /rankings/weekly`, `GET /rankings/monthly`
- [ ] `GET /rankings/all-time`, `GET /rankings/me`
- [ ] `GET /rankings/hall-of-fame`
- [ ] 산책 완료 응답에 `earned_badges` 필드 추가

### Phase 3: 소셜
> 목표: "다른 사람과 연결"

- [ ] 팔로우/언팔로우
- [ ] `GET /follows/following`, `GET /follows/followers`, `GET /follows/count`
- [ ] 소셜 피드 (좋아요/댓글)
- [ ] `GET /feed`
- [ ] `POST/DELETE /walks/{id}/like`
- [ ] `GET/POST /walks/{id}/comments`, `DELETE /comments/{id}`
- [ ] 챌린지 시스템 (프로토타입 발견)
- [ ] `POST /challenges`, `GET /challenges`, `GET /challenges/{id}`
- [ ] `POST /challenges/{id}/join`
- [ ] 산책 초대
- [ ] `POST /invitations`, `GET /invitations`, `PATCH /invitations/{id}`
- [ ] 모임
- [ ] `GET /meetups`, `POST /meetups`, `POST /meetups/{id}/join`
- [ ] 사용자 검색, 차단, 신고
- [ ] `GET /users/search`, `POST/DELETE /blocks/{user_id}`, `POST /reports`

### Phase 4: 외부 연동 + 수익화
> 목표: "실용성 + 수익"

- [ ] 날씨/미세먼지 (`GET /weather`)
- [ ] 푸시 알림
- [ ] `POST /push-tokens`
- [ ] `GET /notifications`, `PATCH /notifications/{id}/read`, `PATCH /notifications/read-all`
- [ ] 프리미엄 구독 + 결제
- [ ] `POST /payments/subscribe`, `GET /subscriptions/me`
- [ ] 결제 웹훅 (Toss/Apple/Google)

### Phase 5: 안정화 + 출시
> 목표: "스토어 심사 통과"

- [ ] 에러 핸들링 표준화
- [ ] 보안 점검
- [ ] 성능 최적화
- [ ] 모니터링 (Sentry)

---

## 4. 기술 스택 (확정)

| 항목 | 선택 | 비고 |
|------|------|------|
| Language | Python 3.12 | |
| Framework | FastAPI | 자동 Swagger, async |
| ORM | SQLAlchemy 2.0 (async) | |
| DB | PostgreSQL 15+ | PostGIS 확장 포함 |
| Migration | Alembic | |
| Auth | python-jose (JWT) + httpx (OAuth) | |
| Deploy | Render (Docker) | Singapore 리전 |
| Cache | Redis | 날씨 캐싱, 빈도 제한 |
| Storage | Cloudflare R2 (boto3) | 사진 저장 |
| Push | firebase-admin | FCM/APNs |
| Payment | httpx → Toss Payments | |
| Scheduler | APScheduler | 랭킹 집계, 캐싱 |
| Map API | 카카오맵 API (or Google Places) | 장소 검색 |

---

## 5. DB 테이블 (Phase별)

### Phase 1 테이블
| 테이블 | 용도 | 구현 상태 |
|--------|------|----------|
| users | 사용자 | **완료** |
| pets | 반려동물 | **완료** |
| walks | 산책 기록 | **완료** |
| walk_photos | 산책 사진 | **완료** (모델만) |

> 지도/장소 데이터는 외부 API에서 실시간 조회 → 별도 테이블 불필요 (캐싱은 Redis)

### Phase 2 테이블
| 테이블 | 용도 |
|--------|------|
| badge_definitions | 뱃지 정의 (45개 시드) |
| user_badges | 사용자별 뱃지 상태 |
| grade_definitions | 등급 정의 (10단계 시드) |
| title_definitions | 칭호 정의 (10개 시드) |
| user_titles | 사용자별 칭호 |
| rankings | 주간/월간/전체 랭킹 |
| hall_of_fame | 명예의 전당 |

### Phase 3 테이블
| 테이블 | 용도 |
|--------|------|
| follows | 팔로우 관계 |
| likes | 좋아요 |
| comments | 댓글 |
| challenges | 챌린지 정의 (신규 발견) |
| challenge_participants | 챌린지 참가자 (신규 발견) |
| invitations | 산책 초대 |
| meetups | 산책 모임 |
| meetup_participants | 모임 참가자 |
| blocks | 차단 |
| reports | 신고 |

### Phase 4 테이블
| 테이블 | 용도 |
|--------|------|
| push_tokens | FCM/APNs 토큰 |
| notifications | 알림 내역 |
| subscriptions | 구독/결제 |

---

## 6. 신규 발견 사항 (프로토타입 분석)

프로토타입 분석 중 기존 기획에 없던 항목들:

| 항목 | 출처 | 설명 |
|------|------|------|
| `GET /walks/weekly-summary` | 메인페이지 | 이번 주 총 거리/횟수/시간 + 목표 달성률 |
| `GET /walks/stats` | 산책기록, 마이페이지 | 누적 통계 (총 횟수/거리/시간/칼로리) |
| `GET /places/search` | 지도 | 장소 키워드 검색 |
| `GET /rankings/all-time` | 랭킹 | 전체 기간 랭킹 (주간/월간 외) |
| `GET /rankings/me` | 랭킹 | 내 현재 순위 |
| `GET /follows/count` | 마이페이지 | 팔로잉/팔로워 수만 반환 |
| `PATCH /notifications/read-all` | 알림 | 모두 읽음 일괄 처리 |
| challenges 테이블 | 소셜 | invitation과 별개의 목표 기반 챌린지 |
| `GET /users/search` | 소셜 | 사용자 검색 (친구 찾기) |
| `GET /auth/onboarding-status` | 온보딩 | 첫 로그인 후 펫 등록 여부 확인 |

---

## 7. Phase 1 구현 TODO (우선순위순)

> Phase 1에서 구현해야 할 TODO 항목, 우선순위 내림차순

### 최우선 (산책 트래킹)
1. `GET /walks/weekly-summary` — 주간 요약 API 신규 개발
2. `GET /walks/stats` — 누적 통계 API 신규 개발
3. `GET /walks` 기간 필터 (`period` 파라미터) 추가

### 최우선 (지도)
4. 외부 지도 API 키 발급 (카카오맵 or Google Places)
5. `GET /places/nearby` — 주변 장소 검색 API
6. `GET /places/search` — 장소 키워드 검색 API

### 높음 (인증 보완)
7. `GET /auth/onboarding-status` — 온보딩 상태 확인
8. `DELETE /users/me` — 회원 탈퇴 (soft delete)

### 보통 (사진)
9. R2 presigned URL 발급 (`GET /upload/presigned`)
10. `POST /walks/{id}/photos` — 산책 사진 업로드

---

## 8. 서비스 모듈 (Phase별)

### Phase 1
| 서비스 | 역할 |
|--------|------|
| walk_stats_service.py | 주간 요약, 누적 통계 집계 |
| place_service.py | 외부 지도 API 연동, 장소 검색 |
| storage_service.py | R2 presigned URL + 이미지 리사이징 |

### Phase 2
| 서비스 | 역할 |
|--------|------|
| badge_service.py | 산책 완료 시 뱃지 진행률 계산 |
| ranking_service.py | 주간/월간 랭킹 집계 (APScheduler) |
| grade_service.py | 누적 거리 → 등급 계산 |

### Phase 3
| 서비스 | 역할 |
|--------|------|
| feed_service.py | 소셜 피드 정렬 알고리즘 |
| challenge_service.py | 챌린지 생성/참가/진행 관리 |
| recommend_service.py | 친구 추천 (지역/시간/견종 가중치) |

### Phase 4
| 서비스 | 역할 |
|--------|------|
| weather_service.py | 기상청/에어코리아 API + Redis 캐싱 |
| push_service.py | FCM/APNs 푸시 전송 + 빈도 제한 |
| payment_service.py | 결제 처리 + 구독 상태 머신 |

---

*작성일: 2026-02-26*
*상태: 확정 — 프로토타입 전체 분석 완료*
*기준: prototype/ 폴더 HTML 12개 페이지*
