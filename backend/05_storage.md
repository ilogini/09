# 05. 파일 저장 (Storage)

> 기준: Cloudflare R2 + 프로토타입 (산책상세.html, 온보딩.html, 메인페이지.html)
> 상위 문서: [BACKEND_PLAN.md](./BACKEND_PLAN.md)

---

## 1. 현재 구현 상태

| 기능 | 엔드포인트 | 상태 |
|------|-----------|------|
| presigned URL 발급 | `GET /upload/presigned` | **TODO** |
| 산책 사진 업로드 | `POST /walks/{id}/photos` | **TODO** |
| 산책 사진 삭제 | `DELETE /walks/{id}/photos/{photo_id}` | **TODO** |

> 전체 신규 개발 필요

---

## 2. 설계 방침

| 항목 | 결정 |
|------|------|
| 저장소 | **Cloudflare R2** (S3 호환) |
| 업로드 방식 | **Presigned URL** (프론트 → R2 직접 업로드, 서버 부하 없음) |
| 리사이징 | **업로드 시 서버에서 처리** (원본 + 썸네일 동시 생성) |
| 라이브러리 | `boto3` (R2 접속), `Pillow` (리사이징) |

---

## 3. 아키텍처

```
[산책 사진 업로드 흐름]

프론트                        서버                         R2
──────                      ──────                       ──────
① GET /upload/presigned →   presigned URL 생성     →     (준비)
   { type: "walk_photo" }     └── 반환: { url, fields, key }

② 사진을 presigned URL로  ─────────────────────────→   원본 저장
   직접 업로드 (서버 안 거침)                              /walks/{walk_id}/orig_{uuid}.jpg

③ POST /walks/{id}/photos →  원본 다운로드
   { photo_url: "...",         ├── Pillow 리사이징  →    썸네일 저장
     lat, lng, taken_at }      │   (300px)                /walks/{walk_id}/thumb_{uuid}.jpg
                                ├── Walk에 photo 레코드 저장
                                └── 반환: WalkPhotoResponse

[펫 프로필 사진]
동일 흐름 — type: "pet_photo" → /pets/{pet_id}/orig_{uuid}.jpg

[경로 이미지 (02_walks에서 생성)]
서버 내부 처리 — staticmap/matplotlib → bytes → R2 직접 업로드
  → /walks/{walk_id}/route_{uuid}.png
  → /walks/{walk_id}/route_thumb_{uuid}.png
```

---

## 4. R2 버킷 구조

```
withbowwow/
├── walks/
│   └── {walk_id}/
│       ├── orig_{uuid}.jpg        # 산책 사진 원본 (1200px)
│       ├── thumb_{uuid}.jpg       # 산책 사진 썸네일 (300px)
│       ├── route_{uuid}.png       # 경로 지도 이미지
│       └── route_thumb_{uuid}.png # 경로 미니멀 이미지
├── pets/
│   └── {pet_id}/
│       ├── orig_{uuid}.jpg        # 펫 프로필 원본
│       └── thumb_{uuid}.jpg       # 펫 프로필 썸네일
└── users/
    └── {user_id}/
        ├── orig_{uuid}.jpg        # 유저 프로필 원본 (향후)
        └── thumb_{uuid}.jpg       # 유저 프로필 썸네일 (향후)
```

---

## 5. API 상세

### 5.1 Presigned URL 발급 — `GET /upload/presigned`

**요청**
```
GET /upload/presigned?type=walk_photo&walk_id=123&ext=jpg
```

| 파라미터 | 필수 | 설명 |
|---------|------|------|
| type | O | `walk_photo`, `pet_photo`, `user_photo` |
| walk_id | 조건부 | type=walk_photo 시 필수 |
| pet_id | 조건부 | type=pet_photo 시 필수 |
| ext | X | 확장자 (기본 `jpg`) |

**응답**
```json
{
  "upload_url": "https://withbowwow.r2.cloudflarestorage.com/...",
  "fields": { ... },
  "key": "walks/123/orig_a1b2c3d4.jpg",
  "public_url": "https://r2-public.withbowwow.com/walks/123/orig_a1b2c3d4.jpg",
  "expires_in": 600
}
```

> presigned URL 유효기간: 10분

### 5.2 산책 사진 등록 — `POST /walks/{id}/photos`

**요청**
```json
{
  "photo_url": "https://r2-public.withbowwow.com/walks/123/orig_a1b2c3d4.jpg",
  "latitude": 37.5642,
  "longitude": 127.0016,
  "taken_at": "2026-02-26T15:35:00Z"
}
```

**서버 처리**
1. photo_url 유효성 확인 (R2 도메인 + 해당 walk 경로인지)
2. 원본 이미지 다운로드
3. Pillow로 썸네일 생성 (300px, JPEG 85%)
4. 썸네일 R2 업로드
5. WalkPhoto 레코드 저장 (photo_url + thumbnail_url)
6. 응답 반환

**응답**: WalkPhotoResponse (201 Created)

### 5.3 산책 사진 삭제 — `DELETE /walks/{id}/photos/{photo_id}`

1. WalkPhoto 레코드 삭제
2. R2에서 원본 + 썸네일 삭제

204 No Content

---

## 6. 이미지 리사이징

### 6.1 사양

| 용도 | 파일명 | 최대 크기 | 품질 | 포맷 |
|------|--------|----------|------|------|
| 원본 | orig_{uuid}.jpg | 1200px (긴 변) | 90% | JPEG |
| 썸네일 | thumb_{uuid}.jpg | 300px (긴 변) | 85% | JPEG |
| 경로 이미지 (지도) | route_{uuid}.png | 600×400px | - | PNG |
| 경로 이미지 (미니멀) | route_thumb_{uuid}.png | 300×300px | - | PNG |

### 6.2 리사이징 코드

```python
from PIL import Image
import io

def resize_image(image_bytes: bytes, max_size: int, quality: int = 85) -> bytes:
    """이미지를 max_size 이하로 리사이징"""
    img = Image.open(io.BytesIO(image_bytes))

    # EXIF 회전 보정
    from PIL import ImageOps
    img = ImageOps.exif_transpose(img)

    # RGB 변환 (PNG→JPEG 대응)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    # 리사이징 (비율 유지)
    ratio = max_size / max(img.size)
    if ratio < 1:
        new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()
```

> **EXIF 회전 보정 필수** — 모바일 사진은 EXIF orientation 태그로 회전 정보 저장. 이거 안 하면 썸네일이 옆으로 누워서 나옴.

---

## 7. R2 연동 (boto3)

### 7.1 클라이언트 설정

```python
import boto3
from app.config import settings

def get_r2_client():
    return boto3.client(
        's3',
        endpoint_url=f'https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com',
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        region_name='auto',
    )
```

### 7.2 Presigned URL 생성

```python
def generate_presigned_url(key: str, content_type: str = 'image/jpeg', expires: int = 600) -> dict:
    client = get_r2_client()
    url = client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': settings.R2_BUCKET_NAME,
            'Key': key,
            'ContentType': content_type,
        },
        ExpiresIn=expires,
    )
    return {
        'upload_url': url,
        'key': key,
        'public_url': f'{settings.R2_PUBLIC_URL}/{key}',
        'expires_in': expires,
    }
```

### 7.3 서버에서 직접 업로드 (경로 이미지용)

```python
def upload_bytes(key: str, data: bytes, content_type: str = 'image/png'):
    client = get_r2_client()
    client.put_object(
        Bucket=settings.R2_BUCKET_NAME,
        Key=key,
        Body=data,
        ContentType=content_type,
    )
    return f'{settings.R2_PUBLIC_URL}/{key}'
```

---

## 8. 서비스 모듈 구조

```
server/app/
├── services/
│   └── storage_service.py   # R2 연동 + presigned URL + 리사이징
├── routers/
│   └── upload.py            # presigned URL 엔드포인트
│   └── walks.py             # (기존) 사진 등록/삭제 추가
├── models/
│   └── walk.py              # (기존) WalkPhoto 모델
└── schemas/
    └── walk.py              # (기존) WalkPhotoResponse
```

---

## 9. 환경변수

| 변수 | 용도 | 상태 |
|------|------|------|
| `R2_ACCOUNT_ID` | R2 계정 ID | config.py에 존재 |
| `R2_ACCESS_KEY_ID` | R2 접근 키 | config.py에 존재 |
| `R2_SECRET_ACCESS_KEY` | R2 비밀 키 | config.py에 존재 |
| `R2_BUCKET_NAME` | 버킷 이름 (기본: withbowwow) | config.py에 존재 |
| `R2_PUBLIC_URL` | 공개 URL 도메인 | config.py에 존재 |

> 추가 환경변수 없음. 기존 설정으로 충분.

---

## 10. 업로드 제한

| 항목 | 값 |
|------|-----|
| 최대 파일 크기 | 10MB |
| 허용 포맷 | JPEG, PNG, HEIC |
| 산책당 최대 사진 수 | 20장 |
| presigned URL 유효기간 | 10분 |

---

## 11. 구현 우선순위

| 순서 | 항목 | 난이도 |
|------|------|--------|
| 1 | storage_service.py (R2 연동 + presigned) | 중간 |
| 2 | 리사이징 함수 (Pillow) | 쉬움 |
| 3 | `GET /upload/presigned` | 쉬움 |
| 4 | `POST /walks/{id}/photos` + 썸네일 생성 | 중간 |
| 5 | 경로 이미지 R2 저장 연동 (02_walks 연결) | 쉬움 |
| 6 | `DELETE /walks/{id}/photos/{photo_id}` | 쉬움 |

---

## 12. 필요 라이브러리

```
boto3          # R2 (S3 호환) 연동
Pillow         # 이미지 리사이징, EXIF 보정
```

---

*작성일: 2026-02-27*
*기준: Cloudflare R2 + boto3 + Pillow*
