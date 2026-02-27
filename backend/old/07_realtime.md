# 실시간 기능 - 멍이랑 (withbowwow)

> 코어 파일: [00_overview.md](./00_overview.md)
> 구현: FastAPI WebSocket

---

## 1. 실시간 기능 개요

FastAPI의 내장 WebSocket 지원을 사용하여 실시간 기능을 구현한다.

### 1.1 실시간이 필요한 기능

| 기능 | 방식 | 설명 |
|------|------|------|
| **함께 산책 위치 공유** | WebSocket | 산책 중 상대방 위치 실시간 표시 |
| **소셜 피드 새 글** | Polling (30초) | 피드 새로고침 |
| **좋아요/댓글 카운트** | Polling (30초) | 피드 인터랙션 업데이트 |
| **산책 초대** | Push Notification | 초대 수신 알림 |
| **랭킹 변동** | Push Notification | 랭킹 변동 알림 |

> WebSocket은 "함께 산책 위치 공유"에만 사용. 나머지는 Push + Polling으로 충분.
> 사이드 프로젝트 단계에서 WebSocket 연결 수를 최소화하여 서버 부하를 줄인다.

---

## 2. 함께 산책 위치 공유 (WebSocket)

### 2.1 연결 플로우

```
산책 초대 수락 (invitations.status = 'accepted')
  → 양쪽 클라이언트가 WebSocket 연결
  → ws://api.withbowwow.com/ws/walk-together/{invitation_id}
  → JWT 토큰으로 인증
  → 5초 간격으로 위치 브로드캐스트
  → 산책 종료 시 연결 해제
```

### 2.2 WebSocket 핸들러

```python
# app/websocket/walk_together.py
from fastapi import WebSocket, WebSocketDisconnect
from jose import jwt, JWTError
import json


class WalkTogetherManager:
    """함께 산책 WebSocket 연결 관리"""

    def __init__(self):
        # invitation_id → {user_id: WebSocket}
        self.rooms: dict[str, dict[str, WebSocket]] = {}

    async def connect(self, invitation_id: str, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if invitation_id not in self.rooms:
            self.rooms[invitation_id] = {}
        self.rooms[invitation_id][user_id] = websocket

    def disconnect(self, invitation_id: str, user_id: str):
        if invitation_id in self.rooms:
            self.rooms[invitation_id].pop(user_id, None)
            if not self.rooms[invitation_id]:
                del self.rooms[invitation_id]

    async def broadcast_location(
        self, invitation_id: str, sender_id: str, data: dict
    ):
        """상대방에게 위치 브로드캐스트"""
        room = self.rooms.get(invitation_id, {})
        for user_id, ws in room.items():
            if user_id != sender_id:
                try:
                    await ws.send_json(data)
                except Exception:
                    pass


manager = WalkTogetherManager()
```

### 2.3 WebSocket 라우트

```python
# app/main.py 또는 app/routers/websocket.py
from app.websocket.walk_together import manager


@app.websocket("/ws/walk-together/{invitation_id}")
async def walk_together_ws(websocket: WebSocket, invitation_id: str):
    # 1. JWT 인증 (query param으로 전달)
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload["sub"]
    except JWTError:
        await websocket.close(code=4001, reason="Invalid token")
        return

    # 2. 초대 유효성 검증
    async with get_async_session() as db:
        invitation = await db.get(Invitation, invitation_id)
        if not invitation or invitation.status != "accepted":
            await websocket.close(code=4002, reason="Invalid invitation")
            return

        # 초대 참여자인지 확인
        if user_id not in [str(invitation.inviter_id), str(invitation.invitee_id)]:
            await websocket.close(code=4003, reason="Not a participant")
            return

    # 3. 연결
    await manager.connect(invitation_id, user_id, websocket)

    try:
        while True:
            # 클라이언트로부터 위치 데이터 수신
            data = await websocket.receive_json()

            # 위치 데이터 형식: {"lat": 37.5, "lng": 127.0, "timestamp": 1707750000}
            location_data = {
                "user_id": user_id,
                "lat": data["lat"],
                "lng": data["lng"],
                "timestamp": data.get("timestamp"),
            }

            # 상대방에게 브로드캐스트
            await manager.broadcast_location(invitation_id, user_id, location_data)

    except WebSocketDisconnect:
        manager.disconnect(invitation_id, user_id)
```

---

## 3. Polling 기반 실시간 (피드/랭킹)

### 3.1 피드 Polling

```
클라이언트 (소셜 탭 진입 시):
  → 30초마다 GET /feed?since={last_updated_at}
  → 새 글이 있으면 피드 상단에 "새 글 N개" 배너 표시
  → 사용자가 탭하면 피드 갱신
```

### 3.2 좋아요/댓글 Polling

```
특정 산책 기록 상세 화면:
  → 30초마다 GET /walks/{id}/interactions
  → 좋아요 수, 댓글 목록 갱신
```

### 3.3 Push 기반 실시간

나머지 실시간 기능은 Push Notification으로 처리:

| 이벤트 | 방식 |
|--------|------|
| 산책 초대 수신 | FCM Push → 앱 내 알림 화면 |
| 랭킹 변동 | FCM Push → 앱 내 알림 화면 |
| 뱃지 획득 | FCM Push → 앱 내 알림 화면 |
| 팔로우/좋아요/댓글 | FCM Push → 앱 내 알림 화면 |

---

## 4. 구독 관리 전략

### 4.1 WebSocket 생명주기

```
산책 초대 수락 → WebSocket 연결
산책 진행 중 → 5초 간격 위치 공유
산책 종료 → WebSocket 해제
앱 백그라운드 → WebSocket 유지 (산책 중일 때만)
앱 종료 → WebSocket 자동 해제
```

### 4.2 네트워크 재연결

```python
# 클라이언트 (React Native) 에서 처리
# expo-web-socket 또는 기본 WebSocket에 reconnect 로직 구현
# 서버는 상태 없이(stateless) 동작 → 재연결 시 새로 연결
```

---

## 5. 성능 고려사항

| 항목 | 값 | 설명 |
|------|-----|------|
| 동시 WebSocket 수 | ~50 | Render Free tier 기준 (메모리 512MB) |
| 위치 공유 간격 | 5초 | 배터리 + 네트워크 절약 |
| Polling 간격 | 30초 | 피드/랭킹 (서버 부하 최소화) |
| WebSocket 사용 범위 | 함께 산책만 | 전체 앱에 WebSocket 남용 방지 |

> 사용자 규모가 커지면 Redis Pub/Sub 또는 별도 WebSocket 서버로 분리 고려

---

*작성일: 2026-02-12*
*버전: 2.0 — FastAPI WebSocket으로 전환*
