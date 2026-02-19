from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    DEBUG: bool = True
    CORS_ORIGINS: str = "*"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/withbowwow"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Social Login
    KAKAO_CLIENT_ID: str = ""
    KAKAO_CLIENT_SECRET: str = ""
    NAVER_CLIENT_ID: str = ""
    NAVER_CLIENT_SECRET: str = ""
    APPLE_CLIENT_ID: str = ""
    APPLE_TEAM_ID: str = ""
    APPLE_KEY_ID: str = ""
    APPLE_PRIVATE_KEY: str = ""

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # External APIs
    WEATHER_API_KEY: str = ""
    AIR_KOREA_API_KEY: str = ""
    PUBLIC_DATA_API_KEY: str = ""
    KAKAO_REST_API_KEY: str = ""

    # Firebase
    FIREBASE_CREDENTIALS_JSON: str = ""

    # Payment
    TOSS_CLIENT_KEY: str = ""
    TOSS_SECRET_KEY: str = ""

    # Storage (Cloudflare R2)
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = "withbowwow"
    R2_PUBLIC_URL: str = ""

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
