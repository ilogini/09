# 04. 지도 / 장소 검색

> 기준: 프로토타입 (지도.html, 메인페이지.html) + 카카오 로컬 API
> 상위 문서: [BACKEND_PLAN.md](./BACKEND_PLAN.md)

---

## 1. 현재 구현 상태

| 기능 | 엔드포인트 | 상태 |
|------|-----------|------|
| 주변 장소 검색 | `GET /places/nearby` | **TODO** |
| 장소 키워드 검색 | `GET /places/search` | **TODO** |
| 장소 상세 | `GET /places/{id}` | **TODO** |
| 즐겨찾기 등록 | `POST /places/favorites` | **TODO** |
| 즐겨찾기 목록 | `GET /places/favorites` | **TODO** |
| 즐겨찾기 삭제 | `DELETE /places/favorites/{id}` | **TODO** |

> 전체 신규 개발 필요

---

## 2. 설계 방침

| 항목 | 결정 |
|------|------|
| 외부 API | **카카오 로컬 API** (키워드 검색 + 카테고리 검색) |
| 데이터 방식 | **실시간 외부 호출 + Redis 캐싱** (자체 DB에 장소 저장 안 함) |
| DB 저장 대상 | **즐겨찾기만** (유저별, kakao place_id 참조) |
| API 호출 방식 | **서버 경유** (API 키 보호, 캐싱, 응답 가공) |

---

## 3. 아키텍처

```
프론트                        서버                         외부
──────                      ──────                       ──────
GET /places/nearby    →     place_service.py      →     카카오 로컬 API
  { lat, lng, type }          │                           (키워드/카테고리 검색)
                               ├── Redis 캐시 확인
                               │     ├── HIT → 캐시 반환
                               │     └── MISS → 카카오 호출 → 캐시 저장
                               ├── 응답 가공 (필요 필드만)
                               ├── 즐겨찾기 여부 합침
                               └── 반환
```

---

## 4. 장소 카테고리

| 카테고리 | 앱 표시명 | 카카오 카테고리 코드 | 검색 키워드 |
|---------|----------|-------------------|-----------|
| hospital | 동물병원 | `HP8` (병원) | "동물병원" |
| salon | 애견미용 | - | "애견미용", "펫미용" |
| cafe | 애견카페 | `CE7` (카페) | "애견카페", "펫카페" |
| park | 공원/놀이터 | - | "반려동물 공원", "애견 놀이터" |
| pharmacy | 동물약국 | `PM9` (약국) | "동물약국" |
| shop | 펫샵 | - | "펫샵", "애견용품" |

> 카카오 카테고리 코드가 있는 것은 **카테고리 검색**, 없는 것은 **키워드 검색** 사용
> 카테고리는 서버에서 관리 → 추후 추가/변경 시 앱 업데이트 불필요

---

## 5. 카카오 로컬 API 사용

### 5.1 카테고리로 장소 검색

```
GET https://dapi.kakao.com/v2/local/search/category.json
  ?category_group_code=HP8
  &x=127.0016        (경도)
  &y=37.5642         (위도)
  &radius=3000        (반경 3km)
  &sort=distance
  &size=15
Headers:
  Authorization: KakaoAK {REST_API_KEY}
```

### 5.2 키워드로 장소 검색

```
GET https://dapi.kakao.com/v2/local/search/keyword.json
  ?query=애견미용
  &x=127.0016
  &y=37.5642
  &radius=3000
  &sort=distance
  &size=15
Headers:
  Authorization: KakaoAK {REST_API_KEY}
```

### 5.3 카카오 응답 → 서버 가공

카카오 원본 응답:
```json
{
  "documents": [
    {
      "id": "12345678",
      "place_name": "해피 동물병원",
      "category_group_code": "HP8",
      "category_group_name": "병원",
      "phone": "02-123-4567",
      "address_name": "서울 관악구 봉천동 123",
      "road_address_name": "서울 관악구 봉천로 45",
      "x": "126.9512",
      "y": "37.4813",
      "distance": "450"
    }
  ],
  "meta": { "total_count": 12, "is_end": false }
}
```

서버 가공 후 응답:
```json
{
  "id": "kakao_12345678",
  "name": "해피 동물병원",
  "category": "hospital",
  "phone": "02-123-4567",
  "address": "서울 관악구 봉천로 45",
  "lat": 37.4813,
  "lng": 126.9512,
  "distance_m": 450,
  "is_favorite": false
}
```

> 프론트에게는 깔끔하게 정제된 데이터만 전달

---

## 6. API 상세

### 6.1 주변 장소 — `GET /places/nearby`

**요청**
```
GET /places/nearby?lat=37.5642&lng=127.0016&type=hospital&radius=3000
```

| 파라미터 | 필수 | 기본값 | 설명 |
|---------|------|--------|------|
| lat | O | - | 위도 |
| lng | O | - | 경도 |
| type | X | all | 카테고리 (`hospital`, `salon`, `cafe`, `park`, `pharmacy`, `shop`, `all`) |
| radius | X | 3000 | 반경 (미터, 최대 5000) |
| size | X | 15 | 결과 수 (최대 45) |

**응답**
```json
{
  "items": [
    {
      "id": "kakao_12345678",
      "name": "해피 동물병원",
      "category": "hospital",
      "phone": "02-123-4567",
      "address": "서울 관악구 봉천로 45",
      "lat": 37.4813,
      "lng": 126.9512,
      "distance_m": 450,
      "is_favorite": false
    }
  ],
  "total": 12,
  "type": "hospital"
}
```

**서버 처리 흐름**
1. `type`에 따라 카카오 API 호출 방식 결정 (카테고리 or 키워드)
2. `type=all`이면 모든 카테고리 병렬 호출
3. Redis 캐시 키: `places:{type}:{lat_3자리}:{lng_3자리}:{radius}`
4. 캐시 TTL: 10분
5. 사용자 즐겨찾기 목록 조회 → `is_favorite` 플래그 합침
6. 거리순 정렬 후 반환

### 6.2 키워드 검색 — `GET /places/search`

**요청**
```
GET /places/search?q=애견카페&lat=37.5642&lng=127.0016
```

| 파라미터 | 필수 | 기본값 | 설명 |
|---------|------|--------|------|
| q | O | - | 검색 키워드 |
| lat | X | - | 내 위치 (거리순 정렬용) |
| lng | X | - | 내 위치 |
| size | X | 15 | 결과 수 |

**응답**: nearby와 동일 형식

### 6.3 즐겨찾기 등록 — `POST /places/favorites`

**요청**
```json
{
  "kakao_place_id": "12345678",
  "name": "해피 동물병원",
  "category": "hospital",
  "lat": 37.4813,
  "lng": 126.9512,
  "address": "서울 관악구 봉천로 45"
}
```

> 카카오에서 받은 장소 정보를 그대로 저장 (즐겨찾기 시점의 스냅샷)

### 6.4 즐겨찾기 목록 — `GET /places/favorites`

**응답**
```json
{
  "items": [
    {
      "id": 1,
      "kakao_place_id": "12345678",
      "name": "해피 동물병원",
      "category": "hospital",
      "lat": 37.4813,
      "lng": 126.9512,
      "address": "서울 관악구 봉천로 45",
      "created_at": "2026-02-26T10:00:00Z"
    }
  ]
}
```

### 6.5 즐겨찾기 삭제 — `DELETE /places/favorites/{id}`

204 No Content

---

## 7. DB 테이블

> 장소 자체는 저장하지 않음. 즐겨찾기만 저장.

### place_favorites

| 필드 | 타입 | 설명 |
|------|------|------|
| id | BigInteger PK | |
| user_id | BigInteger FK | 사용자 |
| kakao_place_id | String(20) | 카카오 장소 ID |
| name | String(100) | 장소명 (스냅샷) |
| category | String(20) | 카테고리 |
| lat | Numeric(10,7) | 위도 |
| lng | Numeric(10,7) | 경도 |
| address | Text | 주소 |
| created_at | DateTime | 등록일 |

> UNIQUE(user_id, kakao_place_id) — 같은 장소 중복 즐겨찾기 방지

---

## 8. Redis 캐싱 전략

```python
# 캐시 키 예시
# 소수점 3자리까지 = 약 100m 범위 동일 취급
cache_key = f"places:hospital:37.564:127.002:3000"
TTL = 600  # 10분
```

| 상황 | 처리 |
|------|------|
| 같은 위치에서 10분 내 재검색 | Redis에서 즉시 반환 |
| 위치가 100m 이상 이동 | 캐시 키 달라짐 → 카카오 새로 호출 |
| 10분 경과 | TTL 만료 → 카카오 새로 호출 |

---

## 9. 서비스 모듈 구조

```
server/app/
├── services/
│   └── place_service.py     # 카카오 API 호출 + 캐싱 + 응답 가공
├── routers/
│   └── places.py            # API 엔드포인트
├── models/
│   └── place_favorite.py    # 즐겨찾기 모델
└── schemas/
    └── place.py             # 요청/응답 스키마
```

### place_service.py 핵심 로직

```python
class PlaceService:
    CATEGORY_MAP = {
        "hospital": {"code": "HP8", "keywords": ["동물병원"]},
        "salon":    {"code": None,  "keywords": ["애견미용", "펫미용"]},
        "cafe":     {"code": "CE7", "keywords": ["애견카페", "펫카페"]},
        "park":     {"code": None,  "keywords": ["반려동물 공원", "애견 놀이터"]},
        "pharmacy": {"code": "PM9", "keywords": ["동물약국"]},
        "shop":     {"code": None,  "keywords": ["펫샵", "애견용품"]},
    }

    async def search_nearby(self, lat, lng, type, radius) -> list[dict]:
        # 1. Redis 캐시 확인
        # 2. MISS → 카카오 API 호출 (카테고리 or 키워드)
        # 3. 응답 가공 (통일된 포맷)
        # 4. Redis 저장 (TTL 10분)
        # 5. 즐겨찾기 합침
        # 6. 반환
```

---

## 10. 환경변수

| 변수 | 용도 | 비고 |
|------|------|------|
| `KAKAO_REST_API_KEY` | 카카오 로컬 API 인증 | config.py에 이미 존재 |
| `REDIS_URL` | 캐싱 | config.py에 이미 존재 |

> 추가 환경변수 없음. 기존 설정으로 충분.

---

## 11. 구현 우선순위

| 순서 | 항목 | 난이도 |
|------|------|--------|
| 1 | place_favorite 모델 + 마이그레이션 | 쉬움 |
| 2 | place_service.py (카카오 API 연동) | 중간 |
| 3 | `GET /places/nearby` | 중간 |
| 4 | `GET /places/search` | 쉬움 (nearby 재활용) |
| 5 | 즐겨찾기 CRUD | 쉬움 |
| 6 | Redis 캐싱 적용 | 중간 |

---

## 12. 참고: 카카오 API 제한

| 항목 | 값 |
|------|-----|
| 무료 할당량 | 월 300,000건 |
| 1회 최대 결과 | 45건 (page × size) |
| 반경 최대 | 20,000m (20km) |
| 필요 키 | REST API 키 (카카오 개발자 콘솔) |

> 월 30만 건이면 내부 테스트에 충분. 캐싱 적용 시 실 호출량은 훨씬 적음.

---

*작성일: 2026-02-27*
*기준: 카카오 로컬 API + 프로토타입 지도.html*
