# 인증 시스템 - 멍이랑 (withbowwow)

> 코어 파일: [00_overview.md](./00_overview.md)
> 스키마: [01_database_schema.md](./01_database_schema.md)
> 구현: python-jose (JWT) + httpx (OAuth)

---

## 1. 인증 방식

### 1.1 소셜 로그인 (자체 구현)

| 제공자 | 우선순위 | 구현 방식 | 설정 |
|--------|---------|----------|------|
| **카카오** | 필수 | OAuth2 Authorization Code | Kakao Developers 앱 등록 → REST API 키 발급 |
| **네이버** | 필수 | OAuth2 Authorization Code | 네이버 개발자센터 → Client ID/Secret 발급 |
| **Apple** | 필수 (iOS) | Sign in with Apple (JWT) | Apple Developer → Service ID + Key 설정 |

### 1.2 인증 플로우

```
[앱 온보딩]
  │
  ├── 인트로 슬라이드 (3장)
  │
  ├── 소셜 로그인 선택
  │     ├── 카카오 로그인 ──┐
  │     ├── 네이버 로그인 ──┤── FastAPI /auth/{provider}/callback
  │     └── Apple 로그인 ──┘     → JWT Access + Refresh 토큰 발급
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

### 1.3 소셜 로그인 구현 (FastAPI)

```python
# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/kakao")
async def login_with_kakao(
    body: KakaoLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    클라이언트에서 카카오 SDK로 받은 authorization_code를
    서버로 전달 → 서버에서 토큰 교환 + 사용자 정보 조회
    """
    auth_service = AuthService(db)

    # 1. 카카오 토큰 교환
    kakao_token = await auth_service.exchange_kakao_token(body.code)

    # 2. 카카오 사용자 정보 조회
    kakao_user = await auth_service.get_kakao_user(kakao_token["access_token"])

    # 3. DB에서 사용자 조회 또는 생성
    user, is_new = await auth_service.get_or_create_user(
        provider="kakao",
        provider_id=str(kakao_user["id"]),
        email=kakao_user.get("kakao_account", {}).get("email"),
        nickname=kakao_user.get("properties", {}).get("nickname"),
    )

    # 4. JWT 발급
    tokens = auth_service.create_tokens(user.id)

    # 5. 리프레시 토큰 해시 저장
    await auth_service.save_refresh_token(user.id, tokens["refresh_token"])

    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "is_new_user": is_new,
        "user": UserResponse.model_validate(user),
    }


@router.post("/naver")
async def login_with_naver(body: NaverLoginRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)
    naver_token = await auth_service.exchange_naver_token(body.code, body.state)
    naver_user = await auth_service.get_naver_user(naver_token["access_token"])

    user, is_new = await auth_service.get_or_create_user(
        provider="naver",
        provider_id=naver_user["response"]["id"],
        email=naver_user["response"].get("email"),
        nickname=naver_user["response"].get("nickname"),
    )

    tokens = auth_service.create_tokens(user.id)
    await auth_service.save_refresh_token(user.id, tokens["refresh_token"])

    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "is_new_user": is_new,
    }


@router.post("/apple")
async def login_with_apple(body: AppleLoginRequest, db: AsyncSession = Depends(get_db)):
    auth_service = AuthService(db)

    # Apple의 경우 identity_token(JWT)을 직접 검증
    apple_user = await auth_service.verify_apple_token(body.identity_token)

    user, is_new = await auth_service.get_or_create_user(
        provider="apple",
        provider_id=apple_user["sub"],
        email=apple_user.get("email"),
        nickname=body.full_name,  # Apple은 첫 로그인 때만 이름 제공
    )

    tokens = auth_service.create_tokens(user.id)
    await auth_service.save_refresh_token(user.id, tokens["refresh_token"])

    return {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "is_new_user": is_new,
    }


@router.post("/refresh")
async def refresh_token(body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """리프레시 토큰으로 새 액세스 토큰 발급"""
    auth_service = AuthService(db)
    tokens = await auth_service.refresh_access_token(body.refresh_token)
    return tokens
```

---

## 2. AuthService 구현

```python
# app/services/auth_service.py
import httpx
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ── 카카오 ──

    async def exchange_kakao_token(self, code: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://kauth.kakao.com/oauth/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": settings.KAKAO_CLIENT_ID,
                    "client_secret": settings.KAKAO_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.KAKAO_REDIRECT_URI,
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def get_kakao_user(self, access_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            resp.raise_for_status()
            return resp.json()

    # ── 네이버 ──

    async def exchange_naver_token(self, code: str, state: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://nid.naver.com/oauth2.0/token",
                data={
                    "grant_type": "authorization_code",
                    "client_id": settings.NAVER_CLIENT_ID,
                    "client_secret": settings.NAVER_CLIENT_SECRET,
                    "code": code,
                    "state": state,
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def get_naver_user(self, access_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://openapi.naver.com/v1/nid/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            resp.raise_for_status()
            return resp.json()

    # ── Apple ──

    async def verify_apple_token(self, identity_token: str) -> dict:
        """Apple identity_token(JWT)을 검증하고 페이로드를 반환"""
        # Apple 공개 키 가져오기
        async with httpx.AsyncClient() as client:
            resp = await client.get("https://appleid.apple.com/auth/keys")
            apple_keys = resp.json()["keys"]

        # JWT 헤더에서 kid 추출 → 매칭되는 키로 검증
        header = jwt.get_unverified_header(identity_token)
        key = next(k for k in apple_keys if k["kid"] == header["kid"])

        payload = jwt.decode(
            identity_token,
            key,
            algorithms=["RS256"],
            audience=settings.APPLE_CLIENT_ID,
            issuer="https://appleid.apple.com",
        )
        return payload

    # ── 사용자 생성/조회 ──

    async def get_or_create_user(
        self, provider: str, provider_id: str, email: str | None, nickname: str | None
    ) -> tuple[User, bool]:
        """기존 사용자 조회 또는 신규 생성. (User, is_new) 반환"""
        stmt = select(User).where(
            User.provider == provider,
            User.provider_id == provider_id,
        )
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            # 소프트 삭제된 사용자가 재로그인하면 복구
            if user.deleted_at is not None:
                user.deleted_at = None
                await self.db.commit()
            return user, False

        # 신규 사용자 생성
        new_user = User(
            provider=provider,
            provider_id=provider_id,
            email=email,
            nickname=nickname or f"멍이랑{provider_id[:4]}",
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user, True

    # ── JWT 토큰 ──

    def create_tokens(self, user_id: str) -> dict:
        access_token = jwt.encode(
            {
                "sub": str(user_id),
                "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
                "type": "access",
            },
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        refresh_token = jwt.encode(
            {
                "sub": str(user_id),
                "exp": datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
                "type": "refresh",
            },
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
        return {"access_token": access_token, "refresh_token": refresh_token}

    async def save_refresh_token(self, user_id: str, refresh_token: str):
        hashed = pwd_context.hash(refresh_token)
        stmt = update(User).where(User.id == user_id).values(hashed_refresh_token=hashed)
        await self.db.execute(stmt)
        await self.db.commit()

    async def refresh_access_token(self, refresh_token: str) -> dict:
        try:
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid token type")

            user_id = payload["sub"]
            user = await self.db.get(User, user_id)
            if not user or not pwd_context.verify(refresh_token, user.hashed_refresh_token):
                raise HTTPException(status_code=401, detail="Invalid refresh token")

            tokens = self.create_tokens(user_id)
            await self.save_refresh_token(user_id, tokens["refresh_token"])
            return tokens

        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
```

---

## 3. 온보딩

### 3.1 온보딩 완료 체크

```python
# app/routers/users.py

@router.get("/me/onboarding-status")
async def check_onboarding(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(Pet).where(Pet.user_id == current_user.id).limit(1)
    result = await self.db.execute(stmt)
    has_pet = result.scalar_one_or_none() is not None

    return {
        "has_nickname": bool(current_user.nickname) and not current_user.nickname.startswith("멍이랑"),
        "has_pet": has_pet,
        "has_location": bool(current_user.region_dong),
        "has_notification": False,  # 프론트에서 확인
    }
```

---

## 4. 토큰 관리

### 4.1 JWT 토큰

| 항목 | 값 |
|------|-----|
| 발급자 | FastAPI 서버 (python-jose) |
| 액세스 토큰 만료 | 1시간 |
| 리프레시 토큰 만료 | 7일 |
| 저장소 (클라이언트) | expo-secure-store (암호화 저장) |
| 갱신 | POST /auth/refresh |

### 4.2 토큰 구조

```json
// Access Token Payload
{
  "sub": "user-uuid-here",
  "exp": 1707750000,
  "type": "access"
}

// Refresh Token Payload
{
  "sub": "user-uuid-here",
  "exp": 1708354800,
  "type": "refresh"
}
```

---

## 5. 계정 관리

### 5.1 닉네임 변경

- 규칙: 한글/영문/숫자, 2~12자
- 중복 검사: 실시간 (debounce 300ms)
- 변경 제한: 7일에 1회

### 5.2 계정 삭제

```
사용자 삭제 요청
  → users.deleted_at = NOW() (소프트 삭제)
  → 30일 유예 기간
  → 유예 기간 내 재로그인 시 복구 가능
  → 30일 후 APScheduler Cron으로 완전 삭제:
    - CASCADE로 관련 데이터 전부 삭제
    - R2 Storage 파일 삭제
```

### 5.3 로그아웃

```python
@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 리프레시 토큰 무효화
    current_user.hashed_refresh_token = None
    await db.commit()

    # 푸시 토큰 비활성화
    stmt = (
        update(PushToken)
        .where(PushToken.user_id == current_user.id)
        .values(is_active=False)
    )
    await db.execute(stmt)
    await db.commit()

    return {"message": "Logged out"}
```

---

## 6. 퍼널 KPI (온보딩)

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
*버전: 2.0 — python-jose JWT + httpx OAuth로 전환*
