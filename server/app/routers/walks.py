from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.walk import Walk
from app.schemas.walk import WalkComplete, WalkCreate, WalkListResponse, WalkResponse

router = APIRouter()

# 산책 유효성 검증 상수
MAX_SPEED_KMH = 15  # 시속 15km 이상이면 부정행위
MIN_DISTANCE_M = 100  # 100m 미만이면 무효


@router.post("", response_model=WalkResponse, status_code=status.HTTP_201_CREATED)
async def start_walk(
    body: WalkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """산책 시작 (진행 중인 산책 기록 생성)"""
    walk = Walk(
        user_id=current_user.id,
        pet_id=body.pet_id,
        started_at=body.started_at,
    )
    db.add(walk)
    await db.commit()
    await db.refresh(walk)
    return walk


@router.post("/{walk_id}/complete", response_model=WalkResponse)
async def complete_walk(
    walk_id: int,
    body: WalkComplete,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """산책 완료 처리"""
    result = await db.execute(
        select(Walk).where(Walk.id == walk_id, Walk.user_id == current_user.id)
    )
    walk = result.scalar_one_or_none()
    if walk is None:
        raise HTTPException(status_code=404, detail="산책 기록을 찾을 수 없습니다")

    if walk.ended_at is not None:
        raise HTTPException(status_code=400, detail="이미 완료된 산책입니다")

    # 유효성 검증
    is_valid = True
    if body.avg_speed_kmh and body.avg_speed_kmh > MAX_SPEED_KMH:
        is_valid = False
    if body.distance_m < MIN_DISTANCE_M:
        is_valid = False

    # 산책 완료 데이터 저장
    walk.ended_at = body.ended_at
    walk.distance_m = body.distance_m
    walk.duration_sec = body.duration_sec
    walk.calories = body.calories
    walk.avg_speed_kmh = body.avg_speed_kmh
    walk.route_geojson = body.route_geojson
    walk.weather = body.weather
    walk.memo = body.memo
    walk.shared_to_feed = body.shared_to_feed
    walk.is_valid = is_valid

    await db.commit()
    await db.refresh(walk)

    # TODO: 백그라운드 태스크 — 뱃지 진행률 업데이트, 랭킹 반영, 푸시 알림

    return walk


@router.get("", response_model=WalkListResponse)
async def list_walks(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """내 산책 기록 목록"""
    offset = (page - 1) * size

    # 총 개수
    count_result = await db.execute(
        select(func.count()).select_from(Walk).where(Walk.user_id == current_user.id)
    )
    total = count_result.scalar()

    # 목록 조회
    result = await db.execute(
        select(Walk)
        .where(Walk.user_id == current_user.id)
        .order_by(Walk.created_at.desc())
        .offset(offset)
        .limit(size)
    )
    walks = result.scalars().all()

    return WalkListResponse(items=walks, total=total, page=page, size=size)


@router.get("/{walk_id}", response_model=WalkResponse)
async def get_walk(
    walk_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """산책 상세 조회"""
    result = await db.execute(
        select(Walk).where(Walk.id == walk_id, Walk.user_id == current_user.id)
    )
    walk = result.scalar_one_or_none()
    if walk is None:
        raise HTTPException(status_code=404, detail="산책 기록을 찾을 수 없습니다")
    return walk


@router.delete("/{walk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_walk(
    walk_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """산책 기록 삭제"""
    result = await db.execute(
        select(Walk).where(Walk.id == walk_id, Walk.user_id == current_user.id)
    )
    walk = result.scalar_one_or_none()
    if walk is None:
        raise HTTPException(status_code=404, detail="산책 기록을 찾을 수 없습니다")

    await db.delete(walk)
    await db.commit()
