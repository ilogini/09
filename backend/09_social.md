# 09. 소셜 시스템

> 기준: 프로토타입 (소셜.html) + 사용자 확정 사항
> 상위 문서: [BACKEND_PLAN.md](./BACKEND_PLAN.md)

---

## 0. 핵심 요약

| 항목 | 내용 |
|------|------|
| **친구 방식** | 요청 → 수락 (쌍방향) |
| **친구 검색** | #태그 (고유 코드) + 강아지 이름 |
| **소셜 탭 구성** | 리더보드 + 챌린지 (2탭) |
| **피드/좋아요/댓글** | 없음 (제외) |
| **모임** | 없음 (제외) |
| **차단/신고** | 기본 구현 (앱스토어 심사 필수) |

---

## 1. 태그 시스템

### 1.1 개요

각 유저에게 고유한 **#태그** (숫자 코드)를 부여해서, 이미 알고 있는 유저를 친구 추가할 수 있게 한다.

```
예: 초코#1234, 달이#5678
표시: {닉네임}#{4자리 코드}
```

### 1.2 태그 생성 규칙

| 항목 | 규칙 |
|------|------|
| 형식 | 4자리 숫자 (0000~9999) |
| 생성 시점 | 회원가입(온보딩 완료) 시 자동 발급 |
| 고유성 | **닉네임 + 태그** 조합이 유니크 |
| 변경 | 불가 (고정) |

> 같은 닉네임 "초코"가 2명이어도 #1234, #5678로 구분 가능
> 닉네임 변경 시 태그는 유지

### 1.3 users 테이블 변경

| 추가 필드 | 타입 | 설명 |
|----------|------|------|
| tag_code | String(4) | 4자리 고유 코드 |

```python
# 태그 생성 로직
import random

async def generate_unique_tag(db, nickname: str) -> str:
    """닉네임+태그 조합이 유니크한 4자리 코드 생성"""
    for _ in range(100):  # 최대 100회 시도
        code = f"{random.randint(0, 9999):04d}"
        exists = await db.execute(
            select(User).where(User.nickname == nickname, User.tag_code == code)
        )
        if not exists.scalar_one_or_none():
            return code
    raise ValueError("태그 생성 실패 (닉네임 중복 과다)")
```

---

## 2. 친구 시스템

### 2.1 친구 요청 흐름

```
A가 B에게 친구 요청
  → friend_requests 테이블에 (from=A, to=B, status=pending) 저장
  → B에게 푸시 알림 (Phase 4)

B가 수락
  → friend_requests.status = 'accepted'
  → friendships 테이블에 (user_a, user_b) 저장 (양방향)
  → A에게 알림

B가 거절
  → friend_requests.status = 'rejected'
  → 끝 (A에게 별도 알림 없음)
```

### 2.2 친구 관계 특징

| 항목 | 설명 |
|------|------|
| 관계 | 양방향 (A↔B) |
| 저장 | 항상 user_a_id < user_b_id 로 정규화 (중복 방지) |
| 해제 | 어느 쪽이든 가능 (한쪽이 해제하면 관계 삭제) |
| 제한 | 최대 친구 수: 500명 |
| 중복 | 이미 친구인 상대에게 재요청 불가 |
| 차단 | 차단된 유저에게 요청 불가, 요청도 안 보임 |

---

## 3. 친구 검색

### 3.1 검색 방식

프로토타입 기준: `#태그 또는 강아지 이름으로 검색`

```
[검색어 판별 로직]

입력: "#1234"  → 태그 검색 (닉네임+태그 정확 매칭)
입력: "#초코"  → 닉네임 앞에 # → 닉네임 검색으로 처리
입력: "초코"   → 강아지 이름 OR 닉네임 통합 검색
입력: "골든"   → 견종 검색
```

### 3.2 검색 API 로직

```python
async def search_users(query: str, current_user_id: int):
    """유저/펫 통합 검색"""

    # 1. #태그 검색 (정확 매칭)
    if query.startswith('#') and query[1:].isdigit():
        tag_code = query[1:]
        return await db.execute(
            select(User).where(User.tag_code == tag_code)
        )

    # 2. 닉네임 + 펫 이름 + 견종 LIKE 검색
    keyword = f"%{query}%"
    users = await db.execute(
        select(User)
        .outerjoin(Pet)
        .where(
            or_(
                User.nickname.ilike(keyword),
                Pet.name.ilike(keyword),
                Pet.breed.ilike(keyword),
            ),
            User.id != current_user_id,  # 자신 제외
            ~User.id.in_(blocked_user_ids),  # 차단 유저 제외
        )
        .distinct()
        .limit(20)
    )
    return users
```

---

## 4. 친구 리더보드 (소셜 탭 1)

프로토타입의 "리더보드" 탭 = **친구들 간의 일별/주간 산책 현황**

### 4.1 주간 캘린더

```
[월] [화] [수] [목] [금] [토] [일]
 17   18   19   20   21   22   23
 🐾   🐾   🐾   🐾
```

> 각 요일에 친구들의 산책 여부를 발바닥 아이콘으로 표시
> 프론트가 주간 데이터를 한번에 받아서 렌더링

### 4.2 일별 리더보드

특정 날짜를 선택하면 해당 일의 **친구들 산책 거리 순위** 표시:

```
1위  초코#1234   4.2km
2위  달이#5678   3.8km
3위  나 (콩이)    2.1km  ← 내 순위 하이라이트
```

### 4.3 API

#### `GET /friends/leaderboard` — 친구 주간 리더보드

**요청**
```
GET /friends/leaderboard?week=2026-W09
```

| 파라미터 | 필수 | 기본값 | 설명 |
|---------|------|--------|------|
| week | X | 현재 주 | ISO 주차 (YYYY-WNN) |

**응답**
```json
{
  "week": "2026-W09",
  "week_label": "3월 1주차",
  "days": [
    {
      "date": "2026-03-02",
      "day_label": "월",
      "walks": [
        {
          "user_id": 101,
          "nickname": "초코",
          "tag_code": "1234",
          "pet_name": "보리",
          "distance_km": 3.5
        },
        {
          "user_id": 102,
          "nickname": "달이맘",
          "tag_code": "5678",
          "pet_name": "달이",
          "distance_km": 2.8
        }
      ]
    }
  ],
  "my_weekly_total_km": 12.3
}
```

> 친구 + 자신의 7일간 산책 데이터를 한 번에 반환
> 프론트에서 날짜 선택 시 해당 일 데이터로 리더보드 렌더링 (추가 API 호출 없음)

---

## 5. 차단/신고

### 5.1 차단

| 항목 | 설명 |
|------|------|
| 효과 | 차단된 유저의 친구 요청 차단, 검색 결과에서 제외, 리더보드에서 숨김 |
| 기존 관계 | 차단 시 친구 관계 자동 해제 |
| 양방향 | 차단하면 상대도 나를 검색/요청 불가 |
| 해제 | 차단 해제 가능 (친구 관계는 복원 안 됨, 재요청 필요) |

### 5.2 신고

| 항목 | 설명 |
|------|------|
| 신고 유형 | `spam`, `abuse`, `inappropriate_profile`, `other` |
| 처리 | 관리자 수동 검토 (자동 처리 없음) |
| 중복 | 같은 대상에 대해 1회만 가능 |
| 신고 후 | 자동으로 차단 추가 |

---

## 6. API 목록

### 6.1 친구 요청

| Method | Path | 설명 |
|--------|------|------|
| POST | `/friends/request/{user_id}` | 친구 요청 보내기 |
| GET | `/friends/requests/received` | 받은 요청 목록 |
| GET | `/friends/requests/sent` | 보낸 요청 목록 |
| PATCH | `/friends/requests/{request_id}/accept` | 수락 |
| PATCH | `/friends/requests/{request_id}/reject` | 거절 |
| DELETE | `/friends/requests/{request_id}` | 보낸 요청 취소 |

### 6.2 친구 관리

| Method | Path | 설명 |
|--------|------|------|
| GET | `/friends` | 내 친구 목록 |
| GET | `/friends/count` | 친구 수 |
| DELETE | `/friends/{user_id}` | 친구 해제 |
| GET | `/friends/leaderboard` | 친구 주간 리더보드 |

### 6.3 검색

| Method | Path | 설명 |
|--------|------|------|
| GET | `/users/search?q=` | 유저 검색 (#태그 / 닉네임 / 펫이름) |

### 6.4 차단/신고

| Method | Path | 설명 |
|--------|------|------|
| POST | `/blocks/{user_id}` | 차단 |
| DELETE | `/blocks/{user_id}` | 차단 해제 |
| GET | `/blocks` | 차단 목록 |
| POST | `/reports` | 신고 |

---

## 7. DB 테이블

### friend_requests (친구 요청)

| 필드 | 타입 | 설명 |
|------|------|------|
| id | Integer PK | |
| from_user_id | BigInteger FK | 요청 보낸 유저 |
| to_user_id | BigInteger FK | 요청 받은 유저 |
| status | String(10) | `pending`, `accepted`, `rejected` |
| created_at | DateTime | 요청 시각 |
| responded_at | DateTime | 수락/거절 시각 |

> UNIQUE(from_user_id, to_user_id)
> 인덱스: (to_user_id, status) — 받은 요청 조회 최적화

### friendships (친구 관계)

| 필드 | 타입 | 설명 |
|------|------|------|
| id | Integer PK | |
| user_a_id | BigInteger FK | 항상 작은 ID |
| user_b_id | BigInteger FK | 항상 큰 ID |
| created_at | DateTime | 친구 성립 시각 |

> UNIQUE(user_a_id, user_b_id)
> 저장 규칙: `user_a_id < user_b_id` (정규화)
> 친구 조회: `WHERE user_a_id = :me OR user_b_id = :me`

### blocks (차단)

| 필드 | 타입 | 설명 |
|------|------|------|
| id | Integer PK | |
| blocker_id | BigInteger FK | 차단한 유저 |
| blocked_id | BigInteger FK | 차단당한 유저 |
| created_at | DateTime | |

> UNIQUE(blocker_id, blocked_id)

### reports (신고)

| 필드 | 타입 | 설명 |
|------|------|------|
| id | Integer PK | |
| reporter_id | BigInteger FK | 신고한 유저 |
| reported_id | BigInteger FK | 신고당한 유저 |
| reason | String(30) | `spam`, `abuse`, `inappropriate_profile`, `other` |
| detail | Text | 상세 사유 (선택) |
| status | String(10) | `pending`, `reviewed`, `dismissed` |
| created_at | DateTime | |

> UNIQUE(reporter_id, reported_id)

---

## 8. 서비스 모듈 구조

```
server/app/
├── services/
│   ├── friend_service.py      # 요청/수락/거절, 친구 목록, 리더보드
│   ├── block_service.py       # 차단/해제
│   └── report_service.py      # 신고
├── routers/
│   ├── friends.py             # 친구 API
│   ├── blocks.py              # 차단 API
│   └── reports.py             # 신고 API
├── models/
│   ├── friendship.py          # FriendRequest, Friendship
│   ├── block.py               # Block
│   └── report.py              # Report
└── schemas/
    ├── friend.py              # 요청/응답 스키마
    └── report.py              # 신고 스키마
```

---

## 9. BACKEND_PLAN 대비 변경사항

| BACKEND_PLAN 원본 | 변경 |
|-------------------|------|
| `follows` 테이블 (일방향 팔로우) | `friendships` + `friend_requests` (양방향 친구) |
| `GET /follows/following`, `GET /follows/followers` | `GET /friends`, `GET /friends/requests/*` |
| `GET /follows/count` | `GET /friends/count` |
| `likes`, `comments` 테이블 | **삭제** (피드 없음) |
| `GET /feed`, `POST/DELETE /walks/{id}/like` | **삭제** |
| `GET/POST /walks/{id}/comments` | **삭제** |
| `meetups`, `meetup_participants` 테이블 | **삭제** (모임 기능 제외) |
| `invitations` 테이블 (산책 초대) | **삭제** (모임과 함께 제외) |
| `GET /users/search` | 유지 (태그 검색 추가) |

---

## 10. 구현 우선순위

| 순서 | 항목 | 난이도 |
|------|------|--------|
| 1 | users.tag_code 필드 + 태그 생성 로직 | 쉬움 |
| 2 | friend_requests / friendships 모델 | 쉬움 |
| 3 | 친구 요청/수락/거절 API | 중간 |
| 4 | 친구 목록/검색 API | 중간 |
| 5 | 친구 리더보드 API | 중간 |
| 6 | blocks / reports 모델 + API | 쉬움 |
| 7 | 검색 시 차단 유저 필터링 | 쉬움 |

---

*작성일: 2026-03-04*
*기준: 프로토타입 소셜.html + 사용자 확정 (양방향 친구, 태그 시스템, 피드/모임 제외)*
