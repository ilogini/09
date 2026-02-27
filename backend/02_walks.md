# 02. 산책 시스템

> 기준: server/app/routers/walks.py, models/walk.py + 프로토타입 (메인페이지.html, 산책기록.html, 산책상세.html)
> 상위 문서: [BACKEND_PLAN.md](./BACKEND_PLAN.md)

---

## 1. 현재 구현 상태

| 기능 | 엔드포인트 | 상태 |
|------|-----------|------|
| 산책 시작 | `POST /walks` | **완료** |
| 산책 완료 | `POST /walks/{id}/complete` | **완료** |
| 산책 목록 | `GET /walks` | **완료** (기간 필터 추가 필요) |
| 산책 상세 | `GET /walks/{id}` | **완료** |
| 산책 삭제 | `DELETE /walks/{id}` | **완료** |
| 주간 요약 | `GET /walks/weekly-summary` | **TODO (신규)** |
| 누적 통계 | `GET /walks/stats` | **TODO (신규)** |
| 경로 이미지 생성 | 산책 완료 시 자동 생성 | **TODO (신규)** |
| 사진 업로드 | `POST /walks/{id}/photos` | **TODO** |

---

## 2. 산책 라이프사이클

```
[1. 산책 시작]
  프론트: POST /walks { pet_id, started_at }
  서버: Walk 레코드 생성 (ended_at=NULL)
  프론트: walk_id 수신, GPS 트래킹 시작
    │
[2. 산책 중 — GPS 트래킹 (프론트 전용)]
  매 3~5초: GPS 좌표 수집 → 로컬 배열에 저장
  실시간 거리/시간/칼로리 계산 (프론트)
  사진 촬영 시: 로컬 저장 (완료 후 업로드)
    │
[3. 산책 완료]
  프론트: POST /walks/{id}/complete
    { route_geojson, distance_m, duration_sec, ... }
  서버:
    ① Walk 레코드 업데이트
    ② 유효성 검증 (속도/거리)
    ③ 좌표 필터링 + 경로 이미지 생성 (비동기)
    ④ route_image_url 저장
    ⑤ 응답 반환
    │
[4. 결과 확인]
  프론트: 산책 상세 화면에 경로 이미지 + 통계 표시
```

---

## 3. GPS 트래킹 데이터

### 3.1 프론트에서 수집하는 데이터

```
매 3~5초마다:
{
  lat: 37.5642,          // 위도
  lng: 127.0016,         // 경도
  timestamp: 1708937405, // Unix timestamp
  speed: 4.2,            // km/h (GPS 센서 제공)
  altitude: 25.3         // 고도 (선택)
}
```

### 3.2 산책 완료 시 서버 전송 형식

```json
{
  "ended_at": "2026-02-26T16:12:00Z",
  "distance_m": 3200,
  "duration_sec": 2520,
  "calories": 165,
  "avg_speed_kmh": 4.6,
  "route_geojson": {
    "type": "Feature",
    "geometry": {
      "type": "LineString",
      "coordinates": [
        [127.0016, 37.5642],
        [127.0020, 37.5645],
        [127.0025, 37.5650]
      ]
    },
    "properties": {
      "timestamps": [1708937405, 1708937410, 1708937415],
      "speeds": [4.2, 4.5, 4.3]
    }
  },
  "memo": "날씨 좋은 산책",
  "shared_to_feed": false
}
```

> GeoJSON 표준: coordinates는 **[경도, 위도]** 순서 (lng, lat)

---

## 4. 경로 이미지 생성

### 4.1 방식: 서버에서 Python 라이브러리로 자체 생성

외부 지도 API 없이, 서버에서 직접 이미지를 만든다.

| 라이브러리 | 용도 | 결과물 |
|-----------|------|--------|
| `staticmap` | 지도 + 경로 이미지 | OSM 지도 위에 경로 폴리라인 |
| `matplotlib` | 경로만 이미지 (미니멀) | 배경 없이 경로 선만 (나이키 스타일) |
| `Pillow` | 이미지 후처리 | 리사이징, 포맷 변환 |

**필요 패키지**: `pip install staticmap matplotlib Pillow`

### 4.2 지도 + 경로 이미지 (staticmap)

```python
from staticmap import StaticMap, Line, CircleMarker
import io

def generate_map_image(coordinates: list[list[float]], width=600, height=400) -> bytes:
    """좌표 리스트로 지도+경로 이미지 생성 (PNG bytes 반환)"""
    m = StaticMap(width, height, padding_x=20, padding_y=20)

    # 경로 폴리라인
    coords_tuple = [(c[0], c[1]) for c in coordinates]  # [lng, lat]
    m.add_line(Line(coords_tuple, '#C5D900', 4))

    # 출발/도착 마커
    m.add_marker(CircleMarker(coords_tuple[0], '#0099FF', 8))   # 출발 (파랑)
    m.add_marker(CircleMarker(coords_tuple[-1], '#EF4444', 8))  # 도착 (빨강)

    image = m.render()  # PIL Image
    buf = io.BytesIO()
    image.save(buf, format='PNG')
    return buf.getvalue()
```

- OSM(OpenStreetMap) 무료 타일 사용
- 자동 줌/센터 계산 → 경로가 지도를 벗어나지 않음
- 별도 API 키 불필요

### 4.3 경로만 이미지 — 미니멀 스타일 (matplotlib)

```python
import matplotlib
matplotlib.use('Agg')  # 서버 환경 (GUI 없음)
import matplotlib.pyplot as plt
import io

def generate_route_only_image(coordinates: list[list[float]], width=600, height=600) -> bytes:
    """지도 없이 경로 선만 그린 이미지 (PNG bytes 반환)"""
    lngs = [c[0] for c in coordinates]
    lats = [c[1] for c in coordinates]

    dpi = 150
    fig, ax = plt.subplots(figsize=(width/dpi, height/dpi), dpi=dpi)

    # 경로 선
    ax.plot(lngs, lats, color='#C5D900', linewidth=3, solid_capstyle='round', solid_joinstyle='round')

    # 출발/도착 마커
    ax.scatter(lngs[0], lats[0], color='#0099FF', s=60, zorder=5, edgecolors='white', linewidths=1.5)
    ax.scatter(lngs[-1], lats[-1], color='#EF4444', s=60, zorder=5, edgecolors='white', linewidths=1.5)

    ax.set_aspect('equal')
    ax.axis('off')
    fig.patch.set_alpha(0)  # 투명 배경

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', transparent=True, pad_inches=0.1)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()
```

### 4.4 이미지 생성 타이밍

```
POST /walks/{id}/complete 처리 흐름:

1. Walk 레코드 업데이트 (즉시)
2. 유효성 검증 (즉시)
3. 응답 반환 (즉시) ← 프론트는 여기서 결과 화면 표시
4. [BackgroundTask] 좌표 필터링 → 이미지 생성 → R2 업로드 → route_image_url 저장
```

FastAPI `BackgroundTasks`로 이미지 생성을 비동기 처리 → 응답 속도에 영향 없음.

프론트는 첫 응답에서 `route_image_url`이 null이면 `route_geojson`으로 직접 지도 렌더링,
이후 조회 시 `route_image_url`이 있으면 이미지 사용.

---

## 5. 좌표 필터링 (이미지 생성 전 정제)

### 5.1 발생하는 문제와 해결

| 문제 | 원인 | 해결 |
|------|------|------|
| GPS 튐 (순간이동) | 건물/터널/고가도로 | 속도 필터 (> 15km/h 제거) |
| 좌표 뭉침 | 실내 진입 시 GPS 정확도 하락 | 최소 거리 필터 (< 1m 중복 제거) |
| 좌표 과다 | 30분 산책 = 약 360~600개 좌표 | Douglas-Peucker 단순화 |

### 5.2 필터링 파이프라인

```python
from math import radians, sin, cos, sqrt, atan2
from shapely.geometry import LineString

def haversine(coord1, coord2) -> float:
    """두 좌표 간 거리 (미터)"""
    lng1, lat1 = coord1
    lng2, lat2 = coord2
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))


def filter_route(coordinates: list[list[float]], interval_sec: float = 5.0) -> list[list[float]]:
    """
    좌표 필터링 파이프라인
    coordinates: [[lng, lat], [lng, lat], ...]
    """
    if len(coordinates) < 2:
        return coordinates

    # ① 속도 필터: GPS 튐 제거 (산책 기준 15km/h 초과 = 비정상)
    speed_filtered = [coordinates[0]]
    for i in range(1, len(coordinates)):
        dist = haversine(speed_filtered[-1], coordinates[i])
        speed_kmh = (dist / 1000) / (interval_sec / 3600)
        if speed_kmh <= 15.0:
            speed_filtered.append(coordinates[i])

    # ② 최소 거리 필터: 1m 이내 중복 제거 (실내 정체)
    dist_filtered = [speed_filtered[0]]
    for coord in speed_filtered[1:]:
        if haversine(dist_filtered[-1], coord) >= 1.0:
            dist_filtered.append(coord)

    # ③ Douglas-Peucker 단순화: 좌표 수 줄이기 (약 10m 오차 허용)
    if len(dist_filtered) >= 3:
        line = LineString(dist_filtered)
        simplified = line.simplify(0.0001)  # 약 10m
        return list(simplified.coords)

    return dist_filtered
```

### 5.3 필터링 결과 예시

```
원본:     600개 좌표 (30분, 5초 간격)
① 속도필터: 585개 (GPS 튐 15개 제거)
② 거리필터: 520개 (실내 정체 65개 제거)
③ 단순화:   180개 (이미지 렌더링에 충분)
```

---

## 6. Walk 모델 필드

### 현재 모델 (walk.py)

| 필드 | 타입 | 설명 | 상태 |
|------|------|------|------|
| id | BigInteger PK | 산책 ID | 완료 |
| user_id | BigInteger FK | 사용자 | 완료 |
| pet_id | BigInteger FK | 반려동물 (nullable) | 완료 |
| started_at | DateTime | 시작 시각 | 완료 |
| ended_at | DateTime | 종료 시각 | 완료 |
| distance_m | Integer | 거리 (미터) | 완료 |
| duration_sec | Integer | 시간 (초) | 완료 |
| calories | Integer | 칼로리 | 완료 |
| avg_speed_kmh | Numeric(5,2) | 평균 속도 | 완료 |
| route_geojson | JSONB | GeoJSON 경로 데이터 | 완료 |
| route_geometry | Geometry(LINESTRING) | PostGIS 공간 쿼리용 | 완료 |
| start_point | Geometry(POINT) | 출발 좌표 | 완료 |
| end_point | Geometry(POINT) | 도착 좌표 | 완료 |
| weather | JSONB | 날씨 정보 | 완료 |
| memo | Text | 메모 | 완료 |
| is_valid | Boolean | 유효성 | 완료 |
| shared_to_feed | Boolean | 피드 공유 여부 | 완료 |
| created_at | DateTime | 생성일 | 완료 |
| **route_image_url** | **Text** | **경로 지도 이미지 URL** | **추가 필요** |
| **route_thumbnail_url** | **Text** | **경로만 이미지 URL (미니멀)** | **추가 필요** |

### 추가 필요 필드

```python
# Walk 모델에 추가
route_image_url: Mapped[str | None] = mapped_column(Text)       # 지도+경로 이미지
route_thumbnail_url: Mapped[str | None] = mapped_column(Text)   # 경로만 이미지 (미니멀)
```

```python
# WalkResponse 스키마에 추가
route_image_url: str | None = None
route_thumbnail_url: str | None = None
```

---

## 7. 유효성 검증

### 현재 구현 (walks.py)

```python
MAX_SPEED_KMH = 15   # 평균 시속 15km 초과 → 부정행위 (자전거/차량 의심)
MIN_DISTANCE_M = 100  # 100m 미만 → 무효 (의미 없는 산책)
```

- `is_valid = False`인 산책은 랭킹/뱃지 집계에서 제외
- 프론트에서는 표시하되 "유효하지 않은 산책" 라벨 처리

---

## 8. TODO API 상세

### 8.1 주간 요약 — `GET /walks/weekly-summary`

**용도**: 메인페이지 주간 요약 카드

**응답**
```json
{
  "week_start": "2026-02-24",
  "week_end": "2026-03-02",
  "total_distance_m": 18500,
  "total_count": 5,
  "total_duration_sec": 7200,
  "total_calories": 850,
  "goal_km": 20.0,
  "goal_progress": 0.925
}
```

**로직**
- 현재 주(월~일) 기준으로 완료된 산책 집계
- `goal_km`은 `users.weekly_goal_km` (기본 20km)
- `goal_progress` = `total_distance_m / 1000 / goal_km`

### 8.2 누적 통계 — `GET /walks/stats`

**용도**: 산책기록 페이지 상단, 마이페이지 통계

**응답**
```json
{
  "total_count": 187,
  "total_distance_m": 312400,
  "total_duration_sec": 339120,
  "total_calories": 17200,
  "longest_distance_m": 8500,
  "longest_duration_sec": 5400,
  "first_walk_date": "2026-01-15",
  "streak_days": 3
}
```

### 8.3 산책 목록 기간 필터 — `GET /walks?period=weekly`

**현재**: page/size만 지원
**추가**: `period` 파라미터

| period | 범위 |
|--------|------|
| `weekly` | 이번 주 (월~일) |
| `monthly` | 이번 달 |
| `yearly` | 올해 |
| 미지정 | 전체 (현재 동작 유지) |

---

## 9. 필요 라이브러리 추가

```
# requirements.txt 또는 pip install
staticmap      # 지도+경로 이미지 생성 (OSM 타일)
matplotlib     # 경로만 이미지 생성 (미니멀)
shapely        # 좌표 필터링 (Douglas-Peucker)
```

---

## 10. 구현 우선순위

| 순서 | 항목 | 난이도 |
|------|------|--------|
| 1 | Walk 모델에 `route_image_url` 필드 추가 | 쉬움 |
| 2 | 좌표 필터링 함수 (`filter_route`) | 중간 |
| 3 | 경로 이미지 생성 서비스 (`staticmap` + `matplotlib`) | 중간 |
| 4 | 산책 완료 시 BackgroundTask로 이미지 생성 연동 | 중간 |
| 5 | `GET /walks/weekly-summary` API | 쉬움 |
| 6 | `GET /walks/stats` API | 쉬움 |
| 7 | `GET /walks` 기간 필터 추가 | 쉬움 |
| 8 | 사진 업로드 (`POST /walks/{id}/photos`) | R2 연동 필요 |

---

*작성일: 2026-02-26*
*기준: server/app/routers/walks.py, models/walk.py 실제 구현 코드*
