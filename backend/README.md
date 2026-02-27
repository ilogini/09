# 멍이랑 백엔드 문서

> 이 폴더는 백엔드 기획/설계 문서를 관리합니다.
> 프로토타입 HTML 페이지 기준으로 필요한 기능을 도출하고, 기능 단위로 문서를 작성합니다.

---

## 문서 목록

| # | 문서 | 범위 | Phase | 상태 |
|---|------|------|-------|------|
| - | [BACKEND_PLAN.md](./BACKEND_PLAN.md) | 마스터 플랜 (전체 Phase, API 목록, 우선순위) | 전체 | **완료** |
| 01 | [01_auth.md](./01_auth.md) | 소셜 로그인, JWT, 온보딩, 회원 탈퇴 | 1 | **완료** |
| 02 | [02_walks.md](./02_walks.md) | 산책 시작/완료/목록/상세, 주간 요약, 누적 통계, 기간 필터, 경로 이미지 생성 | 1 | **완료** |
| 03 | [03_pets.md](./03_pets.md) | 반려동물 CRUD, 온보딩 시 필수 등록 | 1 | **완료** |
| 04 | [04_map_places.md](./04_map_places.md) | 지도, 주변 장소 검색, 카카오 로컬 API, 즐겨찾기 | 1 | **완료** |
| 05 | [05_storage.md](./05_storage.md) | 사진 업로드, R2 presigned URL, 이미지 리사이징 | 1 | **완료** |
| 06 | 06_badges.md | 뱃지 45개 (6카테고리), 진행률, 산책 완료 시 자동 체크 | 2 | TODO |
| 07 | 07_grades_titles.md | 등급 10단계, 칭호 10개, 레벨업 로직 | 2 | TODO |
| 08 | 08_rankings.md | 주간/월간/전체 랭킹, 지역별, 명예의 전당 | 2 | TODO |
| 09 | 09_social.md | 팔로우, 피드, 좋아요/댓글, 차단/신고 | 3 | TODO |
| 10 | 10_challenges.md | 챌린지 생성/참가/리더보드, 산책 초대 | 3 | TODO |
| 11 | 11_notifications.md | 푸시 알림, 알림 내역, FCM 연동 | 4 | TODO |
| 12 | 12_premium.md | 구독/결제, Toss/Apple/Google 웹훅 | 4 | TODO |
| 13 | 13_weather.md | 날씨/미세먼지, 산책 추천, Redis 캐싱 | 4 | TODO |

---

## 프로토타입 ↔ 문서 매핑

| 프로토타입 페이지 | 관련 문서 |
|------------------|----------|
| 로그인.html, 온보딩.html | 01_auth, 03_pets |
| 메인페이지.html | 02_walks, 04_map, 06_badges, 13_weather |
| 산책기록.html | 02_walks |
| 산책상세.html | 02_walks, 05_storage |
| 지도.html | 04_map_places |
| 마이페이지.html | 02_walks, 03_pets, 06_badges, 07_grades_titles |
| 뱃지.html | 06_badges |
| 랭킹.html | 08_rankings |
| 소셜.html | 09_social, 10_challenges |
| 알림.html | 11_notifications |
| 설정.html | 01_auth, 11_notifications, 12_premium |
| 프리미엄.html | 12_premium |

---

## 작업 우선순위

### 즉시 (Phase 1 핵심)
1. **02_walks.md** — 산책이 핵심 기능, 신규 API 3개 (weekly-summary, stats, 기간필터)
2. **04_map_places.md** — 최우선도, 외부 API 선정 필요
3. **05_storage.md** — 산책 사진 업로드

### 다음 (Phase 1 보완)
4. **03_pets.md** — 이미 구현 완료, 문서화만 필요

### 이후 (Phase 2~4)
5. 06~13번 — Phase 순서대로

---

## 참고

- `old/` 폴더: 구버전 설계 문서 (00~09, env_setup). 참고용으로 보관
- 각 문서는 **현행 서버 코드 기준**으로 작성 (구버전 문서와 차이점 있을 수 있음)
- 프로토타입: `prototype/` 폴더 HTML 파일 기준

---

*최종 수정: 2026-02-26*
