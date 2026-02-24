from datetime import date, datetime

from pydantic import BaseModel


class PetCreate(BaseModel):
    name: str
    species: str = "dog"
    breed: str | None = None
    size: str | None = None  # small, medium, large
    birth_date: date | None = None
    weight_kg: float | None = None
    photo_url: str | None = None
    is_primary: bool = False


class PetUpdate(BaseModel):
    name: str | None = None
    breed: str | None = None
    size: str | None = None
    birth_date: date | None = None
    weight_kg: float | None = None
    photo_url: str | None = None
    is_primary: bool | None = None


class PetResponse(BaseModel):
    id: int
    user_id: int
    name: str
    species: str
    breed: str | None = None
    size: str | None = None
    birth_date: date | None = None
    weight_kg: float | None = None
    photo_url: str | None = None
    is_primary: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}
