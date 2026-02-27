# 결제 시스템 - 멍이랑 (withbowwow)

> 코어 파일: [00_overview.md](./00_overview.md)
> HTTP 클라이언트: httpx (Toss Payments API, Google Play API)

---

## 1. 결제 구조

### 1.1 수익 모델

| 유형 | 항목 | 가격 |
|------|------|------|
| **구독 (월간)** | 프리미엄 월간 | 3,900원/월 |
| **구독 (연간)** | 프리미엄 연간 | 31,200원/년 (월 2,600원) |
| **인앱 구매** | 프로필 뱃지 팩 | 1,000원 |
| **인앱 구매** | 산책 테마 | 2,000원 |
| **인앱 구매** | 펫 의상 | 500~1,500원 |
| **광고** | 카카오 AdFit 배너 | CPM 1,000~3,000원 |

### 1.2 결제 수단

| 플랫폼 | 결제 수단 | 수수료 |
|--------|----------|--------|
| iOS | Apple IAP (필수) | 15~30% |
| Android | Google Play Billing (필수) | 15~30% |
| 웹/기타 | Toss Payments (카드, 카카오페이, 네이버페이) | 3.3% |

---

## 2. 프리미엄 기능 비교

| 기능 | 무료 | 프리미엄 |
|------|------|---------||
| 기본 산책 기록 | O | O |
| 주간 랭킹 | O | O |
| 뱃지 획득 | O | O |
| **광고 제거** | X | O |
| **상세 통계 리포트** | X | O |
| **실시간 랭킹 + 지역별** | 주간만 | 전체 |
| **무제한 뱃지 트래킹** | 기본만 | 전체 |
| **커스텀 산책 코스 생성** | X | O |
| **반려동물 건강 리포트** | X | O |
| **연속 기록 휴식일 (월 1회)** | X | O |
| **프로필 프리미엄 뱃지** | X | O |

---

## 3. iOS IAP 연동

### 3.1 상품 등록 (App Store Connect)

| Product ID | 유형 | 가격 |
|-----------|------|------|
| `com.withbowwow.premium.monthly` | Auto-Renewable Subscription | 3,900원 |
| `com.withbowwow.premium.annual` | Auto-Renewable Subscription | 31,200원 |
| `com.withbowwow.badge_pack` | Non-Consumable | 1,000원 |
| `com.withbowwow.theme.*` | Non-Consumable | 2,000원 |

### 3.2 구독 플로우

```
[프리미엄 가입 화면]
  → 플랜 선택 (월간/연간)
  → "무료 체험 시작" (7일 무료)
  → iOS IAP 결제 시트
  → Apple 결제 완료
  → App Store Server Notification (Webhook)
  → FastAPI: POST /payments/webhook/apple
    → subscriptions 테이블 INSERT
    → users.is_premium = TRUE
    → users.premium_until = 결제 종료일
```

### 3.3 Server-to-Server Notification

```python
# app/services/payment_service.py
import httpx
from datetime import datetime


class PaymentService:

    async def handle_apple_notification(self, db: AsyncSession, payload: dict):
        """App Store Server Notification v2 처리"""
        notification_type = payload.get("notificationType")
        data = payload.get("data", {})

        match notification_type:
            case "SUBSCRIBED" | "DID_RENEW":
                await self._activate_subscription(db, data, provider="ios_iap")
            case "DID_FAIL_TO_RENEW" | "EXPIRED":
                await self._deactivate_subscription(db, data)
            case "REFUND":
                await self._handle_refund(db, data)

    async def _activate_subscription(self, db: AsyncSession, data: dict, provider: str):
        user_id = data.get("user_id")
        user = await db.get(User, user_id)
        if not user:
            return

        user.is_premium = True
        user.premium_until = datetime.fromisoformat(data["expires_date"])

        # subscriptions 테이블 업데이트
        subscription = Subscription(
            user_id=user_id,
            plan_type=data.get("plan_type", "monthly"),
            status="active",
            payment_provider=provider,
            provider_subscription_id=data.get("subscription_id"),
            current_period_start=datetime.fromisoformat(data["start_date"]),
            current_period_end=datetime.fromisoformat(data["expires_date"]),
        )
        db.add(subscription)
        await db.commit()

    async def _deactivate_subscription(self, db: AsyncSession, data: dict):
        user_id = data.get("user_id")
        user = await db.get(User, user_id)
        if user:
            user.is_premium = False
            await db.commit()
```

---

## 4. Google Play Billing 연동

### 4.1 상품 등록 (Google Play Console)

- 동일한 Product ID 구조
- Real-time Developer Notifications 설정 (Cloud Pub/Sub)

### 4.2 영수증 검증

```python
async def verify_google_purchase(self, purchase_token: str, product_id: str) -> dict:
    """Google Play 구독 영수증 검증"""
    # Google OAuth2로 액세스 토큰 발급
    access_token = await self._get_google_access_token()

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://androidpublisher.googleapis.com/androidpublisher/v3"
            f"/applications/com.withbowwow/purchases/subscriptions"
            f"/{product_id}/tokens/{purchase_token}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        return resp.json()
```

---

## 5. Toss Payments 연동 (웹 결제)

### 5.1 결제 플로우

```
결제 요청 → Toss Payments SDK (프론트) → 결제 완료
  → 클라이언트에서 paymentKey, orderId, amount 수신
  → POST /payments/confirm 호출
  → Toss Payments 결제 승인 API 호출 (서버)
  → 승인 성공 → subscriptions 테이블 업데이트
```

### 5.2 결제 승인 (서버)

```python
async def confirm_toss_payment(
    self, payment_key: str, order_id: str, amount: int
) -> dict:
    """Toss Payments 결제 승인"""
    import base64

    auth = base64.b64encode(
        f"{settings.TOSS_SECRET_KEY}:".encode()
    ).decode()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://api.tosspayments.com/v1/payments/confirm",
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/json",
            },
            json={
                "paymentKey": payment_key,
                "orderId": order_id,
                "amount": amount,
            },
        )
        resp.raise_for_status()
        return resp.json()
```

### 5.3 정기결제 (빌링키)

```python
async def charge_subscription(
    self, billing_key: str, user_id: str, amount: int
) -> dict:
    """빌링키로 자동 정기결제"""
    import base64
    import uuid

    auth = base64.b64encode(
        f"{settings.TOSS_SECRET_KEY}:".encode()
    ).decode()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"https://api.tosspayments.com/v1/billing/{billing_key}",
            headers={
                "Authorization": f"Basic {auth}",
                "Content-Type": "application/json",
            },
            json={
                "customerKey": user_id,
                "amount": amount,
                "orderId": str(uuid.uuid4()),
                "orderName": "멍이랑 프리미엄 구독",
            },
        )
        resp.raise_for_status()
        return resp.json()
```

---

## 6. 구독 상태 관리

### 6.1 상태 머신

```
trial → active → (cancelled → expired) 또는 (active 갱신)

trial:     무료 체험 기간 (7일)
active:    활성 구독 중
cancelled: 해지 요청 (현재 기간 종료까지 프리미엄 유지)
expired:   구독 만료 (무료로 전환)
```

### 6.2 구독 만료 Cron (APScheduler)

```python
# app/scheduler/tasks.py

async def expire_subscriptions():
    """매일 자정: 만료된 구독 처리"""
    async with get_async_session() as db:
        now = datetime.utcnow()

        # 프리미엄 만료 처리
        stmt = (
            update(User)
            .where(User.premium_until < now, User.is_premium == True)
            .values(is_premium=False)
        )
        await db.execute(stmt)

        # 구독 상태 업데이트
        stmt = (
            update(Subscription)
            .where(
                Subscription.current_period_end < now,
                Subscription.status.in_(["active", "cancelled"]),
            )
            .values(status="expired")
        )
        await db.execute(stmt)
        await db.commit()
```

### 6.3 무료 체험

```
7일 무료 체험:
- 최초 1회만 제공
- 체험 종료 후 자동 결제 전환 (IAP 표준)
- 체험 종료 1일 전 알림: "내일 프리미엄 구독이 시작돼요"
- 체험 중 해지 가능 (요금 미부과)
```

---

*작성일: 2026-02-12*
*버전: 2.0 — httpx (Python)로 전환*
