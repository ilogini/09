# 데이터베이스 스키마 - 멍이랑 (withbowwow)

> 코어 파일: [00_overview.md](./00_overview.md)
> PostgreSQL 15+ / PostGIS 확장 / Supabase 관리형

---

## 1. ER 다이어그램 (관계 요약)

```
users (1) ──── (N) pets (1) ──── (N) pet_health
  │                  │
  │ (1:N)            │ (1:N)
  │                  │
  ├── walks ─────────┘
  │     │ (1:N)
  │     └── walk_photos
  │
  ├── user_badges (N) ──── (1) badge_definitions
  │
  ├── rankings
  │
  ├── follows (self-referencing: follower_id → users, following_id → users)
  │
  ├── likes ──── walks
  ├── comments ──── walks
  │
  ├── invitations (inviter_id → users, invitee_id → users)
  ├── meetups ──── meetup_participants
  │
  ├── push_tokens
  ├── notifications
  └── subscriptions
```

---

## 2. 테이블 정의

### 2.1 users (사용자)

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  auth_id UUID UNIQUE NOT NULL,           -- Supabase Auth UID
  email TEXT,
  nickname TEXT NOT NULL,                  -- 2~12자, 한글/영문/숫자
  profile_photo_url TEXT,                  -- 대표 반려동물 사진 (선택)
  region_sido TEXT,                        -- 시/도 (예: "서울특별시")
  region_sigungu TEXT,                     -- 시/군/구 (예: "성동구")
  region_dong TEXT,                        -- 동 (예: "성수동1가")
  is_premium BOOLEAN DEFAULT FALSE,
  premium_until TIMESTAMPTZ,
  weekly_goal_km NUMERIC DEFAULT 20,      -- 주간 목표 (km)
  walk_unit TEXT DEFAULT 'km',            -- km / mile
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ                   -- 소프트 삭제 (30일 유예)
);

-- 인덱스
CREATE INDEX idx_users_auth_id ON users(auth_id);
CREATE INDEX idx_users_region ON users(region_sigungu, region_dong);
CREATE INDEX idx_users_premium ON users(is_premium) WHERE is_premium = TRUE;
```

### 2.2 pets (반려동물)

```sql
CREATE TABLE pets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,                      -- 반려동물 이름
  species TEXT NOT NULL DEFAULT 'dog',     -- dog / cat
  breed TEXT,                              -- 견종/묘종 (예: "골든리트리버")
  size TEXT,                               -- small / medium / large
  birth_date DATE,                         -- 생년월일
  weight_kg NUMERIC,                       -- 현재 체중 (kg)
  photo_url TEXT,                          -- 프로필 사진 URL
  is_primary BOOLEAN DEFAULT FALSE,        -- 대표 반려동물 여부
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_pets_user_id ON pets(user_id);
CREATE INDEX idx_pets_breed ON pets(breed);
CREATE INDEX idx_pets_size ON pets(size);
```

### 2.3 pet_health (반려동물 건강 기록)

```sql
CREATE TABLE pet_health (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  pet_id UUID NOT NULL REFERENCES pets(id) ON DELETE CASCADE,
  record_type TEXT NOT NULL,               -- weight / vaccination / hospital_visit
  record_date DATE NOT NULL,
  value_numeric NUMERIC,                   -- 체중 기록 시 kg 값
  title TEXT,                              -- "광견병 예방접종", "정기 건강검진" 등
  memo TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_pet_health_pet_id ON pet_health(pet_id);
CREATE INDEX idx_pet_health_type_date ON pet_health(pet_id, record_type, record_date);
```

### 2.4 walks (산책 기록) - 핵심 테이블

```sql
-- PostGIS 확장 활성화
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE walks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  pet_id UUID NOT NULL REFERENCES pets(id),
  started_at TIMESTAMPTZ NOT NULL,
  ended_at TIMESTAMPTZ,
  duration_sec INTEGER,                    -- 총 산책 시간 (초)
  distance_m INTEGER,                      -- 총 거리 (미터)
  calories INTEGER,                        -- 소모 칼로리
  avg_speed_kmh NUMERIC(4,1),              -- 평균 속도 (km/h)
  route_geojson JSONB,                     -- GeoJSON LineString (전체 경로)
  route_geometry GEOMETRY(LineString, 4326), -- PostGIS 공간 인덱스용
  start_point GEOMETRY(Point, 4326),       -- 시작 지점
  end_point GEOMETRY(Point, 4326),         -- 종료 지점
  weather JSONB,                           -- {"temp": 12, "sky": "맑음", "pm10": 30, "pm25": 15}
  memo TEXT,                               -- "오늘 산책 한마디"
  is_valid BOOLEAN DEFAULT TRUE,           -- 유효성 검증 통과 여부
  shared_to_feed BOOLEAN DEFAULT FALSE,    -- 소셜 피드 공개 여부
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_walks_user_id ON walks(user_id);
CREATE INDEX idx_walks_pet_id ON walks(pet_id);
CREATE INDEX idx_walks_started_at ON walks(started_at DESC);
CREATE INDEX idx_walks_user_started ON walks(user_id, started_at DESC);
CREATE INDEX idx_walks_distance ON walks(distance_m) WHERE is_valid = TRUE;
CREATE INDEX idx_walks_route_geometry ON walks USING GIST(route_geometry);
CREATE INDEX idx_walks_start_point ON walks USING GIST(start_point);
CREATE INDEX idx_walks_feed ON walks(created_at DESC) WHERE shared_to_feed = TRUE AND is_valid = TRUE;
```

### 2.5 walk_photos (산책 사진)

```sql
CREATE TABLE walk_photos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  walk_id UUID NOT NULL REFERENCES walks(id) ON DELETE CASCADE,
  photo_url TEXT NOT NULL,                 -- Supabase Storage URL
  thumbnail_url TEXT,                      -- 썸네일 URL
  location GEOMETRY(Point, 4326),          -- 촬영 위치 GPS
  taken_at TIMESTAMPTZ DEFAULT NOW(),
  sort_order INTEGER DEFAULT 0
);

-- 인덱스
CREATE INDEX idx_walk_photos_walk_id ON walk_photos(walk_id);
```

### 2.6 badge_definitions (뱃지 정의)

```sql
CREATE TABLE badge_definitions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  category TEXT NOT NULL,                  -- distance / streak / exploration / time / special / season
  name TEXT NOT NULL,                      -- "5km 클럽"
  description TEXT,                        -- "누적 5킬로미터를 걸었어요"
  icon TEXT,                               -- 이모지 또는 아이콘 코드
  condition_type TEXT NOT NULL,            -- cumulative_distance / consecutive_days / unique_places / cumulative_time / special_* / season_*
  condition_value NUMERIC,                 -- 5000 (미터), 7 (일), 10 (곳) 등
  condition_extra JSONB,                   -- 추가 조건 (예: {"hour_before": 6} 얼리버드)
  difficulty TEXT NOT NULL,                -- beginner / easy / normal / hard / very_hard / legendary / mythic
  season_start DATE,                       -- 시즌 뱃지 시작일 (NULL이면 상시)
  season_end DATE,                         -- 시즌 뱃지 종료일
  hint TEXT,                               -- 미발견 뱃지의 힌트 텍스트
  sort_order INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_badge_definitions_category ON badge_definitions(category);
CREATE INDEX idx_badge_definitions_condition ON badge_definitions(condition_type);
```

### 2.7 user_badges (사용자별 뱃지 상태)

```sql
CREATE TABLE user_badges (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  badge_id UUID NOT NULL REFERENCES badge_definitions(id),
  status TEXT NOT NULL DEFAULT 'locked',   -- locked / in_progress / earned
  progress_value NUMERIC DEFAULT 0,        -- 현재 진행 수치 (예: 7200m)
  progress_percent NUMERIC DEFAULT 0,      -- 진행률 % (예: 72.0)
  earned_at TIMESTAMPTZ,                   -- 획득 시각
  earned_walk_id UUID REFERENCES walks(id),-- 획득 시 산책 ID
  pet_id UUID REFERENCES pets(id),         -- 어떤 반려동물과 달성했는지
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, badge_id)
);

-- 인덱스
CREATE INDEX idx_user_badges_user_id ON user_badges(user_id);
CREATE INDEX idx_user_badges_status ON user_badges(user_id, status);
CREATE INDEX idx_user_badges_in_progress ON user_badges(user_id) WHERE status = 'in_progress';
```

### 2.8 rankings (랭킹)

```sql
CREATE TABLE rankings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  pet_id UUID REFERENCES pets(id),
  period_type TEXT NOT NULL,               -- weekly / monthly / alltime
  period_key TEXT NOT NULL,                -- "2026-W07", "2026-02", "alltime"
  total_distance_m INTEGER DEFAULT 0,
  total_duration_sec INTEGER DEFAULT 0,
  walk_count INTEGER DEFAULT 0,
  rank INTEGER,
  prev_rank INTEGER,                       -- 이전 기간 순위 (변동 표시용)
  region_sigungu TEXT,                     -- 구 단위 지역
  region_dong TEXT,                        -- 동 단위 지역
  calculated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, period_type, period_key, region_sigungu)
);

-- 인덱스
CREATE INDEX idx_rankings_period ON rankings(period_type, period_key);
CREATE INDEX idx_rankings_region ON rankings(period_type, period_key, region_sigungu);
CREATE INDEX idx_rankings_rank ON rankings(period_type, period_key, region_sigungu, rank);
CREATE INDEX idx_rankings_user ON rankings(user_id, period_type);
```

### 2.9 hall_of_fame (명예의 전당)

```sql
CREATE TABLE hall_of_fame (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  pet_id UUID REFERENCES pets(id),
  category TEXT NOT NULL,                  -- monthly_mvp / longest_streak / longest_walk / top_cumulative / season_champion
  period_key TEXT,                         -- "2026-02", "2026-Q1" 등
  record_value NUMERIC,                    -- 거리(m), 일수 등
  message TEXT,                            -- "비가 와도 뽀삐랑 산책!" (사용자 한 줄 코멘트)
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_hall_of_fame_category ON hall_of_fame(category, period_key);
```

### 2.10 follows (팔로우)

```sql
CREATE TABLE follows (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  follower_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  following_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(follower_id, following_id),
  CHECK(follower_id != following_id)
);

-- 인덱스
CREATE INDEX idx_follows_follower ON follows(follower_id);
CREATE INDEX idx_follows_following ON follows(following_id);
```

### 2.11 likes (좋아요)

```sql
CREATE TABLE likes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  walk_id UUID NOT NULL REFERENCES walks(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, walk_id)
);

-- 인덱스
CREATE INDEX idx_likes_walk_id ON likes(walk_id);
CREATE INDEX idx_likes_user_id ON likes(user_id);
```

### 2.12 comments (댓글)

```sql
CREATE TABLE comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  walk_id UUID NOT NULL REFERENCES walks(id) ON DELETE CASCADE,
  content TEXT NOT NULL,                   -- 최대 200자
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ
);

-- 인덱스
CREATE INDEX idx_comments_walk_id ON comments(walk_id, created_at);
CREATE INDEX idx_comments_user_id ON comments(user_id);
```

### 2.13 invitations (산책 초대)

```sql
CREATE TABLE invitations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  inviter_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  invitee_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  scheduled_at TIMESTAMPTZ NOT NULL,       -- 산책 예정 시간
  location_name TEXT,                      -- "한강공원 뚝섬입구"
  location_point GEOMETRY(Point, 4326),    -- 만남 장소 GPS
  message TEXT,                            -- "오늘 날씨 좋은데 같이 가요~"
  status TEXT NOT NULL DEFAULT 'pending',  -- pending / accepted / declined / expired
  expires_at TIMESTAMPTZ,                  -- 예정 시간 30분 전 만료
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_invitations_invitee ON invitations(invitee_id, status);
CREATE INDEX idx_invitations_inviter ON invitations(inviter_id);
```

### 2.14 meetups (산책 모임)

```sql
CREATE TABLE meetups (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  creator_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,                     -- "성수동 골든리트리버 모임"
  description TEXT,
  location_name TEXT NOT NULL,             -- "서울숲 메타세쿼이아길"
  location_point GEOMETRY(Point, 4326),
  scheduled_at TIMESTAMPTZ NOT NULL,
  is_recurring BOOLEAN DEFAULT FALSE,      -- 정기 모임 여부
  recurrence_rule TEXT,                    -- "weekly" 등
  max_participants INTEGER DEFAULT 15,
  size_filter TEXT,                        -- small / medium / large / all
  status TEXT DEFAULT 'active',            -- active / cancelled / completed
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE meetup_participants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  meetup_id UUID NOT NULL REFERENCES meetups(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  status TEXT DEFAULT 'joined',            -- joined / left
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(meetup_id, user_id)
);

-- 인덱스
CREATE INDEX idx_meetups_location ON meetups USING GIST(location_point);
CREATE INDEX idx_meetups_scheduled ON meetups(scheduled_at) WHERE status = 'active';
CREATE INDEX idx_meetup_participants_meetup ON meetup_participants(meetup_id);
```

### 2.15 push_tokens (푸시 토큰)

```sql
CREATE TABLE push_tokens (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  platform TEXT NOT NULL,                  -- ios / android
  token TEXT NOT NULL,                     -- FCM 또는 APNs 토큰
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, token)
);

-- 인덱스
CREATE INDEX idx_push_tokens_user ON push_tokens(user_id) WHERE is_active = TRUE;
```

### 2.16 notifications (알림 내역)

```sql
CREATE TABLE notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type TEXT NOT NULL,                      -- badge_earned / badge_progress / ranking_change / walk_reminder / social / system / season_deadline
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  data JSONB,                              -- 딥링크 등 추가 데이터
  is_read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_notifications_user ON notifications(user_id, created_at DESC);
CREATE INDEX idx_notifications_unread ON notifications(user_id) WHERE is_read = FALSE;
```

### 2.17 subscriptions (구독/결제)

```sql
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  plan_type TEXT NOT NULL,                 -- monthly / annual
  status TEXT NOT NULL DEFAULT 'active',   -- active / cancelled / expired / trial
  payment_provider TEXT NOT NULL,          -- toss / ios_iap / google_play
  provider_subscription_id TEXT,           -- 외부 구독 ID
  price_krw INTEGER,                       -- 결제 금액 (원)
  trial_ends_at TIMESTAMPTZ,               -- 무료 체험 종료일
  current_period_start TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,
  cancelled_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_active ON subscriptions(user_id) WHERE status = 'active';
CREATE INDEX idx_subscriptions_expiring ON subscriptions(current_period_end) WHERE status = 'active';
```

### 2.18 blocks (차단)

```sql
CREATE TABLE blocks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  blocker_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  blocked_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(blocker_id, blocked_id),
  CHECK(blocker_id != blocked_id)
);

-- 인덱스
CREATE INDEX idx_blocks_blocker ON blocks(blocker_id);
CREATE INDEX idx_blocks_blocked ON blocks(blocked_id);
```

### 2.19 reports (신고)

```sql
CREATE TABLE reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reporter_id UUID NOT NULL REFERENCES users(id),
  target_type TEXT NOT NULL,               -- user / walk / comment / meetup
  target_id UUID NOT NULL,
  reason TEXT NOT NULL,                    -- inappropriate / spam / harassment / animal_abuse / privacy
  description TEXT,
  status TEXT DEFAULT 'pending',           -- pending / reviewed / resolved / dismissed
  reviewed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_reports_status ON reports(status) WHERE status = 'pending';
```

---

## 3. 뱃지 시드 데이터 (47개)

```sql
INSERT INTO badge_definitions (category, name, description, icon, condition_type, condition_value, condition_extra, difficulty, hint, sort_order) VALUES
-- 거리 뱃지 (7개)
('distance', '첫 발자국', '누적 1킬로미터를 걸었어요', '🐾', 'cumulative_distance', 1000, NULL, 'beginner', '첫 산책을 시작해보세요', 1),
('distance', '5km 클럽', '누적 5킬로미터를 걸었어요', '🏃', 'cumulative_distance', 5000, NULL, 'easy', '조금만 더 걸어보세요', 2),
('distance', '10km 탐험가', '누적 10킬로미터를 걸었어요', '🗺️', 'cumulative_distance', 10000, NULL, 'normal', '꾸준히 산책하면 도달해요', 3),
('distance', '50km 마라토너', '누적 50킬로미터를 걸었어요', '🏅', 'cumulative_distance', 50000, NULL, 'hard', '대단한 걸음이에요', 4),
('distance', '100km 철인', '누적 100킬로미터를 걸었어요', '🥇', 'cumulative_distance', 100000, NULL, 'very_hard', '산책의 달인이 되어가고 있어요', 5),
('distance', '500km 전설', '누적 500킬로미터를 걸었어요', '👑', 'cumulative_distance', 500000, NULL, 'legendary', '전설적인 산책러에요', 6),
('distance', '1000km 신화', '누적 1000킬로미터를 걸었어요', '💎', 'cumulative_distance', 1000000, NULL, 'mythic', '신화적인 기록이에요', 7),

-- 연속 뱃지 (7개)
('streak', '3일 연속', '3일 연속 산책했어요', '🔥', 'consecutive_days', 3, NULL, 'beginner', '매일 산책을 시작해보세요', 1),
('streak', '일주일 전사', '7일 연속 산책했어요', '💪', 'consecutive_days', 7, NULL, 'easy', '일주일을 채워보세요', 2),
('streak', '2주 챔피언', '14일 연속 산책했어요', '⚡', 'consecutive_days', 14, NULL, 'normal', '2주간 꾸준히 도전!', 3),
('streak', '한 달 철인', '30일 연속 산책했어요', '🌟', 'consecutive_days', 30, NULL, 'hard', '한 달의 기적을 만들어보세요', 4),
('streak', '60일 마스터', '60일 연속 산책했어요', '🏆', 'consecutive_days', 60, NULL, 'very_hard', '두 달의 여정', 5),
('streak', '100일 레전드', '100일 연속 산책했어요', '🔱', 'consecutive_days', 100, NULL, 'legendary', '100일의 전설', 6),
('streak', '365일 신화', '365일 연속 산책했어요', '💎', 'consecutive_days', 365, NULL, 'mythic', '1년간의 신화', 7),

-- 탐험 뱃지 (5개)
('exploration', '동네 탐험가', '3곳의 다른 장소에서 산책했어요', '🧭', 'unique_places', 3, NULL, 'beginner', '새로운 곳에서 산책해보세요', 1),
('exploration', '코스 수집가', '5곳의 다른 장소에서 산책했어요', '📍', 'unique_places', 5, NULL, 'easy', '다양한 코스를 탐험해보세요', 2),
('exploration', '지역 탐험대장', '10곳의 다른 장소에서 산책했어요', '🗺️', 'unique_places', 10, NULL, 'normal', '더 넓은 세상을 탐험하세요', 3),
('exploration', '산책 마스터', '20곳의 다른 장소에서 산책했어요', '🏔️', 'unique_places', 20, NULL, 'hard', '산책의 달인이 되어가요', 4),
('exploration', '전국 여행자', '50곳의 다른 장소에서 산책했어요', '✈️', 'unique_places', 50, NULL, 'legendary', '전국 방방곡곡!', 5),

-- 시간 뱃지 (5개)
('time', '첫 1시간', '누적 1시간 산책했어요', '⏱️', 'cumulative_time', 3600, NULL, 'beginner', '산책 시간을 늘려보세요', 1),
('time', '5시간 러너', '누적 5시간 산책했어요', '⏰', 'cumulative_time', 18000, NULL, 'easy', '꾸준히 시간을 채워가요', 2),
('time', '10시간 워커', '누적 10시간 산책했어요', '🕐', 'cumulative_time', 36000, NULL, 'normal', '열심히 걷고 있어요', 3),
('time', '50시간 마스터', '누적 50시간 산책했어요', '🕰️', 'cumulative_time', 180000, NULL, 'hard', '대단한 시간이에요', 4),
('time', '100시간 레전드', '누적 100시간 산책했어요', '💫', 'cumulative_time', 360000, NULL, 'legendary', '전설적인 시간이에요', 5),

-- 스페셜 뱃지 (10개)
('special', '얼리버드', '오전 6시 전에 산책을 시작했어요', '🌅', 'special_early_bird', 1, '{"hour_before": 6}', 'easy', '이른 아침에 산책해보세요', 1),
('special', '올빼미', '밤 10시 이후에 산책을 시작했어요', '🦉', 'special_night_owl', 1, '{"hour_after": 22}', 'easy', '늦은 밤에 산책해보세요', 2),
('special', '레인 워커', '비 오는 날 산책했어요', '🌧️', 'special_rain_walk', 1, '{"weather": "rain"}', 'normal', '특별한 날씨에 산책해보세요', 3),
('special', '스노우 워커', '눈 오는 날 산책했어요', '❄️', 'special_snow_walk', 1, '{"weather": "snow"}', 'normal', '특별한 날씨에 산책해보세요', 4),
('special', '새해 첫 산책', '1월 1일에 산책했어요', '🎆', 'special_new_year', 1, '{"month": 1, "day": 1}', 'easy', '새해 첫날을 기대하세요', 5),
('special', '생일 산책', '반려동물 생일에 산책했어요', '🎂', 'special_pet_birthday', 1, NULL, 'easy', '반려동물의 특별한 날', 6),
('special', '마라토너', '1회 산책에서 10km 이상 걸었어요', '🏃‍♂️', 'special_single_marathon', 10000, NULL, 'hard', '한 번에 아주 멀리 걸어보세요', 7),
('special', '소셜 워커', '함께 산책을 5회 했어요', '🤝', 'special_social_walk', 5, NULL, 'normal', '친구와 함께 산책해보세요', 8),
('special', '사진 작가', '산책 중 사진을 50장 촬영했어요', '📸', 'special_photographer', 50, NULL, 'normal', '산책 중 사진을 찍어보세요', 9),
('special', '랭킹 챔피언', '동네 랭킹 1위를 달성했어요', '👑', 'special_ranking_champion', 1, NULL, 'very_hard', '동네 최고가 되어보세요', 10),

-- 시즌 뱃지 (4개)
('season', '봄꽃길', '3~5월에 공원 5곳을 방문했어요', '🌸', 'season_spring', 5, '{"places": "park"}', 'normal', '봄에 공원을 방문해보세요', 1),
('season', '여름바다', '6~8월에 해안가에서 3회 산책했어요', '🏖️', 'season_summer', 3, '{"places": "beach"}', 'normal', '여름에 바다 근처를 산책해보세요', 2),
('season', '가을단풍', '9~11월에 산 또는 공원 5곳을 방문했어요', '🍂', 'season_autumn', 5, '{"places": "park_or_mountain"}', 'normal', '가을에 자연을 느껴보세요', 3),
('season', '겨울왕국', '12~2월에 눈 오는 날 산책했어요', '⛄', 'season_winter', 1, '{"weather": "snow"}', 'normal', '겨울에 눈 내리는 날을 기다려보세요', 4);
```

**총 45개** (기획서 47개 중 시즌 뱃지 세부 조건에 따라 조정 가능)

---

## 4. Row Level Security (RLS) 정책

```sql
-- 모든 테이블에 RLS 활성화
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE pets ENABLE ROW LEVEL SECURITY;
ALTER TABLE walks ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_badges ENABLE ROW LEVEL SECURITY;
-- ... (모든 테이블)

-- users: 본인 데이터만 수정 가능, 다른 사용자 닉네임/지역 읽기 가능
CREATE POLICY "users_select_all" ON users FOR SELECT USING (true);
CREATE POLICY "users_update_own" ON users FOR UPDATE USING (auth.uid() = auth_id);

-- pets: 본인 반려동물만 CRUD, 다른 사용자 반려동물 읽기 가능
CREATE POLICY "pets_select_all" ON pets FOR SELECT USING (true);
CREATE POLICY "pets_insert_own" ON pets FOR INSERT WITH CHECK (
  user_id IN (SELECT id FROM users WHERE auth_id = auth.uid())
);
CREATE POLICY "pets_update_own" ON pets FOR UPDATE USING (
  user_id IN (SELECT id FROM users WHERE auth_id = auth.uid())
);
CREATE POLICY "pets_delete_own" ON pets FOR DELETE USING (
  user_id IN (SELECT id FROM users WHERE auth_id = auth.uid())
);

-- walks: 본인 산책 CRUD, 피드 공개된 산책은 모두 읽기 가능
CREATE POLICY "walks_select_own" ON walks FOR SELECT USING (
  user_id IN (SELECT id FROM users WHERE auth_id = auth.uid())
);
CREATE POLICY "walks_select_feed" ON walks FOR SELECT USING (
  shared_to_feed = TRUE AND is_valid = TRUE
);
CREATE POLICY "walks_insert_own" ON walks FOR INSERT WITH CHECK (
  user_id IN (SELECT id FROM users WHERE auth_id = auth.uid())
);

-- follows: 본인 팔로우 관계만 CRUD
CREATE POLICY "follows_select_all" ON follows FOR SELECT USING (true);
CREATE POLICY "follows_insert_own" ON follows FOR INSERT WITH CHECK (
  follower_id IN (SELECT id FROM users WHERE auth_id = auth.uid())
);
CREATE POLICY "follows_delete_own" ON follows FOR DELETE USING (
  follower_id IN (SELECT id FROM users WHERE auth_id = auth.uid())
);

-- blocks: 차단한 사용자의 콘텐츠 필터링
CREATE POLICY "blocks_select_own" ON blocks FOR SELECT USING (
  blocker_id IN (SELECT id FROM users WHERE auth_id = auth.uid())
);
```

---

## 5. 데이터베이스 함수 (Stored Procedures)

### 5.1 연속 산책일수 계산

```sql
CREATE OR REPLACE FUNCTION calculate_streak_days(p_user_id UUID)
RETURNS INTEGER AS $$
DECLARE
  streak INTEGER := 0;
  check_date DATE := CURRENT_DATE;
  walk_exists BOOLEAN;
BEGIN
  -- 하루 기준: 오전 4시 ~ 다음날 오전 4시
  LOOP
    SELECT EXISTS(
      SELECT 1 FROM walks
      WHERE user_id = p_user_id
        AND is_valid = TRUE
        AND distance_m >= 500
        AND started_at >= (check_date + INTERVAL '4 hours')
        AND started_at < (check_date + INTERVAL '28 hours')
    ) INTO walk_exists;

    IF walk_exists THEN
      streak := streak + 1;
      check_date := check_date - INTERVAL '1 day';
    ELSE
      EXIT;
    END IF;
  END LOOP;

  RETURN streak;
END;
$$ LANGUAGE plpgsql;
```

### 5.2 주간 랭킹 집계

```sql
CREATE OR REPLACE FUNCTION refresh_weekly_rankings(p_period_key TEXT)
RETURNS VOID AS $$
BEGIN
  -- 기존 해당 기간 랭킹 삭제
  DELETE FROM rankings WHERE period_type = 'weekly' AND period_key = p_period_key;

  -- 새 랭킹 삽입
  INSERT INTO rankings (user_id, pet_id, period_type, period_key, total_distance_m, total_duration_sec, walk_count, rank, region_sigungu, region_dong)
  SELECT
    w.user_id,
    (SELECT id FROM pets WHERE user_id = w.user_id AND is_primary = TRUE LIMIT 1),
    'weekly',
    p_period_key,
    SUM(w.distance_m),
    SUM(w.duration_sec),
    COUNT(w.id),
    RANK() OVER (PARTITION BY u.region_sigungu ORDER BY SUM(w.distance_m) DESC),
    u.region_sigungu,
    u.region_dong
  FROM walks w
  JOIN users u ON w.user_id = u.id
  WHERE w.started_at >= date_trunc('week', CURRENT_DATE)
    AND w.is_valid = TRUE
    AND w.distance_m >= 500
  GROUP BY w.user_id, u.region_sigungu, u.region_dong;
END;
$$ LANGUAGE plpgsql;
```

---

*작성일: 2026-02-12*
*버전: 1.0*
