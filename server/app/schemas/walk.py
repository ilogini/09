from datetime import datetime
from typing import Any

from pydantic import BaseModel


class WalkCreate(BaseModel):
    pet_id: int | None = None
    started_at: datetime


class WalkComplete(BaseModel):
    ended_at: datetime
    distance_m: int
    duration_sec: int
    calories: int | None = None
    avg_speed_kmh: float | None = None
    route_geojson: dict[str, Any] | None = None
    weather: dict[str, Any] | None = None
    memo: str | None = None
    shared_to_feed: bool = False


class WalkPhotoResponse(BaseModel):
    id: int
    photo_url: str
    thumbnail_url: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    taken_at: datetime | None = None
    sort_order: int = 0

    model_config = {"from_attributes": True}


class WalkResponse(BaseModel):
    id: int
    user_id: int
    pet_id: int | None = None
    started_at: datetime
    ended_at: datetime | None = None
    distance_m: int
    duration_sec: int
    calories: int | None = None
    avg_speed_kmh: float | None = None
    route_geojson: dict[str, Any] | None = None
    weather: dict[str, Any] | None = None
    memo: str | None = None
    is_valid: bool
    shared_to_feed: bool
    photos: list[WalkPhotoResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class WalkListResponse(BaseModel):
    items: list[WalkResponse]
    total: int
    page: int
    size: int
