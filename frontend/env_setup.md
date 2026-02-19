# 프론트엔드 환경 세팅 가이드

> 멍이랑 (withbowwow) React Native 앱 개발 환경 구축
> 최종 업데이트: 2026-02-19

---

## 1. 확정 기술 스택

### 1.1 코어

| 항목 | 패키지 | 버전 | 비고 |
|------|--------|------|------|
| **Runtime** | Expo SDK | **54** | 최신 안정 (2026-02 기준) |
| **Framework** | React Native | 0.81 | SDK 54 포함 |
| **React** | React | 19.1 | SDK 54 포함 |
| **Language** | TypeScript | 5.x | Strict mode 권장 |
| **Navigation** | React Navigation | v7 | Bottom Tabs + Native Stack |
| **State** | Zustand | 5.x | 경량 전역 상태 |
| **Server State** | TanStack Query | v5 | API 캐싱, 리트라이, 백그라운드 리페치 |
| **Styling** | NativeWind | v4.1 | Tailwind CSS for RN |
| **Animation** | react-native-reanimated | v3 (~3.16.x) | NativeWind v4와 호환 (v4 아님 주의) |
| **HTTP** | axios | 1.13.x | API 호출 |

### 1.2 네이티브 기능

| 항목 | 패키지 | 비고 |
|------|--------|------|
| **지도** | @mj-studio/react-native-naver-map | v2.x, 한국 시장 필수 |
| **GPS** | expo-location | 포그라운드 + 백그라운드 |
| **백그라운드** | expo-task-manager | GPS 백그라운드 태스크 |
| **카메라/갤러리** | expo-image-picker | 산책 중 사진 |
| **푸시 알림** | expo-notifications | FCM + APNs |
| **보안 저장소** | expo-secure-store | JWT 토큰 |

### 1.3 소셜 로그인 SDK

| 프로바이더 | 패키지 | 비고 |
|-----------|--------|------|
| **카카오** | @react-native-kakao/core | 네이티브 SDK, Expo config plugin 지원 |
| **네이버** | expo-auth-session | 웹 OAuth 방식 |
| **Apple** | expo-apple-authentication | Expo 내장 |

---

## 2. 개발 환경 요구사항

### 2.1 필수 설치

```
# 최소 요구사항
- Node.js 20 LTS 이상
- npm 10+ 또는 yarn 4+ 또는 bun 1.x
- Git 2.40+
- Watchman (macOS, 선택사항이지만 권장)

# 모바일 빌드
- Xcode 16+ (iOS 빌드, macOS 필수)
- Android Studio Hedgehog 이상 + JDK 17
- CocoaPods (iOS)

# Expo CLI
- npx expo (Expo SDK 54에 포함, 별도 글로벌 설치 불필요)
- eas-cli (EAS Build/Submit용)
```

### 2.2 설치 명령

```bash
# Node.js (nvm 사용 권장)
nvm install 20
nvm use 20

# EAS CLI 글로벌 설치
npm install -g eas-cli

# Expo 계정 로그인
eas login
```

---

## 3. 프로젝트 초기화

### 3.1 프로젝트 생성

```bash
# Expo SDK 54 프로젝트 생성 (TypeScript 템플릿)
npx create-expo-app@latest withbowwow --template blank-typescript
cd withbowwow
```

### 3.2 핵심 패키지 설치

```bash
# Navigation
npx expo install react-native-screens react-native-safe-area-context
npm install @react-navigation/native @react-navigation/bottom-tabs @react-navigation/native-stack

# State Management
npm install zustand
npm install @tanstack/react-query

# Styling
npm install nativewind tailwindcss
npx expo install react-native-reanimated@~3.16.0

# HTTP
npm install axios

# 지도 (네이버 지도)
npx expo install @mj-studio/react-native-naver-map

# GPS / 백그라운드
npx expo install expo-location expo-task-manager

# 카메라 / 이미지
npx expo install expo-image-picker

# 푸시 알림
npx expo install expo-notifications expo-device expo-constants

# 보안 저장소
npx expo install expo-secure-store

# 소셜 로그인
npm install @react-native-kakao/core
npx expo install expo-apple-authentication expo-auth-session expo-crypto
```

### 3.3 Tailwind CSS 설정

```bash
# tailwind.config.js 생성
npx tailwindcss init
```

```javascript
// tailwind.config.js
module.exports = {
  content: ["./app/**/*.{js,jsx,ts,tsx}", "./components/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        primary: '#FF6B35',
        secondary: '#4ECDC4',
        background: '#FFF8F0',
        'text-primary': '#2D1B0E',
      },
    },
  },
  plugins: [],
};
```

---

## 4. 중요: Development Build 필수

### 4.1 왜 Expo Go를 쓸 수 없는가

아래 라이브러리들은 **Expo Go에서 동작하지 않습니다**:

| 라이브러리 | Expo Go | Development Build |
|-----------|---------|-------------------|
| @mj-studio/react-native-naver-map | X | O |
| expo-location (백그라운드) | X | O |
| expo-task-manager (Android) | X | O |
| @react-native-kakao/core | X | O |
| expo-notifications (SDK 53+) | X | O |

> **결론: 프로젝트 시작부터 Development Build를 사용해야 합니다.**

### 4.2 EAS Build 설정

```bash
# EAS 프로젝트 초기화
eas init

# eas.json 생성/수정
```

```json
// eas.json
{
  "cli": {
    "version": ">= 12.0.0",
    "appVersionSource": "remote"
  },
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": {
        "simulator": false
      },
      "android": {
        "buildType": "apk"
      },
      "env": {
        "EXPO_PUBLIC_API_URL": "http://localhost:8000"
      }
    },
    "development-simulator": {
      "developmentClient": true,
      "distribution": "internal",
      "ios": {
        "simulator": true
      },
      "env": {
        "EXPO_PUBLIC_API_URL": "http://localhost:8000"
      }
    },
    "preview": {
      "distribution": "internal",
      "env": {
        "EXPO_PUBLIC_API_URL": "https://withbowwow-api-staging.onrender.com"
      }
    },
    "production": {
      "autoIncrement": true,
      "env": {
        "EXPO_PUBLIC_API_URL": "https://withbowwow-api.onrender.com"
      }
    }
  },
  "submit": {
    "production": {
      "ios": {
        "appleId": "your-apple-id@email.com",
        "ascAppId": "your-asc-app-id"
      },
      "android": {
        "serviceAccountKeyPath": "./google-service-account.json"
      }
    }
  }
}
```

### 4.3 빌드 명령

```bash
# iOS 시뮬레이터용 개발 빌드
eas build --profile development-simulator --platform ios

# 실제 기기용 개발 빌드 (iOS + Android)
eas build --profile development --platform all

# 빌드 완료 후 개발 서버 실행
npx expo start --dev-client
```

---

## 5. app.json / app.config.ts 설정

```typescript
// app.config.ts
import { ExpoConfig, ConfigContext } from 'expo/config';

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: '멍이랑',
  slug: 'withbowwow',
  version: '0.1.0',
  orientation: 'portrait',
  icon: './assets/icon.png',
  scheme: 'withbowwow',
  userInterfaceStyle: 'light',

  ios: {
    bundleIdentifier: 'com.withbowwow.app',
    supportsTablet: false,
    infoPlist: {
      NSLocationWhenInUseUsageDescription: '산책 경로를 기록하기 위해 위치 권한이 필요합니다.',
      NSLocationAlwaysAndWhenInUseUsageDescription: '백그라운드에서도 산책을 기록하기 위해 항상 위치 권한이 필요합니다.',
      NSCameraUsageDescription: '산책 중 사진을 촬영하기 위해 카메라 권한이 필요합니다.',
      NSPhotoLibraryUsageDescription: '산책 사진을 저장하기 위해 갤러리 권한이 필요합니다.',
      UIBackgroundModes: ['location', 'fetch', 'remote-notification'],
    },
  },

  android: {
    package: 'com.withbowwow.app',
    adaptiveIcon: {
      foregroundImage: './assets/adaptive-icon.png',
      backgroundColor: '#FF6B35',
    },
    permissions: [
      'ACCESS_FINE_LOCATION',
      'ACCESS_COARSE_LOCATION',
      'ACCESS_BACKGROUND_LOCATION',
      'CAMERA',
      'READ_EXTERNAL_STORAGE',
      'RECEIVE_BOOT_COMPLETED',
      'VIBRATE',
    ],
  },

  plugins: [
    'expo-router',
    'expo-secure-store',
    [
      'expo-location',
      {
        locationAlwaysAndWhenInUsePermission: '백그라운드에서도 산책을 기록하기 위해 항상 위치 권한이 필요합니다.',
        isAndroidBackgroundLocationEnabled: true,
        isAndroidForegroundServiceEnabled: true,
      },
    ],
    [
      'expo-notifications',
      {
        icon: './assets/notification-icon.png',
        color: '#FF6B35',
      },
    ],
    [
      'expo-image-picker',
      {
        photosPermission: '산책 사진을 선택하기 위해 갤러리 접근이 필요합니다.',
        cameraPermission: '산책 중 사진을 촬영하기 위해 카메라 접근이 필요합니다.',
      },
    ],
    [
      '@mj-studio/react-native-naver-map',
      {
        client_id: process.env.EXPO_PUBLIC_NAVER_MAP_CLIENT_ID,
      },
    ],
    [
      '@react-native-kakao/core',
      {
        nativeAppKey: process.env.EXPO_PUBLIC_KAKAO_NATIVE_KEY,
        ios: {
          handleKakaoOpenUrl: true,
        },
      },
    ],
  ],

  extra: {
    eas: {
      projectId: 'your-eas-project-id',
    },
  },
});
```

---

## 6. 환경 변수

### 6.1 .env (로컬 개발용)

```env
# API
EXPO_PUBLIC_API_URL=http://localhost:8000

# 지도
EXPO_PUBLIC_NAVER_MAP_CLIENT_ID=your-naver-map-client-id

# 소셜 로그인
EXPO_PUBLIC_KAKAO_NATIVE_KEY=your-kakao-native-app-key
EXPO_PUBLIC_NAVER_CLIENT_ID=your-naver-client-id
```

### 6.2 환경별 분리

| 환경 | API URL | 용도 |
|------|---------|------|
| **local** | `http://localhost:8000` | 로컬 개발 |
| **staging** | `https://withbowwow-api-staging.onrender.com` | 테스트 |
| **production** | `https://withbowwow-api.onrender.com` | 실서비스 |

> `eas.json`의 각 빌드 프로필에서 `env` 블록으로 환경별 변수를 주입합니다.

---

## 7. GPS 트래킹 최적화 (배터리)

산책 앱의 핵심 — 배터리 소모를 줄이면서 정확한 경로를 기록해야 합니다.

### 7.1 권장 설정

```typescript
// hooks/useWalkTracking.ts
import * as Location from 'expo-location';
import * as TaskManager from 'expo-task-manager';

const WALK_TRACKING_TASK = 'walk-background-tracking';

// 반드시 글로벌 스코프에서 정의 (컴포넌트 밖)
TaskManager.defineTask(WALK_TRACKING_TASK, ({ data, error }) => {
  if (error) return;
  const { locations } = data as { locations: Location.LocationObject[] };
  // Zustand store에 경로 포인트 추가
});

// 산책 시작 시 호출
export async function startWalkTracking() {
  await Location.startLocationUpdatesAsync(WALK_TRACKING_TASK, {
    accuracy: Location.Accuracy.Balanced,    // High 대신 Balanced 권장
    timeInterval: 10000,                     // 10초마다 (5초 → 10초로 완화)
    distanceInterval: 10,                    // 10m 이동 시에만 업데이트
    deferredUpdatesInterval: 15000,          // 15초 단위 배치 처리
    showsBackgroundLocationIndicator: true,  // iOS 상단 파란 바
    foregroundService: {                     // Android 알림
      notificationTitle: '멍이랑 - 산책 중',
      notificationBody: '산책을 기록하고 있습니다 🐾',
      notificationColor: '#FF6B35',
    },
    pausesUpdatesAutomatically: false,       // 자동 일시정지 비활성화
  });
}
```

### 7.2 배터리 비교

| 설정 | 예상 배터리 소모 (1시간) | 정확도 |
|------|------------------------|--------|
| Accuracy.Highest + 5초 | ~15% | 1~3m |
| **Accuracy.Balanced + 10초** | **~5~8%** | **5~10m** |
| Accuracy.Low + 30초 | ~2~3% | 50~100m |

> 산책 앱에는 **Balanced + 10초**가 최적. 경로가 자연스럽고 배터리 소모가 적습니다.

---

## 8. 테스트 빌드 배포 (Test Version)

### 8.1 iOS — TestFlight

```bash
# 1. 프로덕션 빌드
eas build --profile production --platform ios

# 2. App Store Connect에 제출
eas submit --platform ios

# 3. 또는 한 번에 (빌드 + 제출)
npx testflight
```

- Apple Developer 계정 필요 ($99/년)
- Internal Testing: 팀 멤버 최대 100명, 심사 불필요, ~10분 후 테스트 가능
- External Testing: 최대 10,000명, 간단한 심사 필요 (1~2일)

### 8.2 Android — Internal Testing

```bash
# 1. AAB 빌드
eas build --profile production --platform android

# 2. Google Play Console에 제출
eas submit --platform android
```

- Google Play Developer 계정 필요 ($25 일회성)
- Internal Testing Track: 이메일로 테스터 초대, Play Store 비공개 링크
- 심사 불필요, 즉시 배포

### 8.3 개발 중 팀 내 테스트 (심사 없이)

```bash
# Ad-hoc 빌드 (TestFlight/Play Store 없이 직접 설치)
eas build --profile preview --platform all
```

- iOS: 테스트 기기의 UDID를 Apple Developer 포털에 등록 필요
- Android: APK 직접 설치 (sideload)
- QR 코드로 다운로드 링크 공유 가능

---

## 9. 작업 시 주의사항

### 9.1 Expo Go 사용 불가

이 프로젝트는 네이티브 모듈(@mj-studio/react-native-naver-map, @react-native-kakao/core)을 사용하므로 **Expo Go에서 실행할 수 없습니다**. 반드시 Development Build를 사용하세요.

### 9.2 NativeWind v4 + Reanimated 버전 충돌

- NativeWind v4.1은 **Reanimated v3**과만 호환
- Reanimated v4를 설치하면 NativeWind가 깨짐
- `npx expo install react-native-reanimated@~3.16.0`으로 버전 고정

### 9.3 New Architecture

- Expo SDK 54는 New Architecture가 기본 활성화
- @mj-studio/react-native-naver-map v2.x는 New Architecture **필수**
- SDK 54에서는 선택적 비활성화 가능, SDK 55부터는 강제 적용

### 9.4 백그라운드 GPS — 플랫폼 차이

| | iOS | Android |
|--|-----|---------|
| 앱 종료 후 GPS | 재시작 시 자동 재개 | 앱 열어야 재개 |
| 배터리 최적화 | OS가 자동 관리 | 제조사별 다름 (삼성: 배터리 최적화 예외 필요) |
| 포그라운드 서비스 | 상단 파란 바 | 알림 영역에 서비스 표시 |

### 9.5 API 키 발급 필요 목록

| 서비스 | 발급처 | 용도 |
|--------|--------|------|
| 네이버 지도 API | [Naver Cloud Platform](https://www.ncloud.com/) | 지도 표시 |
| 카카오 로그인 | [Kakao Developers](https://developers.kakao.com/) | 소셜 로그인 |
| 네이버 로그인 | [Naver Developers](https://developers.naver.com/) | 소셜 로그인 |
| Apple 로그인 | Apple Developer Portal | 소셜 로그인 |
| Firebase | [Firebase Console](https://console.firebase.google.com/) | 푸시 알림 |
| Apple Developer | [Apple Developer](https://developer.apple.com/) | TestFlight, 앱 빌드 |
| Google Play | [Google Play Console](https://play.google.com/console/) | 내부 테스트 |

---

*작성일: 2026-02-19*
*버전: 1.0*
