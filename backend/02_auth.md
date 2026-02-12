# 인증 시스템 - 멍이랑 (withbowwow)

> 코어 파일: [00_overview.md](./00_overview.md)
> 스키마: [01_database_schema.md](./01_database_schema.md)

---

## 1. 인증 방식

### 1.1 소셜 로그인 (Supabase Auth)

| 제공자 | 우선순위 | Supabase 지원 | 설정 방법 |
|--------|---------|-------------|----------|
| **카카오** | 필수 | OAuth2 Provider | Kakao Developers 앱 등록 → Client ID/Secret 발급 → Supabase Auth Provider 설정 |
| **네이버** | 필수 | Custom OIDC Provider | 네이버 개발자센터 → OIDC 설정 → Supabase Custom Provider |
| **Apple** | 필수 (iOS 필수) | 내장 지원 | Apple Developer → Sign in with Apple 설정 → Supabase Apple Provider |

### 1.2 인증 플로우

```
[앱 온보딩]
  │
  ├── 인트로 슬라이드 (3장)
  │
  ├── 소셜 로그인 선택
  │     ├── 카카오 로그인 ──┐
  │     ├── 네이버 로그인 ──┤── Supabase Auth → JWT 발급
  │     └── Apple 로그인 ──┘
  │
  ├── [신규 사용자] 온보딩
  │     ├── 닉네임 설정 (2~12자)
  │     ├── 반려동물 등록 (필수 1마리)
  │     │     ├── 이름
  │     │     ├── 종류 (개/고양이)
  │     │     ├── 견종/묘종
  │     │     ├── 생년월일 (선택)
  │     │     ├── 체중 (선택)
  │     │     └── 사진 (선택)
  │     ├── 위치 권한 요청
  │     └── 알림 권한 요청
  │
  └── [기존 사용자] → 홈 화면 진입
```

### 1.3 Supabase Auth 설정 (TypeScript)

```typescript
// supabase/config.ts
import { createClient } from '@supabase/supabase-js';

export const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
);

// 카카오 로그인
async function signInWithKakao() {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'kakao',
    options: {
      redirectTo: 'withbowwow://auth/callback',
      scopes: 'profile_nickname profile_image',
    },
  });
}

// 네이버 로그인 (Custom OIDC)
async function signInWithNaver() {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'naver' as any, // Custom Provider
    options: {
      redirectTo: 'withbowwow://auth/callback',
    },
  });
}

// Apple 로그인
async function signInWithApple() {
  const { data, error } = await supabase.auth.signInWithOAuth({
    provider: 'apple',
    options: {
      redirectTo: 'withbowwow://auth/callback',
    },
  });
}
```

---

## 2. 신규 사용자 등록 플로우

### 2.1 Database Trigger: 사용자 자동 생성

```sql
-- Supabase Auth 가입 시 users 테이블에 자동 레코드 생성
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (auth_id, email, nickname)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'nickname', '멍이랑' || substr(NEW.id::text, 1, 4))
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
```

### 2.2 온보딩 완료 체크

```typescript
// 온보딩 완료 여부 확인
interface OnboardingStatus {
  hasNickname: boolean;   // 닉네임 설정 완료
  hasPet: boolean;        // 반려동물 등록 완료
  hasLocation: boolean;   // 위치 권한 허용
  hasNotification: boolean; // 알림 권한 허용
}

async function checkOnboarding(userId: string): Promise<OnboardingStatus> {
  const { data: user } = await supabase
    .from('users')
    .select('nickname')
    .eq('id', userId)
    .single();

  const { data: pets } = await supabase
    .from('pets')
    .select('id')
    .eq('user_id', userId)
    .limit(1);

  return {
    hasNickname: !!user?.nickname && !user.nickname.startsWith('멍이랑'),
    hasPet: (pets?.length ?? 0) > 0,
    hasLocation: false, // 프론트에서 확인
    hasNotification: false, // 프론트에서 확인
  };
}
```

---

## 3. 토큰 관리

### 3.1 JWT 토큰

| 항목 | 값 |
|------|-----|
| 발급자 | Supabase Auth |
| 액세스 토큰 만료 | 1시간 (기본값) |
| 리프레시 토큰 만료 | 7일 |
| 저장소 | expo-secure-store (암호화 저장) |
| 자동 갱신 | Supabase Client 자동 처리 |

### 3.2 세션 관리

```typescript
// 앱 시작 시 세션 복원
const { data: { session } } = await supabase.auth.getSession();

// 세션 변경 감지
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'SIGNED_OUT') {
    // 로그아웃 처리
  } else if (event === 'TOKEN_REFRESHED') {
    // 토큰 갱신됨
  }
});
```

---

## 4. 계정 관리

### 4.1 닉네임 변경

- 규칙: 한글/영문/숫자, 2~12자
- 중복 검사: 실시간 (debounce 300ms)
- 변경 제한: 7일에 1회

### 4.2 계정 삭제

```
사용자 삭제 요청
  → users.deleted_at = NOW() (소프트 삭제)
  → 30일 유예 기간
  → 유예 기간 내 재로그인 시 복구 가능
  → 30일 후 Cron Job으로 완전 삭제:
    - Supabase Auth 계정 삭제
    - CASCADE로 관련 데이터 전부 삭제
    - Storage 파일 삭제
```

### 4.3 로그아웃

```typescript
async function signOut() {
  await supabase.auth.signOut();
  // 로컬 캐시 클리어
  // 푸시 토큰 비활성화
  await supabase
    .from('push_tokens')
    .update({ is_active: false })
    .eq('user_id', currentUserId);
}
```

---

## 5. 퍼널 KPI (온보딩)

| 단계 | 목표 전환율 |
|------|-----------|
| 앱 설치 → 인트로 완료 | 90% |
| 인트로 → 소셜 로그인 완료 | 70% |
| 로그인 → 반려동물 등록 완료 | 85% |
| 등록 → 위치 권한 허용 | 80% |
| 위치 권한 → 알림 권한 허용 | 60% |
| 알림 권한 → 첫 산책 완료 | 40% |

---

*작성일: 2026-02-12*
*버전: 1.0*
