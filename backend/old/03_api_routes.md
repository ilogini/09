# API 라우트 및 서비스 - 멍이랑 (withbowwow)

> 코어 파일: [00_overview.md](./00_overview.md)
> 스키마: [01_database_schema.md](./01_database_schema.md)
> 런타임: Python 3.11+ / FastAPI / SQLAlchemy 2.0

---

## 1. 서비스 모듈 목록

| 모듈 | 트리거 | 실행 빈도 | 우선순위 |
|------|--------|----------|---------|
| `walk_service.on_walk_complete()` | 산책 완료 (POST /walks/{id}/complete) | 매 산책 완료 | MVP |
| `walk_service.validate_walk()` | 산책 저장 전 | 매 산책 완료 | MVP |
| `badge_service.check_progress()` | on_walk_complete 내부 | 매 산책 완료 | Phase 2 |
| `ranking_service.calculate()` | APScheduler (1시간마다) | 24회/일 | Phase 2 |
| `recommend_service.get_recommendations()` | APScheduler (12시간마다) | 2회/일 | Phase 3 |
| `push_service.send()` | 이벤트 기반 | 이벤트 발생 시 | Phase 2 |
| `weather_service.cache_weather()` | APScheduler (1시간마다) | 24회/일 | Phase 4 |
| `payment_service.process_webhook()` | Webhook (Toss/IAP) | 결제 발생 시 | Phase 4 |

---

## 2. validate_walk (산책 유효성 검증)

### 2.1 검증 규칙

```python
# app/services/walk_service.py
from dataclasses import dataclass
import math


@dataclass
class WalkValidation:
    is_valid: bool
    invalid_reasons: list[str]


def validate_walk(walk_data: WalkCreateRequest) -> WalkValidation:
    reasons: list[str] = []

    # 1. 최소 거리: 500m 미만은 기록 불가
    if walk_data.distance_m < 500:
        reasons.append("minimum_distance")

    # 2. 최대 시간: 12시간 이상은 비정상
    if walk_data.duration_sec > 43200:
        reasons.append("max_duration_exceeded")

    # 3. 평균 속도: 시속 15km 이상이면 차량 탑승 의심
    if walk_data.duration_sec > 0:
        avg_speed_kmh = (walk_data.distance_m / 1000) / (walk_data.duration_sec / 3600)
        if avg_speed_kmh > 15:
            reasons.append("speed_too_high")

    # 4. GPS 좌표 검증: 연속 좌표 간 비현실적 이동 필터
    if walk_data.route_geojson and walk_data.route_geojson.get("coordinates"):
        coords = walk_data.route_geojson["coordinates"]
        filtered = [coords[0]]
        for i in range(1, len(coords)):
            dist = haversine_distance(coords[i - 1], coords[i])
            # 인접 좌표 간 거리가 비정상적이면 제외
            if dist < 500:  # 500m 이내 이동만 유효
                filtered.append(coords[i])
        walk_data.route_geojson["coordinates"] = filtered

    return WalkValidation(
        is_valid=len(reasons) == 0,
        invalid_reasons=reasons,
    )


def haversine_distance(coord1: list, coord2: list) -> float:
    """두 GPS 좌표 간 거리(미터) 계산"""
    R = 6371000  # 지구 반지름 (미터)
    lat1, lon1 = math.radians(coord1[1]), math.radians(coord1[0])
    lat2, lon2 = math.radians(coord2[1]), math.radians(coord2[0])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
```

---

## 3. on_walk_complete (산책 완료 처리)

### 3.1 실행 흐름

```
산책 완료 (POST /walks/{id}/complete)
  │
  ├── 1. validate_walk() → 유효성 검증
  │
  ├── 2. badge_service.check_progress() 호출
  │     ├── 거리 뱃지: SUM(walks.distance_m) 계산
  │     ├── 연속 뱃지: calculate_streak_days() 호출
  │     ├── 탐험 뱃지: COUNT(DISTINCT 장소) 계산
  │     ├── 시간 뱃지: SUM(walks.duration_sec) 계산
  │     ├── 스페셜 뱃지: 개별 조건 체크
  │     └── 시즌 뱃지: 기간 + 특수 조건 체크
  │
  ├── 3. 뱃지 상태 업데이트
  │     ├── locked → in_progress (진행률 > 0%)
  │     └── in_progress → earned (진행률 = 100%)
  │
  ├── 4. 랭킹 실시간 업데이트
  │
  ├── 5. 푸시 알림 전송 (조건부)
  │     ├── 뱃지 획득 시
  │     ├── 뱃지 임박 시
  │     └── 랭킹 변동 시
  │
  └── 6. 소셜 피드 업데이트 (shared_to_feed = true인 경우)
```

### 3.2 라우터 + 서비스

```python
# app/routers/walks.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks

router = APIRouter(prefix="/walks", tags=["walks"])


@router.post("/{walk_id}/complete")
async def complete_walk(
    walk_id: str,
    body: WalkCompleteRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 1. 산책 데이터 조회
    walk = await db.get(Walk, walk_id)
    if not walk or walk.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Walk not found")

    # 2. 유효성 검증
    validation = validate_walk(body)
    if not validation.is_valid:
        walk.is_valid = False
        await db.commit()
        return {"valid": False, "reasons": validation.invalid_reasons}

    # 3. 산책 데이터 업데이트
    walk.ended_at = body.ended_at
    walk.duration_sec = body.duration_sec
    walk.distance_m = body.distance_m
    walk.calories = body.calories
    walk.avg_speed_kmh = body.avg_speed_kmh
    walk.route_geojson = body.route_geojson
    walk.weather = body.weather
    walk.memo = body.memo
    walk.shared_to_feed = body.shared_to_feed
    await db.commit()

    # 4. 백그라운드에서 뱃지/랭킹/푸시 처리
    background_tasks.add_task(
        process_walk_completion, walk_id, current_user.id
    )

    return {"valid": True, "walk_id": walk_id}


# app/services/walk_service.py
async def process_walk_completion(walk_id: str, user_id: str):
    """산책 완료 후 백그라운드 처리"""
    async with get_async_session() as db:
        walk = await db.get(Walk, walk_id)

        # 뱃지 진행률 업데이트
        badge_updates = await badge_service.check_progress(db, walk)

        # 랭킹 업데이트
        await ranking_service.update_user_ranking(db, user_id)

        # 푸시 알림
        for badge in badge_updates.newly_earned:
            await push_service.send(db, user_id, PushPayload(
                type="badge_earned",
                title="새 뱃지를 획득했어요!",
                body=f"{badge.name} 뱃지를 달성했어요!",
                data={"badge_id": str(badge.id)},
            ))
```

---

## 4. badge_service.check_progress (뱃지 진행률)

### 4.1 카테고리별 계산 로직

```python
# app/services/badge_service.py
from sqlalchemy import select, func, text


class BadgeService:

    async def check_progress(self, db: AsyncSession, walk: Walk) -> BadgeResult:
        user_id = walk.user_id
        result = BadgeResult(updated=[], newly_earned=[])

        # 모든 활성 뱃지 정의 조회
        stmt = select(BadgeDefinition).where(BadgeDefinition.is_active == True)
        badges = (await db.execute(stmt)).scalars().all()

        for badge in badges:
            progress = await self._calculate_progress(db, badge, walk, user_id)
            progress = max(0, min(progress, 100))

            if progress > 0:
                await self._update_user_badge(db, user_id, badge, walk, progress, result)

        await db.commit()
        return result

    async def _calculate_progress(
        self, db: AsyncSession, badge: BadgeDefinition, walk: Walk, user_id: str
    ) -> float:
        match badge.condition_type:
            # ── 거리 뱃지 ──
            case "cumulative_distance":
                total = await self._sum_user_distance(db, user_id)
                return total / badge.condition_value * 100

            # ── 연속 뱃지 ──
            case "consecutive_days":
                streak = await db.execute(
                    text("SELECT calculate_streak_days(:uid)"),
                    {"uid": user_id},
                )
                days = streak.scalar()
                return days / badge.condition_value * 100

            # ── 탐험 뱃지 ──
            case "unique_places":
                places = await db.execute(
                    text("SELECT count_unique_places(:uid)"),
                    {"uid": user_id},
                )
                count = places.scalar()
                return count / badge.condition_value * 100

            # ── 시간 뱃지 ──
            case "cumulative_time":
                total = await self._sum_user_duration(db, user_id)
                return total / badge.condition_value * 100

            # ── 스페셜 뱃지 ──
            case "special_early_bird":
                hour = walk.started_at.hour
                return 100.0 if hour < 6 else 0.0

            case "special_night_owl":
                hour = walk.started_at.hour
                return 100.0 if hour >= 22 else 0.0

            case "special_rain_walk":
                weather = walk.weather or {}
                return 100.0 if weather.get("pty") == "rain" else 0.0

            case "special_snow_walk":
                weather = walk.weather or {}
                return 100.0 if weather.get("pty") == "snow" else 0.0

            case "special_single_marathon":
                return 100.0 if walk.distance_m >= 10000 else 0.0

            case "special_photographer":
                total_photos = await self._count_user_photos(db, user_id)
                return total_photos / badge.condition_value * 100

            case "special_new_year":
                return 100.0 if walk.started_at.month == 1 and walk.started_at.day == 1 else 0.0

            # ── 시즌 뱃지 ──
            case s if s.startswith("season_"):
                return await self._calculate_season_progress(db, user_id, badge)

            case _:
                return 0.0

    async def _sum_user_distance(self, db: AsyncSession, user_id: str) -> int:
        stmt = select(func.coalesce(func.sum(Walk.distance_m), 0)).where(
            Walk.user_id == user_id, Walk.is_valid == True
        )
        return (await db.execute(stmt)).scalar()

    async def _sum_user_duration(self, db: AsyncSession, user_id: str) -> int:
        stmt = select(func.coalesce(func.sum(Walk.duration_sec), 0)).where(
            Walk.user_id == user_id, Walk.is_valid == True
        )
        return (await db.execute(stmt)).scalar()

    async def _count_user_photos(self, db: AsyncSession, user_id: str) -> int:
        stmt = (
            select(func.count(WalkPhoto.id))
            .join(Walk, WalkPhoto.walk_id == Walk.id)
            .where(Walk.user_id == user_id)
        )
        return (await db.execute(stmt)).scalar()

    async def _update_user_badge(
        self, db, user_id, badge, walk, progress, result
    ):
        new_status = "earned" if progress >= 100 else "in_progress"

        stmt = select(UserBadge).where(
            UserBadge.user_id == user_id,
            UserBadge.badge_id == badge.id,
        )
        existing = (await db.execute(stmt)).scalar_one_or_none()

        if existing:
            if existing.status != "earned":
                existing.status = new_status
                existing.progress_value = progress * badge.condition_value / 100
                existing.progress_percent = progress
                if new_status == "earned":
                    existing.earned_at = datetime.utcnow()
                    existing.earned_walk_id = walk.id
                    result.newly_earned.append(badge)
        else:
            new_badge = UserBadge(
                user_id=user_id,
                badge_id=badge.id,
                status=new_status,
                progress_value=progress * badge.condition_value / 100,
                progress_percent=progress,
                earned_at=datetime.utcnow() if new_status == "earned" else None,
                earned_walk_id=walk.id if new_status == "earned" else None,
                pet_id=walk.pet_id,
            )
            db.add(new_badge)
            if new_status == "earned":
                result.newly_earned.append(badge)
```

### 4.2 연속 뱃지 특수 로직

```
하루 기준: 오전 4시 ~ 다음날 오전 4시 (새벽 산책 고려)
최소 거리: 500m 이상이어야 "산책한 날"로 인정
연속 끊김: 진행률 리셋 (0부터 재시작)
프리미엄 면제: 월 1회 "휴식일" 사용 가능 (연속 기록 유지)
```

---

## 5. ranking_service (랭킹 집계)

### 5.1 APScheduler 설정

```python
# app/scheduler/jobs.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# 매시간 정각: 랭킹 집계
scheduler.add_job(
    ranking_service.calculate_all,
    "cron",
    minute=0,
    id="refresh_rankings",
)

# 12시간마다: 친구 추천
scheduler.add_job(
    recommend_service.refresh_all,
    "cron",
    hour="0,12",
    id="refresh_recommendations",
)

# 매시간: 날씨 캐싱
scheduler.add_job(
    weather_service.cache_weather,
    "cron",
    minute=5,
    id="cache_weather",
)

# 매일 자정: 정리 작업
scheduler.add_job(
    cleanup_service.run_daily,
    "cron",
    hour=0,
    minute=30,
    id="daily_cleanup",
)
```

### 5.2 랭킹 기준

| 기간 | 기본 정렬 | 동점 처리 | 리셋 |
|------|----------|----------|------|
| 주간 | 총 거리 (km) DESC | 산책 횟수 많은 쪽 우선 | 매주 월요일 00:00 |
| 월간 | 총 거리 (km) DESC | 산책 횟수 많은 쪽 우선 | 매월 1일 00:00 |
| 전체 | 총 거리 (km) DESC | 산책 횟수 많은 쪽 우선 | 리셋 없음 |

### 5.3 지역별 랭킹

```
동 단위: region_dong 기준 (예: 성수동1가)
구 단위: region_sigungu 기준 (예: 성동구)
전국: 지역 필터 없음
```

---

## 6. recommend_service (친구 추천)

### 6.1 추천 알고리즘

```python
# app/services/recommend_service.py

async def get_recommendations(db: AsyncSession, user_id: str, limit: int = 20):
    """가중치 기반 친구 추천"""
    candidates = await db.execute(
        text("SELECT * FROM get_friend_candidates(:uid, :lim)"),
        {"uid": user_id, "lim": limit},
    )

    results = []
    for c in candidates:
        score = (
            c.distance_score * 0.40 +    # 지리적 근접성 (40%)
            c.time_score * 0.25 +         # 산책 시간대 유사성 (25%)
            c.breed_score * 0.20 +        # 견종/크기 유사성 (20%)
            c.activity_score * 0.15       # 활동량 유사성 (15%)
        )
        results.append({"user": c, "score": score})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results
```

### 6.2 후보 쿼리

```sql
CREATE OR REPLACE FUNCTION get_friend_candidates(p_user_id UUID, p_limit INTEGER)
RETURNS TABLE(
  id UUID, nickname TEXT, pet_name TEXT, breed TEXT, size TEXT, photo_url TEXT,
  distance_score FLOAT, time_score FLOAT, breed_score FLOAT, activity_score FLOAT
) AS $$
  SELECT
    u.id, u.nickname, p.name, p.breed, p.size, p.photo_url,
    CASE
      WHEN u.region_dong = me.region_dong THEN 1.0
      WHEN u.region_sigungu = me.region_sigungu THEN 0.6
      ELSE 0.0
    END AS distance_score,
    1.0 - ABS(avg_walk_hour(u.id) - avg_walk_hour(p_user_id)) / 12.0 AS time_score,
    CASE WHEN p.size = my_pet.size THEN 1.0 ELSE 0.3 END AS breed_score,
    1.0 - ABS(weekly_distance(u.id) - weekly_distance(p_user_id))
      / GREATEST(weekly_distance(p_user_id), 1) AS activity_score
  FROM users u
  JOIN pets p ON p.user_id = u.id AND p.is_primary = TRUE
  CROSS JOIN (SELECT * FROM users WHERE id = p_user_id) me
  CROSS JOIN (SELECT * FROM pets WHERE user_id = p_user_id AND is_primary = TRUE LIMIT 1) my_pet
  WHERE u.id != p_user_id
    AND u.id NOT IN (SELECT following_id FROM follows WHERE follower_id = p_user_id)
    AND u.id NOT IN (SELECT blocked_id FROM blocks WHERE blocker_id = p_user_id)
    AND u.deleted_at IS NULL
  ORDER BY distance_score DESC
  LIMIT p_limit;
$$ LANGUAGE sql;
```

---

## 7. 산책 피드 정렬 알고리즘

```python
# app/services/feed_service.py
from datetime import datetime


def calculate_feed_score(walk: Walk, viewer: User, intimacy: float) -> float:
    """피드 정렬 점수 계산"""
    age_hours = (datetime.utcnow() - walk.created_at).total_seconds() / 3600

    return (
        # 시간 최신순 (40%) - 시간이 지날수록 감소
        (1 / (1 + age_hours / 24)) * 0.40
        # 친밀도 (30%) - 최근 인터랙션 빈도
        + intimacy * 0.30
        # 지역 근접성 (20%) - 같은 동네 우선
        + get_region_score(viewer, walk) * 0.20
        # 인게이지먼트 (10%) - 좋아요/댓글 수
        + min(walk.like_count + walk.comment_count, 50) / 50 * 0.10
    )


def get_region_score(viewer: User, walk: Walk) -> float:
    if viewer.region_dong == walk.user.region_dong:
        return 1.0
    elif viewer.region_sigungu == walk.user.region_sigungu:
        return 0.6
    return 0.0
```

---

## 8. API 엔드포인트 요약

| Method | Path | 설명 | Auth |
|--------|------|------|------|
| POST | /auth/kakao | 카카오 로그인 | - |
| POST | /auth/naver | 네이버 로그인 | - |
| POST | /auth/apple | Apple 로그인 | - |
| POST | /auth/refresh | 토큰 갱신 | - |
| POST | /auth/logout | 로그아웃 | O |
| GET | /users/me | 내 프로필 | O |
| PATCH | /users/me | 프로필 수정 | O |
| DELETE | /users/me | 계정 삭제 | O |
| GET | /users/{id} | 사용자 프로필 | O |
| POST | /pets | 반려동물 등록 | O |
| GET | /pets | 내 반려동물 목록 | O |
| PATCH | /pets/{id} | 반려동물 수정 | O |
| DELETE | /pets/{id} | 반려동물 삭제 | O |
| POST | /walks | 산책 시작 | O |
| POST | /walks/{id}/complete | 산책 완료 | O |
| GET | /walks | 내 산책 기록 | O |
| GET | /walks/{id} | 산책 상세 | O |
| GET | /badges | 뱃지 목록 (진행률 포함) | O |
| GET | /badges/{id} | 뱃지 상세 | O |
| GET | /rankings | 랭킹 조회 (기간/지역 필터) | O |
| GET | /rankings/me | 내 랭킹 | O |
| GET | /feed | 소셜 피드 | O |
| POST | /follows/{user_id} | 팔로우 | O |
| DELETE | /follows/{user_id} | 언팔로우 | O |
| POST | /likes/{walk_id} | 좋아요 | O |
| DELETE | /likes/{walk_id} | 좋아요 취소 | O |
| POST | /comments | 댓글 작성 | O |
| DELETE | /comments/{id} | 댓글 삭제 | O |
| GET | /recommendations | 친구 추천 | O |
| POST | /invitations | 산책 초대 | O |
| PATCH | /invitations/{id} | 초대 수락/거절 | O |
| GET | /meetups | 모임 목록 | O |
| POST | /meetups | 모임 생성 | O |
| POST | /meetups/{id}/join | 모임 참가 | O |
| GET | /notifications | 알림 목록 | O |
| PATCH | /notifications/{id}/read | 알림 읽음 | O |
| GET | /weather | 날씨/미세먼지 | O |
| POST | /upload/image | 이미지 업로드 | O |
| POST | /payments/webhook/toss | Toss 결제 웹훅 | - |
| POST | /payments/webhook/apple | Apple IAP 웹훅 | - |
| POST | /payments/webhook/google | Google Play 웹훅 | - |

> Swagger UI: `GET /docs` 에서 전체 API 명세 확인 가능

---

*작성일: 2026-02-12*
*버전: 2.0 — FastAPI + SQLAlchemy로 전환*
