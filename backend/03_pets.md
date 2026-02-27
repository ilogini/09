# 03. 반려동물 시스템

> 기준: server/app/routers/pets.py, models/pet.py + 프로토타입 (온보딩.html, 마이페이지.html)
> 상위 문서: [BACKEND_PLAN.md](./BACKEND_PLAN.md)

---

## 1. 현재 구현 상태

| 기능 | 엔드포인트 | 상태 |
|------|-----------|------|
| 목록 조회 | `GET /pets` | **완료** |
| 등록 | `POST /pets` | **완료** |
| 상세 조회 | `GET /pets/{id}` | **완료** |
| 수정 | `PATCH /pets/{id}` | **완료** |
| 삭제 | `DELETE /pets/{id}` | **완료** |

> 전체 CRUD **구현 완료**. 추가 개발 불필요.

---

## 2. 모델 필드

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| id | BigInteger PK | 자동 | |
| user_id | BigInteger FK | O | 소유자 |
| name | String(30) | O | 이름 |
| species | String(10) | O | 종류: `dog` (고정) |
| breed | String(50) | X | 견종/묘종 (예: 포메라니안, 코숏) |
| size | String(10) | X | 크기: `small`, `medium`, `large` |
| birth_date | Date | X | 생년월일 |
| weight_kg | Numeric(5,2) | X | 체중 (kg) |
| photo_url | Text | X | 프로필 사진 URL |
| is_primary | Boolean | O | 대표 펫 여부 (기본 false) |
| created_at | DateTime | 자동 | |
| updated_at | DateTime | 자동 | |

---

## 3. API 상세

### 3.1 등록 — `POST /pets`

**요청**
```json
{
  "name": "초코",
  "species": "dog",
  "breed": "포메라니안",
  "size": "small",
  "birth_date": "2023-03-15",
  "weight_kg": 3.5,
  "photo_url": null,
  "is_primary": true
}
```

**응답**: PetResponse (201 Created)

### 3.2 목록 — `GET /pets`

현재 사용자의 펫만 반환. `created_at` 순 정렬.

**응답**: `PetResponse[]`

### 3.3 수정 — `PATCH /pets/{id}`

`exclude_unset=True`로 보낸 필드만 업데이트.

### 3.4 삭제 — `DELETE /pets/{id}`

Hard delete. 204 No Content.

---

## 4. 온보딩 연동

> 프로토타입 온보딩.html 기준

**온보딩 시 펫 등록 흐름**:
```
[소셜 로그인 완료]
  → GET /auth/onboarding-status → has_pet: false
  → 온보딩 화면 진입
  → 펫 등록 폼 작성
  → POST /pets { name, species, breed, ... , is_primary: true }
  → 완료 → 홈 진입
```

- 온보딩에서 **최소 1마리 필수 등록**
- 첫 번째 펫은 자동으로 `is_primary: true`
- 이후 마이페이지에서 추가/수정/삭제 가능

---

## 5. 프로토타입과의 차이점

| 프로토타입 (온보딩.html) | 현재 모델 | 비고 |
|------------------------|----------|------|
| 종류: 강아지/고양이/기타 | species: `dog` 고정 | 멍이랑 = 강아지 전용 앱, 고양이/기타 제거 |
| 나이 (숫자 입력) | birth_date (Date) | 프론트에서 나이→생년 변환 or 서버에서 나이 계산 |
| 사진 업로드 | photo_url (URL) | R2 업로드 후 URL 저장 (05_storage 참조) |

### species 값

```
dog — 강아지 (고정)
```

> "멍이랑"은 강아지 산책 전용 앱. species 필드는 `dog` 고정값으로 사용.
> 프론트 온보딩에서 종류 선택 UI 제거, 서버에서 기본값 `dog` 자동 적용.

### 나이 처리

프론트에서 "3살"을 입력하면:
- **방법 A**: 프론트에서 `2023년생` → `birth_date: "2023-01-01"` 변환 후 전송
- **방법 B**: 서버 응답에 `age` 계산 필드 추가

→ **방법 A 권장** (서버 변경 없음)

---

## 6. 산책과의 연동

- `Walk.pet_id` → `Pet.id` FK 관계
- 산책 시작 시 펫 선택 (메인페이지 펫 선택 모달)
- `pet_id`는 nullable → 펫 미선택 산책도 가능

---

*작성일: 2026-02-26*
*기준: server/app/routers/pets.py, models/pet.py 실제 구현 코드*
