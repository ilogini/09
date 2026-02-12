# 데이터베이스 스키마 - 멍이랑 (withbowwow)

> 코어 파일: [00_overview.md](./00_overview.md)
> PostgreSQL 15+ / PostGIS 확장 / 자체 운영 DB
> ORM: SQLAlchemy 2.0 + GeoAlchemy2 / 마이그레이션: Alembic

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
  email TEXT,
  nickname TEXT NOT NULL,                  -- 2~12자, 한글/영문/숫자
  profile_photo_url TEXT,
  provider TEXT NOT NULL,                  -- kakao / naver / apple
  provider_id TEXT NOT NULL,               -- 소셜 로그인 고유 ID
  region_sido TEXT,                        -- 시/도 (예: "서울특별시")
  region_sigungu TEXT,                     -- 시/군/구 (예: "성동구")
  region_dong TEXT,                        -- 동 (예: "성수동1가")
  is_premium BOOLEAN DEFAULT FALSE,
  premium_until TIMESTAMPTZ,
  weekly_goal_km NUMERIC DEFAULT 20,
  walk_unit TEXT DEFAULT 'km',
  notification_settings JSONB DEFAULT '{}',
  hashed_refresh_token TEXT,               -- 리프레시 토큰 해시 저장
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ,                  -- 소프트 삭제 (30일 유예)
  UNIQUE(provider, provider_id)
);

-- 인덱스
CREATE INDEX idx_users_provider ON users(provider, provider_id);
CREATE INDEX idx_users_region ON users(region_sigungu, region_dong);
CREATE INDEX idx_users_premium ON users(is_premium) WHERE is_premium = TRUE;
CREATE INDEX idx_users_nickname ON users(nickname);
```

### 2.2 pets (반려동물)

```sql
CREATE TABLE pets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  species TEXT NOT NULL DEFAULT 'dog',     -- dog / cat
  breed TEXT,
  size TEXT,                               -- small / medium / large
  birth_date DATE,
  weight_kg NUMERIC,
  photo_url TEXT,
  is_primary BOOLEAN DEFAULT FALSE,
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
  value_numeric NUMERIC,
  title TEXT,
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
  duration_sec INTEGER,
  distance_m INTEGER,
  calories INTEGER,
  avg_speed_kmh NUMERIC(4,1),
  route_geojson JSONB,                     -- GeoJSON LineString (전체 경로)
  route_geometry GEOMETRY(LineString, 4326),
  start_point GEOMETRY(Point, 4326),
  end_point GEOMETRY(Point, 4326),
  weather JSONB,                           -- {"temp": 12, "sky": "맑음", "pm10": 30}
  memo TEXT,
  is_valid BOOLEAN DEFAULT TRUE,
  shared_to_feed BOOLEAN DEFAULT FALSE,
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
  photo_url TEXT NOT NULL,                 -- Cloudflare R2 URL
  thumbnail_url TEXT,
  location GEOMETRY(Point, 4326),
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
  name TEXT NOT NULL,
  description TEXT,
  icon TEXT,
  condition_type TEXT NOT NULL,
  condition_value NUMERIC,
  condition_extra JSONB,
  difficulty TEXT NOT NULL,                -- beginner / easy / normal / hard / very_hard / legendary / mythic
  season_start DATE,
  season_end DATE,
  hint TEXT,
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
  progress_value NUMERIC DEFAULT 0,
  progress_percent NUMERIC DEFAULT 0,
  earned_at TIMESTAMPTZ,
  earned_walk_id UUID REFERENCES walks(id),
  pet_id UUID REFERENCES pets(id),
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
  prev_rank INTEGER,
  region_sigungu TEXT,
  region_dong TEXT,
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
  category TEXT NOT NULL,
  period_key TEXT,
  record_value NUMERIC,
  message TEXT,
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
  content TEXT NOT NULL,
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
  scheduled_at TIMESTAMPTZ NOT NULL,
  location_name TEXT,
  location_point GEOMETRY(Point, 4326),
  message TEXT,
  status TEXT NOT NULL DEFAULT 'pending',  -- pending / accepted / declined / expired
  expires_at TIMESTAMPTZ,
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
  title TEXT NOT NULL,
  description TEXT,
  location_name TEXT NOT NULL,
  location_point GEOMETRY(Point, 4326),
  scheduled_at TIMESTAMPTZ NOT NULL,
  is_recurring BOOLEAN DEFAULT FALSE,
  recurrence_rule TEXT,
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
  token TEXT NOT NULL,
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
  type TEXT NOT NULL,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  data JSONB,
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
  provider_subscription_id TEXT,
  price_krw INTEGER,
  trial_ends_at TIMESTAMPTZ,
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
  reason TEXT NOT NULL,
  description TEXT,
  status TEXT DEFAULT 'pending',           -- pending / reviewed / resolved / dismissed
  reviewed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_reports_status ON reports(status) WHERE status = 'pending';
```

---

## 3. 뱃지 시드 데이터 (45개)

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

---

## 4. 접근 제어 (Application-Level)

> Supabase RLS 대신 FastAPI 의존성 주입(Depends)으로 접근 제어를 구현한다.

```python
# app/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """JWT 토큰에서 현재 사용자를 추출하는 의존성"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = await db.get(User, user_id)
    if user is None or user.deleted_at is not None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


async def require_premium(
    current_user: User = Depends(get_current_user),
) -> User:
    """프리미엄 사용자만 접근 가능한 엔드포인트용 의존성"""
    if not current_user.is_premium:
        raise HTTPException(status_code=403, detail="Premium required")
    return current_user
```

### 4.1 주요 접근 제어 규칙

| 리소스 | 읽기 | 쓰기 | 삭제 |
|--------|------|------|------|
| users | 모두 (닉네임/지역) | 본인만 | 본인만 (소프트 삭제) |
| pets | 모두 | 본인 반려동물만 | 본인만 |
| walks | 본인 + 피드 공개 | 본인만 | 본인만 |
| follows | 모두 | 본인 팔로우만 | 본인만 |
| likes/comments | 모두 | 인증 사용자 | 본인만 |
| notifications | 본인만 | 시스템만 | 본인만 |
| blocks | 본인만 | 본인만 | 본인만 |

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
  DELETE FROM rankings WHERE period_type = 'weekly' AND period_key = p_period_key;

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

### 5.3 고유 장소 수 계산

```sql
CREATE OR REPLACE FUNCTION count_unique_places(p_user_id UUID)
RETURNS INTEGER AS $$
  SELECT COUNT(DISTINCT cluster_id)::INTEGER
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

*작성일: 2026-02-12*
*버전: 2.0 — 자체 PostgreSQL + FastAPI 접근 제어로 전환*
