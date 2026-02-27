# 외부 API 연동 - 멍이랑 (withbowwow)

> 코어 파일: [00_overview.md](./00_overview.md)
> HTTP 클라이언트: httpx (비동기)
> 캐싱: Redis (1시간)

---

## 1. API 목록

| API | 용도 | 비용 | 호출 빈도 | 캐싱 |
|-----|------|------|----------|------|
| 기상청 단기예보 | 기온, 강수, 하늘 상태 | 무료 | 1시간마다 | Redis 1시간 |
| 에어코리아 | 미세먼지 PM10, PM2.5 | 무료 | 1시간마다 | Redis 1시간 |
| 공공데이터 (동물병원) | 주변 동물병원 정보 | 무료 | 캐시 24시간 | DB 24시간 |
| 공공데이터 (반려동물 공원) | 반려동물 놀이터/공원 | 무료 | 캐시 24시간 | DB 24시간 |
| 카카오 로컬 API | 반려동물 카페, 장소 검색 | 무료 (일 30만건) | 사용자 요청 시 | Redis 1시간 |
| 네이버 지도 API | 지도 표시 (프론트) | 무료 (일 20만건) | 프론트 직접 호출 | - |

---

## 2. 기상청 단기예보 API

### 2.1 엔드포인트

```
GET http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst
```

### 2.2 요청 파라미터

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| serviceKey | `WEATHER_API_KEY` | 인증키 |
| numOfRows | 10 | 응답 개수 |
| pageNo | 1 | 페이지 |
| dataType | JSON | 응답 형식 |
| base_date | 20260212 | 기준 날짜 |
| base_time | 0600 | 기준 시간 |
| nx | 60 | 격자 X |
| ny | 127 | 격자 Y |

### 2.3 응답 파싱

```python
# app/services/weather_service.py
import httpx
from dataclasses import dataclass
from app.config import settings


@dataclass
class WeatherData:
    temp: float       # T1H: 기온 (°C)
    humidity: float   # REH: 습도 (%)
    pty: str          # PTY: 강수형태 (none/rain/snow/rain_snow)
    rn1: float        # RN1: 1시간 강수량 (mm)
    sky: str          # SKY: 하늘상태 (clear/cloudy/overcast)


def parse_weather_response(items: list[dict]) -> WeatherData:
    data = {}
    for item in items:
        data[item["category"]] = item["obsrValue"]

    return WeatherData(
        temp=float(data.get("T1H", 0)),
        humidity=float(data.get("REH", 0)),
        pty=_parse_pty(data.get("PTY", "0")),
        rn1=float(data.get("RN1", 0)),
        sky=_parse_sky(data.get("SKY", "1")),
    )


def _parse_pty(code: str) -> str:
    return {"0": "none", "1": "rain", "2": "rain_snow", "3": "snow"}.get(code, "none")


def _parse_sky(code: str) -> str:
    return {"1": "clear", "3": "cloudy", "4": "overcast"}.get(code, "clear")
```

### 2.4 GPS → 격자 좌표 변환

```python
import math


def lat_lng_to_grid(lat: float, lng: float) -> tuple[int, int]:
    """기상청 API용 Lambert Conformal Conic Projection 변환"""
    RE = 6371.00877
    GRID = 5.0
    SLAT1 = 30.0
    SLAT2 = 60.0
    OLON = 126.0
    OLAT = 38.0
    XO = 43
    YO = 136

    DEGRAD = math.pi / 180.0

    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)

    ra = math.tan(math.pi * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / math.pow(ra, sn)
    theta = lng * DEGRAD - olon
    if theta > math.pi:
        theta -= 2.0 * math.pi
    if theta < -math.pi:
        theta += 2.0 * math.pi
    theta *= sn

    nx = int(ra * math.sin(theta) + XO + 0.5)
    ny = int(ro - ra * math.cos(theta) + YO + 0.5)

    return nx, ny
```

---

## 3. 에어코리아 API

### 3.1 엔드포인트

```
GET http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty
```

### 3.2 응답 파싱

```python
@dataclass
class AirQualityData:
    pm10_value: int      # 미세먼지 (μg/m³)
    pm25_value: int      # 초미세먼지 (μg/m³)
    pm10_grade: str      # good / moderate / bad / very_bad
    pm25_grade: str


def get_air_quality_grade(pm10: int) -> str:
    if pm10 <= 30:
        return "good"
    if pm10 <= 80:
        return "moderate"
    if pm10 <= 150:
        return "bad"
    return "very_bad"
```

---

## 4. 산책 적합도 판정

```python
@dataclass
class WalkSuitability:
    level: str     # optimal / moderate / caution
    message: str
    color: str


def calculate_walk_suitability(
    weather: WeatherData, air: AirQualityData
) -> WalkSuitability:
    # 주의 조건
    if (
        weather.pty != "none"
        or air.pm10_value > 80
        or weather.temp < 0
        or weather.temp > 35
    ):
        return WalkSuitability(
            level="caution",
            message=_get_caution_message(weather, air),
            color="#EF4444",
        )

    # 최적 조건
    if (
        weather.sky == "clear"
        and air.pm10_value <= 30
        and 10 <= weather.temp <= 25
    ):
        return WalkSuitability(
            level="optimal",
            message="산책하기 좋은 날이에요!",
            color="#10B981",
        )

    # 보통
    return WalkSuitability(
        level="moderate",
        message="산책 가능하지만 날씨를 확인하세요",
        color="#F59E0B",
    )
```

---

## 5. 공공데이터 API

### 5.1 동물병원 현황

```
GET http://apis.data.go.kr/1543061/animalHospitalSrvc/animalHospital
```

- 응답: 병원명, 주소, 전화번호, 위경도
- 캐싱: DB 테이블에 24시간 주기 동기화

### 5.2 반려동물 놀이터

```
GET http://apis.data.go.kr/...  (반려동물 놀이터 API)
```

- 응답: 공원명, 주소, 시설 정보, 위경도
- 캐싱: DB 테이블에 24시간 주기 동기화

---

## 6. 카카오 로컬 API

### 6.1 키워드 장소 검색

```
GET https://dapi.kakao.com/v2/local/search/keyword.json
Authorization: KakaoAK {KAKAO_REST_API_KEY}
```

| 파라미터 | 예시 | 설명 |
|---------|------|------|
| query | "반려동물 카페" | 검색어 |
| x | 127.0 | 경도 |
| y | 37.5 | 위도 |
| radius | 2000 | 반경 (m) |
| category_group_code | CE7 | 카페 카테고리 |

### 6.2 역지오코딩 (좌표 → 주소)

```
GET https://dapi.kakao.com/v2/local/geo/coord2regioncode.json
```

- 용도: GPS 좌표 → 행정구역명 (시/구/동) 변환
- 사용 시점: 사용자 지역 자동 설정, 랭킹 지역 분류

---

## 7. 캐싱 전략

### 7.1 weather_service (APScheduler로 1시간마다 실행)

```python
# app/services/weather_service.py
import redis.asyncio as redis

GRID_POINTS = [
    {"name": "강남구", "nx": 61, "ny": 126},
    {"name": "성동구", "nx": 60, "ny": 127},
    # ...
]


async def cache_weather():
    """1시간마다 실행: 주요 지역 날씨 + 미세먼지 캐싱"""
    r = redis.from_url(settings.REDIS_URL)

    async with httpx.AsyncClient() as client:
        for point in GRID_POINTS:
            # 기상청 API 호출
            weather = await _fetch_weather(client, point["nx"], point["ny"])
            # 에어코리아 API 호출
            air = await _fetch_air_quality(client, point["name"])
            # 산책 적합도 계산
            suitability = calculate_walk_suitability(weather, air)

            # Redis에 캐싱 (TTL 1시간)
            cache_data = {
                "weather": weather.__dict__,
                "air_quality": air.__dict__,
                "suitability": suitability.__dict__,
                "cached_at": datetime.utcnow().isoformat(),
            }
            await r.set(
                f"weather:{point['name']}",
                json.dumps(cache_data, ensure_ascii=False),
                ex=3600,
            )

    await r.aclose()
```

### 7.2 API 라우터

```python
# app/routers/weather.py

@router.get("/weather")
async def get_weather(
    region: str,
    current_user: User = Depends(get_current_user),
):
    """Redis 캐시에서 날씨 데이터 조회"""
    r = redis.from_url(settings.REDIS_URL)
    cached = await r.get(f"weather:{region}")
    await r.aclose()

    if cached:
        return json.loads(cached)

    raise HTTPException(status_code=404, detail="Weather data not available")
```

---

*작성일: 2026-02-12*
*버전: 2.0 — httpx + Redis 캐싱으로 전환*
