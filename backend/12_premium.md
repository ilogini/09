# 12. 프리미엄 / 결제

> **상태: 보류 — 추후 구성 예정**
> 프로토타입 단계에서는 구현하지 않음. 정식 출시 전 확정 필요.
> 상위 문서: [BACKEND_PLAN.md](./BACKEND_PLAN.md)

---

## 0. 프로토타입 기준 정리

프로토타입(프리미엄.html)에 명시된 내용:

### 가격

| 플랜 | 가격 | 비고 |
|------|------|------|
| 월간 | ₩3,900/월 | |
| 연간 | ₩35,900/년 | 23% 할인, 월 ₩2,992 환산 |
| 무료 체험 | 7일 | 체험 중 해지 시 무과금 |

### 프리미엄 혜택 (프로토타입 기준)

| 혜택 | 무료 | 프리미엄 |
|------|------|---------|
| GPS 산책 기록 | O | O |
| 기본 통계 | O | O |
| 기본 뱃지 | O | O |
| 동네 랭킹 | 주간만 | 전체 |
| 상세 리포트 (속도 그래프, 칼로리) | X | O |
| 지역별/견종별 랭킹 | X | O |
| 광고 제거 | X | O |
| 프리미엄 전용 뱃지 | X | O |

### FAQ 내용

- 7일 이내 전액 환불 가능
- 해지 후에도 결제 기간 종료까지 혜택 유지
- 패밀리 플랜 (최대 5명) 출시 예정

---

## 1. 추후 확정 필요 사항

| # | 항목 | 선택지 | 비고 |
|---|------|--------|------|
| 1 | **결제 수단** | Apple IAP + Google Play Billing | 앱 내 디지털 구독은 스토어 결제 필수 (정책) |
| 2 | **가격** | 프로토타입 기준 유지 or 조정 | 출시 전 시장 조사 후 확정 |
| 3 | **혜택 범위** | 프로토타입 4가지 유지 or 조정 | 무료/프리미엄 경계 재검토 |
| 4 | **환불 정책** | 스토어 기본 정책 따름 or 자체 정책 | Apple/Google 각각 다름 |
| 5 | **패밀리 플랜** | 포함 여부 | 첫 출시에는 미포함 추천 |
| 6 | **구독 상태 머신** | trial → active → cancelled → expired | 웹훅 처리 로직 |
| 7 | **서버 검증** | 영수증 검증 (Apple/Google 서버) | 결제 위변조 방지 필수 |

---

## 2. 구현 시 필요한 것

### DB 테이블 (예정)

| 테이블 | 용도 |
|--------|------|
| subscriptions | 구독 상태 (유저별 플랜, 시작/만료일, 상태) |
| payment_history | 결제 이력 (영수증, 금액, 상태) |

### API (예정)

| Method | Path | 설명 |
|--------|------|------|
| GET | `/subscriptions/me` | 내 구독 상태 |
| POST | `/subscriptions/verify` | 영수증 검증 (Apple/Google) |
| POST | `/subscriptions/webhook/apple` | Apple 서버 알림 웹훅 |
| POST | `/subscriptions/webhook/google` | Google RTDN 웹훅 |

### 환경변수 (예정)

| 변수 | 용도 |
|------|------|
| `APPLE_SHARED_SECRET` | Apple 영수증 검증 |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Google Play 검증 |

---

## 3. 참고: 스토어 정책 요약

### Apple IAP

- 앱 내 디지털 콘텐츠/구독은 IAP 필수 (수수료 15~30%)
- 서버 측 영수증 검증 필수
- Server-to-Server Notifications V2 지원

### Google Play Billing

- 동일 정책 (수수료 15~30%)
- Real-time Developer Notifications (RTDN) 지원
- Google Play Developer API로 구독 상태 조회

> Toss 등 외부 PG사는 앱 내 디지털 구독에 사용 불가 (물리적 상품/서비스만 가능)

---

*작성일: 2026-03-04*
*상태: 보류 — 프로토타입 기준 정리만, 구현은 정식 출시 전 진행*
