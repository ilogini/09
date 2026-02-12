# 멍이랑 (withBowwow) 디자인 시스템 가이드

> 컨셉3: **시원하고 청량한 맑은날의 산책**
> #Refreshing #Vivid #Transparent #Airy

---

## 1. 컬러 시스템

### 1-1. 브랜드 컬러

| 이름 | HEX | 용도 |
|------|-----|------|
| **Lime Punch** | `#C5D900` | Primary - 주요 액센트, CTA, 활성 상태 |
| **Lime Dark** | `#9FB300` | Primary Dark - 텍스트 강조, 아이콘 활성 |
| **Azure** | `#0099FF` | Secondary - 보조 액센트, 링크, 정보 강조 |
| **Azure Dark** | `#0077CC` | Secondary Dark - 날씨, 거리 텍스트 |

### 1-2. 텍스트 컬러

| 이름 | HEX | 용도 |
|------|-----|------|
| **Text Primary** | `#1A2B3C` | 제목, 본문 텍스트 |
| **Text Secondary** | `#5C6F82` | 부가 텍스트, 아이콘 기본색 |
| **Text Muted** | `#94A3B8` | 힌트, 라벨, 비활성 텍스트 |

### 1-3. 배경 컬러

| 이름 | 값 | 용도 |
|------|---|------|
| **BG Base** | `#F8FCFA` | 앱 전체 배경 |
| **BG White** | `#FFFFFF` | 카드, 콘텐츠 영역 |
| **Glass BG** | `rgba(255,255,255,0.65)` | 글래스모피즘 카드 |
| **Glass BG Heavy** | `rgba(255,255,255,0.80)` | 헤더, 네비게이션, 패널 |
| **Glass Border** | `rgba(197,217,0,0.12)` | 글래스 카드 테두리 |

### 1-4. 투명도 변형 (Alpha Variants)

| 이름 | 값 | 용도 |
|------|---|------|
| **Lime Light** | `rgba(197,217,0,0.10)` | 아이콘 배경, 선택 하이라이트 |
| **Lime Glow** | `rgba(197,217,0,0.25)` | 그림자, 발광 효과 |
| **Azure Light** | `rgba(0,153,255,0.08)` | 정보 배경, 뱃지 배경 |
| **Azure Glow** | `rgba(0,153,255,0.20)` | 호버 그림자 |

### 1-5. 시맨틱 컬러

| 이름 | HEX | 용도 |
|------|-----|------|
| **Danger** | `#EF4444` | 삭제, 중지, 에러 |
| **Warning** | `#F59E0B` | 일시정지, 주의 |
| **Purple** | `#8B5CF6` | 시간 관련, 특별 챌린지 |
| **Gold** | `#D4A017` | 1등 랭킹 |
| **Silver** | `#8A9BAE` | 2등 랭킹 |
| **Bronze** | `#C8763E` | 3등 랭킹 |

### 1-6. CSS 변수

```css
:root {
    /* Brand */
    --lime: #C5D900;
    --lime-dark: #9FB300;
    --lime-light: rgba(197, 217, 0, 0.10);
    --lime-glow: rgba(197, 217, 0, 0.25);
    --azure: #0099FF;
    --azure-dark: #0077CC;
    --azure-light: rgba(0, 153, 255, 0.08);
    --azure-glow: rgba(0, 153, 255, 0.20);

    /* Text */
    --text-primary: #1A2B3C;
    --text-secondary: #5C6F82;
    --text-muted: #94A3B8;

    /* Background */
    --bg-base: #F8FCFA;
    --bg-white: #FFFFFF;

    /* Glass */
    --glass-bg: rgba(255, 255, 255, 0.65);
    --glass-bg-heavy: rgba(255, 255, 255, 0.80);
    --glass-border: rgba(197, 217, 0, 0.12);
    --glass-blur: blur(20px);

    /* Semantic */
    --danger: #EF4444;
}
```

---

## 2. 타이포그래피

### 2-1. 서체

| 우선순위 | 서체 | 비고 |
|---------|------|------|
| 1 | **Pretendard Variable** | 메인 서체 (CDN) |
| 2 | Pretendard | Fallback |
| 3 | -apple-system | iOS |
| 4 | BlinkMacSystemFont | macOS Chrome |
| 5 | system-ui, sans-serif | 시스템 기본 |

```css
font-family: 'Pretendard Variable', 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
```

### 2-2. 폰트 스케일

| 토큰 | 크기 | Weight | 용도 | 예시 |
|------|------|--------|------|------|
| **Display** | 52px | 300 (Light) | 산책 타이머 | `00:12:34` |
| **Hero** | 36px | 200 (Thin) | 날씨 온도 | `12°` |
| **Heading 1** | 26px | 700 (Bold) | 주간 통계 수치 | `12.5km` |
| **Heading 2** | 22px | 700 (Bold) | 결과 수치, 통계값 | `3.2 km` |
| **Heading 3** | 19px | 300/700 | 로고 텍스트 | **멍이**랑 |
| **Heading 4** | 18px | 700 | 랭킹 순위 번호 | `1`, `2` |
| **Title** | 16px | 600 | 섹션 제목, 버튼 텍스트 | 산책 시작하기 |
| **Subtitle** | 15px | 600 | 카드 헤더, 랭킹 거리 | 이번 주 산책 |
| **Body 1** | 14px | 600 | 카드 이름, 장소명 | 초코, 보라매공원 |
| **Body 2** | 13px | 500/600 | 탭, 챌린지 제목, 배너 | 주간, 7일 연속 산책 |
| **Caption 1** | 12px | 400~600 | 프로그레스 라벨, 부가정보 | 주간 목표 20km |
| **Caption 2** | 11px | 400~500 | 품종, 상세정보, 뱃지 | 골든 리트리버 · 3살 |
| **Tiny** | 10px | 500~600 | 네비 라벨, 단위, AD태그 | 홈, kcal, /월 |
| **Micro** | 9px | 600 | AD 태그 | AD |

### 2-3. letter-spacing

| 용도 | 값 |
|------|---|
| 타이머 숫자 | `3px` |
| 온도 숫자 | `-1px` |
| 통계 수치 | `-0.5px` |
| 로고 | `-0.3px` |

### 2-4. 숫자 전용

```css
font-variant-numeric: tabular-nums;  /* 타이머, 거리, 통계에 적용 */
```

---

## 3. 레이아웃 시스템

### 3-1. 앱 프레임

| 속성 | 값 |
|------|---|
| 최대 너비 | `480px` |
| 좌우 마진 | `auto` (중앙 정렬) |
| 좌우 패딩 | `16px` (콘텐츠), `20px` (헤더) |

### 3-2. 고정 영역

| 요소 | 높이 | 위치 |
|------|------|------|
| **Header** | `58px` | `sticky top: 0` / `z-index: 100` |
| **Bottom Nav** | `76px` | `fixed bottom: 0` / `z-index: 200` |
| **Walk Screen** | 전체화면 | `fixed inset: 0` / `z-index: 300` |
| **Result Modal** | 바텀시트 | `fixed inset: 0` / `z-index: 400` |
| **Toast** | auto | `fixed bottom: 92px` / `z-index: 500` |

### 3-3. 간격 체계

| 토큰 | 값 | 용도 |
|------|---|------|
| **xs** | `2~4px` | 텍스트 간격, 미세 간격 |
| **sm** | `6~8px` | 아이콘-텍스트 간격, 카드 내 요소 |
| **md** | `10~14px` | 카드 간격, 리스트 아이템 패딩 |
| **lg** | `16~18px` | 섹션 마진, 카드 패딩 |
| **xl** | `20~24px` | 카드 큰 패딩 |
| **2xl** | `28px` | 섹션 타이틀 상단 패딩 |

---

## 4. 라운딩 (Border Radius)

| 토큰 | 값 | 용도 |
|------|---|------|
| **radius-xl** | `28px` | 결과 모달 상단, 산책 통계 패널 |
| **radius-lg** | `24px` | 주요 카드 (주간요약, 날씨, 산책시작) |
| **radius-md** | `20px` | 일반 카드 (펫, 챌린지, 맵, 프리미엄) |
| **radius-sm** | `14px` | 작은 카드 (산책기록, 광고, 통계칩) |
| **radius-xs** | `10px` | 아이콘 박스, 맵 버튼 |
| **pill** | `20px` | GPS 알약, 뱃지칩 |
| **circle** | `50%` | 아바타, 원형 버튼, 인디케이터 |

---

## 5. 글래스모피즘 (Glassmorphism)

### 5-1. Glass 스타일

컨셉3의 핵심 비주얼 언어. 투명감과 블러 효과로 청량한 느낌을 구현.

```css
/* 기본 글래스 - 카드, 챌린지, 펫카드 */
.glass {
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(197, 217, 0, 0.12);
}

/* 강한 글래스 - 헤더, 네비, 패널 */
.glass-heavy {
    background: rgba(255, 255, 255, 0.80);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(197, 217, 0, 0.12);
}

/* 헤더 전용 */
.header-glass {
    background: rgba(255, 255, 255, 0.70);
    backdrop-filter: blur(24px);
}

/* 네비게이션 전용 */
.nav-glass {
    background: rgba(255, 255, 255, 0.72);
    backdrop-filter: blur(24px);
}
```

### 5-2. 블러 수치

| 용도 | blur 값 |
|------|---------|
| 기본 카드 | `blur(12px)` |
| 표준 글래스 | `blur(20px)` |
| 헤더/네비 | `blur(24px)` |
| 맵 컨트롤 | `blur(12px)` |
| 오버레이 배경 | `blur(4px)` |
| 토스트 | `blur(12px)` |

---

## 6. 그림자 (Shadows)

그림자 대신 **glow 효과**와 **투명 배경**으로 깊이감 표현 (청량한 컨셉 유지).

| 용도 | 값 |
|------|---|
| Lime Glow (CTA) | `0 8px 32px rgba(197,217,0,0.25)` |
| Lime Glow (Nav) | `0 4px 20px rgba(197,217,0,0.25)` |
| Azure Glow (Hover) | `0 4px 20px rgba(0,153,255,0.20)` |
| 카드 Hover | `0 8px 24px rgba(0,0,0,0.04)` |
| 산책기록 Hover | `0 4px 16px rgba(0,0,0,0.04)` |
| Danger Glow | `0 4px 20px rgba(239,68,68,0.30)` |
| 마커 점 | `0 2px 10px rgba(0,0,0,0.20)` |
| 로고 점 | `0 0 8px rgba(197,217,0,0.25)` |

---

## 7. 아이콘 시스템

### 7-1. 아이콘 라이브러리

**Lucide Icons** (stroke 기반 아이콘)

### 7-2. 아이콘 크기

| 토큰 | 크기 | stroke-width | 용도 |
|------|------|-------------|------|
| **sm** | 16px | 1.8 | 메타 정보, 작은 라벨 |
| **default** | 20px | 1.8 | 기본 아이콘 |
| **lg** | 24px | 1.6 | 네비 아이콘, 중앙 산책 버튼 |
| **xl** | 28px | 1.5 | 강조 아이콘 |
| **hero** | 32px | 1.4 | 날씨 아이콘 |

### 7-3. 주요 아이콘 매핑

| 기능 | 아이콘 |
|------|--------|
| 홈 | `home` |
| 소셜 | `users` |
| 랭킹 | `trophy` |
| 마이페이지 | `user` |
| 알림 | `bell` |
| 산책 시작 | `arrow-right` |
| 재생 | `play` |
| 일시정지 | `pause` |
| 중지 | `square` |
| 카메라 | `camera` |
| 닫기 | `x` |
| 날씨 (맑음) | `sun` |
| 통계 | `bar-chart-2` |
| 반려동물 | `heart` |
| 랭킹 | `trophy` |
| 챌린지 | `target` |
| 내 주변 | `map-pin` |
| 최근 산책 | `clock` |
| 공원 | `trees` |
| 카페 | `coffee` |
| 병원 | `heart-pulse` |
| 프리미엄 | `crown` |
| 칼로리 | `flame` |
| 거리 | `map` |
| 탐험 | `compass` |
| 추가 | `plus` |
| 뱃지 | `award` |
| 내 위치 | `locate` |
| 따라가기 | `crosshair` |
| 더보기 | `chevron-right` |

---

## 8. 컴포넌트 가이드

### 8-1. 카드 (Card)

```
[ Glass Card ]
├── padding: 18~24px
├── border-radius: radius-md (20px) ~ radius-lg (24px)
├── background: glass 또는 glass-heavy
├── border: 1px solid glass-border
└── hover: translateY(-3px) + 미세 그림자
```

**카드 종류:**

| 카드 | 라운딩 | 패딩 | 특징 |
|------|--------|------|------|
| 날씨 카드 | 24px | 20px 22px | 그라데이션 배경 + 구름 애니메이션 |
| 주간 요약 카드 | 24px | 22px 24px | 통계 3분할 + 프로그레스 바 |
| 펫 카드 | 20px | 18px 14px | 가로 스크롤, min-width: 130px |
| 챌린지 카드 | 20px | 18px | 가로 스크롤, min-width: 190px |
| 산책 기록 카드 | 14px | 14px 16px | 가로 배치 (이미지 + 정보) |

### 8-2. 버튼 (Button)

**Primary CTA (산책 시작)**
```css
border: 2px solid var(--lime);
background: transparent;
border-radius: 24px;
hover: background lime, glow shadow
animation: floatBtn 3s ease-in-out infinite;
```

**Go 버튼 (GPS 산책 시작)**
```css
background: linear-gradient(135deg, var(--lime), var(--lime-dark));
border-radius: 20px;
box-shadow: 0 6px 24px lime-glow;
```

**컨트롤 버튼 (일시정지/카메라)**
```css
width: 48px; height: 48px;
border-radius: 50%;
background: glass;
border: 1.5px solid glass-border;
```

**정지 버튼**
```css
width: 64px; height: 64px;
border-radius: 50%;
background: linear-gradient(135deg, #EF4444, #DC2626);
color: white;
box-shadow: 0 4px 20px rgba(239,68,68,0.3);
```

**결과 버튼**
```css
/* 닫기 */
background: rgba(0,0,0,0.04);
color: text-secondary;

/* 저장 */
background: var(--azure);
color: white;
border-radius: 20px;
```

### 8-3. 하단 네비게이션 (Bottom Nav)

```
[ Bottom Nav - glass-heavy ]
├── 높이: 76px
├── 아이템 5개 (홈, 소셜, 산책, 랭킹, MY)
├── 기본: text-muted 아이콘 + 10px 라벨
├── 활성: lime-dark 아이콘 + 600 weight + 하단 4px lime dot
└── 중앙 산책 버튼:
    ├── 54x54px 원형
    ├── gradient: lime → lime-dark
    ├── 위로 -16px 돌출
    ├── glow shadow
    └── float 애니메이션
```

### 8-4. 프로그레스 바 (Progress Bar)

```css
/* 트랙 */
height: 4px;
background: rgba(197,217,0,0.12);
border-radius: 4px;

/* 바 */
background: linear-gradient(90deg, var(--lime), var(--azure));
border-radius: 4px;
transition: width 1.2s cubic-bezier(0.22, 1, 0.36, 1);
```

**챌린지 프로그레스 (작은 버전)**
```css
height: 3px;
/* fill 색상: lime, red, amber, purple */
```

### 8-5. 탭 (Tabs)

```css
/* 기본 */
font-size: 13px; font-weight: 500;
color: var(--text-muted);
border: none; background: none;

/* 활성 */
color: var(--text-primary);
font-weight: 600;
border-bottom: 2px solid var(--lime);  /* ::after pseudo */
```

### 8-6. GPS 알약 (GPS Pill)

```css
/* 비활성 */
padding: 5px 12px;
border-radius: 20px;
font-size: 11px;
background: rgba(248,252,250,0.8);
color: text-muted;

/* 활성 */
background: lime-light;
color: lime-dark;
/* 6px 인디케이터 dot: lime + pulse 애니메이션 */
```

### 8-7. 뱃지/칩 (Badge Chip)

```css
padding: 6px 12px;
border-radius: 20px;
background: var(--azure-light);
font-size: 12px;
font-weight: 600;
color: var(--azure-dark);
```

### 8-8. 토스트 (Toast)

```css
background: rgba(26,43,60,0.88);
backdrop-filter: blur(12px);
color: white;
padding: 10px 22px;
border-radius: 24px;
font-size: 13px;
/* bottom: 92px, 2.5초 후 fade out */
```

### 8-9. 리스트 아이템

```css
/* 랭킹 아이템 */
padding: 13px 0;
border-bottom: 1px solid rgba(0,0,0,0.04);
/* 내 항목: 왼쪽 3px lime 보더 + lime 배경 tint */

/* 주변 장소 아이템 */
padding: 14px 4px;
border-bottom: 1px solid rgba(0,0,0,0.03);
/* hover: padding-left 8px 슬라이드 */
```

### 8-10. 아바타/아이콘 원형

| 크기 | 용도 | border |
|------|------|--------|
| 60px | 펫 아바타 | 2px solid rgba(197,217,0,0.2) |
| 46px | 날씨 아이콘 래퍼 | 없음 |
| 42px | 산책 시작 아이콘, 프리미엄 아이콘 | 없음 |
| 40px | 랭킹 아바타, 장소 아이콘, 챌린지 아이콘 | 없음 |
| 48px | 산책 기록 미니 루트 | 없음 (radius-xs) |
| 36px | 헤더 아이콘 버튼 | 없음 |

---

## 9. 그라데이션 (Gradients)

| 이름 | 값 | 용도 |
|------|---|------|
| **Lime CTA** | `linear-gradient(135deg, #C5D900, #9FB300)` | Go 버튼, 네비 중앙 버튼 |
| **Azure Premium** | `linear-gradient(135deg, #0077CC, #0099FF 60%, #33BBFF)` | 프리미엄 배너 |
| **Danger** | `linear-gradient(135deg, #EF4444, #DC2626)` | 정지 버튼 |
| **Sky Weather** | `linear-gradient(135deg, rgba(0,153,255,0.06), rgba(0,153,255,0.12) 40%, rgba(197,217,0,0.06))` | 날씨 카드 |
| **Progress** | `linear-gradient(90deg, #C5D900, #0099FF)` | 프로그레스 바 |
| **Ad BG** | `linear-gradient(135deg, rgba(197,217,0,0.06), rgba(0,153,255,0.04))` | 광고 배너 |

---

## 10. 애니메이션 (Animations)

### 10-1. 트랜지션 기본값

```css
/* 표준 트랜지션 */
transition: all 0.2s;              /* 기본 인터랙션 */
transition: all 0.3s ease;         /* 카드, 상태 변화 */
transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1);  /* CTA 버튼 */
transition: color 0.2s;            /* 텍스트 색상만 */
```

### 10-2. 키프레임 애니메이션

**Fade In Up (진입)**
```css
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(14px); }
    to { opacity: 1; transform: translateY(0); }
}
/* 0.5s, stagger: 0.05s 간격 */
```

**Float (부유 효과)**
```css
@keyframes floatBtn {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-3px); }
}
/* 3s ease-in-out infinite */
```

**Lime Pulse (GPS 인디케이터)**
```css
@keyframes limePulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(197,217,0,0.4); }
    50% { box-shadow: 0 0 0 6px rgba(197,217,0,0); }
}
/* 2s ease-in-out infinite */
```

**Cloud Drift (구름)**
```css
@keyframes cloudDrift {
    0%, 100% { transform: translateX(0); }
    50% { transform: translateX(12px); }
}
/* 8s / 12s ease-in-out infinite */
```

**Slide Up (바텀시트)**
```css
@keyframes slideUp {
    from { transform: translateY(100%); }
    to { transform: translateY(0); }
}
/* 0.35s cubic-bezier(0.22, 1, 0.36, 1) */
```

**Confetti Fall (축하)**
```css
@keyframes confettiFall {
    0% { transform: translateY(-20px) rotate(0deg); opacity: 1; }
    100% { transform: translateY(120px) rotate(360deg); opacity: 0; }
}
/* 2s ease-in, 색상: lime, azure, lime-dark, #33BBFF, #E8F4FF */
```

### 10-3. 인터랙션 패턴

| 액션 | 효과 |
|------|------|
| 카드 Hover | `translateY(-3px)` + 미세 그림자 |
| 카드 Scale Hover | `scale(1.03)` (펫카드) |
| 버튼 Hover | `translateY(-2px)` + glow 강화 |
| 버튼 Active | `scale(0.98)` 또는 `scale(0.92)` |
| 리스트 Hover | `padding-left: 8px` (슬라이드) |
| 화살표 Hover | `translateX(4px)` |

---

## 11. 반응형 (Responsive)

### 11-1. Breakpoint

| 이름 | 값 | 대상 |
|------|---|------|
| **Small** | `max-width: 360px` | 소형 모바일 |
| **App Frame** | `max-width: 480px` | 앱 기본 프레임 |

### 11-2. Small (360px) 조정

```css
@media (max-width: 360px) {
    .weekly-stat-item .value { font-size: 22px; }  /* 26 → 22 */
    .walk-timer { font-size: 44px; }               /* 52 → 44 */
    .weather-temp { font-size: 30px; }              /* 36 → 30 */
}
```

### 11-3. Safe Area

```css
padding-bottom: env(safe-area-inset-bottom, 0);  /* 하단 네비에 적용 */
```

---

## 12. 스크롤 패턴

### 12-1. 가로 스크롤 카드

```css
display: flex;
gap: 12px;
overflow-x: auto;
scroll-snap-type: x mandatory;
scrollbar-width: none;  /* Firefox */
&::-webkit-scrollbar { display: none; }  /* Chrome/Safari */

/* 개별 카드 */
scroll-snap-align: start;
flex-shrink: 0;
```

적용 대상: 펫 카드, 챌린지 카드

### 12-2. 세로 리스트

```css
display: flex;
flex-direction: column;
gap: 2~8px;
```

적용 대상: 랭킹 리스트, 주변 장소, 산책 기록

---

## 13. 외부 의존성

| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| **Pretendard** | v1.3.9 | 서체 (CDN) |
| **Leaflet.js** | 1.9.4 | 지도 |
| **Lucide Icons** | latest | 아이콘 |
| **OpenStreetMap** | - | 지도 타일 |

---

## 14. 디자인 원칙 요약

1. **투명감 (Transparency)**: 글래스모피즘으로 레이어 간 깊이감 표현
2. **청량감 (Freshness)**: Lime + Azure 조합, 밝은 배경, 가벼운 그림자
3. **가벼움 (Lightness)**: thin/light weight 폰트, 미니멀 보더, 넓은 여백
4. **생동감 (Vivid)**: float/pulse 애니메이션, hover 전환, glow 효과
5. **일관성 (Consistency)**: CSS 변수 기반 토큰, 재사용 가능한 glass 클래스
