from datetime import datetime

from pydantic import BaseModel


class PetCreate(BaseModel):
    name: str
    species: str = "dog"
    breed: str | None = None
    birth_year: int | None = None
    weight_kg: float | None = None
    photo_url: str | None = None


class PetUpdate(BaseModel):
    name: str | None = None
    breed: str | None = None
    birth_year: int | None = None
    weight_kg: float | None = None
    photo_url: str | None = None


class PetResponse(BaseModel):
    id: int
    user_id: int
    name: str
    species: str
    breed: str | None = None
    birth_year: int | None = None
    weight_kg: float | None = None
    photo_url: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
