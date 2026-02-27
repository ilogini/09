# 백엔드 환경 세팅 가이드

> 멍이랑 (withbowwow) FastAPI 백엔드 개발 환경 구축
> 최종 업데이트: 2026-02-19

---

## 1. 확정 기술 스택

| 항목 | 선택 | 버전 | 비고 |
|------|------|------|------|
| **Language** | Python | 3.11+ (권장 3.12) | async/await, match/case 지원 |
| **Framework** | FastAPI | 0.115+ | 비동기 API, 자동 Swagger |
| **ORM** | SQLAlchemy | 2.0+ | async 지원, 타입 힌트 |
| **Migration** | Alembic | 1.13+ | 스키마 버전 관리 |
| **Database** | PostgreSQL | 15+ | PostGIS 확장 필수 |
| **Geo** | GeoAlchemy2 | 0.14+ | PostGIS ORM 바인딩 |
| **Auth** | python-jose | 3.3+ | JWT 발급/검증 |
| **HTTP Client** | httpx | 0.27+ | 비동기 외부 API 호출 |
| **Cache** | Redis | 7+ | 날씨 캐시, 빈도 제한 |
| **Push** | firebase-admin | 6.4+ | FCM/APNs |
| **Scheduler** | APScheduler | 3.10+ | 주기 작업 (랭킹, 날씨) |
| **Storage** | Cloudflare R2 + boto3 | - | S3 호환 파일 저장소 |
| **Deploy** | Render | - | Free → Starter $7/월 |
| **Validation** | Pydantic | v2.6+ | 요청/응답 스키마 |
| **Image** | Pillow | 10.2+ | 서버사이드 이미지 리사이징 |

---

## 2. 로컬 개발 환경 요구사항

### 2.1 필수 소프트웨어

```
# 시스템 요구사항
- Python 3.11 이상 (3.12 권장)
- PostgreSQL 15+ (PostGIS 확장 포함)
- Redis 7+
- Git 2.40+

# Windows 추가
- Visual Studio Build Tools (C 확장 컴파일용)
- PostgreSQL은 pgAdmin 포함 설치 권장

# macOS 추가
- Homebrew 통해 설치 권장
- Xcode Command Line Tools
```

### 2.2 설치 가이드

#### Python (pyenv 사용 권장)

```bash
# Windows (PowerShell) — pyenv-win
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
pyenv install 3.12.8
pyenv global 3.12.8

# macOS
brew install pyenv
pyenv install 3.12.8
pyenv global 3.12.8

# 설치 확인
python --version   # Python 3.12.8
```

#### PostgreSQL + PostGIS

```bash
# Windows — 공식 인스톨러 사용
# https://www.postgresql.org/download/windows/
# 설치 후 Stack Builder에서 PostGIS 추가 설치

# macOS
brew install postgresql@15 postgis

# PostgreSQL 서비스 시작
# Windows: services.msc에서 PostgreSQL 시작
# macOS: brew services start postgresql@15

# DB 생성
psql -U postgres
CREATE DATABASE withbowwow;
\c withbowwow
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;   -- 검색 최적화용
```

#### Redis

```bash
# Windows — WSL2 사용 권장 (Redis 공식 Windows 미지원)
wsl --install
# WSL 내에서:
sudo apt update && sudo apt install redis-server
sudo service redis-server start

# Windows 대안 — Memurai (Redis 호환)
# https://www.memurai.com/

# macOS
brew install redis
brew services start redis

# 연결 확인
redis-cli ping    # PONG
```

---

## 3. 프로젝트 초기화

### 3.1 디렉토리 구조 생성

```bash
# 프로젝트 루트에서
mkdir -p backend-app
cd backend-app

# 가상 환경 생성
python -m venv .venv

# 가상 환경 활성화
# Windows (Git Bash)
source .venv/Scripts/activate
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

# pip 업그레이드
pip install --upgrade pip
```

### 3.2 의존성 설치

```bash
# requirements.txt 기반 설치
pip install -r requirements.txt

# 또는 개별 설치
pip install "fastapi[standard]>=0.115.0"
pip install "uvicorn[standard]>=0.27.0"
pip install "sqlalchemy[asyncio]>=2.0.0"
pip install "asyncpg>=0.29.0"
pip install "alembic>=1.13.0"
pip install "geoalchemy2>=0.14.0"
pip install "pydantic>=2.6.0"
pip install "pydantic-settings>=2.1.0"
pip install "python-jose[cryptography]>=3.3.0"
pip install "passlib[bcrypt]>=1.7.4"
pip install "httpx>=0.27.0"
pip install "firebase-admin>=6.4.0"
pip install "apscheduler>=3.10.0"
pip install "redis>=5.0.0"
pip install "boto3>=1.34.0"
pip install "python-multipart>=0.0.9"
pip install "pillow>=10.2.0"

# 개발용 추가 패키지
pip install pytest pytest-asyncio httpx  # 테스트
pip install ruff                         # 린트 + 포맷
pip install pre-commit                   # Git 훅
```

### 3.3 requirements.txt

```
# === Core ===
fastapi[standard]>=0.115.0
uvicorn[standard]>=0.27.0
pydantic>=2.6.0
pydantic-settings>=2.1.0

# === Database ===
sqlalchemy[asyncio]>=2.0.0
asyncpg>=0.29.0
alembic>=1.13.0
geoalchemy2>=0.14.0

# === Auth ===
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# === HTTP / External API ===
httpx>=0.27.0

# === Push Notification ===
firebase-admin>=6.4.0

# === Scheduler ===
apscheduler>=3.10.0

# === Cache ===
redis>=5.0.0

# === Storage ===
boto3>=1.34.0

# === Utilities ===
python-multipart>=0.0.9
pillow>=10.2.0

# === Dev Only ===
pytest>=8.0.0
pytest-asyncio>=0.23.0
ruff>=0.3.0
pre-commit>=3.6.0
```

---

## 4. Alembic 마이그레이션 설정

### 4.1 초기화

```bash
# Alembic 초기화 (async 지원)
alembic init -t async alembic
```

### 4.2 alembic.ini 수정

```ini
# alembic.ini
[alembic]
script_location = alembic

# DB URL은 env.py에서 환경 변수로 주입
# sqlalchemy.url = (비워둠)
```

### 4.3 alembic/env.py 수정

```python
# alembic/env.py
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import settings
from app.database import Base
# 모든 모델을 import해야 Alembic이 인식
from app.models import user, pet, walk, badge, ranking, social, notification, subscription

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
```

### 4.4 마이그레이션 명령

```bash
# 마이그레이션 파일 자동 생성
alembic revision --autogenerate -m "initial schema"

# 마이그레이션 적용
alembic upgrade head

# 마이그레이션 되돌리기
alembic downgrade -1

# 현재 상태 확인
alembic current
```

---

## 5. 핵심 설정 파일

### 5.1 app/config.py

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET_KEY: str
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

    # App
    APP_ENV: str = "development"  # development | staging | production
    DEBUG: bool = True
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

### 5.2 app/database.py

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=5,          # Free tier 적합
    max_overflow=10,
    pool_pre_ping=True,   # 끊어진 연결 자동 복구
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 5.3 app/main.py

```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 시작 시 — APScheduler, Redis 연결 등
    print("Starting up...")
    # scheduler.start()
    yield
    # 서버 종료 시 — 리소스 정리
    print("Shutting down...")
    # scheduler.shutdown()


app = FastAPI(
    title="멍이랑 API",
    description="반려동물 산책 앱 백엔드",
    version="0.1.0",
    docs_url="/docs",
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
# from app.routers import auth, users, pets, walks, badges, rankings
# app.include_router(auth.router, prefix="/auth", tags=["auth"])
# app.include_router(users.router, prefix="/users", tags=["users"])
# ...


@app.get("/health")
async def health_check():
    return {"status": "ok", "env": settings.APP_ENV}
```

---

## 6. 환경 변수 (.env)

### 6.1 로컬 개발용 .env 템플릿

```env
# === App ===
APP_ENV=development
DEBUG=true
CORS_ORIGINS=*

# === Database ===
# Windows 로컬
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/withbowwow
# macOS 로컬 (기본 유저)
# DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/withbowwow

# === JWT ===
JWT_SECRET_KEY=local-dev-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# === Social Login (개발 시에는 빈 값 가능) ===
KAKAO_CLIENT_ID=
KAKAO_CLIENT_SECRET=
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
APPLE_CLIENT_ID=
APPLE_TEAM_ID=
APPLE_KEY_ID=
APPLE_PRIVATE_KEY=

# === Redis ===
REDIS_URL=redis://localhost:6379

# === External APIs (공공데이터 포털에서 발급) ===
WEATHER_API_KEY=
AIR_KOREA_API_KEY=
PUBLIC_DATA_API_KEY=
KAKAO_REST_API_KEY=

# === Firebase (JSON을 Base64 인코딩) ===
FIREBASE_CREDENTIALS_JSON=

# === Payment ===
TOSS_CLIENT_KEY=
TOSS_SECRET_KEY=

# === Storage (Cloudflare R2) ===
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=withbowwow-dev
R2_PUBLIC_URL=
```

### 6.2 환경별 차이

| 항목 | development | staging | production |
|------|-------------|---------|------------|
| DEBUG | true | false | false |
| CORS_ORIGINS | * | 프론트 URL | 프론트 URL |
| DB | 로컬 PostgreSQL | Render PostgreSQL | Render PostgreSQL |
| Redis | 로컬 | Render Redis | Render Redis |
| JWT_SECRET_KEY | 아무 값 | 랜덤 생성 | 랜덤 생성 |
| R2_BUCKET | withbowwow-dev | withbowwow-staging | withbowwow |

---

## 7. 로컬 개발 서버 실행

### 7.1 기본 실행

```bash
# 가상 환경 활성화 후
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 또는 (FastAPI CLI)
fastapi dev app/main.py --port 8000
```

### 7.2 확인

```
API 서버:     http://localhost:8000
Swagger UI:   http://localhost:8000/docs
ReDoc:        http://localhost:8000/redoc
Health Check: http://localhost:8000/health
```

### 7.3 모바일 기기에서 로컬 서버 접속

앱 개발 시 모바일 기기에서 로컬 백엔드에 접속해야 합니다:

```bash
# 같은 Wi-Fi 네트워크에서 PC의 로컬 IP 확인
# Windows
ipconfig   # IPv4 주소 확인 (예: 192.168.0.10)

# macOS
ifconfig | grep "inet "   # en0 인터페이스의 IP

# 프론트엔드 .env에 설정
EXPO_PUBLIC_API_URL=http://192.168.0.10:8000
```

> **주의**: Windows 방화벽에서 8000 포트를 허용해야 할 수 있습니다.

---

## 8. Docker 설정 (배포용)

### 8.1 Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 시스템 패키지 (PostGIS 클라이언트, Pillow 의존성)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libgeos-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드
COPY . .

# 포트
EXPOSE 8000

# 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 8.2 .dockerignore

```
.venv/
__pycache__/
*.pyc
.env
.git/
alembic/versions/__pycache__/
.pytest_cache/
```

### 8.3 로컬 Docker 테스트

```bash
# 빌드
docker build -t withbowwow-api .

# 실행 (.env 파일 사용)
docker run --env-file .env -p 8000:8000 withbowwow-api
```

---

## 9. Render 배포 설정

### 9.1 render.yaml

```yaml
services:
  - type: web
    name: withbowwow-api
    runtime: docker
    repo: https://github.com/ilogini/withBowwow
    branch: main
    rootDir: backend-app
    dockerfilePath: ./Dockerfile
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: withbowwow-db
          property: connectionString
      - key: REDIS_URL
        fromService:
          name: withbowwow-redis
          type: redis
          property: connectionString
      - key: APP_ENV
        value: production
      - key: DEBUG
        value: "false"
      - key: JWT_SECRET_KEY
        generateValue: true
      # 나머지 환경 변수는 Render 대시보드에서 직접 설정

databases:
  - name: withbowwow-db
    plan: free
    databaseName: withbowwow
    postgresMajorVersion: "15"
    ipAllowList: []
```

### 9.2 배포 프로세스

```
1. GitHub main 브랜치에 push
2. Render가 자동 감지 → Docker 빌드 → 배포
3. 배포 완료 후 https://withbowwow-api.onrender.com/docs 확인
```

### 9.3 Render 무료 티어 제약사항

| 항목 | 제약 |
|------|------|
| 슬립 | 15분 비활동 시 슬립 (첫 요청 시 ~30초 콜드스타트) |
| DB | PostgreSQL Free: 256MB, 97일 후 자동 삭제 |
| Redis | Free: 25MB |
| 빌드 | 월 750시간 (1개 서비스 상시 운영 가능) |

> **테스트 기간에는 Free tier로 충분**합니다.
> 서비스 슬립을 방지하려면 Starter ($7/월)로 업그레이드하거나,
> 외부 모니터링(UptimeRobot 등)으로 주기적 ping을 보내는 방법도 있습니다.

---

## 10. 개발 워크플로우

### 10.1 일상 개발 사이클

```
1. 가상 환경 활성화
2. uvicorn app.main:app --reload 실행
3. 코드 수정 → 자동 리로드
4. http://localhost:8000/docs 에서 API 테스트
5. DB 스키마 변경 시: alembic revision --autogenerate -m "설명" → alembic upgrade head
```

### 10.2 테스트 실행

```bash
# 전체 테스트
pytest

# 특정 파일
pytest tests/test_walks.py

# 비동기 테스트 (pytest-asyncio)
pytest tests/test_auth.py -v
```

### 10.3 코드 품질

```bash
# 린트 + 자동 수정
ruff check --fix .

# 포맷팅
ruff format .
```

### 10.4 Git 브랜치 전략

```
main         ← 프로덕션 (Render 자동 배포)
├── develop  ← 개발 통합 브랜치
│   ├── feature/auth       ← 인증 기능
│   ├── feature/walks      ← 산책 기능
│   └── feature/badges     ← 뱃지 기능
└── hotfix/  ← 긴급 수정
```

---

## 11. 프론트엔드 ↔ 백엔드 연동 체크리스트

프론트/백엔드 개발자 간 협업 시 확인 사항:

| # | 항목 | 설명 |
|---|------|------|
| 1 | Swagger UI 공유 | 프론트 개발자가 `/docs`에서 API 명세 확인 |
| 2 | CORS 설정 | 프론트 도메인/IP를 `CORS_ORIGINS`에 추가 |
| 3 | JWT 토큰 형식 | `Authorization: Bearer {token}` 헤더 규약 |
| 4 | 에러 응답 형식 | `{"detail": "에러 메시지"}` 통일 |
| 5 | 파일 업로드 | `multipart/form-data`, 최대 10MB |
| 6 | WebSocket URL | `ws://{host}/ws/walk-together/{id}?token={jwt}` |
| 7 | 날짜 형식 | ISO 8601 (`2026-02-19T09:00:00Z`) |
| 8 | 페이지네이션 | `?page=1&size=20` → `{ items: [], total: 100 }` |
| 9 | 환경별 API URL | 로컬/스테이징/프로덕션 URL 공유 |

---

## 12. API 키 발급 필요 목록

| 서비스 | 발급처 | 용도 | 비용 |
|--------|--------|------|------|
| 기상청 API | [공공데이터 포털](https://www.data.go.kr/) | 날씨 정보 | 무료 |
| 에어코리아 API | [공공데이터 포털](https://www.data.go.kr/) | 미세먼지 | 무료 |
| 동물병원 API | [공공데이터 포털](https://www.data.go.kr/) | 주변 병원 | 무료 |
| 카카오 REST API | [Kakao Developers](https://developers.kakao.com/) | 장소 검색, 로그인 | 무료 |
| 네이버 로그인 | [Naver Developers](https://developers.naver.com/) | 소셜 로그인 | 무료 |
| Apple 로그인 | Apple Developer Portal | 소셜 로그인 | 개발자 계정 필요 |
| Firebase | [Firebase Console](https://console.firebase.google.com/) | 푸시 알림 | 무료 (Spark) |
| Toss Payments | [Toss Payments](https://www.tosspayments.com/) | 결제 | 수수료 3.3% |
| Cloudflare R2 | [Cloudflare Dashboard](https://dash.cloudflare.com/) | 파일 저장소 | 무료 10GB |

---

*작성일: 2026-02-19*
*버전: 1.0*
