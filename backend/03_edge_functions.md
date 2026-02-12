# Edge Functions (비즈니스 로직) - 멍이랑 (withbowwow)

> 코어 파일: [00_overview.md](./00_overview.md)
> 스키마: [01_database_schema.md](./01_database_schema.md)
> 런타임: Supabase Edge Functions (Deno / TypeScript)

---

## 1. 함수 목록 및 트리거

| 함수명 | 트리거 | 실행 빈도 | 우선순위 |
|--------|--------|----------|---------|
| `on-walk-complete` | 산책 완료 (walks INSERT) | 매 산책 완료 | MVP |
| `validate-walk` | 산책 저장 전 | 매 산책 완료 | MVP |
| `check-badge-progress` | `on-walk-complete` 내부 | 매 산책 완료 | Phase 2 |
| `calculate-rankings` | Cron (1시간마다) | 24회/일 | Phase 2 |
| `recommend-friends` | Cron (12시간마다) | 2회/일 | Phase 3 |
| `send-push` | 이벤트 기반 | 이벤트 발생 시 | Phase 2 |
| `weather-cache` | Cron (1시간마다) | 24회/일 | Phase 4 |
| `process-payment` | Webhook (Toss/IAP) | 결제 발생 시 | Phase 4 |

---

## 2. validate-walk (산책 유효성 검증)

### 2.1 검증 규칙

```typescript
// supabase/functions/validate-walk/index.ts

interface WalkValidation {
  isValid: boolean;
  invalidReasons: string[];
}

function validateWalk(walkData: WalkInput): WalkValidation {
  const reasons: string[] = [];

  // 1. 최소 거리: 500m 미만은 기록 불가
  if (walkData.distance_m < 500) {
    reasons.push('minimum_distance');
  }

  // 2. 최대 시간: 12시간 이상은 비정상
  if (walkData.duration_sec > 43200) {
    reasons.push('max_duration_exceeded');
  }

  // 3. 평균 속도: 시속 15km 이상이면 차량 탑승 의심
  const avgSpeedKmh = (walkData.distance_m / 1000) / (walkData.duration_sec / 3600);
  if (avgSpeedKmh > 15) {
    reasons.push('speed_too_high');
  }

  // 4. GPS 좌표 검증: 연속 좌표 간 비현실적 이동 필터
  if (walkData.route_geojson) {
    const coords = walkData.route_geojson.coordinates;
    for (let i = 1; i < coords.length; i++) {
      const dist = haversineDistance(coords[i - 1], coords[i]);
      const timeDiff = coords[i][2] - coords[i - 1][2]; // timestamp
      const speed = dist / timeDiff * 3600; // km/h
      if (speed > 15) {
        // 해당 구간 제외 (전체 무효화 아님)
        coords.splice(i, 1);
        i--;
      }
    }
  }

  // 5. GPS 스푸핑 감지: 좌표가 정확히 일직선이면 의심
  // (구현 상세: 좌표 분산이 비정상적으로 낮으면 flag)

  return {
    isValid: reasons.length === 0,
    invalidReasons: reasons,
  };
}
```

---

## 3. on-walk-complete (산책 완료 처리)

### 3.1 실행 흐름

```
산책 완료 (walks INSERT)
  │
  ├── 1. validate-walk 호출 → 유효성 검증
  │
  ├── 2. check-badge-progress 호출
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
  │     └── 해당 사용자의 주간/월간/전체 랭킹 갱신
  │
  ├── 5. 푸시 알림 전송 (조건부)
  │     ├── 뱃지 획득 시: "새 뱃지를 획득했어요!"
  │     ├── 뱃지 임박 시: "5km 뱃지까지 0.3km!"
  │     └── 랭킹 변동 시: "동네 랭킹 7위로 올라갔어요"
  │
  └── 6. 소셜 피드 업데이트 (shared_to_feed = true인 경우)
```

### 3.2 코드 구조

```typescript
// supabase/functions/on-walk-complete/index.ts
import { serve } from 'https://deno.land/std@0.177.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

serve(async (req) => {
  const { walk_id } = await req.json();

  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  );

  // 1. 산책 데이터 조회
  const { data: walk } = await supabase
    .from('walks')
    .select('*, users!inner(*)')
    .eq('id', walk_id)
    .single();

  // 2. 유효성 검증
  const validation = validateWalk(walk);
  if (!validation.isValid) {
    await supabase.from('walks').update({ is_valid: false }).eq('id', walk_id);
    return new Response(JSON.stringify({ valid: false }));
  }

  // 3. 뱃지 진행률 업데이트
  const badgeUpdates = await checkBadgeProgress(supabase, walk);

  // 4. 랭킹 업데이트
  await updateRankings(supabase, walk.user_id);

  // 5. 푸시 알림
  for (const badge of badgeUpdates.newlyEarned) {
    await sendPush(supabase, walk.user_id, {
      type: 'badge_earned',
      title: '새 뱃지를 획득했어요!',
      body: `${badge.name} 뱃지를 달성했어요!`,
    });
  }

  return new Response(JSON.stringify({ success: true, badgeUpdates }));
});
```

---

## 4. check-badge-progress (뱃지 진행률)

### 4.1 카테고리별 계산 로직

```typescript
async function checkBadgeProgress(supabase: any, walk: Walk) {
  const userId = walk.user_id;
  const results = { updated: [], newlyEarned: [] };

  // 모든 뱃지 정의 조회
  const { data: badges } = await supabase
    .from('badge_definitions')
    .select('*')
    .eq('is_active', true);

  for (const badge of badges) {
    let progress = 0;

    switch (badge.condition_type) {
      // ── 거리 뱃지 ──
      case 'cumulative_distance': {
        const { data } = await supabase.rpc('sum_user_distance', { p_user_id: userId });
        progress = data / badge.condition_value * 100;
        break;
      }

      // ── 연속 뱃지 ──
      case 'consecutive_days': {
        const { data } = await supabase.rpc('calculate_streak_days', { p_user_id: userId });
        progress = data / badge.condition_value * 100;
        break;
      }

      // ── 탐험 뱃지 ──
      case 'unique_places': {
        // 시작 지점을 500m 반경 클러스터링하여 고유 장소 수 계산
        const { data } = await supabase.rpc('count_unique_places', { p_user_id: userId });
        progress = data / badge.condition_value * 100;
        break;
      }

      // ── 시간 뱃지 ──
      case 'cumulative_time': {
        const { data } = await supabase.rpc('sum_user_duration', { p_user_id: userId });
        progress = data / badge.condition_value * 100;
        break;
      }

      // ── 스페셜 뱃지 ──
      case 'special_early_bird': {
        const hour = new Date(walk.started_at).getHours();
        if (hour < 6) progress = 100;
        break;
      }
      case 'special_night_owl': {
        const hour = new Date(walk.started_at).getHours();
        if (hour >= 22) progress = 100;
        break;
      }
      case 'special_rain_walk': {
        if (walk.weather?.pty === 'rain') progress = 100;
        break;
      }
      case 'special_snow_walk': {
        if (walk.weather?.pty === 'snow') progress = 100;
        break;
      }
      case 'special_single_marathon': {
        if (walk.distance_m >= 10000) progress = 100;
        break;
      }
      case 'special_photographer': {
        const { count } = await supabase
          .from('walk_photos')
          .select('id', { count: 'exact' })
          .eq('walk_id', walk.id);
        // 누적 사진 수로 계산
        const { data: totalPhotos } = await supabase.rpc('count_user_photos', { p_user_id: userId });
        progress = totalPhotos / badge.condition_value * 100;
        break;
      }

      // ── 시즌 뱃지 ──
      case 'season_spring':
      case 'season_summer':
      case 'season_autumn':
      case 'season_winter': {
        const now = new Date();
        if (badge.season_start && badge.season_end) {
          const start = new Date(badge.season_start);
          const end = new Date(badge.season_end);
          if (now >= start && now <= end) {
            // 시즌 내 조건 체크 (장소/날씨)
            progress = await calculateSeasonProgress(supabase, userId, badge);
          }
        }
        break;
      }
    }

    // 진행률 캡 (0~100)
    progress = Math.min(Math.max(progress, 0), 100);

    // user_badges 업데이트
    const newStatus = progress >= 100 ? 'earned' : progress > 0 ? 'in_progress' : 'locked';
    const { data: existing } = await supabase
      .from('user_badges')
      .select('*')
      .eq('user_id', userId)
      .eq('badge_id', badge.id)
      .single();

    if (existing) {
      if (existing.status !== 'earned') {
        await supabase.from('user_badges').update({
          status: newStatus,
          progress_value: progress * badge.condition_value / 100,
          progress_percent: progress,
          earned_at: newStatus === 'earned' ? new Date().toISOString() : null,
          earned_walk_id: newStatus === 'earned' ? walk.id : null,
          updated_at: new Date().toISOString(),
        }).eq('id', existing.id);

        if (newStatus === 'earned' && existing.status !== 'earned') {
          results.newlyEarned.push(badge);
        }
      }
    } else if (progress > 0) {
      await supabase.from('user_badges').insert({
        user_id: userId,
        badge_id: badge.id,
        status: newStatus,
        progress_value: progress * badge.condition_value / 100,
        progress_percent: progress,
        earned_at: newStatus === 'earned' ? new Date().toISOString() : null,
        earned_walk_id: newStatus === 'earned' ? walk.id : null,
        pet_id: walk.pet_id,
      });

      if (newStatus === 'earned') {
        results.newlyEarned.push(badge);
      }
    }
  }

  return results;
}
```

### 4.2 연속 뱃지 특수 로직

```
하루 기준: 오전 4시 ~ 다음날 오전 4시 (새벽 산책 고려)
최소 거리: 500m 이상이어야 "산책한 날"로 인정
연속 끊김: 진행률 리셋 (0부터 재시작)
프리미엄 면제: 월 1회 "휴식일" 사용 가능 (연속 기록 유지)
```

### 4.3 탐험 뱃지 장소 계산

```sql
-- 고유 장소 수 계산 (시작 지점 기준, 500m 반경 클러스터링)
CREATE OR REPLACE FUNCTION count_unique_places(p_user_id UUID)
RETURNS INTEGER AS $$
  SELECT COUNT(DISTINCT cluster_id)
  FROM (
    SELECT
      ST_ClusterDBSCAN(start_point, eps := 500, minpoints := 1) OVER () AS cluster_id
    FROM walks
    WHERE user_id = p_user_id
      AND is_valid = TRUE
      AND start_point IS NOT NULL
  ) clusters;
$$ LANGUAGE sql;
```

---

## 5. calculate-rankings (랭킹 집계)

### 5.1 Cron 설정

```sql
-- Supabase pg_cron 확장 (또는 Edge Function Cron)
SELECT cron.schedule(
  'refresh-rankings',
  '0 * * * *',  -- 매시간 정각
  $$SELECT refresh_weekly_rankings(to_char(CURRENT_DATE, 'YYYY-"W"IW'))$$
);
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

## 6. recommend-friends (친구 추천)

### 6.1 추천 알고리즘

```typescript
async function recommendFriends(userId: string) {
  // 가중치 기반 점수 계산
  const candidates = await supabase.rpc('get_friend_candidates', {
    p_user_id: userId,
    p_limit: 20,
  });

  return candidates.map(c => ({
    ...c,
    score:
      c.distance_score * 0.40 +    // 지리적 근접성 (40%)
      c.time_score * 0.25 +         // 산책 시간대 유사성 (25%)
      c.breed_score * 0.20 +        // 견종/크기 유사성 (20%)
      c.activity_score * 0.15,      // 활동량 유사성 (15%)
  })).sort((a, b) => b.score - a.score);
}
```

### 6.2 후보 쿼리

```sql
CREATE OR REPLACE FUNCTION get_friend_candidates(p_user_id UUID, p_limit INTEGER)
RETURNS TABLE(...) AS $$
  SELECT
    u.id,
    u.nickname,
    p.name AS pet_name,
    p.breed,
    p.size,
    p.photo_url,
    -- 지리적 근접성 (같은 구/동)
    CASE
      WHEN u.region_dong = me.region_dong THEN 1.0
      WHEN u.region_sigungu = me.region_sigungu THEN 0.6
      ELSE 0.0
    END AS distance_score,
    -- 산책 시간대 유사성
    -- (최근 7일 산책 시작 시간 평균 비교)
    1.0 - ABS(avg_walk_hour(u.id) - avg_walk_hour(p_user_id)) / 12.0 AS time_score,
    -- 견종 크기 유사성
    CASE WHEN p.size = my_pet.size THEN 1.0 ELSE 0.3 END AS breed_score,
    -- 활동량 유사성
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

```typescript
// 피드 정렬 점수 계산
function calculateFeedScore(walk: Walk, viewer: User) {
  const ageHours = (Date.now() - new Date(walk.created_at).getTime()) / 3600000;

  return (
    // 시간 최신순 (40%) - 시간이 지날수록 감소
    (1 / (1 + ageHours / 24)) * 0.40 +
    // 친밀도 (30%) - 최근 인터랙션 빈도
    getIntimacyScore(viewer.id, walk.user_id) * 0.30 +
    // 지역 근접성 (20%) - 같은 동네 우선
    getRegionScore(viewer, walk) * 0.20 +
    // 인게이지먼트 (10%) - 좋아요/댓글 수
    Math.min(walk.likeCount + walk.commentCount, 50) / 50 * 0.10
  );
}
```

---

*작성일: 2026-02-12*
*버전: 1.0*
