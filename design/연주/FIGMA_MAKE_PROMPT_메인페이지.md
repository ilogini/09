# Figma Make - 메인페이지 디자인 프롬프트

> 아래 프롬프트를 Figma Make에 섹션별로 입력하여 디자인을 생성할 수 있습니다.
> 전체 프롬프트 또는 섹션별 프롬프트를 상황에 맞게 사용하세요.

---

## 1. 전체 화면 프롬프트 (한번에 생성)

```
Design a mobile pet walking app home screen (390x844, iPhone 14 size).

App name: "멍이랑" (withBowwow) - a pet walking tracker app.
Design concept: "Refreshing clear-day walk" — airy, transparent, vivid.

DESIGN SYSTEM:
- Font: Pretendard Variable (Light 300, Regular 400, Medium 500, SemiBold 600, Bold 700)
- Primary color: Lime #C5D900 (CTA, accents, active states)
- Secondary color: Azure #0099FF (info, weather, stats)
- Text: Primary #1A2B3C, Secondary #5C6F82, Muted #94A3B8
- Background: #F8FCFA (off-white with slight green tint)
- Glassmorphism: White 65% opacity + 20px blur + 1px border rgba(197,217,0,0.12)
- Heavy glass: White 80% opacity + 24px blur
- Border radius: XL 28px, LG 24px, MD 20px, SM 14px, XS 10px
- Icons: Lucide stroke icons, 1.6-1.8 stroke width
- No heavy drop shadows — use subtle lime glow (rgba(197,217,0,0.25)) instead

LAYOUT (top to bottom):
1. Sticky glass header (58px height)
2. Weather card with sky gradient
3. Weekly summary glass card
4. Walk start button (outlined, lime border)
5. Recent walks section
6. Challenge horizontal scroll cards
7. Nearby places with mini map
8. Ad banner
9. Premium upgrade banner (azure gradient)
10. Glass bottom navigation (76px height)

Make the overall feel light, transparent, and refreshing like a clear spring morning walk.
```

---

## 2. 섹션별 프롬프트

### 2-1. Header (글라스 헤더)

```
Design a mobile app sticky header bar, 58px height, full width.

Style: Glassmorphism — background white 70% opacity, backdrop blur 24px,
bottom border 1px solid rgba(197,217,0,0.08).

Left side:
- App logo text "멍이랑" — "멍이" in Bold 700, "랑" in Light 300, 19px, color #1A2B3C
- Small 7px lime dot (#C5D900) next to the text with subtle glow shadow

Right side (horizontal, 10px gap):
- GPS status pill: rounded capsule (20px radius), 11px text, "GPS 활성"
  - Active state: lime tinted background rgba(197,217,0,0.10), lime border, lime dot with pulse animation
  - Inactive state: muted gray background, gray text
- Bell icon button: 36px circle, Lucide "bell" icon, subtle hover state
  - Small azure (#0099FF) notification dot (7px) at top-right corner with white border
```

### 2-2. Weather Card (날씨 카드)

```
Design a weather info card for a mobile app. Width: full width minus 32px margin (16px each side).

Style:
- Rounded corners 24px (radius-lg)
- Background: subtle diagonal gradient — from azure 6% opacity to azure 12% to lime 6%
- Backdrop blur 12px
- 1px border rgba(0,153,255,0.08)
- Decorative: two floating white cloud shapes (ellipses) at top-right with gentle horizontal drift animation

Layout: Horizontal, space-between alignment
- Left side:
  - Sun icon (Lucide "sun", 32px, azure color #0099FF)
  - Text block:
    - "산책하기 좋은 날이에요!" (14px, SemiBold 600, #1A2B3C)
    - "미세먼지 좋음 · 습도 45%" (12px, Regular, #0077CC)
- Right side:
  - Temperature "12°" — 36px, ultralight (200 weight), #0077CC, with small superscript degree symbol
```

### 2-3. Weekly Summary Card (주간 요약 카드)

```
Design a weekly walk summary card for a mobile pet walking app.

Style: Glass card — white 65% opacity background, 20px blur, 1px lime-tinted border rgba(197,217,0,0.12), 24px border radius.
Padding: 22px horizontal, 24px vertical.

Section 1 - Header row:
- Left: "이번 주 산책" with Lucide "bar-chart-2" icon (azure colored), 15px SemiBold
- Right: "2.3 ~ 2.9" period text, 11px, muted gray

Section 2 - Stats row (3 columns, evenly spaced with vertical dividers):
- Column 1: "12.5 km" (26px Bold) + "총 거리" label (11px muted)
- Column 2: "5 회" (26px Bold) + "산책 횟수" label
- Column 3: "2:15" (26px Bold) + "총 시간" label
- Dividers: 1px lines, 36px tall, rgba(197,217,0,0.15)
- Unit text ("km", "회") in 12px, muted color, lighter weight

Section 3 - Progress bar:
- Label row: "주간 목표 20km" (left, 12px muted) + "62%" (right, 12px lime-dark SemiBold)
- Track: 4px height, rounded, rgba(197,217,0,0.12) background
- Fill: 62% width, gradient from lime #C5D900 to azure #0099FF, rounded
```

### 2-4. Walk Start Button (산책 시작 버튼)

```
Design a large call-to-action button for starting a walk in a pet walking app.

Style:
- Full width (minus 32px margin), height approximately 78px
- Transparent background with 2px solid lime (#C5D900) border
- 24px border radius
- Gentle floating animation (3px up and down, 3 seconds loop)

Layout: Horizontal, centered alignment, 16px gap
- Left: 42px circle with lime-light background rgba(197,217,0,0.10)
  - Arrow-right Lucide icon inside, lime-dark color
- Center (flex: 1, left-aligned text):
  - Main text: "산책 시작하기" (16px, SemiBold 600)
  - Sub text: "햇살 한 모금, 풀내음 한 조각" (12px, Regular, muted gray)
- Right: Chevron-right icon, muted gray

Hover state:
- Background fills with solid lime #C5D900
- Box shadow: 0 8px 32px rgba(197,217,0,0.25)
- Subtle lift (translateY -2px)
- Arrow slides right 4px
```

### 2-5. Recent Walks (최근 산책)

```
Design a "Recent Walks" section for a mobile pet walking app.

Section header:
- Left: Lucide "clock" icon (azure) + "최근 산책" text (16px SemiBold), 8px gap
- Right: "전체보기" link (12px, muted gray, hover turns lime-dark)

Walk history cards (2 items, stacked vertically, 8px gap):
Each card:
- Glass card style: white 65% opacity, blur 8px, lime-tinted border, 14px radius
- Padding: 14px horizontal, 16px vertical
- Layout: Horizontal, 14px gap

- Left: 48px square rounded (10px radius), lime-light background
  - Lucide "map" icon, lime-dark color
- Center (flex: 1):
  - Date: "오늘 오전 7:30" (11px, muted)
  - Title: "보라매공원 코스 · 초코" (14px, SemiBold)
  - Stats row (12px gap):
    - map-pin icon + "3.2km" (bold)
    - clock icon + "42분" (bold)
    - flame icon + "165kcal" (bold)
    - Icons are 12px, muted; values are primary color bold

Card 2: "어제 오후 6:15" / "한강 산책로 · 초코" / 4.7km, 58분, 231kcal
```

### 2-6. Challenge Cards (챌린지 카드 횡스크롤)

```
Design a horizontally scrollable challenge card section for a pet walking app.

Section header: Lucide "target" icon (azure) + "진행 중인 챌린지" (16px SemiBold)

Scrollable row (horizontal, 12px gap, overflow visible to show scroll hint):
4 cards, each 190px min-width, flex-shrink 0:

Each card:
- Glass style: white 65% opacity, blur 12px, lime-tinted border, 20px radius
- Padding: 18px all sides
- Hover: lift 3px with subtle shadow

Card content (vertical):
1. Icon badge (40px square, 10px radius):
   - Distance: azure-light bg + Lucide "map" icon (azure)
   - Streak: red-light bg + Lucide "flame" icon (red)
   - Explore: lime-light bg + Lucide "compass" icon (lime-dark)
   - Time: purple-light bg + Lucide "clock" icon (purple)

2. Title: "주간 50km 달성" (13px SemiBold)
3. Description: "이번 주 총 50km 걷기" (11px muted)

4. Progress bar row:
   - Track: 3px height, very light gray
   - Fill: gradient or solid color matching the category
     - Distance: lime-to-azure gradient (76%)
     - Streak: red #EF4444 (71%)
     - Explore: amber #F59E0B (40%)
     - Time: purple #8B5CF6 (85%)
   - Percentage text: "38/50km" (11px, SemiBold, muted)
```

### 2-7. Nearby Section (내 주변)

```
Design a "Nearby Places" section for a pet walking app.

Section header: Lucide "map-pin" icon (azure) + "내 주변" + "지도보기" link

Map area:
- Full width (minus 32px margin), 170px height
- Rounded 20px corners, 1px lime-tinted border
- Show an OpenStreetMap or simple map placeholder with a lime dot marker

Place list (3 items, stacked, no outer card — just list items):
Each item:
- Padding: 14px vertical, 4px horizontal
- Bottom border: 1px rgba(0,0,0,0.03) — last item no border
- Layout: Horizontal, 14px gap

- Left: 40px circle icon
  - Park: lime-light bg (rgba(197,217,0,0.08)), Lucide "trees" icon, lime-dark color
  - Cafe: amber-light bg (rgba(245,158,11,0.08)), Lucide "coffee" icon, amber color
  - Hospital: azure-light bg, Lucide "heart-pulse" icon, azure color

- Center:
  - Name: "보라매공원 반려동물 놀이터" (14px SemiBold)
  - Detail: "반려동물 전용 · 무료 입장" (11px muted)

- Right: Distance "450m" (13px SemiBold, azure #0099FF)

Items:
1. Park — 보라매공원 반려동물 놀이터 — 450m
2. Cafe — 멍멍카페 — 800m
3. Hospital — 해피 동물병원 — 1.2km
```

### 2-8. Ad Banner + Premium Banner

```
Design two promotional banners stacked vertically for a pet walking app.

Banner 1 - Ad Banner:
- Full width minus 32px, 14px padding
- Background: subtle diagonal gradient lime 6% to azure 4%
- 1px border rgba(197,217,0,0.08), 14px radius
- Layout: horizontal, 12px gap
- "AD" tag: absolute top-right, 9px font, muted, tiny gray badge
- Left: bone emoji 🦴 (28px)
- Right text: "프리미엄 강아지 간식 20% 할인!" (13px SemiBold) + "산책 후 맛있는 간식 어때요?" (11px muted)

Banner 2 - Premium Upgrade:
- Full width minus 32px, 18px padding
- Background: rich azure gradient (dark #0077CC → medium #0099FF → light #33BBFF at 135deg)
- 20px radius
- Decorative: two translucent white circles (8% and 5% opacity) at top-right and bottom-right
- Layout: horizontal, 14px gap

- Left: 42px square (10px radius), white 15% opacity bg
  - Lucide "crown" icon, white
- Center:
  - "멍이랑 프리미엄" (14px Bold, white)
  - "광고 제거 + 상세 통계 + 무제한 챌린지" (11px, white 70% opacity)
- Right:
  - "₩3,900" (16px Bold, lime #C5D900)
  - "/월" (10px, white 60% opacity)
```

### 2-9. Bottom Navigation (하단 네비게이션)

```
Design a mobile bottom navigation bar for a pet walking app.

Style:
- Fixed at bottom, full width (max 480px), 76px height
- Glassmorphism: white 72% opacity, backdrop blur 24px
- Top border: 1px solid rgba(197,217,0,0.08)
- Safe area padding at bottom for notch devices

5 navigation items, evenly spaced:
1. "홈" — Lucide "home" icon — ACTIVE state (lime-dark color, bold label, 4px lime dot below)
2. "소셜" — Lucide "users" icon — default (muted gray icon and label)
3. "산책" — CENTER BUTTON:
   - Elevated 16px above the bar
   - 54px circle with lime gradient (135deg, #C5D900 to #9FB300)
   - White paw emoji "🐾" or paw-print icon inside
   - Lime glow shadow (0 4px 20px rgba(197,217,0,0.25))
   - Gentle floating animation (2px, 3s loop)
   - Label "산책" below in lime-dark, SemiBold
4. "랭킹" — Lucide "trophy" icon — default
5. "MY" — Lucide "user" icon — default

Icon size: 22px, stroke width 1.6
Label: 10px, Medium 500 weight
Active state: lime-dark #9FB300 color, SemiBold 600, small lime dot indicator
```

---

## 3. 독립 화면 프롬프트 (각각 별도 프레임으로 생성)

> 아래 3개 화면은 각각 **새 프레임(390x844)**을 만들어서 프롬프트를 입력하세요.
> 메인화면 포함 총 4개 프레임이 됩니다.

### 3-1. 반려동물 선택 화면 (Screen 2)

```
Design a separate mobile screen (390x844, iPhone 14 size) for a pet selection page in a pet walking app called "멍이랑".

App design system: Lime #C5D900 primary, Azure #0099FF secondary, Pretendard font, glassmorphism style, background #F8FCFA.

This is a full standalone screen that appears when the user taps "산책 시작하기" on the home screen.

TOP - Header bar (58px height):
- Glassmorphism: white 70% opacity, backdrop blur 24px
- Left: Close "X" button (34px circle, light gray bg, Lucide "x" icon)
- Center: "함께 산책할 반려동물" (16px SemiBold)
- Right: empty 34px spacer for balance
- Bottom border: 1px solid rgba(197,217,0,0.08)

MIDDLE - Body (scrollable area, flex: 1):
- Top padding 24px, horizontal padding 20px
- Subtitle: "산책할 반려동물을 선택해주세요" (13px, muted gray #94A3B8, centered)
- 20px gap below subtitle

- Pet card list (2 cards, vertical stack, 12px gap):

  Card 1 (SELECTED state):
  - Glass card: white 65% opacity, blur 12px, 20px border radius
  - 2px solid lime (#C5D900) border
  - Background tinted: rgba(197,217,0,0.10)
  - Padding: 16px, horizontal layout, 14px gap
  - Left: 52px circle avatar with 2px lime border, dog emoji 🐕 (28px) centered
  - Center: "초코" (15px SemiBold) + "골든 리트리버 · 3살" (11px muted)
  - Right: 28px circle, solid lime (#C5D900) fill, white checkmark "✓" inside

  Card 2 (DEFAULT state):
  - Same glass card but 2px transparent border
  - No tinted background
  - Left: 52px circle avatar with light lime border, cat emoji 🐈 (28px)
  - Center: "나비" (15px SemiBold) + "코리안 숏헤어 · 2살" (11px muted)
  - Right: 28px circle, 2px light gray border, empty inside

BOTTOM - Footer (fixed at bottom):
- Top border: 1px solid rgba(197,217,0,0.08)
- Padding: 16px horizontal 20px
- Full-width CTA button:
  - Background: lime gradient (135deg, #C5D900 to #9FB300)
  - Text: "산책 시작하기" (16px SemiBold, dark text #1A2B3C)
  - Height: about 52px, 20px border radius
  - Box shadow: 0 6px 24px rgba(197,217,0,0.25)
```

### 3-2. 산책 추적 화면 (Screen 3)

```
Design a separate mobile screen (390x844, iPhone 14 size) for a GPS walk tracking page in a pet walking app called "멍이랑".

App design system: Lime #C5D900 primary, Azure #0099FF secondary, Pretendard font, glassmorphism style.

This is a full standalone screen showing active walk tracking with a map and live stats.

TOP HALF - Map area (takes about 55% of the screen):
- Full-width map placeholder (light gray/green tinted map with streets)
- A lime-colored (#C5D900) dot marker showing current location (20px circle with white border and lime glow)
- A lime polyline showing the walked route path
- A small lime circle marker at the start point

- Bottom-left floating chip overlay:
  - Glass style: white 80% opacity, blur 16px, lime border rgba(197,217,0,0.12)
  - 14px border radius, padding 10px 16px
  - Content: pulsing lime dot (8px) + "1.25" (22px Bold) + "km" (11px muted)

BOTTOM HALF - Stats panel (about 45% of screen):
- Glass panel: white 80% opacity, backdrop blur 20px
- Top corners rounded 28px, flat bottom edges
- Top border: 1px solid rgba(197,217,0,0.12)
- Padding: 18px horizontal 20px, 30px bottom

Content (vertically stacked, centered):
1. Pet label: "초코와 산책 중" (13px, Medium 500, lime-dark #9FB300, centered)

2. Timer display: "00:12:34" (52px, Light 300 weight, letter-spacing 3px, color #1A2B3C, centered)
   - Monospace/tabular number style

3. Stats grid (2 equal columns, 10px gap):
   - Left card: lime-tinted bg rgba(197,217,0,0.06), 1px lime border rgba(197,217,0,0.08), 14px radius
     - "0.45" (22px SemiBold) + "km" (10px muted)
     - Icon row: Lucide map-pin (12px) + "거리" (10px muted)
   - Right card: same style
     - "24" (22px SemiBold) + "kcal" (10px muted)
     - Icon row: Lucide flame (12px) + "칼로리" (10px muted)

4. Control buttons row (centered, 22px gap between buttons):
   - Left: Pause button — 48px circle, glass bg (white 65%), glass border, Lucide "pause" icon (gray)
   - Center: Stop button — 64px circle, red gradient (#EF4444 to #DC2626), white Lucide "square" icon, red glow shadow
   - Right: Camera button — 48px circle, glass bg, glass border, Lucide "camera" icon (gray)
```

### 3-3. 산책 완료 화면 (Screen 4)

```
Design a separate mobile screen (390x844, iPhone 14 size) for a walk completion result page in a pet walking app called "멍이랑".

App design system: Lime #C5D900 primary, Azure #0099FF secondary, Pretendard font, glassmorphism style.

This is a full standalone screen showing walk results after completing a walk. The background is a dark overlay with a bottom sheet card.

BACKGROUND:
- Dark overlay: rgba(0,0,0,0.35) with subtle 4px blur effect covering the full screen

BOTTOM SHEET CARD (takes about 80% of screen height, anchored to bottom):
- Glass style: white 80% opacity, backdrop blur 24px, lime border rgba(197,217,0,0.12)
- Top corners rounded 28px, flat bottom
- Padding: 28px horizontal 20px, 36px bottom

Content (vertically stacked):

1. Confetti decoration at the very top:
   - Scattered colorful small dots (lime #C5D900, azure #0099FF, light blue #33BBFF, #9FB300)
   - About 20-30 small circles (4-8px) scattered across the top 120px area

2. Header (centered):
   - Party emoji 🎉 (48px)
   - "산책 완료!" (22px Bold, #1A2B3C)
   - "초코와 즐거운 산책이었어요" (13px, muted #94A3B8)

3. Route map placeholder:
   - Full width, 150px height, 20px border radius
   - Light background with lime border rgba(197,217,0,0.12)
   - Show a simple map with a lime (#C5D900) route line
   - Green circle at start, red circle at end

4. Stats row (3 equal columns, 10px gap):
   - Each stat box: light gray bg rgba(0,0,0,0.02), 14px border radius, 16px vertical padding
   - Centered content in each:
     - Icon: azure color (#0099FF), 18px Lucide icon
     - Value: 22px Bold
     - Label: 11px muted
   - Column 1: Lucide "map" icon + "3.20 km" + "거리"
   - Column 2: Lucide "timer" icon + "42분 30초" + "시간"
   - Column 3: Lucide "flame" icon + "165 kcal" + "칼로리"

5. Badges section:
   - Header: Lucide "award" icon + "획득한 배지" (13px SemiBold)
   - Badge chips row (flex wrap, 8px gap):
     - Each chip: azure-light bg rgba(0,153,255,0.08), 20px pill radius, 6px 12px padding
     - Text: 12px SemiBold, azure-dark #0077CC
     - Chips: "1km 달성", "30분 산책"

6. Action buttons (2 columns, 12px gap):
   - Left button: "닫기" — light gray bg rgba(0,0,0,0.04), secondary text #5C6F82, 14px radius, 14px padding
   - Right button: "저장하기" — azure bg #0099FF, white text, 20px radius, 14px padding
   - Both: 15px SemiBold font
```

---

## 4. 디자인 시스템 컴포넌트 프롬프트

```
Create a design system component library for "멍이랑" pet walking app:

COLOR TOKENS:
- Lime: #C5D900 (primary CTA, active states, accents)
- Lime Dark: #9FB300 (hover, pressed states)
- Lime Light: rgba(197,217,0,0.10) (backgrounds, tints)
- Lime Glow: rgba(197,217,0,0.25) (shadows, glows)
- Azure: #0099FF (secondary, info, links)
- Azure Dark: #0077CC (hover states)
- Azure Light: rgba(0,153,255,0.08) (backgrounds)
- Text Primary: #1A2B3C
- Text Secondary: #5C6F82
- Text Muted: #94A3B8
- Background: #F8FCFA
- Danger: #EF4444

GLASS STYLES:
- Light glass: bg white 65%, blur 20px, border rgba(197,217,0,0.12)
- Heavy glass: bg white 80%, blur 24px, same border
- Glass border only visible on close inspection — very subtle

RADIUS SCALE:
- XL: 28px (modals, bottom sheets)
- LG: 24px (cards, buttons)
- MD: 20px (medium cards, inputs)
- SM: 14px (small cards, chips)
- XS: 10px (icons, tags)

TYPOGRAPHY (Pretendard Variable):
- H1: 22px Bold
- H2: 16px SemiBold
- H3: 15px SemiBold
- Body: 14px Regular
- Caption: 12px Regular/Medium
- Micro: 11px Regular
- Label: 10px Medium

SPACING:
- Section gap: 18-28px
- Card padding: 18-24px
- Item gap: 12-14px
- Page margin: 16px each side (32px total)

ICON STYLE:
- Lucide icons, stroke-based
- Default: 20px, stroke-width 1.8
- Small: 16px, stroke-width 1.8
- Large: 24px, stroke-width 1.6
- Colors match context (azure for info, lime-dark for active, muted for default)
```

---

## 5. 사용 팁

### Figma Make 입력 순서 (권장)

1. **디자인 시스템 컴포넌트** (섹션 4) 먼저 생성
2. **전체 화면 프롬프트** (섹션 1)로 전체 레이아웃 잡기
3. **섹션별 프롬프트** (섹션 2)로 개별 섹션 디테일 수정
4. **모달 프롬프트** (섹션 3)로 오버레이 화면 추가

### 수정 시 유용한 추가 프롬프트

```
// 간격 조정
"Reduce the gap between weather card and weekly summary card to 12px"

// 컬러 미세 조정
"Make the lime color slightly more yellow-green, try #D4E600"

// 글라스 효과 강도 조정
"Increase the glass opacity from 65% to 75% for better readability"

// 그림자 조정
"Add a very subtle lime glow (0 4px 16px rgba(197,217,0,0.15)) to the walk start button"

// 아이콘 변경
"Replace the sun weather icon with cloud-sun for partly cloudy"

// 다크모드 변환
"Convert this screen to dark mode: background #0F172A, glass bg rgba(30,41,59,0.65), text white/gray"
```
