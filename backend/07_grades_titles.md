# 07. 등급 / 칭호 시스템

> 기준: PROPOSAL.md v2.0 + 06_badges.md 연동
> 상위 문서: [BACKEND_PLAN.md](./BACKEND_PLAN.md)

---

## 0. 등급 vs 칭호 — 구분

| | 등급 (Grade) | 칭호 (Title) |
|--|-------------|-------------|
| **개념** | 레벨 (경험치) | 훈장 (장식) |
| **기준** | 누적 산책 거리 | 뱃지/챌린지 달성 |
| **적용** | **자동** — 거리 달성 시 자동 승급 | **유저 선택** — 해금된 것 중 1개 장착 |
| **표시** | 프로필에 항상 표시 (Lv.5 등) | 프로필 닉네임 옆에 선택한 칭호 표시 |
| **변경** | 불가 (올라가기만 함) | 자유롭게 변경 가능 |

---

## 1. 등급 시스템 (10단계)

### 1.1 등급 테이블

| 레벨 | 등급명 | 필요 누적 거리 | 아이콘 |
|------|--------|--------------|--------|
| 1 | 산책 새싹 | 0 km | 🌱 |
| 2 | 산책 입문자 | 10 km | 🐕 |
| 3 | 동네 산책러 | 30 km | 🚶 |
| 4 | 산책 탐험가 | 70 km | 🧭 |
| 5 | 산책 매니아 | 150 km | 🏃 |
| 6 | 산책 전문가 | 300 km | 🎯 |
| 7 | 산책 달인 | 500 km | ⭐ |
| 8 | 산책 마스터 | 1,000 km | 🏅 |
| 9 | 산책 그랜드마스터 | 2,000 km | 👑 |
| 10 | 산책 레전드 | 5,000 km | 💎 |

### 1.2 자동 승급 로직

```
POST /walks/{id}/complete 처리 흐름:

1. Walk 저장
2. [BackgroundTask] 뱃지 체크 (06_badges)
3. [BackgroundTask] 등급 체크 ← 여기
     │
     ├── 현재 누적 거리 조회
     ├── grade_definitions에서 해당 거리의 등급 계산
     ├── 현재 등급과 비교
     ├── 승급 시 → users.grade_id 업데이트
     └── 승급 결과 반환 (알림용)
```

```python
async def check_grade(self, user_id: int) -> dict | None:
    """등급 체크. 승급 시 새 등급 반환, 변동 없으면 None."""
    total_km = await self._get_total_distance_km(user_id)

    # 거리에 해당하는 최고 등급 조회
    new_grade = await db.execute(
        select(GradeDefinition)
        .where(GradeDefinition.required_km <= total_km)
        .order_by(GradeDefinition.level.desc())
        .limit(1)
    )
    # 현재 등급과 비교 → 다르면 승급
```

### 1.3 프로필 표시

```
┌─────────────────────────┐
│  🐕 Lv.3 동네 산책러      │  ← 등급
│  닉네임  [꾸준한 산책러]    │  ← 칭호
│  다음 등급까지 28.5km      │  ← 진행률
└─────────────────────────┘
```

---

## 2. 칭호 시스템

### 2.1 칭호 = 뱃지/챌린지 달성 보상

칭호는 **별도 테이블에 정의**하되, 해금 조건이 **뱃지 또는 챌린지 달성**에 연동됨.

```
뱃지 D06 "누적 100km" 달성
  → 칭호 "백리길의 주인공" 자동 해금
  → 유저가 프로필에서 선택 가능
```

### 2.2 칭호 목록 (10개, 샘플)

| ID | 칭호명 | 해금 조건 | 연동 |
|----|--------|---------|------|
| T01 | 첫걸음의 주인공 | 뱃지 D01 달성 (첫 산책) | 뱃지 |
| T02 | 꾸준한 산책러 | 뱃지 S02 달성 (7일 연속) | 뱃지 |
| T03 | 비가 와도 산책 | 뱃지 P03 달성 (비 오는 날) | 뱃지 |
| T04 | 백리길의 주인공 | 뱃지 D06 달성 (누적 100km) | 뱃지 |
| T05 | 동네 탐험 대장 | 뱃지 E03 달성 (10곳 탐험) | 뱃지 |
| T06 | 새벽의 산책자 | 뱃지 P01 달성 (얼리버드) | 뱃지 |
| T07 | 사계절 산책러 | 시즌 뱃지 4개 모두 달성 (N01~N04) | 뱃지 |
| T08 | 챌린지 정복자 | 챌린지 5개 완료 | 챌린지 |
| T09 | 천리길의 전설 | 뱃지 D08 달성 (누적 1,000km) | 뱃지 |
| T10 | 산책의 레전드 | 뱃지 30개 이상 달성 | 뱃지 |

> 칭호는 점진적으로 추가 가능. 뱃지/챌린지가 늘어나면 칭호도 함께 늘어남.

### 2.3 해금 로직

```
뱃지 달성 시 (badge_service.check_badges):
  → 새로 달성한 뱃지 확인
  → title_definitions에서 해당 뱃지가 해금 조건인 칭호 조회
  → 조건 충족 시 user_titles에 INSERT (해금)

챌린지 완료 시 (challenge_service, Phase 3):
  → 완료한 챌린지 수 확인
  → 챌린지 기반 칭호 조건 체크
```

### 2.4 칭호 선택/변경

```
PATCH /users/me/title
{ "title_id": "T02" }

→ 유저가 해금한 칭호 중에서만 선택 가능
→ users.active_title_id 업데이트
→ title_id가 null이면 칭호 해제
```

---

## 3. DB 테이블

### grade_definitions (시드 데이터 10개)

| 필드 | 타입 | 설명 |
|------|------|------|
| id | Integer PK | 레벨 (1~10) |
| name | String(30) | 등급명 |
| required_km | Integer | 필요 누적 거리 (km) |
| icon | String(10) | 이모지 아이콘 |

### title_definitions (시드 데이터 10개)

| 필드 | 타입 | 설명 |
|------|------|------|
| id | String(5) PK | 칭호 코드 (T01~T10) |
| name | String(30) | 칭호명 |
| unlock_type | String(20) | 해금 유형: `badge`, `badge_count`, `challenge_count` |
| unlock_value | String(20) | 해금 값: 뱃지 ID, 개수 등 |
| description | Text | 해금 조건 설명 |

**unlock_type 종류:**

| unlock_type | unlock_value 예시 | 설명 |
|-------------|-----------------|------|
| `badge` | `D01` | 특정 뱃지 1개 달성 |
| `badge_multi` | `N01,N02,N03,N04` | 특정 뱃지 여러 개 모두 달성 |
| `badge_count` | `30` | 뱃지 N개 이상 달성 |
| `challenge_count` | `5` | 챌린지 N개 이상 완료 |

### user_titles (유저별 해금 기록)

| 필드 | 타입 | 설명 |
|------|------|------|
| id | BigInteger PK | |
| user_id | BigInteger FK | 사용자 |
| title_id | String(5) FK | 칭호 코드 |
| unlocked_at | DateTime | 해금 시각 |

> UNIQUE(user_id, title_id)

### users 테이블 변경

| 추가 필드 | 타입 | 설명 |
|----------|------|------|
| grade_id | Integer FK → grade_definitions | 현재 등급 (기본 1) |
| active_title_id | String(5) FK → title_definitions | 선택한 칭호 (nullable) |

---

## 4. API 상세

### 4.1 등급 목록 — `GET /grades`

```json
{
  "grades": [
    { "level": 1, "name": "산책 새싹", "icon": "🌱", "required_km": 0 },
    { "level": 2, "name": "산책 입문자", "icon": "🐕", "required_km": 10 },
    ...
  ]
}
```

### 4.2 내 현재 등급 — `GET /users/me/grade`

```json
{
  "current": {
    "level": 3,
    "name": "동네 산책러",
    "icon": "🚶"
  },
  "total_km": 41.5,
  "next": {
    "level": 4,
    "name": "산책 탐험가",
    "icon": "🧭",
    "required_km": 70,
    "remaining_km": 28.5,
    "progress": 0.593
  }
}
```

### 4.3 칭호 목록 — `GET /titles`

```json
{
  "titles": [
    {
      "id": "T01",
      "name": "첫걸음의 주인공",
      "description": "첫 산책 완료",
      "is_unlocked": true,
      "unlocked_at": "2026-02-20T15:30:00Z",
      "is_active": false
    },
    {
      "id": "T02",
      "name": "꾸준한 산책러",
      "description": "7일 연속 산책 달성",
      "is_unlocked": true,
      "unlocked_at": "2026-02-27T10:00:00Z",
      "is_active": true
    },
    {
      "id": "T04",
      "name": "백리길의 주인공",
      "description": "누적 100km 달성",
      "is_unlocked": false,
      "linked_badge": "D06",
      "badge_progress": 0.623
    }
  ],
  "unlocked_count": 2,
  "total_count": 10
}
```

### 4.4 칭호 변경 — `PATCH /users/me/title`

**요청**
```json
{ "title_id": "T02" }
```

**검증**: 해당 칭호가 해금되었는지 확인
**응답**: 200 + UserResponse

칭호 해제: `{ "title_id": null }`

---

## 5. 산책 완료 응답 확장

`POST /walks/{id}/complete` 응답에 등급 승급 정보 추가:

```json
{
  "id": 123,
  "distance_m": 3200,
  "earned_badges": [{ "id": "D05", "name": "누적 50km", "icon": "🛤️" }],
  "earned_titles": [{ "id": "T04", "name": "백리길의 주인공" }],
  "grade_up": {
    "from": { "level": 2, "name": "산책 입문자" },
    "to": { "level": 3, "name": "동네 산책러" }
  }
}
```

> `earned_badges`, `earned_titles`, `grade_up` 모두 없으면 null

---

## 6. 구현 우선순위

| 순서 | 항목 | 난이도 |
|------|------|--------|
| 1 | grade_definitions, title_definitions 모델 + 시드 | 쉬움 |
| 2 | user_titles 모델 + users에 grade_id, active_title_id 추가 | 쉬움 |
| 3 | 등급 자동 체크 (산책 완료 시) | 쉬움 |
| 4 | 칭호 자동 해금 (뱃지 달성 시 연동) | 중간 |
| 5 | `GET /grades`, `GET /users/me/grade` | 쉬움 |
| 6 | `GET /titles`, `PATCH /users/me/title` | 쉬움 |
| 7 | 산책 완료 응답에 grade_up, earned_titles 추가 | 중간 |

---

*작성일: 2026-03-03*
*기준: PROPOSAL.md v2.0 + 06_badges.md 연동*
