from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str | None] = mapped_column(Text)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)  # kakao, naver, apple
    provider_id: Mapped[str] = mapped_column(String(100), nullable=False)
    nickname: Mapped[str] = mapped_column(String(30), nullable=False)
    profile_photo_url: Mapped[str | None] = mapped_column(Text)
    region_sido: Mapped[str | None] = mapped_column(String(20))
    region_sigungu: Mapped[str | None] = mapped_column(String(20))
    region_dong: Mapped[str | None] = mapped_column(String(20))
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    premium_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    weekly_goal_km: Mapped[float | None] = mapped_column(default=20.0)
    walk_unit: Mapped[str] = mapped_column(String(5), default="km")
    notification_settings: Mapped[dict | None] = mapped_column(JSONB, default={})
    hashed_refresh_token: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    pets = relationship("Pet", back_populates="owner", lazy="selectin")

    __table_args__ = (
        {"comment": "사용자 계정"},
    )
