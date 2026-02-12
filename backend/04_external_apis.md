# 외부 API 연동 - 멍이랑 (withbowwow)

> 코어 파일: [00_overview.md](./00_overview.md)

---

## 1. API 목록

| API | 용도 | 비용 | 호출 빈도 | 캐싱 |
|-----|------|------|----------|------|
| 기상청 단기예보 | 기온, 강수, 하늘 상태 | 무료 | 1시간마다 | 1시간 |
| 에어코리아 | 미세먼지 PM10, PM2.5 | 무료 | 1시간마다 | 1시간 |
| 공공데이터 (동물병원) | 주변 동물병원 정보 | 무료 | 캐시 24시간 | 24시간 |
| 공공데이터 (반려동물 공원) | 반려동물 놀이터/공원 | 무료 | 캐시 24시간 | 24시간 |
| 카카오 로컬 API | 반려동물 카페, 장소 검색 | 무료 (일 30만건) | 사용자 요청 시 | 1시간 |
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

```typescript
interface WeatherData {
  temp: number;       // T1H: 기온 (°C)
  humidity: number;   // REH: 습도 (%)
  pty: string;        // PTY: 강수형태 (0:없음, 1:비, 2:비/눈, 3:눈)
  rn1: number;        // RN1: 1시간 강수량 (mm)
  sky: string;        // SKY: 하늘상태 (1:맑음, 3:구름많음, 4:흐림)
}

function parseWeatherResponse(items: any[]): WeatherData {
  const map: Record<string, any> = {};
  for (const item of items) {
    map[item.category] = item.obsrValue;
  }
  return {
    temp: parseFloat(map.T1H),
    humidity: parseFloat(map.REH),
    pty: parsePTY(map.PTY),
    rn1: parseFloat(map.RN1),
    sky: parseSKY(map.SKY),
  };
}
```

### 2.4 GPS → 격자 좌표 변환

기상청 API는 위경도가 아닌 격자 좌표를 사용하므로 변환 필요:

```typescript
// Lambert Conformal Conic Projection 변환
function latLngToGrid(lat: number, lng: number): { nx: number; ny: number } {
  // 기상청 제공 변환 로직 사용
  // 상세 구현은 기상청 좌표 변환 가이드 참고
  const RE = 6371.00877;
  const GRID = 5.0;
  const SLAT1 = 30.0;
  const SLAT2 = 60.0;
  const OLON = 126.0;
  const OLAT = 38.0;
  const XO = 43;
  const YO = 136;
  // ... (변환 계산)
  return { nx, ny };
}
```

---

## 3. 에어코리아 API

### 3.1 엔드포인트

```
GET http://apis.data.go.kr/B552584/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty
```

### 3.2 응답 파싱

```typescript
interface AirQualityData {
  pm10Value: number;    // 미세먼지 (μg/m³)
  pm25Value: number;    // 초미세먼지 (μg/m³)
  pm10Grade: string;    // 좋음/보통/나쁨/매우나쁨
  pm25Grade: string;
}

function getAirQualityGrade(pm10: number): string {
  if (pm10 <= 30) return 'good';      // 좋음
  if (pm10 <= 80) return 'moderate';   // 보통
  if (pm10 <= 150) return 'bad';       // 나쁨
  return 'very_bad';                    // 매우나쁨
}
```

---

## 4. 산책 적합도 판정

```typescript
interface WalkSuitability {
  level: 'optimal' | 'moderate' | 'caution';
  message: string;
  color: string;
}

function calculateWalkSuitability(
  weather: WeatherData,
  air: AirQualityData
): WalkSuitability {
  // 주의 조건
  if (
    weather.pty !== 'none' ||                    // 비/눈
    air.pm10Value > 80 ||                        // 미세먼지 나쁨
    weather.temp < 0 || weather.temp > 35        // 극한 기온
  ) {
    return {
      level: 'caution',
      message: getCautionMessage(weather, air),
      color: '#EF4444',
    };
  }

  // 최적 조건
  if (
    weather.sky === 'clear' &&
    air.pm10Value <= 30 &&
    weather.temp >= 10 && weather.temp <= 25
  ) {
    return {
      level: 'optimal',
      message: '산책하기 좋은 날이에요!',
      color: '#10B981',
    };
  }

  // 보통
  return {
    level: 'moderate',
    message: '산책 가능하지만 날씨를 확인하세요',
    color: '#F59E0B',
  };
}
```

---

## 5. 공공데이터 API

### 5.1 동물병원 현황

```
GET http://apis.data.go.kr/1543061/animalHospitalSrvc/animalHospital
```

- 응답: 병원명, 주소, 전화번호, 위경도
- 캐싱: 24시간 (변동 적음)
- 저장: Supabase DB에 주기적 동기화

### 5.2 반려동물 놀이터

```
GET http://apis.data.go.kr/...  (반려동물 놀이터 API)
```

- 응답: 공원명, 주소, 시설 정보, 위경도
- 캐싱: 24시간

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

### 7.1 weather-cache Edge Function

```typescript
// 1시간마다 실행되는 날씨 캐시 함수
// Supabase DB의 weather_cache 테이블에 저장

// 주요 격자 좌표 (서울 주요 구 기준)
const GRID_POINTS = [
  { name: '강남구', nx: 61, ny: 126 },
  { name: '성동구', nx: 60, ny: 127 },
  // ...
];

async function cacheWeather() {
  for (const point of GRID_POINTS) {
    const weather = await fetchWeatherAPI(point.nx, point.ny);
    const air = await fetchAirQualityAPI(point.name);

    await supabase.from('weather_cache').upsert({
      region: point.name,
      weather_data: weather,
      air_quality_data: air,
      cached_at: new Date().toISOString(),
    });
  }
}
```

### 7.2 캐시 테이블

```sql
CREATE TABLE weather_cache (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  region TEXT UNIQUE NOT NULL,
  weather_data JSONB,
  air_quality_data JSONB,
  suitability JSONB,
  cached_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

*작성일: 2026-02-12*
*버전: 1.0*
