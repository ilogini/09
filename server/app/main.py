from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, pets, users, walks


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작
    print(f"[withbowwow] Starting server (env={settings.APP_ENV})")
    yield
    # 서버 종료
    print("[withbowwow] Shutting down")


app = FastAPI(
    title="멍이랑 API",
    description="반려동물 산책 앱 백엔드 API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth.router, prefix="/auth", tags=["인증"])
app.include_router(users.router, prefix="/users", tags=["사용자"])
app.include_router(pets.router, prefix="/pets", tags=["반려동물"])
app.include_router(walks.router, prefix="/walks", tags=["산책"])


@app.get("/", tags=["시스템"])
async def root():
    return {"message": "멍이랑 API", "version": "0.1.0"}


@app.get("/health", tags=["시스템"])
async def health_check():
    return {"status": "ok", "env": settings.APP_ENV}
