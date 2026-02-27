# 01. 인증 시스템

> 기준: 서버 코드 (server/app/routers/auth.py) + 프로토타입 (로그인.html, 온보딩.html)
> 상위 문서: [BACKEND_PLAN.md](./BACKEND_PLAN.md)

---

## 1. 현재 구현 상태

| 기능 | 엔드포인트 | 상태 |
|------|-----------|------|
| 카카오 로그인 | `POST /auth/kakao` | **완료** |
| 네이버 로그인 | `POST /auth/naver` | **완료** |
| Apple 로그인 | `POST /auth/apple` | **완료** |
| 토큰 갱신 | `POST /auth/refresh` | **완료** |
| 로그아웃 | `POST /auth/logout` | **완료** |
| Google 로그인 | - | **보류** (MVP 제외) |
| 온보딩 상태 확인 | `GET /auth/onboarding-status` | **TODO** |
| 회원 탈퇴 | `DELETE /users/me` | **TODO** |

---

## 2. 인증 플로우

```
[앱 실행]
  │
  ├── 로컬 토큰 있음?
  │     ├── Yes → POST /auth/refresh 시도
  │     │           ├── 성공 → 홈 진입
  │     │           └── 실패 → 로그인 화면
  │     └── No → 로그인 화면
  │
  ├── [로그인 화면] 소셜 로그인 선택
  │     ├── 카카오 → POST /auth/kakao
  │     ├── 네이버 → POST /auth/naver
  │     └── Apple  → POST /auth/apple
  │
  ├── 서버 응답: { access_token, refresh_token }
  │
  ├── GET /auth/onboarding-status (TODO)
  │     ├── 온보딩 완료 → 홈 진입
  │     └── 온보딩 미완료 → 온보딩 화면
  │
  └── [온보딩 화면]
        ├── 인트로 슬라이드 (3장) — 프론트 전용
        ├── 반려동물 등록 (POST /pets) — 필수 1마리
        │     ├── 이름 (필수)
        │     ├── 종류: 강아지/고양이/기타 (필수)
        │     ├── 견종/묘종 (선택)
        │     ├── 나이 (선택)
        │     ├── 체중 (선택)
        │     └── 사진 (선택)
        ├── 위치 권한 요청 — 프론트 전용
        └── 완료 → 홈 진입
```

---

## 3. 소셜 로그인 상세

### 3.1 카카오 (`POST /auth/kakao`)

**요청**
```json
{ "code": "authorization_code_from_kakao_sdk" }
```

**서버 처리 흐름**
1. 카카오 토큰 교환: `POST https://kauth.kakao.com/oauth/token`
2. 사용자 정보 조회: `GET https://kapi.kakao.com/v2/user/me`
3. DB 사용자 조회/생성 (`provider=kakao`, `provider_id=카카오ID`)
4. JWT 토큰 발급 (access + refresh)
5. refresh token 해시 저장

**필요 환경변수**
- `KAKAO_CLIENT_ID` — 카카오 REST API 키
- `KAKAO_CLIENT_SECRET` — 카카오 Client Secret

### 3.2 네이버 (`POST /auth/naver`)

**요청**
```json
{ "code": "authorization_code_from_naver_sdk" }
```

**서버 처리 흐름**
1. 네이버 토큰 교환: `POST https://nid.naver.com/oauth2.0/token`
2. 사용자 정보 조회: `GET https://openapi.naver.com/v1/nid/me`
3. DB 사용자 조회/생성
4. JWT 토큰 발급 + refresh 저장

**필요 환경변수**
- `NAVER_CLIENT_ID`
- `NAVER_CLIENT_SECRET`

### 3.3 Apple (`POST /auth/apple`)

**요청**
```json
{ "code": "identity_token_jwt_from_apple_sdk" }
```

**서버 처리 흐름**
1. Apple 공개 키 조회: `GET https://appleid.apple.com/auth/keys`
2. JWT 헤더의 `kid`로 매칭 키 찾기
3. `RS256`으로 identity_token 검증 (audience + issuer 체크)
4. payload에서 `sub`(provider_id), `email` 추출
5. DB 사용자 조회/생성 + JWT 발급

**필요 환경변수**
- `APPLE_CLIENT_ID` — Apple Service ID (Bundle ID)
- `APPLE_TEAM_ID`, `APPLE_KEY_ID`, `APPLE_PRIVATE_KEY` — (현재 미사용, 향후 서버→Apple 통신 시 필요)

**참고**: Apple은 첫 로그인 시에만 이름/이메일을 제공. 이후에는 `sub`만 반환.

---

## 4. JWT 토큰 관리

### 4.1 토큰 사양

| 항목 | 값 |
|------|-----|
| 라이브러리 | python-jose |
| 알고리즘 | HS256 |
| Access Token 만료 | 60분 (1시간) |
| Refresh Token 만료 | 7일 |
| Refresh 저장 | bcrypt 해시 → users.hashed_refresh_token |

### 4.2 Access Token Payload
```json
{
  "sub": "123",
  "exp": 1707750000
}
```

### 4.3 Refresh Token Payload
```json
{
  "sub": "123",
  "exp": 1708354800,
  "type": "refresh"
}
```

### 4.4 토큰 갱신 (`POST /auth/refresh`)

**요청**
```json
{ "refresh_token": "eyJ..." }
```

**서버 처리**
1. refresh_token JWT 디코딩
2. `type == "refresh"` 확인
3. DB에서 사용자 조회
4. 저장된 해시와 비교 (`bcrypt.verify`)
5. 새 access + refresh 토큰 발급
6. 새 refresh 해시 저장 (rotation)

### 4.5 로그아웃 (`POST /auth/logout`)

**요청**: Authorization 헤더에 Bearer 토큰

**서버 처리**
1. access_token에서 user_id 추출
2. `hashed_refresh_token = None` 으로 무효화

---

## 5. 사용자 인증 미들웨어

> `server/app/dependencies.py`

```
Authorization: Bearer <access_token>
```

- `get_current_user()` 의존성으로 현재 사용자 주입
- soft delete된 사용자 (`deleted_at IS NOT NULL`)는 403 반환

---

## 6. TODO 구현 사항

### 6.1 온보딩 상태 확인 — `GET /auth/onboarding-status`

**응답 (안)**
```json
{
  "has_nickname": true,
  "has_pet": false,
  "is_complete": false
}
```

**로직**
- `has_nickname`: nickname이 자동 생성값(`user_XXXX`)이 아닌지 확인
- `has_pet`: pets 테이블에 1건 이상 존재하는지
- `is_complete`: 위 두 조건 모두 충족

> 이 API는 프론트에서 로그인 직후 호출하여 온보딩 화면 vs 홈 화면 분기에 사용

### 6.2 회원 탈퇴 — `DELETE /users/me`

**처리 방식**: Soft Delete
1. `users.deleted_at = NOW()` 설정
2. `hashed_refresh_token = None` (즉시 로그아웃)
3. 30일 유예 기간
4. 유예 기간 내 재로그인 시 `deleted_at = NULL`로 복구
5. 30일 후 스케줄러로 완전 삭제 (관련 데이터 CASCADE)

**응답**
```json
{ "message": "30일 후 계정이 완전 삭제됩니다. 재로그인하면 복구됩니다." }
```

---

## 7. 코드 vs 구버전 문서 차이점

| 항목 | 구버전 문서 (old/02_auth.md) | 실제 코드 |
|------|---------------------------|----------|
| 구조 | AuthService 클래스 사용 | 라우터에 직접 구현 (서비스 미분리) |
| 로그인 응답 | `is_new_user`, `user` 포함 | `TokenResponse`만 반환 |
| 네이버 state | state 파라미터 사용 | state 미사용 |
| 온보딩 | users.py에 별도 엔드포인트 | 미구현 |
| 삭제 복구 | get_or_create에서 deleted_at 복구 | 미구현 (get_or_create에 삭제 복구 로직 없음) |

### 향후 리팩토링 고려
- AuthService 클래스로 분리하면 테스트/유지보수 용이
- 로그인 응답에 `is_new_user` 추가하면 프론트에서 온보딩 분기 가능
- 단, 현재는 **동작하는 코드 우선**이므로 리팩토링은 Phase 5에서 진행

---

## 8. 환경변수 체크리스트

| 변수 | 용도 | 필수 |
|------|------|------|
| `JWT_SECRET_KEY` | 토큰 서명 | **필수** (운영: 랜덤 64자 이상) |
| `JWT_ALGORITHM` | 서명 알고리즘 | 기본값: HS256 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | 액세스 만료 | 기본값: 60 |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | 리프레시 만료 | 기본값: 7 |
| `KAKAO_CLIENT_ID` | 카카오 REST API 키 | 카카오 로그인 시 필수 |
| `KAKAO_CLIENT_SECRET` | 카카오 Client Secret | 카카오 로그인 시 필수 |
| `NAVER_CLIENT_ID` | 네이버 Client ID | 네이버 로그인 시 필수 |
| `NAVER_CLIENT_SECRET` | 네이버 Client Secret | 네이버 로그인 시 필수 |
| `APPLE_CLIENT_ID` | Apple Service ID | Apple 로그인 시 필수 |

---

*작성일: 2026-02-26*
*기준: server/app/routers/auth.py 실제 구현 코드*
