# 13. 날씨 / 미세먼지 / 산책 추천

> 기준: 프로토타입 (메인페이지.html 상단 날씨 위젯)
> 상위 문서: [BACKEND_PLAN.md](./BACKEND_PLAN.md)

---

## 0. 핵심 요약

| 항목 | 내용 |
|------|------|
| **날씨 API** | 기상청 단기예보 (공공데이터포털, 무료) |
| **미세먼지 API** | 에어코리아 (공공데이터포털, 무료) |
| **산책 추천** | 온도 + 습도 + 미세먼지 + 강수 조합 → 4단계 판정 |
| **캐싱** | Redis, 1시간 갱신 |
| **표시 위치** | 메인페이지 상단 |

---

## 1. 외부 API

### 1.1 기상청 단기예보 API

| 항목 | 내용 |
|------|------|
| 출처 | [공공데이터포털](https://www.data.go.kr/data/15084084/openapi.do) |
| 엔드포인트 | `http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst` |
| 인증 | 서비스키 (API Key) |
| 제공 데이터 | 기온(T1H), 습도(REH), 강수형태(PTY), 풍속(WSD), 하늘상태(SKY) |
| 호출 제한 | 일 10,000회 (무료) |
| 좌표계 | 격자 좌표 (nx, ny) — 위경도 변환 필요 |

```python
# 위경도 → 기상청 격자 좌표 변환
def latlon_to_grid(lat: float, lon: float) -> tuple[int, int]:
    """위경도를 기상청 격자 좌표로 변환 (Lambert Conformal Conic)"""
    import math
    RE = 6371.00877  # 지구 반경 (km)
    GRID = 5.0       # 격자 간격 (km)
    SLAT1 = 30.0     # 표준 위도 1
    SLAT2 = 60.0     # 표준 위도 2
    OLON = 126.0     # 기준점 경도
    OLAT = 38.0      # 기준점 위도
    XO = 43          # 기준점 X좌표
    YO = 136         # 기준점 Y좌표

    DEGRAD = math.pi / 180.0
    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD

    sn = math.log(math.cos(slat1) / math.cos(slat2)) / \
         math.log(math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5))
    sf = (math.tan(math.pi * 0.25 + slat1 * 0.5) ** sn) * math.cos(slat1) / sn
    ro = re * sf / (math.tan(math.pi * 0.25 + olat * 0.5) ** sn)

    ra = re * sf / (math.tan(math.pi * 0.25 + lat * DEGRAD * 0.5) ** sn)
    theta = lon * DEGRAD - olon
    if theta > math.pi: theta -= 2.0 * math.pi
    if theta < -math.pi: theta += 2.0 * math.pi
    theta *= sn

    nx = int(ra * math.sin(theta) + XO + 0.5)
    ny = int(ro - ra * math.cos(theta) + YO + 0.5)
    return nx, ny
```

### 1.2 에어코리아 미세먼지 API

| 항목 | 내용 |
|------|------|
| 출처 | [공공데이터포털](https://www.data.go.kr/data/15073861/openapi.do) |
| 엔드포인트 | `http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty` |
| 인증 | 서비스키 (API Key) |
| 제공 데이터 | PM10, PM2.5, 통합대기환경지수(CAI) |
| 호출 제한 | 일 10,000회 (무료) |
| 조회 기준 | 측정소명 (가장 가까운 측정소) |

```python
# 위경도 → 가장 가까운 측정소 찾기
# 에어코리아 측정소 목록 API: getNearbyMsrstnList
# params: tmX(TM좌표X), tmY(TM좌표Y)
```

---

## 2. 산책 추천 기준

### 2.1 참고 기준

| 출처 | 기준 |
|------|------|
| 수의사 권장 | 강아지 산책 적정 온도 15~25°C |
| Rover.com | 열지수: 온도(°F) + 습도(%) ≥ 150이면 위험 |
| 환경부 | PM2.5 4단계 (좋음/보통/나쁨/매우나쁨) |
| 핏펫 | 30°C 이상 열사병 위험, 7°C 이하 소형견 주의 |

### 2.2 산책 추천 4단계

| 등급 | 라벨 | 색상 | 설명 |
|------|------|------|------|
| **1** | 최고 | 🟢 green | 산책하기 딱 좋아요! |
| **2** | 좋음 | 🔵 blue | 산책 가능, 약간 주의 |
| **3** | 주의 | 🟡 yellow | 짧게 산책하세요 |
| **4** | 위험 | 🔴 red | 오늘은 실내 놀이 추천 |

### 2.3 판정 로직

4개 항목을 각각 점수화 → 최저 점수(가장 나쁜 조건)가 최종 등급.

#### 온도 점수

| 온도 (°C) | 점수 | 판정 |
|-----------|------|------|
| 15 ~ 25 | 1 (최고) | 산책 최적 |
| 10 ~ 14 또는 26 ~ 29 | 2 (좋음) | 약간 춥거나 더움 |
| 5 ~ 9 또는 30 ~ 32 | 3 (주의) | 소형견 주의, 열사병 주의 |
| 4 이하 또는 33 이상 | 4 (위험) | 동상/열사병 위험 |

#### 습도 점수 (온도와 결합)

| 열지수 계산 | 점수 |
|------------|------|
| 온도(°F) + 습도(%) < 120 | 1 |
| 120 ~ 139 | 2 |
| 140 ~ 149 | 3 |
| 150 이상 | 4 |

> 열지수 공식: `temp_f + humidity` (Rover.com 기준)
> `temp_f = temp_c × 1.8 + 32`

#### 미세먼지 점수 (PM2.5)

| PM2.5 (μg/m³) | 환경부 등급 | 점수 |
|---------------|-----------|------|
| 0 ~ 15 | 좋음 | 1 |
| 16 ~ 35 | 보통 | 2 |
| 36 ~ 75 | 나쁨 | 3 |
| 76 이상 | 매우나쁨 | 4 |

#### 강수 점수

| 상태 | 점수 |
|------|------|
| 맑음 / 구름 | 1 |
| 비 예보 (30% 이상) | 3 |
| 현재 비/눈 | 4 |

### 2.4 최종 판정

```python
def calculate_walk_score(temp_c: float, humidity: int, pm25: int, precipitation: int) -> dict:
    """산책 추천 점수 계산"""

    # 온도 점수
    if 15 <= temp_c <= 25:
        temp_score = 1
    elif 10 <= temp_c <= 14 or 26 <= temp_c <= 29:
        temp_score = 2
    elif 5 <= temp_c <= 9 or 30 <= temp_c <= 32:
        temp_score = 3
    else:
        temp_score = 4

    # 열지수 점수 (여름철 보정)
    temp_f = temp_c * 1.8 + 32
    heat_index = temp_f + humidity
    if heat_index < 120:
        heat_score = 1
    elif heat_index < 140:
        heat_score = 2
    elif heat_index < 150:
        heat_score = 3
    else:
        heat_score = 4

    # 미세먼지 점수
    if pm25 <= 15:
        dust_score = 1
    elif pm25 <= 35:
        dust_score = 2
    elif pm25 <= 75:
        dust_score = 3
    else:
        dust_score = 4

    # 강수 점수
    # precipitation: 기상청 PTY (0=없음, 1=비, 2=비/눈, 3=눈, 5=빗방울, 6=빗방울눈날림, 7=눈날림)
    if precipitation == 0:
        rain_score = 1
    elif precipitation in (5, 7):  # 빗방울, 눈날림 (약함)
        rain_score = 3
    else:
        rain_score = 4

    # 최종 = 가장 나쁜 점수
    final_score = max(temp_score, heat_score, dust_score, rain_score)

    labels = {1: '최고', 2: '좋음', 3: '주의', 4: '위험'}
    messages = {
        1: '산책하기 딱 좋은 날씨예요! 🐾',
        2: '산책 가능해요, 약간만 주의하세요',
        3: '짧게 산책하고 빨리 들어오세요',
        4: '오늘은 실내 놀이를 추천해요 🏠',
    }

    return {
        'score': final_score,
        'label': labels[final_score],
        'message': messages[final_score],
        'details': {
            'temp_score': temp_score,
            'heat_score': heat_score,
            'dust_score': dust_score,
            'rain_score': rain_score,
        }
    }
```

---

## 3. API

### `GET /weather`

**요청**
```
GET /weather?lat=37.5665&lng=126.9780
```

| 파라미터 | 필수 | 설명 |
|---------|------|------|
| lat | O | 위도 |
| lng | O | 경도 |

**응답**
```json
{
  "weather": {
    "temperature": 18,
    "humidity": 55,
    "sky": "맑음",
    "precipitation": 0,
    "wind_speed": 2.1
  },
  "air_quality": {
    "pm10": 42,
    "pm25": 22,
    "pm25_grade": "보통",
    "station_name": "종로구"
  },
  "walk_recommendation": {
    "score": 2,
    "label": "좋음",
    "message": "산책 가능해요, 약간만 주의하세요",
    "details": {
      "temp_score": 1,
      "heat_score": 1,
      "dust_score": 2,
      "rain_score": 1
    }
  },
  "cached_at": "2026-03-04T14:00:00+09:00",
  "next_refresh": "2026-03-04T15:00:00+09:00"
}
```

---

## 4. Redis 캐싱

### 4.1 캐시 전략

| 항목 | 키 패턴 | TTL |
|------|--------|-----|
| 날씨 | `weather:{nx}:{ny}` | 1시간 |
| 미세먼지 | `air:{station_name}` | 1시간 |
| 산책 점수 | `walk_score:{nx}:{ny}` | 1시간 |

> 격자 좌표 기준 캐싱 → 같은 동네 유저는 캐시 공유
> 기상청 격자 1칸 = 약 5km × 5km

### 4.2 캐시 흐름

```
GET /weather?lat=37.5665&lng=126.9780
  → 격자 변환: (60, 127)
  → Redis 조회: weather:60:127
  → HIT → 즉시 반환
  → MISS → 기상청 API + 에어코리아 API 호출
         → 산책 점수 계산
         → Redis 저장 (TTL 1시간)
         → 응답 반환
```

---

## 5. 서비스 구조

```python
class WeatherService:

    async def get_weather(self, lat: float, lng: float) -> dict:
        """날씨 + 미세먼지 + 산책 추천 통합 조회"""
        nx, ny = latlon_to_grid(lat, lng)
        cache_key = f"weather:{nx}:{ny}"

        # 1. 캐시 확인
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)

        # 2. 기상청 API 호출
        weather = await self._fetch_weather(nx, ny)

        # 3. 에어코리아 API 호출
        station = await self._find_nearest_station(lat, lng)
        air = await self._fetch_air_quality(station)

        # 4. 산책 점수 계산
        recommendation = calculate_walk_score(
            temp_c=weather['temperature'],
            humidity=weather['humidity'],
            pm25=air['pm25'],
            precipitation=weather['precipitation'],
        )

        # 5. 응답 조합 + 캐시 저장
        result = {
            'weather': weather,
            'air_quality': air,
            'walk_recommendation': recommendation,
            'cached_at': datetime.now(KST).isoformat(),
            'next_refresh': (datetime.now(KST) + timedelta(hours=1)).isoformat(),
        }

        await redis.set(cache_key, json.dumps(result), ex=3600)
        return result
```

---

## 6. 서비스 모듈 구조

```
server/app/
├── services/
│   └── weather_service.py    # 기상청 + 에어코리아 + 산책 점수
├── routers/
│   └── weather.py            # GET /weather
├── schemas/
│   └── weather.py            # 응답 스키마
└── utils/
    └── grid_converter.py     # 위경도 → 격자 변환
```

---

## 7. 환경변수

| 변수 | 용도 | 비고 |
|------|------|------|
| `KMA_API_KEY` | 기상청 API 서비스키 | [공공데이터포털](https://www.data.go.kr) 발급 |
| `AIRKOREA_API_KEY` | 에어코리아 API 서비스키 | 동일 포털 발급 |
| `REDIS_URL` | 캐시 | 기존 |

---

## 8. 구현 우선순위

| 순서 | 항목 | 난이도 |
|------|------|--------|
| 1 | 격자 좌표 변환 유틸 | 쉬움 |
| 2 | 기상청 API 연동 + 파싱 | 중간 |
| 3 | 에어코리아 API 연동 + 파싱 | 중간 |
| 4 | 산책 추천 점수 계산 로직 | 쉬움 |
| 5 | Redis 캐싱 (1시간) | 쉬움 |
| 6 | `GET /weather` API | 쉬움 |

---

## 9. 기상청 API 응답 파싱 참고

기상청 초단기예보 카테고리:

| 카테고리 | 설명 | 단위 |
|---------|------|------|
| T1H | 기온 | °C |
| RN1 | 1시간 강수량 | mm |
| SKY | 하늘상태 | 1=맑음, 3=구름많음, 4=흐림 |
| UUU | 동서바람 | m/s |
| VVV | 남북바람 | m/s |
| REH | 습도 | % |
| PTY | 강수형태 | 0=없음, 1=비, 2=비/눈, 3=눈, 5=빗방울, 6=빗방울눈날림, 7=눈날림 |
| LGT | 낙뢰 | kA |
| VEC | 풍향 | deg |
| WSD | 풍속 | m/s |

---

*작성일: 2026-03-04*
*기준: 기상청 단기예보 + 에어코리아 + 강아지 산책 안전 기준 종합*
*산책 추천 점수: 수의사 권장 온도(핏펫) + 열지수(Rover) + 환경부 PM2.5 기준*
