# 파일 저장소 - 멍이랑 (withbowwow)

> 코어 파일: [00_overview.md](./00_overview.md)
> 스토리지: Cloudflare R2 (S3 호환)
> SDK: boto3 (Python)

---

## 1. Cloudflare R2 구성

### 1.1 왜 R2인가

| 항목 | Cloudflare R2 | AWS S3 | Render Disk |
|------|-------------|--------|-------------|
| 무료 용량 | 10GB | 5GB (12개월) | 1GB |
| 이그레스 | 무료 | 유료 ($0.09/GB) | N/A |
| S3 호환 | O | 기본 | X |
| CDN | Cloudflare 내장 | CloudFront 별도 | X |
| 비용 (10GB+) | $0.015/GB/월 | $0.023/GB/월 | N/A |

### 1.2 버킷 구조

| 폴더 경로 | 용도 | 접근 권한 | 파일 크기 제한 |
|----------|------|----------|--------------|
| `pet-profiles/` | 반려동물 프로필 사진 | Public (읽기), Auth (쓰기) | 5MB |
| `walk-photos/` | 산책 중 촬영 사진 | Public (읽기), Auth (쓰기) | 10MB |
| `share-cards/` | 공유 카드 이미지 | Public (읽기), Auth (쓰기) | 5MB |

### 1.3 디렉토리 구조

```
withbowwow/                          ← R2 버킷
  ├── pet-profiles/
  │   └── {user_id}/
  │       └── {pet_id}/
  │           ├── profile.jpg         ← 대표 프로필 사진
  │           └── profile_thumb.jpg   ← 썸네일 (200x200)
  │
  ├── walk-photos/
  │   └── {user_id}/
  │       └── {walk_id}/
  │           ├── photo_001.jpg       ← 원본
  │           ├── photo_001_thumb.jpg ← 썸네일 (400x400)
  │           └── photo_002.jpg
  │
  └── share-cards/
      └── {user_id}/
          └── {walk_id}/
              └── share_card.png      ← 공유용 카드 이미지
```

---

## 2. R2 클라이언트 설정

```python
# app/services/storage_service.py
import boto3
from botocore.config import Config
from app.config import settings


def get_r2_client():
    """Cloudflare R2 S3 호환 클라이언트"""
    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )
```

---

## 3. 업로드 플로우

### 3.1 반려동물 프로필 사진

```python
# app/routers/upload.py
from fastapi import APIRouter, UploadFile, File, Depends
from PIL import Image
import io

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/pet-profile/{pet_id}")
async def upload_pet_profile(
    pet_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 1. 권한 확인
    pet = await db.get(Pet, pet_id)
    if not pet or pet.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your pet")

    # 2. 이미지 리사이즈 (서버 사이드)
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))
    image.thumbnail((800, 800))

    # 원본 저장
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=80)
    buffer.seek(0)

    # 썸네일 생성
    thumb = image.copy()
    thumb.thumbnail((200, 200))
    thumb_buffer = io.BytesIO()
    thumb.save(thumb_buffer, format="JPEG", quality=70)
    thumb_buffer.seek(0)

    # 3. R2 업로드
    s3 = get_r2_client()
    file_path = f"pet-profiles/{current_user.id}/{pet_id}/profile.jpg"
    thumb_path = f"pet-profiles/{current_user.id}/{pet_id}/profile_thumb.jpg"

    s3.upload_fileobj(buffer, settings.R2_BUCKET_NAME, file_path, ExtraArgs={"ContentType": "image/jpeg"})
    s3.upload_fileobj(thumb_buffer, settings.R2_BUCKET_NAME, thumb_path, ExtraArgs={"ContentType": "image/jpeg"})

    # 4. Public URL 생성
    public_url = f"{settings.R2_PUBLIC_URL}/{file_path}"

    # 5. pets 테이블 업데이트
    pet.photo_url = public_url
    await db.commit()

    return {"photo_url": public_url}
```

### 3.2 산책 사진

```python
@router.post("/walk-photo/{walk_id}")
async def upload_walk_photo(
    walk_id: str,
    file: UploadFile = File(...),
    lat: float = 0,
    lng: float = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 1. 권한 확인
    walk = await db.get(Walk, walk_id)
    if not walk or walk.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your walk")

    # 2. 이미지 리사이즈
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))
    image.thumbnail((1200, 1200))

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=70)
    buffer.seek(0)

    # 3. R2 업로드
    import time
    s3 = get_r2_client()
    file_name = f"photo_{int(time.time())}.jpg"
    file_path = f"walk-photos/{current_user.id}/{walk_id}/{file_name}"

    s3.upload_fileobj(buffer, settings.R2_BUCKET_NAME, file_path, ExtraArgs={"ContentType": "image/jpeg"})

    public_url = f"{settings.R2_PUBLIC_URL}/{file_path}"

    # 4. walk_photos 테이블에 기록
    from geoalchemy2.elements import WKTElement
    walk_photo = WalkPhoto(
        walk_id=walk_id,
        photo_url=public_url,
        location=WKTElement(f"POINT({lng} {lat})", srid=4326) if lat and lng else None,
    )
    db.add(walk_photo)
    await db.commit()

    return {"photo_url": public_url}
```

---

## 4. 이미지 처리

### 4.1 리사이즈 전략

| 용도 | 원본 | 표시용 | 썸네일 |
|------|------|--------|--------|
| 프로필 사진 | 최대 800px | 200x200 (원형 크롭) | 100x100 |
| 산책 사진 | 최대 1200px | 피드: 600px 폭 | 400x400 |
| 공유 카드 | 1080x1920 (Instagram Story) | - | - |

### 4.2 Pillow로 서버 사이드 처리

```python
from PIL import Image
import io


def resize_image(image_bytes: bytes, max_size: int, quality: int = 80) -> bytes:
    """이미지를 최대 크기로 리사이즈"""
    image = Image.open(io.BytesIO(image_bytes))
    image.thumbnail((max_size, max_size))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality)
    buffer.seek(0)
    return buffer.getvalue()


def create_thumbnail(image_bytes: bytes, size: int = 200) -> bytes:
    """정사각형 썸네일 생성"""
    image = Image.open(io.BytesIO(image_bytes))
    image.thumbnail((size, size))
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=70)
    buffer.seek(0)
    return buffer.getvalue()
```

---

## 5. 접근 제어

R2는 퍼블릭 버킷으로 설정하되, 업로드는 반드시 FastAPI 서버를 거치도록 한다.

```
읽기: R2 Public URL 직접 접근 (CDN 캐싱)
쓰기: FastAPI 엔드포인트 → JWT 인증 → R2 업로드 (서버 사이드)
삭제: FastAPI 엔드포인트 → JWT 인증 → R2 삭제 (서버 사이드)
```

> 클라이언트가 R2에 직접 업로드하지 않는다. 모든 파일 업로드는 서버에서 검증 후 처리.

---

## 6. 용량 관리

### 6.1 R2 요금

| 항목 | 무료 | 유료 |
|------|------|------|
| 스토리지 | 10GB | $0.015/GB/월 |
| Class A (쓰기) | 100만 요청/월 | $4.50/100만 |
| Class B (읽기) | 1,000만 요청/월 | $0.36/100만 |
| 이그레스 | 무료 | 무료 |

### 6.2 예상 용량 (MAU 10,000 기준)

| 항목 | 평균 | 월간 예상 |
|------|------|----------|
| 프로필 사진 | 200KB x 1.5 펫/유저 | 3GB |
| 산책 사진 | 300KB x 2장/산책 x 3회/주 | 72GB |
| 공유 카드 | 150KB x 1장/산책 | 18GB |

> MAU 10,000 시점에서 ~93GB → R2 비용: ~$1.4/월

### 6.3 정리 정책

- 30일 이상 접근하지 않은 공유 카드: 삭제
- 계정 삭제 시: 관련 파일 전체 삭제 (30일 유예 후)
- 원본 사진은 영구 보존, 썸네일은 재생성 가능

---

*작성일: 2026-02-12*
*버전: 2.0 — Cloudflare R2 + boto3로 전환*
