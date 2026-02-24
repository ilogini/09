from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    func,
)
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Walk(Base):
    __tablename__ = "walks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    pet_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("pets.id"))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    distance_m: Mapped[int] = mapped_column(Integer, default=0)
    duration_sec: Mapped[int] = mapped_column(Integer, default=0)
    calories: Mapped[int | None] = mapped_column(Integer)
    avg_speed_kmh: Mapped[float | None] = mapped_column(Numeric(5, 2))
    route_geojson: Mapped[dict | None] = mapped_column(JSONB)
    route_geometry = mapped_column(Geometry(geometry_type="LINESTRING", srid=4326), nullable=True)
    start_point = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    end_point = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    weather: Mapped[dict | None] = mapped_column(JSONB)
    memo: Mapped[str | None] = mapped_column(Text)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True)
    shared_to_feed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    photos = relationship("WalkPhoto", back_populates="walk", lazy="selectin")

    __table_args__ = (
        {"comment": "산책 기록"},
    )


class WalkPhoto(Base):
    __tablename__ = "walk_photos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    walk_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("walks.id"), nullable=False)
    photo_url: Mapped[str] = mapped_column(Text, nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    longitude: Mapped[float | None] = mapped_column(Numeric(10, 7))
    taken_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    walk = relationship("Walk", back_populates="photos")

    __table_args__ = (
        {"comment": "산책 중 촬영 사진"},
    )
