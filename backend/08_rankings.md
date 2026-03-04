# 08. 랭킹 시스템

> 기준: 프로토타입 (랭킹.html) + 07_grades_titles.md 연동
> 상위 문서: [BACKEND_PLAN.md](./BACKEND_PLAN.md)

---

## 0. 핵심 요약

| 항목 | 내용 |
|------|------|
| **랭킹 기준** | 산책 거리 (km) |
| **기간** | 주간 / 월간 / 전체 (3종) |
| **지역 필터** | 전체 + 구/군 단위 |
| **갱신 방식** | Redis 캐싱 + 주기적 갱신 (1시간) |
| **표시** | Top 3 (포디움) + 4~10위 (리스트) + 내 순위 |
| **명예의 전당** | 이달의 산책왕 (월간 1위 기록 보관) |

---

## 1. 랭킹 종류

### 1.1 기간별

| 종류 | 기간 | 기준 |
|------|------|------|
| 주간 | 월~일 (한 주) | 해당 주 산책 거리 합산 |
| 월간 | 1일~말일 | 해당 월 산책 거리 합산 |
| 전체 | 가입 이후 전체 | 누적 산책 거리 |

> 주간 기준: 월요일 00:00 시작 ~ 일요일 23:59 종료 (한국 시간 KST)

### 1.2 지역별

| 필터 | 설명 |
|------|------|
| 전체 | 전국 모든 유저 |
| 구/군 | 유저 설정 지역 기준 필터 |

> 지역 정보: users 테이블의 `district` 필드 (온보딩 또는 설정에서 입력)
> 프로토타입 기준: 강남구, 서초구, 마포구, 송파구, 영등포구, 동작구, 관악구, 용산구 등

---

## 2. 아키텍처

```
[랭킹 갱신 흐름]

산책 완료 (POST /walks/{id}/complete)
  → 걸은 거리 기록
  → (실시간 반영 X, 캐시 갱신 주기에 의존)

[주기적 갱신 — 1시간마다]
  ┌─── 스케줄러 (APScheduler / cron) ───┐
  │                                       │
  │  1. DB에서 기간별 거리 합산 쿼리      │
  │  2. 순위 계산                         │
  │  3. Redis Sorted Set에 저장           │
  │  4. 이전 순위와 비교 → 변동 계산      │
  │                                       │
  └───────────────────────────────────────┘

[API 요청 시]
  GET /rankings?period=weekly&district=강남구
    → Redis에서 조회 (캐시 HIT → 즉시 반환)
    → 캐시 MISS → DB 직접 조회 → 캐시 저장
```

### 왜 실시간이 아닌 주기적 갱신?

| | 실시간 | 주기적 (1시간) |
|--|--------|---------------|
| DB 부하 | 산책 완료마다 랭킹 전체 재계산 | 1시간 1회만 |
| 응답 속도 | 매번 집계 쿼리 | Redis에서 즉시 |
| 정확도 | 즉시 반영 | 최대 1시간 지연 |
| 복잡도 | 높음 | 낮음 |

> 산책 앱 특성상 실시간 정확도보다는 안정적인 성능이 중요.
> 유저 입장에서 1시간 지연은 체감하기 어려움.

---

## 3. Redis 데이터 구조

### 3.1 Sorted Set

```
# 주간 랭킹 (전체 지역)
ZADD ranking:weekly:all:{week_key}  45.2  "user:101"
ZADD ranking:weekly:all:{week_key}  38.1  "user:102"

# 주간 랭킹 (지역별)
ZADD ranking:weekly:강남구:{week_key}  45.2  "user:101"

# 월간 랭킹
ZADD ranking:monthly:all:{month_key}  187.3  "user:101"

# 전체 랭킹
ZADD ranking:total:all  1234.5  "user:101"
```

| 키 패턴 | 예시 | TTL |
|---------|------|-----|
| `ranking:weekly:all:{YYYY-WNN}` | `ranking:weekly:all:2026-W09` | 2주 |
| `ranking:weekly:{district}:{YYYY-WNN}` | `ranking:weekly:강남구:2026-W09` | 2주 |
| `ranking:monthly:all:{YYYY-MM}` | `ranking:monthly:all:2026-03` | 2개월 |
| `ranking:monthly:{district}:{YYYY-MM}` | `ranking:monthly:강남구:2026-03` | 2개월 |
| `ranking:total:all` | - | 없음 (영구) |
| `ranking:total:{district}` | `ranking:total:강남구` | 없음 |

> week_key: ISO 8601 주차 (2026-W09 = 2026년 9번째 주)

### 3.2 순위 변동 저장

```
# 이전 순위 스냅샷 (갱신 직전에 저장)
HSET ranking:prev:weekly:all:{week_key}  "user:101"  1
HSET ranking:prev:weekly:all:{week_key}  "user:102"  2

# 변동 = 이전 순위 - 현재 순위
# +2 = 2단계 상승, -1 = 1단계 하락, 0 = 변동 없음
```

### 3.3 유저 메타 캐시

```
# 랭킹 표시용 유저 정보 (DB 조회 줄이기)
HSET user:meta:101  "nickname" "초코아빠"  "pet_name" "보리"  "pet_breed" "골든 리트리버"  "avatar" "🐕"
TTL: 1일
```

---

## 4. DB 쿼리

### 4.1 기간별 거리 합산

```python
# 주간 랭킹 계산
async def calculate_weekly_ranking(week_start: datetime, week_end: datetime, district: str | None = None):
    query = (
        select(
            Walk.user_id,
            func.sum(Walk.distance_m).label('total_distance')
        )
        .where(
            Walk.status == 'completed',
            Walk.completed_at >= week_start,
            Walk.completed_at < week_end,
        )
        .group_by(Walk.user_id)
        .order_by(desc('total_distance'))
    )

    if district:
        query = query.join(User).where(User.district == district)

    return await db.execute(query)
```

### 4.2 전체 랭킹 계산

```python
# 누적 거리 (users 테이블에 캐싱된 값 활용)
async def calculate_total_ranking(district: str | None = None):
    query = (
        select(User.id, User.total_distance_m)
        .where(User.total_distance_m > 0)
        .order_by(desc(User.total_distance_m))
    )

    if district:
        query = query.where(User.district == district)

    return await db.execute(query)
```

> `User.total_distance_m`: 산책 완료 시마다 누적되는 필드 (02_walks에서 이미 관리)

---

## 5. API 상세

### 5.1 랭킹 조회 — `GET /rankings`

**요청**
```
GET /rankings?period=weekly&district=강남구&size=10
```

| 파라미터 | 필수 | 기본값 | 설명 |
|---------|------|--------|------|
| period | X | weekly | `weekly`, `monthly`, `total` |
| district | X | null (전체) | 구/군명 |
| size | X | 10 | 결과 수 (최대 50) |

**응답**
```json
{
  "period": "weekly",
  "period_label": "2026.03.02 ~ 2026.03.08",
  "district": null,
  "total_participants": 128,
  "my_rank": {
    "rank": 2,
    "distance_km": 38.1,
    "change": 2,
    "nickname": "나 (초코 보호자)",
    "pet_name": "초코",
    "pet_breed": "골든 리트리버"
  },
  "top3": [
    {
      "rank": 1,
      "user_id": 101,
      "nickname": "초코아빠",
      "pet_name": "보리",
      "pet_breed": "골든 리트리버",
      "distance_km": 45.2,
      "change": 0
    },
    {
      "rank": 2,
      "user_id": 102,
      "nickname": "나 (초코 보호자)",
      "pet_name": "초코",
      "pet_breed": "골든 리트리버",
      "distance_km": 38.1,
      "change": 2
    },
    {
      "rank": 3,
      "user_id": 103,
      "nickname": "달이맘",
      "pet_name": "달이",
      "pet_breed": "푸들",
      "distance_km": 32.7,
      "change": -1
    }
  ],
  "rankings": [
    {
      "rank": 4,
      "user_id": 104,
      "nickname": "바둑이집사",
      "pet_name": "바둑이",
      "pet_breed": "진돗개",
      "distance_km": 28.4,
      "change": 1
    },
    {
      "rank": 5,
      "user_id": 105,
      "nickname": "콩이엄마",
      "pet_name": "콩이",
      "pet_breed": "러시안블루",
      "distance_km": 21.9,
      "change": -2
    }
  ]
}
```

> `top3`과 `rankings`를 분리하는 이유: 프론트에서 Top 3는 포디움 UI, 4위부터는 리스트 UI로 표시

### 5.2 내 순위 — `GET /rankings/me`

**요청**
```
GET /rankings/me?period=weekly&district=강남구
```

**응답**
```json
{
  "period": "weekly",
  "rank": 2,
  "total_participants": 128,
  "distance_km": 38.1,
  "change": 2,
  "percentile": 1.6
}
```

> `percentile`: 상위 몇 %인지 (2/128 = 상위 1.6%)

### 5.3 명예의 전당 — `GET /rankings/hall-of-fame`

**요청**
```
GET /rankings/hall-of-fame?limit=6
```

| 파라미터 | 필수 | 기본값 | 설명 |
|---------|------|--------|------|
| limit | X | 6 | 최근 N개월 |

**응답**
```json
{
  "current_month": {
    "year": 2026,
    "month": 3,
    "champion": {
      "user_id": 101,
      "nickname": "초코아빠",
      "pet_name": "보리",
      "pet_breed": "골든 리트리버",
      "total_km": 187.3,
      "walk_count": 28,
      "total_minutes": 1935,
      "is_final": false
    }
  },
  "history": [
    {
      "year": 2026,
      "month": 2,
      "champion": {
        "user_id": 101,
        "nickname": "초코아빠",
        "pet_name": "보리",
        "total_km": 203.1,
        "walk_count": 31,
        "total_minutes": 2100,
        "is_final": true
      }
    }
  ]
}
```

> `is_final`: 해당 월이 종료되어 확정된 기록인지 여부
> `current_month`: 현재 진행 중인 월의 1위 (실시간 변동 가능)

---

## 6. DB 테이블

### hall_of_fame (월간 1위 기록 보관)

| 필드 | 타입 | 설명 |
|------|------|------|
| id | Integer PK | |
| year | Integer | 연도 |
| month | Integer | 월 (1~12) |
| user_id | BigInteger FK | 1위 사용자 |
| total_distance_m | Integer | 총 거리 (m) |
| walk_count | Integer | 산책 횟수 |
| total_duration_sec | Integer | 총 시간 (초) |
| recorded_at | DateTime | 기록 확정일 |

> UNIQUE(year, month) — 월당 1명만

### users 테이블 변경

| 추가 필드 | 타입 | 설명 |
|----------|------|------|
| district | String(30) | 유저 소속 지역 (구/군) |

> `district`는 온보딩 시 또는 설정에서 입력/변경
> 이미 `total_distance_m`이 있으면 별도 추가 불필요

---

## 7. 스케줄러 (랭킹 갱신)

### 7.1 갱신 작업

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', hours=1)
async def refresh_rankings():
    """1시간마다 랭킹 갱신"""
    now = datetime.now(KST)

    # 주간 랭킹 갱신
    week_start, week_end = get_current_week_range(now)
    await _refresh_period_ranking('weekly', week_start, week_end)

    # 월간 랭킹 갱신
    month_start, month_end = get_current_month_range(now)
    await _refresh_period_ranking('monthly', month_start, month_end)

    # 전체 랭킹 갱신
    await _refresh_total_ranking()

@scheduler.scheduled_job('cron', day=1, hour=0, minute=5, timezone='Asia/Seoul')
async def finalize_monthly_champion():
    """매월 1일 00:05 — 전월 1위 명예의 전당 기록"""
    prev_month = get_previous_month()
    champion = await get_monthly_champion(prev_month)
    if champion:
        await save_hall_of_fame(prev_month, champion)
```

### 7.2 주간/월간 기간 계산

```python
from datetime import datetime, timedelta
import pytz

KST = pytz.timezone('Asia/Seoul')

def get_current_week_range(now: datetime) -> tuple[datetime, datetime]:
    """현재 주의 월~일 범위 (KST)"""
    monday = now - timedelta(days=now.weekday())
    week_start = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    week_end = week_start + timedelta(days=7)
    return week_start, week_end

def get_week_key(now: datetime) -> str:
    """ISO 주차 키: 2026-W09"""
    return now.strftime('%G-W%V')
```

---

## 8. 서비스 모듈 구조

```
server/app/
├── services/
│   └── ranking_service.py   # 랭킹 계산 + Redis 연동 + 명예의 전당
├── routers/
│   └── rankings.py          # API 엔드포인트
├── models/
│   └── hall_of_fame.py      # 명예의 전당 모델
├── schemas/
│   └── ranking.py           # 요청/응답 스키마
└── tasks/
    └── ranking_scheduler.py # APScheduler 작업 (1시간 갱신 + 월초 확정)
```

### ranking_service.py 핵심 구조

```python
class RankingService:
    PERIODS = ['weekly', 'monthly', 'total']

    async def get_rankings(
        self,
        period: str,
        district: str | None,
        size: int,
        current_user_id: int
    ) -> dict:
        """랭킹 조회 (Redis 우선, 없으면 DB fallback)"""
        cache_key = self._cache_key(period, district)

        # 1. Redis에서 조회
        cached = await self._get_from_redis(cache_key, size)
        if cached:
            rankings = cached
        else:
            # 2. DB fallback
            rankings = await self._calculate_from_db(period, district, size)
            await self._save_to_redis(cache_key, rankings)

        # 3. 내 순위 조회
        my_rank = await self._get_my_rank(cache_key, current_user_id)

        # 4. 유저 메타 정보 합침
        rankings = await self._enrich_user_meta(rankings)

        # 5. top3 / rankings 분리
        return self._format_response(rankings, my_rank, period, district)

    async def _get_my_rank(self, cache_key: str, user_id: int) -> dict:
        """Redis ZREVRANK로 내 순위 조회 — O(log N)"""
        rank = await redis.zrevrank(cache_key, f"user:{user_id}")
        score = await redis.zscore(cache_key, f"user:{user_id}")
        total = await redis.zcard(cache_key)
        # 이전 순위와 비교 → change 계산
        ...
```

---

## 9. 환경변수

| 변수 | 용도 | 비고 |
|------|------|------|
| `REDIS_URL` | 랭킹 캐시 | config.py에 이미 존재 |

> 추가 환경변수 없음. 기존 설정으로 충분.

---

## 10. 참고: 성능 고려사항

### 10.1 Redis Sorted Set 성능

| 연산 | 시간 복잡도 | 설명 |
|------|-----------|------|
| ZADD | O(log N) | 점수 추가/갱신 |
| ZREVRANK | O(log N) | 내 순위 조회 |
| ZREVRANGE | O(log N + M) | Top M명 조회 |
| ZCARD | O(1) | 전체 참여자 수 |

> 유저 10만 명이어도 log(100,000) ≈ 17 → 매우 빠름

### 10.2 지역별 랭킹 확장

현재 프로토타입 기준 구/군 단위(8개 지역). 향후 확장 가능:

| 단계 | 범위 | 키 수 |
|------|------|-------|
| 현재 | 전체 + 구/군 (~30개) | period × 31 = ~93개 |
| 향후 | 시/도 추가 | period × (17 + 250) = ~800개 |

> Redis Sorted Set은 가벼워서 수백 개도 부담 없음

---

## 11. 구현 우선순위

| 순서 | 항목 | 난이도 |
|------|------|--------|
| 1 | hall_of_fame 모델 + users.district 필드 추가 | 쉬움 |
| 2 | ranking_service.py (DB 쿼리 + Redis 연동) | 중간 |
| 3 | `GET /rankings` (기간별/지역별 조회) | 중간 |
| 4 | `GET /rankings/me` (내 순위) | 쉬움 |
| 5 | 스케줄러 — 1시간 갱신 작업 | 중간 |
| 6 | `GET /rankings/hall-of-fame` + 월초 확정 로직 | 중간 |

---

## 12. 필요 라이브러리

```
APScheduler       # 주기적 랭킹 갱신 스케줄러
redis[hiredis]    # Redis 연동 (이미 사용 중이면 추가 불필요)
pytz              # 한국 시간대 처리
```

---

*작성일: 2026-03-03*
*기준: 프로토타입 랭킹.html + Redis Sorted Set 기반 설계*
