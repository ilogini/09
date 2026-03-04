# 10. 챌린지 시스템

> 기준: 프로토타입 (소셜.html 챌린지 탭) + 06_badges.md 구분 정의
> 상위 문서: [BACKEND_PLAN.md](./BACKEND_PLAN.md)

---

## 0. 뱃지 vs 챌린지 (재확인)

| | 뱃지 (06_badges) | 챌린지 (이 문서) |
|--|------------------|-----------------|
| 성격 | 도전 (자동 달성) | 퀘스트 (수락 → 완료) |
| 발동 | 조건 충족 시 자동 | 유저가 참가 신청 |
| 기간 | 없음 (상시) | 시작일 ~ 종료일 |
| 참여자 | 개인 | 개인 또는 그룹 |
| 생성자 | 시스템 (시드 데이터) | 관리자 또는 유저 |
| 보상 | 뱃지 아이콘 + 칭호 해금 | 칭호 / 아이콘 / 스킨 (관리자 챌린지) |

---

## 1. 핵심 요약

| 항목 | 내용 |
|------|------|
| **챌린지 종류** | 관리자 제공 (이달의) + 유저 생성 |
| **목표 유형** | 거리 (km) / 시간 (분) / 횟수 (회) |
| **공개 설정** | 공개 (누구나 참가) / 비공개 (초대 전용 or 개인) |
| **기간** | 시작일 ~ 종료일 자유 설정 |
| **리더보드** | 챌린지 내 참가자 순위 |
| **보상 연동** | 관리자 챌린지 → 기간 한정 칭호/아이콘/스킨 |

---

## 2. 챌린지 종류

### 2.1 관리자 제공 챌린지

| 항목 | 설명 |
|------|------|
| 생성 | 관리자가 생성 (admin API 또는 시드) |
| 주기 | 주간 / 월간 / 이벤트 |
| 노출 | "이달의 챌린지" 섹션에 표시 |
| 참가 | 공개 — 누구나 참가 가능 |
| 보상 | 기간 한정 특수 칭호 / 아이콘 / 스킨 (선택적) |

```
예시:
- "3월 봄맞이 산책 챌린지" — 목표 50km, 3/1~3/31
  → 달성 시 🌸 봄산책러 칭호 + 벚꽃 프로필 프레임
- "주간 10km 도전" — 매주 자동 갱신
  → 달성 시 포인트 or 뱃지 진행률 반영
```

### 2.2 유저 생성 챌린지

| 항목 | 설명 |
|------|------|
| 생성 | 유저가 직접 생성 |
| 공개 | 공개 or 비공개 선택 |
| 참가 | 공개: 누구나 / 비공개: 초대받은 친구만 or 혼자 |
| 보상 | 없음 (기록 + 달성감만) |

```
예시:
- "우리 동네 산책 챌린지" — 공개, 목표 10km, 친구 5명 초대
- "이번 주 매일 산책" — 비공개, 혼자, 목표 7회
```

---

## 3. 목표 유형

| goal_type | 단위 | 설명 | 예시 |
|-----------|------|------|------|
| `distance` | m (미터) | 총 산책 거리 | 50,000 (50km) |
| `duration` | sec (초) | 총 산책 시간 | 36,000 (10시간) |
| `count` | 회 | 산책 횟수 | 20 (20회) |

> DB에는 정수로 저장 (m, sec, 회), 프론트에서 km/시간 변환 표시

---

## 4. 공개/비공개

| visibility | 설명 | 참가 방식 |
|-----------|------|----------|
| `public` | 누구나 검색/참가 가능 | 자유 참가 |
| `private` | 초대받은 친구만 참가, 또는 혼자 | 초대 링크/목록 |

### 비공개 챌린지 초대 흐름

```
유저 A가 비공개 챌린지 생성
  → 친구 목록에서 B, C 선택하여 초대
  → challenge_invitations에 (challenge_id, invited_user_id, status=pending) 저장
  → B, C에게 알림 (Phase 4)

B가 수락 → challenge_participants에 등록
C가 거절 → invitation.status = 'declined'
```

---

## 5. 챌린지 라이프사이클

```
[생성] → [모집 중] → [진행 중] → [종료] → [정산]

created ─→ active ─→ in_progress ─→ completed
                                   ─→ expired (기간 만료)
```

| 상태 | 조건 | 설명 |
|------|------|------|
| `active` | 생성 완료 | 참가자 모집 중 (시작일 전) |
| `in_progress` | 시작일 도달 | 진행 중 (산책 거리/시간/횟수 집계) |
| `completed` | 종료일 도달 | 종료 — 결과 확정 |

> 시작일 = 생성일인 경우 바로 `in_progress`
> 스케줄러가 매일 00:05에 상태 전환 체크

### 개인 달성 여부

```
참가자별 진행률:
  progress = 현재값 / 목표값 × 100

달성 조건:
  progress >= 100% → user_challenge.status = 'achieved'

미달성:
  종료일 경과 + progress < 100% → user_challenge.status = 'failed'
```

---

## 6. 보상 시스템

### 6.1 관리자 챌린지 보상

관리자가 챌린지 생성 시 보상을 설정할 수 있다.

| 보상 유형 | reward_type | 설명 |
|----------|-------------|------|
| 칭호 | `title` | 기간 한정 특수 칭호 (예: 🌸 봄산책러) |
| 아이콘 | `icon` | 프로필 아이콘/프레임 |
| 스킨 | `skin` | 앱 내 시각 요소 (테마 등) |

```python
# challenge_rewards 테이블
{
    "challenge_id": 1,
    "reward_type": "title",           # title / icon / skin
    "reward_name": "봄산책러",
    "reward_icon": "🌸",
    "reward_description": "2026 봄맞이 챌린지 달성자",
    "reward_asset_url": null,         # 아이콘/스킨인 경우 R2 URL
    "is_limited": true,               # 기간 한정 여부
}
```

### 6.2 보상 지급 흐름

```
챌린지 종료 (스케줄러)
  → 달성자 목록 추출 (progress >= 100%)
  → challenge_rewards 확인
  → 있으면 → user_rewards 테이블에 보상 지급
  → 칭호인 경우 → user_titles에도 추가 (07_grades_titles 연동)
```

### 6.3 user_rewards (유저 보상 보관함)

| 필드 | 타입 | 설명 |
|------|------|------|
| id | Integer PK | |
| user_id | BigInteger FK | |
| reward_type | String(10) | `title`, `icon`, `skin` |
| reward_name | String(50) | 표시 이름 |
| reward_icon | String(10) | 이모지/아이콘 |
| reward_asset_url | String(500) | R2 URL (아이콘/스킨) |
| source_type | String(20) | `challenge` (향후 `event`, `premium` 등 확장) |
| source_id | Integer | challenge_id |
| is_limited | Boolean | 기간 한정 여부 |
| earned_at | DateTime | 획득 시점 |

> 07_grades_titles의 title_definitions와 별개로 관리
> title_definitions = 뱃지 기반 상시 칭호
> user_rewards = 챌린지/이벤트 기반 한정 보상

---

## 7. API 목록

### 7.1 챌린지 CRUD

| Method | Path | 설명 |
|--------|------|------|
| POST | `/challenges` | 챌린지 생성 (유저/관리자) |
| GET | `/challenges` | 챌린지 목록 (필터: monthly/public/my) |
| GET | `/challenges/{id}` | 챌린지 상세 (리더보드 포함) |
| PATCH | `/challenges/{id}` | 챌린지 수정 (생성자/관리자만, 시작 전만) |
| DELETE | `/challenges/{id}` | 챌린지 삭제 (생성자/관리자만, 시작 전만) |

### 7.2 참가

| Method | Path | 설명 |
|--------|------|------|
| POST | `/challenges/{id}/join` | 공개 챌린지 참가 |
| DELETE | `/challenges/{id}/leave` | 참가 취소 (시작 전만) |
| POST | `/challenges/{id}/invite` | 비공개 챌린지 친구 초대 |
| PATCH | `/challenges/invitations/{id}/accept` | 초대 수락 |
| PATCH | `/challenges/invitations/{id}/decline` | 초대 거절 |
| GET | `/challenges/invitations` | 내가 받은 초대 목록 |

### 7.3 진행/결과

| Method | Path | 설명 |
|--------|------|------|
| GET | `/challenges/{id}/leaderboard` | 참가자 순위 |
| GET | `/challenges/{id}/my-progress` | 내 진행률 |
| GET | `/challenges/my` | 내가 참가 중인 챌린지 목록 |

### 7.4 관리자 전용

| Method | Path | 설명 |
|--------|------|------|
| POST | `/admin/challenges` | 관리자 챌린지 생성 (보상 포함) |
| POST | `/admin/challenges/{id}/rewards` | 보상 추가 |

---

## 8. API 상세

### 8.1 챌린지 생성 — `POST /challenges`

**요청**
```json
{
  "title": "우리 동네 산책 챌린지",
  "description": "3월 한달간 10km 걸어보자!",
  "goal_type": "distance",
  "goal_value": 10000,
  "start_date": "2026-03-01",
  "end_date": "2026-03-31",
  "visibility": "public",
  "invite_user_ids": []
}
```

**응답**
```json
{
  "id": 42,
  "title": "우리 동네 산책 챌린지",
  "creator": {
    "id": 102,
    "nickname": "초코",
    "tag_code": "1234"
  },
  "goal_type": "distance",
  "goal_value": 10000,
  "goal_display": "10 km",
  "start_date": "2026-03-01",
  "end_date": "2026-03-31",
  "visibility": "public",
  "status": "in_progress",
  "participant_count": 1,
  "is_admin_challenge": false,
  "rewards": [],
  "created_at": "2026-03-01T10:00:00+09:00"
}
```

### 8.2 챌린지 목록 — `GET /challenges`

**요청**
```
GET /challenges?filter=monthly&status=in_progress&page=1&size=10
```

| 파라미터 | 필수 | 기본값 | 설명 |
|---------|------|--------|------|
| filter | X | all | `all`, `monthly` (관리자), `public`, `my` |
| status | X | in_progress | `active`, `in_progress`, `completed` |
| page | X | 1 | 페이지 |
| size | X | 10 | 페이지 크기 |

### 8.3 챌린지 상세 — `GET /challenges/{id}`

**응답**
```json
{
  "id": 42,
  "title": "3월 봄맞이 산책 챌린지",
  "description": "봄을 맞아 50km 걸어보세요!",
  "creator": { "id": 0, "nickname": "멍이랑", "is_admin": true },
  "goal_type": "distance",
  "goal_value": 50000,
  "goal_display": "50 km",
  "start_date": "2026-03-01",
  "end_date": "2026-03-31",
  "days_remaining": 27,
  "visibility": "public",
  "status": "in_progress",
  "participant_count": 87,
  "is_admin_challenge": true,
  "my_progress": {
    "current_value": 23500,
    "current_display": "23.5 km",
    "progress_percent": 47.0,
    "status": "in_progress"
  },
  "rewards": [
    {
      "reward_type": "title",
      "reward_name": "봄산책러",
      "reward_icon": "🌸",
      "reward_description": "2026 봄맞이 챌린지 달성자",
      "is_limited": true
    }
  ],
  "leaderboard_preview": [
    { "rank": 1, "nickname": "초코아빠", "tag_code": "4567", "value": 48200, "display": "48.2 km" },
    { "rank": 2, "nickname": "달이맘", "tag_code": "8901", "value": 41000, "display": "41.0 km" },
    { "rank": 3, "nickname": "나", "tag_code": "1234", "value": 23500, "display": "23.5 km" }
  ]
}
```

---

## 9. DB 테이블

### challenges

| 필드 | 타입 | 설명 |
|------|------|------|
| id | Integer PK | |
| creator_id | BigInteger FK | 생성자 (관리자면 null or 0) |
| title | String(100) | 챌린지 이름 |
| description | Text | 설명 |
| goal_type | String(10) | `distance`, `duration`, `count` |
| goal_value | Integer | 목표값 (m / sec / 회) |
| start_date | Date | 시작일 |
| end_date | Date | 종료일 |
| visibility | String(10) | `public`, `private` |
| status | String(15) | `active`, `in_progress`, `completed` |
| is_admin | Boolean | 관리자 제공 여부 |
| created_at | DateTime | |

### challenge_participants

| 필드 | 타입 | 설명 |
|------|------|------|
| id | Integer PK | |
| challenge_id | Integer FK | |
| user_id | BigInteger FK | |
| current_value | Integer | 현재 진행값 (m / sec / 회) |
| progress_percent | Float | 진행률 (%) |
| status | String(10) | `in_progress`, `achieved`, `failed` |
| joined_at | DateTime | 참가 시점 |
| achieved_at | DateTime | 달성 시점 (nullable) |

> UNIQUE(challenge_id, user_id)

### challenge_invitations

| 필드 | 타입 | 설명 |
|------|------|------|
| id | Integer PK | |
| challenge_id | Integer FK | |
| inviter_id | BigInteger FK | 초대한 유저 |
| invited_id | BigInteger FK | 초대받은 유저 |
| status | String(10) | `pending`, `accepted`, `declined` |
| created_at | DateTime | |

> UNIQUE(challenge_id, invited_id)

### challenge_rewards

| 필드 | 타입 | 설명 |
|------|------|------|
| id | Integer PK | |
| challenge_id | Integer FK | |
| reward_type | String(10) | `title`, `icon`, `skin` |
| reward_name | String(50) | 보상 이름 |
| reward_icon | String(10) | 이모지 |
| reward_description | String(200) | 설명 |
| reward_asset_url | String(500) | R2 URL (nullable) |
| is_limited | Boolean | 기간 한정 여부 |

### user_rewards

| 필드 | 타입 | 설명 |
|------|------|------|
| id | Integer PK | |
| user_id | BigInteger FK | |
| reward_type | String(10) | `title`, `icon`, `skin` |
| reward_name | String(50) | |
| reward_icon | String(10) | |
| reward_asset_url | String(500) | |
| source_type | String(20) | `challenge` (확장: `event`, `premium`) |
| source_id | Integer | challenge_id 등 |
| is_limited | Boolean | |
| earned_at | DateTime | |

> UNIQUE(user_id, source_type, source_id, reward_type)

---

## 10. 진행률 집계

### 10.1 산책 완료 시 업데이트

```python
async def update_challenge_progress(user_id: int, walk: Walk):
    """산책 완료 시 참가 중인 챌린지 진행률 업데이트"""

    # 진행 중인 챌린지에서 내가 참가한 것
    participants = await db.execute(
        select(ChallengeParticipant)
        .join(Challenge)
        .where(
            ChallengeParticipant.user_id == user_id,
            ChallengeParticipant.status == 'in_progress',
            Challenge.status == 'in_progress',
        )
    )

    for p in participants.scalars():
        challenge = p.challenge

        # 목표 유형에 따라 진행값 증가
        if challenge.goal_type == 'distance':
            p.current_value += walk.distance_m
        elif challenge.goal_type == 'duration':
            p.current_value += walk.duration_sec
        elif challenge.goal_type == 'count':
            p.current_value += 1

        # 진행률 계산
        p.progress_percent = min(
            (p.current_value / challenge.goal_value) * 100,
            100.0
        )

        # 달성 체크
        if p.progress_percent >= 100 and p.status != 'achieved':
            p.status = 'achieved'
            p.achieved_at = datetime.now(KST)
            # 보상 지급 (있으면)
            await grant_rewards(user_id, challenge)

    await db.commit()
```

### 10.2 보상 지급

```python
async def grant_rewards(user_id: int, challenge: Challenge):
    """챌린지 달성 시 보상 지급"""
    rewards = await db.execute(
        select(ChallengeReward).where(ChallengeReward.challenge_id == challenge.id)
    )

    for reward in rewards.scalars():
        # user_rewards에 저장
        user_reward = UserReward(
            user_id=user_id,
            reward_type=reward.reward_type,
            reward_name=reward.reward_name,
            reward_icon=reward.reward_icon,
            reward_asset_url=reward.reward_asset_url,
            source_type='challenge',
            source_id=challenge.id,
            is_limited=reward.is_limited,
            earned_at=datetime.now(KST),
        )
        db.add(user_reward)

        # 칭호인 경우 → user_titles에도 추가 (선택 가능하도록)
        if reward.reward_type == 'title':
            await add_user_title(user_id, reward)
```

---

## 11. 스케줄러

```python
@scheduler.scheduled_job('cron', hour=0, minute=5, timezone='Asia/Seoul')
async def update_challenge_statuses():
    """매일 00:05 — 챌린지 상태 전환"""
    today = date.today()

    # active → in_progress (시작일 도달)
    await db.execute(
        update(Challenge)
        .where(Challenge.status == 'active', Challenge.start_date <= today)
        .values(status='in_progress')
    )

    # in_progress → completed (종료일 경과)
    expired = await db.execute(
        select(Challenge)
        .where(Challenge.status == 'in_progress', Challenge.end_date < today)
    )
    for challenge in expired.scalars():
        challenge.status = 'completed'
        # 미달성자 status 변경
        await db.execute(
            update(ChallengeParticipant)
            .where(
                ChallengeParticipant.challenge_id == challenge.id,
                ChallengeParticipant.status == 'in_progress',
            )
            .values(status='failed')
        )

    await db.commit()
```

---

## 12. 서비스 모듈 구조

```
server/app/
├── services/
│   └── challenge_service.py    # CRUD, 참가, 진행률, 보상 지급
├── routers/
│   ├── challenges.py           # 일반 API
│   └── admin_challenges.py     # 관리자 API
├── models/
│   ├── challenge.py            # Challenge, ChallengeParticipant
│   ├── challenge_invitation.py # ChallengeInvitation
│   └── challenge_reward.py     # ChallengeReward, UserReward
├── schemas/
│   └── challenge.py            # 요청/응답 스키마
└── tasks/
    └── challenge_scheduler.py  # 상태 전환 스케줄러
```

---

## 13. 산책 완료 응답 통합

산책 완료 시 (`POST /walks/{id}/complete`) 응답에 포함되는 정보:

```json
{
  "walk": { ... },
  "earned_badges": [...],
  "earned_titles": [...],
  "grade_up": null,
  "challenge_updates": [
    {
      "challenge_id": 42,
      "title": "3월 봄맞이 산책 챌린지",
      "progress_percent": 72.5,
      "just_achieved": false
    },
    {
      "challenge_id": 15,
      "title": "매일 산책 챌린지",
      "progress_percent": 100.0,
      "just_achieved": true,
      "rewards": [
        { "reward_type": "title", "reward_name": "봄산책러", "reward_icon": "🌸" }
      ]
    }
  ]
}
```

---

## 14. 구현 우선순위

| 순서 | 항목 | 난이도 |
|------|------|--------|
| 1 | challenges + challenge_participants 모델 | 쉬움 |
| 2 | 챌린지 CRUD API | 중간 |
| 3 | 참가/탈퇴 API (공개) | 쉬움 |
| 4 | 산책 완료 시 진행률 업데이트 연동 | 중간 |
| 5 | 챌린지 리더보드 API | 중간 |
| 6 | challenge_invitations (비공개 초대) | 중간 |
| 7 | challenge_rewards + user_rewards 모델 | 중간 |
| 8 | 관리자 API + 보상 지급 로직 | 높음 |
| 9 | 스케줄러 (상태 전환) | 중간 |

---

*작성일: 2026-03-04*
*기준: 프로토타입 소셜.html 챌린지 탭 + 06_badges 뱃지/챌린지 구분 + 보상 연동*
