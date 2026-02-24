from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: int
    email: str | None = None
    nickname: str
    profile_photo_url: str | None = None
    region_sido: str | None = None
    region_sigungu: str | None = None
    region_dong: str | None = None
    is_premium: bool = False
    premium_until: datetime | None = None
    weekly_goal_km: float | None = 20.0
    walk_unit: str = "km"
    notification_settings: dict | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    nickname: str | None = None
    profile_photo_url: str | None = None
    region_sido: str | None = None
    region_sigungu: str | None = None
    region_dong: str | None = None
    weekly_goal_km: float | None = None
    walk_unit: str | None = None
    notification_settings: dict | None = None
