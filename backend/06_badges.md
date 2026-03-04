# 06. 뱃지 시스템

> 기준: 프로토타입 (뱃지.html, 메인페이지.html, 마이페이지.html) + PROPOSAL.md
> 상위 문서: [BACKEND_PLAN.md](./BACKEND_PLAN.md)

---

## 0. 뱃지 vs 챌린지 — 명확한 구분

| | 뱃지 (Badge) | 챌린지 (Challenge) |
|--|-------------|-------------------|
| **개념** | 도전 과제 (업적) | 퀘스트 (미션) |
| **달성 방식** | **자동** — 조건 충족 시 서버가 자동 부여 | **수동 수락 → 완료** — 참가 의사 표시 필요 |
| **참여 절차** | 없음. 산책하면 알아서 달성됨 | 수락 → 진행 → 완료 |
| **기간** | 영구 (한 번 달성하면 영원히 보유) | 기간 한정 (주간/월간/커스텀) |
| **제공 주체** | 시스템 고정 (45개, 점진적 추가) | 관리자 기본 제공 + 사용자 직접 생성 |
| **소셜 요소** | 없음 (개인 업적) | 있음 (초대, 참가, 리더보드) |
| **갱신** | 변하지 않음 | 매주/매월 새 챌린지 자동 생성 |
| **Phase** | **Phase 2 (이 문서)** | **Phase 3 (10_challenges.md)** |

**예시로 비교:**
- 뱃지: "누적 100km 달성!" → 산책만 하면 자동으로 달성, 수락 절차 없음
- 챌린지: "이번 주 30km 걷기" → 수락 버튼 클릭 → 진행 → 주말까지 완료 여부 판정

---

## 1. 현재 구현 상태

| 기능 | 엔드포인트 | 상태 |
|------|-----------|------|
| 뱃지 전체 목록 | `GET /badges` | **TODO** |
| 뱃지 상세 | `GET /badges/{id}` | **TODO** |
| 진행 중 뱃지 | `GET /badges/in-progress` | **TODO** |
| 산책 완료 시 뱃지 체크 | (내부 서비스) | **TODO** |

> 전체 신규 개발 필요

---

## 2. 뱃지 카테고리 (6개)

| 코드 | 카테고리 | 설명 | 뱃지 수 |
|------|---------|------|---------|
| `distance` | 거리 | 누적/단일 산책 거리 기준 | 8개 |
| `streak` | 연속 | 연속 산책 일수 | 7개 |
| `explore` | 탐험 | 다양한 장소 방문 | 8개 |
| `time` | 시간 | 누적/단일 산책 시간 | 7개 |
| `special` | 특별 | 특수 조건 (날씨, 시간대 등) | 8개 |
| `season` | 시즌 | 계절/이벤트 한정 | 7개 |
| | | **합계** | **45개** |

---

## 3. 뱃지 전체 목록 (45개)

### 3.1 거리 (distance) — 8개

| ID | 이름 | 조건 | 아이콘 |
|----|------|------|--------|
| D01 | 첫 발자국 | 첫 산책 완료 | 🐾 |
| D02 | 1km 돌파 | 단일 산책 1km 이상 | 📍 |
| D03 | 5km 러너 | 단일 산책 5km 이상 | 🏃 |
| D04 | 10km 챔피언 | 단일 산책 10km 이상 | 🏅 |
| D05 | 누적 50km | 총 누적 거리 50km | 🛤️ |
| D06 | 누적 100km | 총 누적 거리 100km | 🌍 |
| D07 | 누적 500km | 총 누적 거리 500km | 🚀 |
| D08 | 누적 1,000km | 총 누적 거리 1,000km | ⭐ |

### 3.2 연속 (streak) — 7개

| ID | 이름 | 조건 | 아이콘 |
|----|------|------|--------|
| S01 | 3일 연속 | 3일 연속 산책 | 🔥 |
| S02 | 7일 연속 | 7일 연속 산책 | 💪 |
| S03 | 14일 연속 | 14일 연속 산책 | 🌟 |
| S04 | 30일 연속 | 30일 연속 산책 | 👑 |
| S05 | 60일 연속 | 60일 연속 산책 | 💎 |
| S06 | 100일 연속 | 100일 연속 산책 | 🏆 |
| S07 | 365일 연속 | 365일 연속 산책 | 🎖️ |

### 3.3 탐험 (explore) — 8개

| ID | 이름 | 조건 | 아이콘 |
|----|------|------|--------|
| E01 | 동네 탐험가 | 서로 다른 장소 3곳에서 산책 | 🗺️ |
| E02 | 공원 수집가 | 서로 다른 공원 5곳 방문 | 🌳 |
| E03 | 모험가 | 서로 다른 장소 10곳에서 산책 | 🧭 |
| E04 | 도시 탐험가 | 서로 다른 구/동 5곳에서 산책 | 🏙️ |
| E05 | 전국 여행자 | 서로 다른 시/도 3곳에서 산책 | ✈️ |
| E06 | 새 길 개척자 | 이전에 안 가본 경로 10회 | 🛣️ |
| E07 | 단골 산책러 | 같은 장소 20회 방문 | 📌 |
| E08 | 대한민국 정복 | 서로 다른 시/도 10곳에서 산책 | 🇰🇷 |

> 탐험 뱃지의 "장소" 판정: 산책 시작 좌표 기준 반경 500m를 하나의 장소로 간주

### 3.4 시간 (time) — 7개

| ID | 이름 | 조건 | 아이콘 |
|----|------|------|--------|
| T01 | 30분 산책 | 단일 산책 30분 이상 | ⏱️ |
| T02 | 1시간 산책 | 단일 산책 60분 이상 | ⏰ |
| T03 | 2시간 산책 | 단일 산책 120분 이상 | 🕐 |
| T04 | 누적 10시간 | 총 누적 시간 10시간 | ⌛ |
| T05 | 누적 50시간 | 총 누적 시간 50시간 | 🔔 |
| T06 | 누적 100시간 | 총 누적 시간 100시간 | 🎯 |
| T07 | 누적 500시간 | 총 누적 시간 500시간 | 💫 |

### 3.5 특별 (special) — 8개

| ID | 이름 | 조건 | 아이콘 |
|----|------|------|--------|
| P01 | 얼리버드 | 오전 6시 이전 산책 시작 | 🌅 |
| P02 | 올빼미 | 오후 10시 이후 산책 시작 | 🌙 |
| P03 | 비 오는 날 산책 | 비 오는 날 산책 완료 | 🌧️ |
| P04 | 눈 오는 날 산책 | 눈 오는 날 산책 완료 | ❄️ |
| P05 | 사진작가 | 한 산책에서 사진 5장 이상 | 📸 |
| P06 | 소셜 산책러 | 피드에 산책 10회 공유 | 📢 |
| P07 | 꾸준한 산책러 | 한 달간 15회 이상 산책 | 📅 |
| P08 | 주말 산책러 | 토/일요일 산책 10회 | 🎉 |

> 날씨 뱃지(P03, P04): weather JSONB 데이터 기준 판정 (Phase 4 날씨 API 연동 후 활성화)

### 3.6 시즌 (season) — 7개

| ID | 이름 | 조건 | 기간 |
|----|------|------|------|
| N01 | 봄맞이 산책 | 3~5월 중 누적 30km | 3월~5월 |
| N02 | 여름 도전 | 6~8월 중 누적 50km | 6월~8월 |
| N03 | 가을 단풍길 | 9~11월 중 누적 30km | 9월~11월 |
| N04 | 겨울 용사 | 12~2월 중 누적 20km | 12월~2월 |
| N05 | 새해 첫 산책 | 1월 1일 산책 | 1월 1일 |
| N06 | 크리스마스 산책 | 12월 25일 산책 | 12월 25일 |
| N07 | 반려동물의 날 | 10월 4일 산책 | 10월 4일 (세계 동물의 날) |

> 시즌 뱃지는 해당 기간에만 달성 가능. 매년 반복 (재획득은 불가, 최초 1회).

---

## 4. 자동 달성 로직

### 4.1 체크 타이밍

```
POST /walks/{id}/complete 처리 흐름:

1. Walk 레코드 저장
2. 유효성 검증
3. [BackgroundTask] 경로 이미지 생성 (02_walks)
4. [BackgroundTask] 뱃지 체크 ← 여기
     │
     ├── badge_service.check_badges(user_id, walk)
     │     ├── 거리 뱃지 체크 (단일 + 누적)
     │     ├── 연속 뱃지 체크 (streak 계산)
     │     ├── 탐험 뱃지 체크 (장소 비교)
     │     ├── 시간 뱃지 체크 (단일 + 누적)
     │     ├── 특별 뱃지 체크 (시간대, 사진 수, 날씨)
     │     └── 시즌 뱃지 체크 (현재 날짜 기준)
     │
     ├── 새로 달성한 뱃지 → user_badges에 INSERT
     └── 달성 결과 저장 (알림용)
```

### 4.2 체크 로직 예시

```python
class BadgeService:

    async def check_badges(self, user_id: int, walk: Walk) -> list[str]:
        """산책 완료 후 뱃지 달성 여부 체크. 새로 달성한 뱃지 ID 리스트 반환."""
        earned = []

        # 이미 보유한 뱃지 조회
        owned = await self._get_owned_badge_ids(user_id)

        # 거리 뱃지
        if "D01" not in owned:
            earned.append("D01")  # 첫 산책은 무조건 달성

        if "D02" not in owned and walk.distance_m >= 1000:
            earned.append("D02")

        # 누적 거리
        total_dist = await self._get_total_distance(user_id)
        if "D05" not in owned and total_dist >= 50000:
            earned.append("D05")

        # 연속 뱃지
        streak = await self._get_current_streak(user_id)
        if "S01" not in owned and streak >= 3:
            earned.append("S01")

        # ... 나머지 뱃지 체크

        # 새로 달성한 뱃지 저장
        for badge_id in earned:
            await self._grant_badge(user_id, badge_id)

        return earned
```

### 4.3 진행률 계산

뱃지 목록 조회 시 아직 달성 안 한 뱃지의 **현재 진행률**을 함께 반환.

```
예: "누적 100km" 뱃지
현재 누적: 62.3km
진행률: 62.3 / 100 = 0.623 (62%)
```

---

## 5. DB 테이블

### badge_definitions (시드 데이터 45개)

| 필드 | 타입 | 설명 |
|------|------|------|
| id | String(5) PK | 뱃지 코드 (D01, S01, ...) |
| category | String(20) | 카테고리 코드 |
| name | String(50) | 뱃지 이름 |
| description | Text | 달성 조건 설명 |
| icon | String(10) | 이모지 아이콘 |
| condition_type | String(20) | 조건 유형 (아래 표 참조) |
| condition_value | Integer | 조건 수치 (1000 = 1km, 3 = 3일 등) |
| season_start | String(5) | 시즌 시작 (MM-DD), null이면 상시 |
| season_end | String(5) | 시즌 종료 (MM-DD) |
| sort_order | Integer | 카테고리 내 정렬 |

### condition_type 종류

| condition_type | 설명 | condition_value 단위 |
|----------------|------|-------------------|
| `single_distance` | 단일 산책 거리 | 미터 |
| `total_distance` | 누적 거리 | 미터 |
| `streak_days` | 연속 산책 일수 | 일 |
| `unique_places` | 서로 다른 장소 수 | 개 |
| `unique_regions` | 서로 다른 지역 수 | 개 |
| `same_place_visits` | 같은 장소 방문 횟수 | 회 |
| `single_duration` | 단일 산책 시간 | 초 |
| `total_duration` | 누적 시간 | 초 |
| `time_before` | 특정 시각 이전 시작 | 시 (6 = 오전 6시) |
| `time_after` | 특정 시각 이후 시작 | 시 (22 = 오후 10시) |
| `weather_condition` | 날씨 조건 | 코드 (rain, snow) |
| `photo_count` | 한 산책 사진 수 | 장 |
| `feed_share_count` | 피드 공유 횟수 | 회 |
| `monthly_walk_count` | 월간 산책 횟수 | 회 |
| `weekend_walk_count` | 주말 산책 횟수 | 회 |
| `season_distance` | 시즌 기간 누적 거리 | 미터 |
| `specific_date` | 특정 날짜 산책 | MMDD |

### user_badges

| 필드 | 타입 | 설명 |
|------|------|------|
| id | BigInteger PK | |
| user_id | BigInteger FK | 사용자 |
| badge_id | String(5) FK | 뱃지 코드 |
| earned_at | DateTime | 달성 시각 |
| walk_id | BigInteger FK | 달성 계기가 된 산책 (nullable) |

> UNIQUE(user_id, badge_id) — 같은 뱃지 중복 달성 방지

---

## 6. API 상세

### 6.1 뱃지 전체 목록 — `GET /badges`

**응답**
```json
{
  "categories": [
    {
      "code": "distance",
      "name": "거리",
      "badges": [
        {
          "id": "D01",
          "name": "첫 발자국",
          "description": "첫 산책 완료",
          "icon": "🐾",
          "is_earned": true,
          "earned_at": "2026-02-20T15:30:00Z",
          "progress": 1.0
        },
        {
          "id": "D05",
          "name": "누적 50km",
          "description": "총 누적 거리 50km",
          "icon": "🛤️",
          "is_earned": false,
          "earned_at": null,
          "progress": 0.623,
          "progress_text": "31.2 / 50 km"
        }
      ],
      "earned_count": 3,
      "total_count": 8
    }
  ],
  "total_earned": 12,
  "total_count": 45
}
```

### 6.2 뱃지 상세 — `GET /badges/{id}`

```json
{
  "id": "D05",
  "name": "누적 50km",
  "description": "총 누적 거리 50km 달성",
  "icon": "🛤️",
  "category": "distance",
  "is_earned": false,
  "progress": 0.623,
  "progress_text": "31.2 / 50 km",
  "condition_type": "total_distance",
  "condition_value": 50000
}
```

### 6.3 진행 중 뱃지 — `GET /badges/in-progress`

**용도**: 메인페이지 챌린지 카드 (진행률 70% 이상인 뱃지 우선)

**응답**: 진행률 상위 4개 뱃지

```json
{
  "items": [
    {
      "id": "S02",
      "name": "7일 연속",
      "icon": "💪",
      "progress": 0.857,
      "progress_text": "6 / 7 일"
    }
  ]
}
```

### 6.4 산책 완료 응답에 뱃지 포함

`POST /walks/{id}/complete` 응답에 추가:

```json
{
  "id": 123,
  "distance_m": 3200,
  "...": "...",
  "earned_badges": [
    {
      "id": "D02",
      "name": "1km 돌파",
      "icon": "📍"
    }
  ]
}
```

---

## 7. 서비스 모듈

```
server/app/
├── services/
│   └── badge_service.py     # 뱃지 체크 + 진행률 계산
├── routers/
│   └── badges.py            # API 엔드포인트
├── models/
│   └── badge.py             # BadgeDefinition, UserBadge 모델
└── schemas/
    └── badge.py             # 요청/응답 스키마
```

---

## 8. 구현 우선순위

| 순서 | 항목 | 난이도 |
|------|------|--------|
| 1 | badge_definitions, user_badges 모델 + 마이그레이션 | 쉬움 |
| 2 | 시드 데이터 45개 INSERT | 쉬움 |
| 3 | badge_service.py (체크 로직) | 높음 |
| 4 | `GET /badges` (전체 목록 + 진행률) | 중간 |
| 5 | `GET /badges/{id}`, `GET /badges/in-progress` | 쉬움 |
| 6 | walks.py complete 응답에 earned_badges 연동 | 중간 |

---

*작성일: 2026-03-03*
*기준: PROPOSAL.md v2.0 + 프로토타입 뱃지.html*
*참고: 챌린지 시스템은 10_challenges.md에서 별도 설계*
