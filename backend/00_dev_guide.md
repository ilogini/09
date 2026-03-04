# 00. 개발 작업 가이드

> 매 작업 세션 시작 전에 이 문서를 확인하세요.
> 서버 코드 현황, 작업 전 체크리스트, 코딩 컨벤션을 정리합니다.

---

## 1. 작업 전 체크리스트

매번 작업을 시작하기 전에 아래 순서대로 확인:

### Step 1: Git 동기화
```bash
git fetch origin
git log --oneline origin/main..HEAD   # 푸시 안 된 로컬 커밋 확인
git log --oneline HEAD..origin/main   # 풀 받아야 할 원격 커밋 확인
git pull origin main                  # 필요시
```

### Step 2: 작업할 기능의 기획 문서 확인
```
backend/
├── 00_dev_guide.md    ← 지금 이 문서
├── 01_auth.md         ← 인증/온보딩
├── 02_walks.md        ← 산책 (경로 이미지 포함)
├── 03_pets.md         ← 반려동물
├── 04_map_places.md   ← 지도/장소 (카카오 API)
├── 05_storage.md      ← 사진 업로드 (R2)
├── 06_badges.md       ← 뱃지 (자동 달성)
├── 07_grades_titles.md ← 등급/칭호
├── 08_rankings.md     ← 랭킹 (Redis Sorted Set)
├── 09_social.md       ← 친구 (양방향), 태그, 차단/신고
├── 10_challenges.md   ← 챌린지 (수락→완료 퀘스트)
├── 11_notifications.md ← 푸시 알림 (FCM)
├── 12_premium.md      ← 결제 (보류)
├── 13_weather.md      ← 날씨/미세먼지/산책 추천
```

### Step 3: 현재 서버 코드 상태 확인
이 문서의 **Section 2 (구현 현황)** 참고.
작업 완료 후 구현 현황 테이블을 업데이트할 것.

### Step 4: 작업 범위 확인
- 해당 기획 문서의 **DB 테이블** → models/ 에 추가/수정 필요?
- 해당 기획 문서의 **API 목록** → routers/ 에 추가 필요?
- 해당 기획 문서의 **서비스 로직** → services/ 에 추가 필요?
- 해당 기획 문서의 **스키마** → schemas/ 에 추가 필요?
- Alembic 마이그레이션 필요?

---

## 2. 서버 구현 현황

> **최종 업데이트: 2026-03-04**
> 작업 완료 시마다 이 테이블을 갱신하세요.

### 2.1 전체 요약

| 영역 | 상태 | 비고 |
|------|------|------|
| FastAPI 서버 구조 | ✅ 완료 | main.py, config.py, database.py |
| JWT 인증 + 소셜 로그인 | ✅ 완료 | 카카오/네이버/Apple |
| 사용자 조회/수정 | ✅ 완료 | GET/PATCH /users/me |
| 반려동물 CRUD | ✅ 완료 | 전체 CRUD |
| 산책 CRUD + 유효성 검증 | ✅ 완료 | 시작/완료/목록/상세/삭제 |
| Docker + Alembic | ✅ 완료 | Dockerfile, alembic/ |
| 서비스 레이어 | ❌ 없음 | services/ 비어있음 |
| 백그라운드 작업 | ❌ 없음 | APScheduler 미구현 (requirements만) |
| Redis 캐싱 | ❌ 없음 | 설정만 존재, 코드 없음 |
| R2 스토리지 | ❌ 없음 | 설정만 존재, 코드 없음 |
| FCM 푸시 | ❌ 없음 | 설정만 존재, 코드 없음 |

### 2.2 파일별 상세

#### models/ (DB 모델)

| 파일 | 모델 | 상태 | 기획 문서 |
|------|------|------|----------|
| user.py | User | ✅ 구현됨 | 01_auth |
| pet.py | Pet | ✅ 구현됨 | 03_pets |
| walk.py | Walk, WalkPhoto | ✅ 구현됨 | 02_walks |
| — | PlaceFavorite | ❌ 미구현 | 04_map_places |
| — | BadgeDefinition, UserBadge | ❌ 미구현 | 06_badges |
| — | GradeDefinition, TitleDefinition, UserTitle | ❌ 미구현 | 07_grades_titles |
| — | HallOfFame | ❌ 미구현 | 08_rankings |
| — | FriendRequest, Friendship | ❌ 미구현 | 09_social |
| — | Block, Report | ❌ 미구현 | 09_social |
| — | Challenge, ChallengeParticipant | ❌ 미구현 | 10_challenges |
| — | ChallengeInvitation, ChallengeReward, UserReward | ❌ 미구현 | 10_challenges |
| — | Notification, PushToken | ❌ 미구현 | 11_notifications |

#### routers/ (API 엔드포인트)

| 파일 | 엔드포인트 | 상태 | 기획 문서 |
|------|-----------|------|----------|
| auth.py | POST /auth/{kakao,naver,apple,refresh,logout} | ✅ 구현됨 | 01_auth |
| — | GET /auth/onboarding-status | ❌ TODO | 01_auth |
| — | DELETE /users/me (탈퇴) | ❌ TODO | 01_auth |
| users.py | GET/PATCH /users/me | ✅ 구현됨 | 01_auth |
| — | GET /users/search | ❌ 미구현 | 09_social |
| pets.py | CRUD /pets | ✅ 구현됨 | 03_pets |
| walks.py | POST /walks, POST /walks/{id}/complete | ✅ 구현됨 | 02_walks |
| walks.py | GET /walks, GET /walks/{id}, DELETE /walks/{id} | ✅ 구현됨 | 02_walks |
| — | GET /walks/weekly-summary | ❌ TODO | 02_walks |
| — | GET /walks/stats | ❌ TODO | 02_walks |
| — | GET /walks (period 필터) | ❌ TODO | 02_walks |
| — | POST /walks/{id}/photos | ❌ TODO | 02_walks, 05_storage |
| — | GET /upload/presigned | ❌ 미구현 | 05_storage |
| — | GET /places/nearby, /places/search | ❌ 미구현 | 04_map_places |
| — | GET /badges, GET /badges/{id} | ❌ 미구현 | 06_badges |
| — | GET /rankings, GET /rankings/me | ❌ 미구현 | 08_rankings |
| — | 친구 관련 전체 | ❌ 미구현 | 09_social |
| — | 챌린지 관련 전체 | ❌ 미구현 | 10_challenges |
| — | 알림 관련 전체 | ❌ 미구현 | 11_notifications |
| — | GET /weather | ❌ 미구현 | 13_weather |

#### services/ (비즈니스 로직)

| 파일 | 상태 | 기획 문서 |
|------|------|----------|
| (비어있음) | — | — |

> 모든 서비스 모듈 미구현. 현재 비즈니스 로직이 routers에 직접 작성되어 있음.

#### schemas/ (요청/응답)

| 파일 | 스키마 | 상태 |
|------|--------|------|
| auth.py | SocialLoginRequest, TokenResponse, RefreshRequest | ✅ |
| user.py | UserResponse, UserUpdate | ✅ |
| pet.py | PetCreate, PetUpdate, PetResponse | ✅ |
| walk.py | WalkCreate, WalkComplete, WalkResponse, WalkListResponse, WalkPhotoResponse | ✅ |

### 2.3 User 모델 필드 — 기획 대비 누락

기획 문서에서 추가해야 할 User 필드:

| 필드 | 기획 문서 | 용도 |
|------|----------|------|
| tag_code | 09_social | #태그 (4자리 고유 코드) |
| district | 08_rankings | 소속 지역 (구/군) |
| total_distance_m | 02_walks, 08_rankings | 누적 산책 거리 |
| grade_id | 07_grades_titles | 현재 등급 |
| active_title_id | 07_grades_titles | 장착 칭호 |

### 2.4 환경변수 현황

config.py에 **이미 정의된** 변수:

| 변수 | 용도 | 코드에서 사용 |
|------|------|-------------|
| DATABASE_URL | PostgreSQL | ✅ 사용 중 |
| JWT_SECRET_KEY 등 | 인증 | ✅ 사용 중 |
| KAKAO/NAVER/APPLE 관련 | 소셜 로그인 | ✅ 사용 중 |
| REDIS_URL | 캐시 | ❌ 미사용 |
| KAKAO_REST_API_KEY | 장소 검색 | ❌ 미사용 |
| R2_* | 스토리지 | ❌ 미사용 |
| FIREBASE_CREDENTIALS_JSON | 푸시 | ❌ 미사용 |
| WEATHER/AIR_KOREA_API_KEY | 날씨 | ❌ 미사용 |
| TOSS_* | 결제 | ❌ 미사용 (보류) |

---

## 3. 코딩 컨벤션

### 3.1 프로젝트 구조

```
server/app/
├── main.py              # FastAPI 앱, 라우터 등록
├── config.py            # 환경변수 (Pydantic BaseSettings)
├── database.py          # SQLAlchemy async 엔진/세션
├── dependencies.py      # 인증 미들웨어 (get_current_user)
├── models/              # SQLAlchemy 모델 (테이블)
│   └── __init__.py      # 모든 모델 import (Alembic용)
├── routers/             # API 엔드포인트
├── schemas/             # Pydantic 요청/응답 스키마
├── services/            # 비즈니스 로직 (추가 필요)
├── tasks/               # 스케줄러 작업 (추가 필요)
└── utils/               # 유틸리티 (추가 필요)
```

### 3.2 네이밍 규칙

| 항목 | 규칙 | 예시 |
|------|------|------|
| 파일명 | snake_case | `badge_service.py` |
| 모델 클래스 | PascalCase | `BadgeDefinition` |
| 테이블명 | snake_case 복수형 | `badge_definitions` |
| API 경로 | kebab-case 또는 snake_case | `/walks/weekly-summary` |
| 스키마 | PascalCase + 접미사 | `WalkCreate`, `WalkResponse` |

### 3.3 인증 패턴

```python
from app.dependencies import get_current_user
from app.models.user import User

@router.get("/something")
async def get_something(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ...
```

### 3.4 에러 응답 패턴

```python
from fastapi import HTTPException

# 404
raise HTTPException(status_code=404, detail="Walk not found")

# 403
raise HTTPException(status_code=403, detail="Not authorized")
```

### 3.5 DB 쿼리 패턴

```python
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

# 단건 조회
result = await db.execute(select(Walk).where(Walk.id == walk_id))
walk = result.scalar_one_or_none()

# 목록 조회 + 페이징
query = select(Walk).where(Walk.user_id == user.id).order_by(Walk.created_at.desc())
result = await db.execute(query.offset((page-1)*size).limit(size))
walks = result.scalars().all()

# 집계
result = await db.execute(select(func.count(Walk.id)).where(...))
total = result.scalar()
```

### 3.6 Walk 유효성 검증 상수

```python
# walk.py 모델에 정의됨
MAX_SPEED_KMH = 15    # 이 이상이면 is_valid = false
MIN_DISTANCE_M = 100   # 이 이하면 is_valid = false
```

---

## 4. 구현 우선순위 (Phase 1 TODO)

Phase 1에서 아직 구현 안 된 것, 우선순위순:

| 순서 | 작업 | 기획 문서 | 영향 범위 |
|------|------|----------|----------|
| 1 | GET /walks/weekly-summary | 02_walks | routers/walks.py |
| 2 | GET /walks/stats | 02_walks | routers/walks.py |
| 3 | GET /walks period 필터 | 02_walks | routers/walks.py |
| 4 | 경로 이미지 생성 (staticmap) | 02_walks | services/route_image.py (신규) |
| 5 | GET /places/nearby, /search | 04_map_places | routers/places.py (신규), services/place_service.py (신규) |
| 6 | R2 presigned URL + 리사이징 | 05_storage | routers/upload.py (신규), services/storage_service.py (신규) |
| 7 | GET /auth/onboarding-status | 01_auth | routers/auth.py |
| 8 | DELETE /users/me (탈퇴) | 01_auth | routers/users.py |

---

## 5. 듀얼 리모트

| 리모트 | URL | 용도 |
|--------|-----|------|
| origin | `ilogini/withBowwow` | 팀 저장소 |
| deploy | `Wanja9229/withBowwow-deploy` | Render 배포용 |

```bash
# 푸시 시 둘 다
git push origin main
git push deploy main
```

---

## 6. 기술 스택 요약

| 항목 | 선택 | 버전 |
|------|------|------|
| Language | Python | 3.12 |
| Framework | FastAPI | ≥0.115 |
| ORM | SQLAlchemy (async) | ≥2.0 |
| DB | PostgreSQL + PostGIS | 15+ |
| Migration | Alembic | ≥1.13 |
| Auth | python-jose (JWT) + httpx (OAuth) | |
| Cache | Redis | ≥5.0 |
| Storage | Cloudflare R2 (boto3) | |
| Push | firebase-admin (FCM) | ≥6.4 |
| Scheduler | APScheduler | ≥3.10 |
| Image | Pillow | ≥10.2 |
| Deploy | Render (Docker) | Singapore |

---

*최종 업데이트: 2026-03-04*
*작업 완료 시마다 Section 2 구현 현황을 갱신할 것*
