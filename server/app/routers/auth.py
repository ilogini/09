from datetime import datetime, timedelta, timezone

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.auth import RefreshRequest, SocialLoginRequest, TokenResponse

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(
        {"sub": str(user_id), "exp": expire},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def create_refresh_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )
    return jwt.encode(
        {"sub": str(user_id), "exp": expire, "type": "refresh"},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


async def get_or_create_user(
    db: AsyncSession, provider: str, provider_id: str, nickname: str
) -> User:
    result = await db.execute(
        select(User).where(User.provider == provider, User.provider_id == provider_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            provider=provider,
            provider_id=provider_id,
            nickname=nickname,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user


@router.post("/kakao", response_model=TokenResponse)
async def kakao_login(body: SocialLoginRequest, db: AsyncSession = Depends(get_db)):
    """카카오 소셜 로그인"""
    # 1. authorization_code → access_token 교환
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": settings.KAKAO_CLIENT_ID,
                "client_secret": settings.KAKAO_CLIENT_SECRET,
                "code": body.code,
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="카카오 토큰 교환 실패",
            )
        kakao_token = token_resp.json().get("access_token")

        # 2. access_token → 사용자 정보
        user_resp = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {kakao_token}"},
        )
        if user_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="카카오 사용자 정보 조회 실패",
            )
        kakao_user = user_resp.json()

    provider_id = str(kakao_user["id"])
    nickname = kakao_user.get("properties", {}).get("nickname", f"user_{provider_id[:8]}")

    # 3. DB 사용자 조회/생성
    user = await get_or_create_user(db, "kakao", provider_id, nickname)

    # 4. JWT 토큰 발급
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    # 5. refresh token 해시 저장
    user.hashed_refresh_token = pwd_context.hash(refresh_token)
    await db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/naver", response_model=TokenResponse)
async def naver_login(body: SocialLoginRequest, db: AsyncSession = Depends(get_db)):
    """네이버 소셜 로그인"""
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            "https://nid.naver.com/oauth2.0/token",
            params={
                "grant_type": "authorization_code",
                "client_id": settings.NAVER_CLIENT_ID,
                "client_secret": settings.NAVER_CLIENT_SECRET,
                "code": body.code,
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="네이버 토큰 교환 실패",
            )
        naver_token = token_resp.json().get("access_token")

        user_resp = await client.get(
            "https://openapi.naver.com/v1/nid/me",
            headers={"Authorization": f"Bearer {naver_token}"},
        )
        if user_resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="네이버 사용자 정보 조회 실패",
            )
        naver_user = user_resp.json().get("response", {})

    provider_id = naver_user.get("id", "")
    nickname = naver_user.get("nickname", f"user_{provider_id[:8]}")

    user = await get_or_create_user(db, "naver", provider_id, nickname)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    user.hashed_refresh_token = pwd_context.hash(refresh_token)
    await db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """리프레시 토큰으로 새 토큰 발급"""
    try:
        payload = jwt.decode(
            body.refresh_token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="유효하지 않은 리프레시 토큰")

        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="토큰 검증 실패")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or user.hashed_refresh_token is None:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다")

    if not pwd_context.verify(body.refresh_token, user.hashed_refresh_token):
        raise HTTPException(status_code=401, detail="리프레시 토큰이 일치하지 않습니다")

    access_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)
    user.hashed_refresh_token = pwd_context.hash(new_refresh_token)
    await db.commit()

    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


@router.post("/logout")
async def logout(
    db: AsyncSession = Depends(get_db),
    credentials=Depends(
        __import__("fastapi.security", fromlist=["HTTPBearer"]).HTTPBearer()
    ),
):
    """로그아웃 (리프레시 토큰 무효화)"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(status_code=401, detail="토큰 검증 실패")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.hashed_refresh_token = None
        await db.commit()

    return {"message": "로그아웃 완료"}
