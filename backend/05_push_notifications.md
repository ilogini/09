# 푸시 알림 - 멍이랑 (withbowwow)

> 코어 파일: [00_overview.md](./00_overview.md)

---

## 1. 인프라

| 플랫폼 | 서비스 | SDK |
|--------|--------|-----|
| Android | Firebase Cloud Messaging (FCM) | expo-notifications |
| iOS | APNs (via FCM) | expo-notifications |

### 1.1 토큰 등록 플로우

```
앱 시작 → expo-notifications 권한 요청
  → FCM 토큰 발급 (Android) / APNs 토큰 발급 (iOS)
  → push_tokens 테이블에 저장/업데이트
  → 로그아웃 시 is_active = FALSE
```

---

## 2. 알림 유형 (7가지)

### 2.1 뱃지 획득

| 항목 | 값 |
|------|-----|
| 트리거 | user_badges.status → 'earned' |
| 제목 | "새 뱃지를 획득했어요!" |
| 본문 | "{badge_name} 뱃지를 달성했어요!" |
| 딥링크 | withbowwow://badges/{badge_id} |
| 빈도 | 발생 시마다 (제한 없음) |

### 2.2 뱃지 달성 임박

| 항목 | 값 |
|------|-----|
| 트리거 | user_badges.progress_percent >= 80 |
| 제목 | "뱃지 달성이 눈앞이에요!" |
| 본문 | "{badge_name} 뱃지까지 {remaining}!" |
| 딥링크 | withbowwow://badges/{badge_id} |
| 빈도 | 뱃지당 1회 (80% 도달 시) |

### 2.3 랭킹 변동

| 항목 | 값 |
|------|-----|
| 트리거 | 랭킹 재계산 후 변동 감지 |
| 제목 (상승) | "축하해요!" |
| 본문 (상승) | "동네 랭킹 {rank}위로 올라갔어요!" |
| 제목 (하락) | "앗!" |
| 본문 (하락) | "{nickname}님이 당신을 추월했어요. 산책 나가볼까요?" |
| 딥링크 | withbowwow://ranking |
| 빈도 | 하락 알림은 1일 1회 제한 |

### 2.4 산책 리마인더

| 항목 | 값 |
|------|-----|
| 트리거 | 사용자 설정 시간 (기본 18:00) |
| 제목 | "산책 시간이에요!" |
| 본문 | "{pet_name}(이)가 산책을 기다리고 있어요" |
| 딥링크 | withbowwow://walk/start |
| 빈도 | 1일 1회 (로컬 알림) |
| 구현 | expo-notifications 로컬 스케줄링 |

### 2.5 소셜 알림

| 이벤트 | 제목 | 본문 |
|--------|------|------|
| 팔로우 | "새 팔로워!" | "{nickname}님이 팔로우했어요" |
| 좋아요 | "좋아요!" | "{nickname}님이 산책 기록을 좋아해요" |
| 댓글 | "새 댓글!" | "{nickname}: {comment_preview}" |
| 산책 초대 | "산책 초대!" | "{nickname}님이 함께 산책하자고 해요" |

### 2.6 시스템 알림

| 이벤트 | 제목 | 본문 |
|--------|------|------|
| 주간 리셋 | "새 주 시작!" | "이번 주 동네 1위에 도전해보세요!" |
| 월간 결산 | "월간 리포트" | "지난달 {region} {rank}위! 이번 달 목표는?" |
| 앱 업데이트 | "업데이트 안내" | "새로운 기능이 추가되었어요" |

### 2.7 시즌 뱃지 마감 임박

| 항목 | 값 |
|------|-----|
| 트리거 | 시즌 뱃지 종료 7일/3일/1일 전 |
| 제목 | "시즌 뱃지 마감 임박!" |
| 본문 | "{badge_name} 뱃지 마감 {days}일 전! 지금 도전하세요" |
| 딥링크 | withbowwow://badges?category=season |
| 빈도 | 뱃지당 최대 3회 (7일/3일/1일) |

---

## 3. 빈도 제한 정책

| 규칙 | 값 |
|------|-----|
| 일일 최대 알림 | 10회 |
| 랭킹 하락 알림 | 1일 1회 |
| 소셜 알림 (좋아요) | 동일 walk에 대해 합산 ("외 N명이 좋아해요") |
| 야간 금지 시간 | 22:00 ~ 08:00 (시스템 알림만 지연 발송) |
| 비활성 사용자 | 7일 미접속 시 "돌아와요" 1회 → 14일 후 1회 → 이후 중단 |

---

## 4. send-push Edge Function

```typescript
// supabase/functions/send-push/index.ts
import * as admin from 'firebase-admin';

interface PushPayload {
  userId: string;
  type: string;
  title: string;
  body: string;
  data?: Record<string, string>;
}

async function sendPush(supabase: any, payload: PushPayload) {
  // 1. 알림 설정 확인
  const settings = await getUserNotificationSettings(supabase, payload.userId);
  if (!isNotificationEnabled(settings, payload.type)) return;

  // 2. 빈도 제한 확인
  if (await isRateLimited(supabase, payload.userId, payload.type)) return;

  // 3. 푸시 토큰 조회
  const { data: tokens } = await supabase
    .from('push_tokens')
    .select('token, platform')
    .eq('user_id', payload.userId)
    .eq('is_active', true);

  // 4. FCM 전송
  for (const t of tokens) {
    await admin.messaging().send({
      token: t.token,
      notification: {
        title: payload.title,
        body: payload.body,
      },
      data: payload.data,
      android: {
        priority: 'high',
        notification: { channelId: 'walk_notifications' },
      },
      apns: {
        payload: {
          aps: { sound: 'default', badge: 1 },
        },
      },
    });
  }

  // 5. notifications 테이블에 기록
  await supabase.from('notifications').insert({
    user_id: payload.userId,
    type: payload.type,
    title: payload.title,
    body: payload.body,
    data: payload.data,
  });
}
```

---

## 5. 알림 설정 (사용자 제어)

| 설정 항목 | 기본값 | notifications 테이블 type |
|----------|--------|-------------------------|
| 산책 리마인더 | ON | walk_reminder |
| 리마인더 시간 | 18:00 | (로컬 스케줄링) |
| 뱃지 달성 임박 | ON | badge_progress |
| 뱃지 획득 | ON | badge_earned |
| 랭킹 변동 | ON | ranking_change |
| 소셜 알림 | ON | social |
| 시즌 뱃지 마감 | ON | season_deadline |
| 시스템 알림 | ON | system |

설정 저장: `AsyncStorage` (로컬) + `users` 테이블 `notification_settings JSONB` (서버 백업)

---

*작성일: 2026-02-12*
*버전: 1.0*
