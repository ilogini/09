# 실시간 기능 - 멍이랑 (withbowwow)

> 코어 파일: [00_overview.md](./00_overview.md)

---

## 1. Supabase Realtime 개요

Supabase Realtime은 PostgreSQL의 WAL(Write-Ahead Logging)을 기반으로 테이블 변경 사항을 WebSocket으로 클라이언트에 실시간 브로드캐스트한다.

### 1.1 사용할 기능

| 기능 | 용도 |
|------|------|
| **Postgres Changes** | 테이블 INSERT/UPDATE/DELETE 감지 |
| **Broadcast** | 커스텀 이벤트 발행 (산책 중 위치 공유) |
| **Presence** | 온라인 상태 추적 (향후) |

---

## 2. 실시간 구독 목록

### 2.1 소셜 피드 (산책 기록 실시간 업데이트)

```typescript
// 팔로잉 중인 사용자의 새 산책 기록 감지
const feedSubscription = supabase
  .channel('walk-feed')
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'walks',
      filter: `shared_to_feed=eq.true`,
    },
    (payload) => {
      // 팔로잉 중인 사용자인지 클라이언트에서 필터
      if (followingIds.includes(payload.new.user_id)) {
        addToFeed(payload.new);
      }
    }
  )
  .subscribe();
```

### 2.2 좋아요/댓글 실시간 카운트

```typescript
// 특정 산책 기록의 좋아요/댓글 실시간 업데이트
const interactionSubscription = supabase
  .channel(`walk-${walkId}`)
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'likes',
      filter: `walk_id=eq.${walkId}`,
    },
    (payload) => {
      incrementLikeCount();
    }
  )
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'comments',
      filter: `walk_id=eq.${walkId}`,
    },
    (payload) => {
      addComment(payload.new);
    }
  )
  .subscribe();
```

### 2.3 산책 초대 수신

```typescript
// 새 산책 초대 실시간 감지
const invitationSubscription = supabase
  .channel('invitations')
  .on(
    'postgres_changes',
    {
      event: 'INSERT',
      schema: 'public',
      table: 'invitations',
      filter: `invitee_id=eq.${currentUserId}`,
    },
    (payload) => {
      showInvitationNotification(payload.new);
    }
  )
  .subscribe();
```

### 2.4 랭킹 변동 실시간

```typescript
// 내 랭킹 변동 감지
const rankingSubscription = supabase
  .channel('my-ranking')
  .on(
    'postgres_changes',
    {
      event: 'UPDATE',
      schema: 'public',
      table: 'rankings',
      filter: `user_id=eq.${currentUserId}`,
    },
    (payload) => {
      updateMyRank(payload.new.rank, payload.old.rank);
    }
  )
  .subscribe();
```

### 2.5 함께 산책 위치 공유 (Broadcast)

```typescript
// 함께 산책 시 실시간 위치 공유 (Broadcast 채널)
const walkTogetherChannel = supabase
  .channel(`walk-together-${invitationId}`)
  .on('broadcast', { event: 'location' }, (payload) => {
    updatePartnerLocation(payload.payload);
  })
  .subscribe();

// 내 위치 브로드캐스트 (5초 간격)
function broadcastMyLocation(lat: number, lng: number) {
  walkTogetherChannel.send({
    type: 'broadcast',
    event: 'location',
    payload: { lat, lng, timestamp: Date.now() },
  });
}
```

---

## 3. 구독 관리 전략

### 3.1 구독 생명주기

```
앱 포그라운드 진입 → 필요한 채널 구독
앱 백그라운드 전환 → 산책 중이 아니면 구독 해제
앱 종료 → 모든 구독 해제
산책 중 → 백그라운드에서도 위치 공유 채널 유지
```

### 3.2 화면별 구독

| 화면 | 구독 채널 | 해제 시점 |
|------|----------|----------|
| 홈 | 랭킹 변동, 뱃지 진행률 | 다른 탭 이동 시 |
| 소셜 | 피드 신규, 좋아요/댓글, 초대 | 다른 탭 이동 시 |
| 산책 중 | 함께 산책 위치 (해당 시) | 산책 종료 시 |
| 랭킹 | 랭킹 변동 | 다른 탭 이동 시 |
| 마이페이지 | 뱃지 상태 변경 | 다른 탭 이동 시 |

### 3.3 네트워크 재연결

```typescript
// 네트워크 끊김 후 재연결 시 자동 복구
supabase.realtime.setAuth(session.access_token);

// 재연결 이벤트 처리
channel.on('system', { event: 'reconnect' }, () => {
  // 끊겼던 동안의 데이터 동기화
  syncMissedData();
});
```

---

## 4. 성능 고려사항

| 항목 | 값 | 설명 |
|------|-----|------|
| 동시 연결 수 (Free) | 200 | Supabase Free tier 제한 |
| 동시 연결 수 (Pro) | 500 | Pro tier |
| 메시지 크기 제한 | 1MB | Supabase Realtime 제한 |
| 위치 공유 간격 | 5초 | 배터리 + 네트워크 절약 |
| 피드 구독 필터 | 서버 사이드 | 클라이언트 부하 최소화 |

---

*작성일: 2026-02-12*
*버전: 1.0*
