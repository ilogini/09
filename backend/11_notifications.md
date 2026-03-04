# 11. 알림 시스템

> 기준: 프로토타입 (알림.html, 설정.html) + 앱 스토어 가이드라인
> 상위 문서: [BACKEND_PLAN.md](./BACKEND_PLAN.md)

---

## 0. 핵심 요약

| 항목 | 내용 |
|------|------|
| **푸시** | FCM (Firebase Cloud Messaging) — iOS/Android 통합 |
| **저장** | PostgreSQL (별도 서버 DB) |
| **알림 유형** | 7종 (확장 가능 모델) |
| **알림 설정** | 유형별 ON/OFF + 산책 리마인더 시간 설정 |
| **빈도 제한** | 앱 스토어 필수 아님, 유저 설정으로 대체 |
| **그룹핑** | 시간별 (오늘 / 어제 / 이번 주 / 이전) |

---

## 1. 알림 유형

### 1.1 확장 가능 모델

알림 유형을 **코드 기반**으로 관리하여, 새로운 유형 추가 시 DB 스키마 변경 없이 확장 가능.

| type | 설명 | 예시 | 아이콘 |
|------|------|------|--------|
| `badge` | 뱃지 획득/진행 | "50km 마라토너 뱃지까지 12km 남았어요!" | award |
| `ranking` | 랭킹 변동 | "동네 랭킹 2위로 올라갔어요!" | trophy |
| `social` | 친구 요청/수락 | "초코아빠님이 친구 요청을 보냈어요" | users |
| `challenge` | 챌린지 초대/달성 | "주간 30km 도전 챌린지에 초대했어요" | swords |
| `reminder` | 산책 리마인더 | "산책 시간이에요! 초코가 기다리고 있어요" | paw-print |
| `season` | 시즌 이벤트 | "겨울왕국 시즌 뱃지 이벤트가 진행 중" | sparkles |
| `system` | 시스템 공지 | "멍이랑 v1.2 업데이트 안내" | megaphone |

### 1.2 향후 추가 가능한 유형

| type | 설명 |
|------|------|
| `weather` | 날씨 경고 (미세먼지 나쁨 등) |
| `premium` | 구독 관련 (만료 예정, 갱신 등) |
| `achievement` | 등급 승급 |

> 새로운 유형 추가: `notification_type` 필드에 문자열 추가만으로 대응
> DB 마이그레이션 불필요 → **확장성 확보**

---

## 2. 푸시 알림 (FCM)

### 2.1 아키텍처

```
[서버에서 알림 발생]
  → notifications 테이블에 저장 (DB)
  → FCM 전송 (푸시)
  → 유저 기기에 표시

[유저 기기]
  → FCM 토큰 발급 (앱 시작 시)
  → POST /push-tokens으로 서버에 등록
  → 토큰 갱신 시 자동 업데이트
```

### 2.2 FCM 토큰 관리

| 상황 | 처리 |
|------|------|
| 앱 최초 실행 | FCM 토큰 발급 → 서버 등록 |
| 토큰 갱신 | 앱에서 감지 → 서버 업데이트 |
| 로그아웃 | 토큰 비활성화 (삭제 X, 재로그인 대비) |
| 여러 기기 | 유저 1명 = 여러 토큰 가능 (핸드폰 + 태블릿) |
| 전송 실패 | FCM 응답에서 invalid 토큰 → 자동 삭제 |

### 2.3 FCM 전송 코드

```python
import firebase_admin
from firebase_admin import credentials, messaging

# 초기화 (앱 시작 시 1회)
cred = credentials.Certificate("firebase-service-account.json")
firebase_admin.initialize_app(cred)

async def send_push(user_id: int, title: str, body: str, data: dict = None):
    """유저의 모든 활성 기기에 푸시 전송"""
    tokens = await get_active_tokens(user_id)
    if not tokens:
        return

    message = messaging.MulticastMessage(
        tokens=tokens,
        notification=messaging.Notification(title=title, body=body),
        data=data or {},
        apns=messaging.APNSConfig(
            payload=messaging.APNSPayload(
                aps=messaging.Aps(badge=1, sound="default")
            )
        ),
    )

    response = messaging.send_each_for_multicast(message)

    # 실패한 토큰 정리
    for i, send_response in enumerate(response.responses):
        if send_response.exception and _is_token_invalid(send_response.exception):
            await deactivate_token(tokens[i])
```

---

## 3. 알림 설정

### 3.1 유저별 설정 (설정.html 기준)

프로토타입의 알림 설정 항목:

| 설정 | 키 | 기본값 | 설명 |
|------|---|--------|------|
| 산책 리마인더 | `reminder_enabled` | true | ON/OFF |
| 리마인더 시간 | `reminder_time` | "16:00" | 목표 산책 시간 (HH:MM) |
| 리마인더 알림 | `reminder_before` | 30 | 몇 분 전 알림 (선택형) |
| 뱃지 획득 알림 | `badge_enabled` | true | ON/OFF |
| 소셜 알림 | `social_enabled` | true | ON/OFF |
| 챌린지 알림 | `challenge_enabled` | true | ON/OFF |
| 랭킹 알림 | `ranking_enabled` | true | ON/OFF |
| 시스템 알림 | `system_enabled` | true | ON/OFF (끌 수 없음) |

### 3.2 산책 리마인더 시간 설정

```
[산책 목표 시간] 오후 4:00  ← 타임피커 (기존 프로토타입)

[리마인더 알림] 30분 전     ← select 옵션
  ┌──────────────┐
  │ 1시간 전     │
  │ 30분 전  ✓   │
  │ 10분 전      │
  │ 5분 전       │
  └──────────────┘

→ 결과: 오후 3:30에 "산책 시간이에요! 초코가 기다리고 있어요" 푸시
```

| reminder_before 값 | 설명 |
|---------------------|------|
| 60 | 1시간 전 |
| 30 | 30분 전 (기본값) |
| 10 | 10분 전 |
| 5 | 5분 전 |

### 3.3 설정 저장 방식

users 테이블의 `notification_settings` JSONB 필드에 저장 (이미 존재):

```json
{
  "reminder_enabled": true,
  "reminder_time": "16:00",
  "reminder_before": 30,
  "badge_enabled": true,
  "social_enabled": true,
  "challenge_enabled": true,
  "ranking_enabled": true,
  "system_enabled": true
}
```

> `PATCH /users/me` 로 업데이트 (기존 API 활용)

---

## 4. 알림 발송 조건

### 4.1 알림 발송 판별

```python
async def should_send_notification(user_id: int, notif_type: str) -> bool:
    """유저 설정에 따라 알림 발송 여부 판별"""
    settings = await get_notification_settings(user_id)

    type_map = {
        'badge': 'badge_enabled',
        'ranking': 'ranking_enabled',
        'social': 'social_enabled',
        'challenge': 'challenge_enabled',
        'reminder': 'reminder_enabled',
        'season': 'badge_enabled',       # 시즌은 뱃지 설정에 종속
        'system': None,                  # 시스템은 항상 발송
    }

    setting_key = type_map.get(notif_type)
    if setting_key is None:
        return True  # system 등 끌 수 없는 유형

    return settings.get(setting_key, True)
```

### 4.2 알림 트리거 시점

| 유형 | 트리거 | 내부 호출 위치 |
|------|--------|--------------|
| badge | 뱃지 획득/진행률 변화 시 | badge_service.py |
| ranking | 랭킹 갱신 시 순위 변동 | ranking_scheduler.py |
| social | 친구 요청/수락 시 | friend_service.py |
| challenge | 챌린지 초대/달성 시 | challenge_service.py |
| reminder | 스케줄러 (유저별 설정 시간) | reminder_scheduler.py |
| season | 관리자가 이벤트 시작 시 | admin API |
| system | 관리자가 공지 작성 시 | admin API |

---

## 5. 산책 리마인더 스케줄러

### 5.1 동작 방식

```python
@scheduler.scheduled_job('cron', minute='*/5', timezone='Asia/Seoul')
async def check_reminders():
    """5분마다 리마인더 대상 유저 체크"""
    now = datetime.now(KST)
    current_time = now.strftime('%H:%M')

    # reminder_time - reminder_before = 현재 시간인 유저 검색
    # 예: reminder_time=16:00, reminder_before=30 → 15:30에 발송

    users = await db.execute(
        select(User).where(
            User.notification_settings['reminder_enabled'].as_boolean() == True,
            # 시간 계산은 DB 레벨에서 처리
        )
    )

    for user in users.scalars():
        settings = user.notification_settings
        target_time = parse_time(settings['reminder_time'])
        before_min = settings.get('reminder_before', 30)
        fire_time = target_time - timedelta(minutes=before_min)

        if fire_time.strftime('%H:%M') == current_time:
            pet_name = await get_primary_pet_name(user.id)
            await create_and_send_notification(
                user_id=user.id,
                type='reminder',
                title='산책 시간이에요!',
                body=f'{pet_name}가 기다리고 있어요 🐾',
            )
```

### 5.2 중복 방지

```python
# 같은 날 같은 유저에게 리마인더 1회만
REMINDER_SENT_KEY = "reminder:sent:{user_id}:{date}"
# Redis에 당일 발송 여부 저장, TTL 24시간
```

---

## 6. API 목록

| Method | Path | 설명 |
|--------|------|------|
| GET | `/notifications` | 알림 목록 (페이징, 그룹핑) |
| GET | `/notifications/unread-count` | 읽지 않은 알림 수 |
| PATCH | `/notifications/{id}/read` | 단일 읽음 처리 |
| PATCH | `/notifications/read-all` | 모두 읽음 처리 |
| POST | `/push-tokens` | FCM 토큰 등록/갱신 |
| DELETE | `/push-tokens/{token}` | 토큰 삭제 (로그아웃 시) |

### 6.1 알림 목록 — `GET /notifications`

**요청**
```
GET /notifications?page=1&size=20
```

**응답**
```json
{
  "unread_count": 4,
  "groups": [
    {
      "label": "오늘",
      "notifications": [
        {
          "id": 101,
          "type": "badge",
          "title": null,
          "body": "50km 마라토너 뱃지까지 12km 남았어요!",
          "is_read": false,
          "action_type": "navigate",
          "action_target": "/badges",
          "extra_data": { "badge_id": "D05" },
          "created_at": "2026-03-04T10:30:00+09:00"
        },
        {
          "id": 102,
          "type": "challenge",
          "title": null,
          "body": "초코#1234님이 '주간 30km 도전' 챌린지에 초대했어요",
          "is_read": false,
          "action_type": "challenge_invite",
          "action_target": "/challenges/invitations/15",
          "extra_data": {
            "challenge_id": 42,
            "invitation_id": 15
          },
          "created_at": "2026-03-04T09:15:00+09:00"
        }
      ]
    },
    {
      "label": "어제",
      "notifications": [...]
    }
  ],
  "page": 1,
  "total_pages": 3
}
```

### 6.2 그룹핑 규칙

| 라벨 | 기준 |
|------|------|
| 오늘 | 오늘 날짜 |
| 어제 | 어제 날짜 |
| 이번 주 | 이번 주 (오늘/어제 제외) |
| 이전 | 이번 주 이전 |

---

## 7. DB 테이블

### notifications

| 필드 | 타입 | 설명 |
|------|------|------|
| id | BigInteger PK | |
| user_id | BigInteger FK | 수신자 |
| type | String(20) | `badge`, `ranking`, `social`, `challenge`, `reminder`, `season`, `system` |
| title | String(100) | 푸시 제목 (nullable) |
| body | String(500) | 알림 내용 |
| is_read | Boolean | 읽음 여부 (기본 false) |
| action_type | String(20) | `navigate`, `challenge_invite`, `friend_request`, `none` |
| action_target | String(200) | 클릭 시 이동 경로 |
| extra_data | JSONB | 추가 데이터 (badge_id, challenge_id 등) |
| created_at | DateTime | |

> 인덱스: (user_id, is_read, created_at DESC) — 읽지 않은 알림 빠른 조회
> 인덱스: (user_id, created_at DESC) — 알림 목록 페이징

### push_tokens

| 필드 | 타입 | 설명 |
|------|------|------|
| id | Integer PK | |
| user_id | BigInteger FK | |
| token | String(500) | FCM 토큰 |
| device_type | String(10) | `ios`, `android` |
| is_active | Boolean | 활성 여부 |
| created_at | DateTime | |
| updated_at | DateTime | |

> UNIQUE(token)
> 인덱스: (user_id, is_active) — 유저별 활성 토큰 조회

---

## 8. 알림 생성 헬퍼

```python
async def create_and_send_notification(
    user_id: int,
    type: str,
    body: str,
    title: str = None,
    action_type: str = 'navigate',
    action_target: str = None,
    extra_data: dict = None,
):
    """알림 저장 + 푸시 전송 통합 함수"""

    # 1. 유저 설정 확인
    if not await should_send_notification(user_id, type):
        return None

    # 2. DB 저장
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        body=body,
        action_type=action_type,
        action_target=action_target,
        extra_data=extra_data or {},
    )
    db.add(notification)
    await db.commit()

    # 3. 푸시 전송 (비동기)
    await send_push(
        user_id=user_id,
        title=title or '멍이랑',
        body=body,
        data={
            'notification_id': str(notification.id),
            'type': type,
            'action_target': action_target or '',
        }
    )

    return notification
```

### 8.1 각 서비스에서 호출 예시

```python
# badge_service.py — 뱃지 획득 시
await create_and_send_notification(
    user_id=user.id,
    type='badge',
    body=f"축하해요! '{badge.name}' 뱃지를 획득했어요!",
    action_type='navigate',
    action_target='/badges',
    extra_data={'badge_id': badge.code},
)

# friend_service.py — 친구 요청 시
await create_and_send_notification(
    user_id=target_user_id,
    type='social',
    body=f"{requester.nickname}#{requester.tag_code}님이 친구 요청을 보냈어요",
    action_type='friend_request',
    action_target='/friends/requests',
    extra_data={'from_user_id': requester.id, 'request_id': request.id},
)

# challenge_service.py — 챌린지 초대 시
await create_and_send_notification(
    user_id=invited_user_id,
    type='challenge',
    body=f"{inviter.nickname}님이 '{challenge.title}' 챌린지에 초대했어요",
    action_type='challenge_invite',
    action_target=f'/challenges/invitations/{invitation.id}',
    extra_data={'challenge_id': challenge.id, 'invitation_id': invitation.id},
)
```

---

## 9. 알림 보관/삭제 정책

| 항목 | 정책 |
|------|------|
| 보관 기간 | 90일 |
| 자동 삭제 | 스케줄러: 매일 02:00에 90일 지난 알림 삭제 |
| 수동 삭제 | 유저별 삭제 기능 없음 (읽음 처리만) |

```python
@scheduler.scheduled_job('cron', hour=2, minute=0, timezone='Asia/Seoul')
async def cleanup_old_notifications():
    """90일 지난 알림 삭제"""
    cutoff = datetime.now(KST) - timedelta(days=90)
    await db.execute(
        delete(Notification).where(Notification.created_at < cutoff)
    )
    await db.commit()
```

---

## 10. 앱 스토어 준수 사항

| 요건 | 대응 | 상태 |
|------|------|------|
| 유저 동의 (opt-in) | 프론트에서 OS 권한 요청 | 프론트 담당 |
| 알림 없이도 앱 동작 | 알림 거부해도 기능 제한 없음 | 설계 반영 |
| 유형별 ON/OFF | notification_settings JSONB | 설계 반영 |
| 광고/마케팅 알림 금지 | 알림에 광고 포함하지 않음 | 정책 |
| 민감 정보 미포함 | body에 개인정보 노출 안 함 | 정책 |

> 빈도 제한: 앱 스토어 필수 아님. 유저가 유형별로 끌 수 있으므로 충분.

---

## 11. 서비스 모듈 구조

```
server/app/
├── services/
│   └── notification_service.py  # 알림 생성/전송/조회
├── routers/
│   └── notifications.py         # 알림 API + 토큰 API
├── models/
│   ├── notification.py          # Notification
│   └── push_token.py            # PushToken
├── schemas/
│   └── notification.py          # 요청/응답 스키마
└── tasks/
    ├── reminder_scheduler.py    # 산책 리마인더 (5분마다)
    └── notification_cleanup.py  # 90일 지난 알림 삭제
```

---

## 12. 환경변수

| 변수 | 용도 | 비고 |
|------|------|------|
| `FIREBASE_CREDENTIALS_PATH` | Firebase 서비스 계정 JSON 경로 | 신규 |
| `REDIS_URL` | 리마인더 중복 방지 캐시 | 기존 |

---

## 13. 구현 우선순위

| 순서 | 항목 | 난이도 |
|------|------|--------|
| 1 | notifications + push_tokens 모델 | 쉬움 |
| 2 | 알림 목록/읽음 처리 API | 쉬움 |
| 3 | FCM 토큰 등록/관리 API | 쉬움 |
| 4 | notification_service.py (생성+전송 통합) | 중간 |
| 5 | 기존 서비스에 알림 호출 연동 (badge, friend, challenge) | 중간 |
| 6 | 산책 리마인더 스케줄러 | 중간 |
| 7 | 알림 정리 스케줄러 (90일) | 쉬움 |

---

*작성일: 2026-03-04*
*기준: 프로토타입 알림.html/설정.html + FCM + PostgreSQL*
*앱 스토어 빈도 제한: 필수 아님 (유형별 ON/OFF로 대응)*
