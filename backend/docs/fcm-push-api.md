# FCM 푸시 알림 API 명세서

> **Base URL**: `http://192.168.0.11:8000`
> **인증**: 모든 요청에 `Authorization: Bearer {token}` 헤더 또는 httpOnly 쿠키 필요
> **최종 수정일**: 2026-02-12

---

## 목차

1. [FCM 토큰 등록](#1-fcm-토큰-등록)
2. [FCM 토큰 삭제](#2-fcm-토큰-삭제)
3. [푸시 알림 수신 데이터 형식](#3-푸시-알림-수신-데이터-형식)
4. [연동 흐름](#4-연동-흐름)
5. [알림 이력 관리](#5-알림-이력-관리)
6. [Firebase 프로젝트 셋업 가이드](#6-firebase-프로젝트-셋업-가이드)

---

## 1. FCM 토큰 등록

앱 로그인 후 Firebase에서 발급받은 FCM 토큰을 서버에 등록합니다.

| 항목 | 값 |
|------|-----|
| **Method** | `POST` |
| **URL** | `/api/student/fcm-token` |
| **권한** | 로그인 사용자 (ADMIN, TEACHER, STUDENT 모두 가능) |
| **Status** | `200 OK` |

### Request Body

```json
{
  "fcm_token": "dK8xH2...(Firebase에서 발급받은 토큰)",
  "device_info": {
    "platform": "android",
    "os_version": "14",
    "app_version": "1.0.0",
    "device_model": "Galaxy S24"
  }
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `fcm_token` | `string` | O | Firebase에서 발급받은 디바이스 토큰 |
| `device_info` | `object` | X | 기기 정보 (디버깅/분석용) |
| `device_info.platform` | `string` | X | 플랫폼 (`android`, `ios`) |
| `device_info.os_version` | `string` | X | OS 버전 |
| `device_info.app_version` | `string` | X | 앱 버전 |
| `device_info.device_model` | `string` | X | 기기 모델명 |

> `device_info`는 선택사항입니다. `fcm_token`만 보내도 동작합니다.

### Response

```json
{
  "success": true,
  "message": "FCM 토큰이 등록되었습니다."
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `success` | `boolean` | 처리 성공 여부 |
| `message` | `string` | 처리 결과 메시지 |

### 동작 방식

- **같은 토큰이 이미 등록된 경우**: user_id와 device_info를 업데이트합니다 (upsert).
- **한 사용자가 여러 기기에서 로그인**: 기기별로 다른 토큰이 각각 저장됩니다.
- **호출 시점**: 앱 로그인 직후 + FCM 토큰 갱신 시마다 호출해야 합니다.

---

## 2. FCM 토큰 삭제

앱 로그아웃 시 등록된 FCM 토큰을 삭제합니다.

| 항목 | 값 |
|------|-----|
| **Method** | `DELETE` |
| **URL** | `/api/student/fcm-token` |
| **권한** | 로그인 사용자 (ADMIN, TEACHER, STUDENT 모두 가능) |
| **Status** | `200 OK` |

### Request Body

```json
{
  "fcm_token": "dK8xH2...(삭제할 FCM 토큰)"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `fcm_token` | `string` | O | 삭제할 FCM 토큰 |

### Response (성공)

```json
{
  "success": true,
  "message": "FCM 토큰이 삭제되었습니다."
}
```

### Response (토큰 없음)

```json
{
  "success": false,
  "message": "해당 FCM 토큰을 찾을 수 없습니다."
}
```

---

## 3. 푸시 알림 수신 데이터 형식

### 출결 알림 (키오스크 등원/하원 시 자동 발송)

학생이 키오스크에서 출석 체크하면 해당 학생의 user_id에 연결된 모든 기기로 푸시 알림이 발송됩니다.

#### 등원 알림

```json
{
  "notification": {
    "title": "등원 알림",
    "body": "김민수 학생이 등원했습니다. (14:30)"
  },
  "data": {
    "type": "attendance",
    "student_id": "1",
    "action": "check_in",
    "time": "14:30"
  }
}
```

#### 하원 알림

```json
{
  "notification": {
    "title": "하원 알림",
    "body": "김민수 학생이 하원했습니다. (17:00)"
  },
  "data": {
    "type": "attendance",
    "student_id": "1",
    "action": "check_out",
    "time": "17:00"
  }
}
```

### data 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| `type` | `string` | 알림 종류 (`attendance`) |
| `student_id` | `string` | 학생 ID |
| `action` | `string` | `check_in` (등원) / `check_out` (하원) |
| `time` | `string` | 처리 시간 (HH:MM) |

> `data` 필드의 모든 값은 **string** 타입입니다. 필요 시 앱에서 파싱하세요.

---

## 4. 연동 흐름

### 앱 시작/로그인 시

```
1. 앱 시작
2. Firebase SDK 초기화 → FCM 토큰 발급
3. 서버 로그인 (POST /auth/login) → JWT 토큰 수신
4. FCM 토큰 등록 (POST /api/student/fcm-token)
```

### FCM 토큰 갱신 시

```
1. Firebase onTokenRefresh 콜백 발생
2. 새 토큰으로 재등록 (POST /api/student/fcm-token)
   → 기존 토큰은 upsert로 자동 교체됨
```

### 로그아웃 시

```
1. FCM 토큰 삭제 (DELETE /api/student/fcm-token)
2. 서버 로그아웃 (POST /auth/logout)
```

### 출결 알림 수신 흐름

```
학생 키오스크 출석 체크
  → 백엔드 출결 처리 (POST /api/kiosk/attendance)
  → 백엔드에서 FCM 푸시 발송
  → 앱에서 알림 수신 (notification + data)
```

---

## 5. 알림 이력 관리

모든 푸시 알림 발송 내역은 `notification_history` 테이블에 자동 기록됩니다.

### 저장 구조

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | `int` | 이력 고유 ID |
| `user_id` | `int` | 수신 대상 사용자 ID |
| `title` | `string` | 알림 제목 (예: "등원 알림") |
| `body` | `string` | 알림 본문 (예: "김민수 학생이 등원했습니다. (14:30)") |
| `notification_type` | `string` | 알림 유형 (`attendance`, `assignment`, `schedule`, `payment` 등) |
| `data` | `JSON` | 알림 data 페이로드 전체 |
| `status` | `string` | 발송 상태 |
| `created_at` | `timestamp` | 발송 시각 |

### 발송 상태 (`status`)

| 값 | 의미 |
|-----|------|
| `success` | 1개 이상의 기기에 발송 성공 |
| `failed` | 모든 기기 발송 실패 (토큰 만료 등) |
| `skipped` | 발송 건너뜀 (등록된 FCM 토큰 없음 또는 Firebase 미설정) |

### 동작 원리

```
send_to_user(user_id, title, body, data) 호출 시:

  ├─ FCM 토큰 없음 → status: "skipped" 기록
  ├─ Firebase 미초기화 → status: "skipped" 기록
  └─ 발송 시도
       ├─ 1개 이상 성공 → status: "success" 기록
       └─ 전부 실패 → status: "failed" 기록
```

> 프론트엔드에서는 별도 호출 없이, 알림 발송 시 백엔드가 자동으로 이력을 저장합니다.
> 향후 "알림 내역 조회" API가 필요하면 백엔드에 요청해주세요.

---

## 6. Firebase 프로젝트 셋업 가이드

FCM 푸시 알림을 실제로 동작시키려면 **백엔드**와 **프론트엔드(앱)** 양쪽 모두 Firebase 설정이 필요합니다.

### 6-1. Firebase 프로젝트 생성

1. [Firebase Console](https://console.firebase.google.com/) 접속
2. **프로젝트 추가** → 프로젝트 이름 입력 (예: `ssmaz-academy`)
3. Google Analytics는 선택사항 (꺼도 됨)
4. 프로젝트 생성 완료

### 6-2. 백엔드: 서비스 계정 키 발급

백엔드 서버가 FCM 메시지를 발송하려면 **서비스 계정 키**(JSON)가 필요합니다.

#### 발급 방법

1. Firebase Console → **프로젝트 설정** (톱니바퀴 아이콘)
2. **서비스 계정** 탭 클릭
3. **새 비공개 키 생성** 버튼 클릭
4. JSON 파일이 다운로드됨 (예: `ssmaz-academy-firebase-adminsdk-xxxxx.json`)



#### 서비스 계정 키 JSON 예시 (구조 참고)

```json
{
  "type": "service_account",
  "project_id": "ssmaz-academy",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxxxx@ssmaz-academy.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

### 6-3. 프론트엔드(앱): Firebase 설정

#### Android

1. Firebase Console → **프로젝트 설정** → **일반** 탭
2. **앱 추가** → Android 아이콘 클릭
3. 패키지 이름 입력 (예: `com.ssmaz.app`)
4. `google-services.json` 다운로드 → `android/app/` 에 배치
5. Gradle 설정:

   ```gradle
   // android/build.gradle
   dependencies {
       classpath 'com.google.gms:google-services:4.4.0'
   }

   // android/app/build.gradle
   apply plugin: 'com.google.gms.google-services'
   dependencies {
       implementation 'com.google.firebase:firebase-messaging:24.0.0'
   }
   ```



┌─────────────────────────────────────────────────────────────────┐
│                     Firebase 프로젝트                             │
│                    (ssmaz-academy)                               │
├────────────────────────┬────────────────────────────────────────┤
│                        │                                        │
│  서비스 계정 키 (JSON)    │    google-services.json /              │
│  → 백엔드 서버           │    GoogleService-Info.plist             │
│                        │    → 프론트엔드 앱                       │
├────────────────────────┼────────────────────────────────────────┤
│                        │                                        │
│  백엔드 (FastAPI)        │    프론트엔드 (앱)                      │
│  - 서비스 계정으로 인증     │    - Firebase SDK 초기화               │
│  - FCM 메시지 발송       │    - FCM 토큰 발급                      │
│                        │    - 토큰을 서버에 등록                    │
│                        │    - 푸시 알림 수신                       │
└────────────────────────┴────────────────────────────────────────┘

알림 흐름:
  학생 키오스크 출석
    → 백엔드: 출결 처리
    → 백엔드: Students.user_id로 학부모 계정 식별
    → 백엔드: fcm_tokens에서 해당 user_id의 토큰 조회
    → 백엔드: Firebase 서비스 계정 권한으로 FCM 발송
    → 백엔드: notification_history에 이력 저장
    → 학부모 앱: 푸시 알림 수신
```

### 6-5. 필요한 파일 체크리스트

| 구분 | 파일 | 발급처 | 용도 |
|------|------|--------|------|
| **백엔드** | `firebase-service-account.json` | Firebase Console → 서비스 계정 → 새 비공개 키 생성 | 서버에서 FCM 메시지 발송 권한 |
| **Android** | `google-services.json` | Firebase Console → 프로젝트 설정 → 일반 → Android 앱 | 앱에서 Firebase SDK 초기화 |
| **iOS** | `GoogleService-Info.plist` | Firebase Console → 프로젝트 설정 → 일반 → iOS 앱 | 앱에서 Firebase SDK 초기화 |
| **iOS** | APNs 인증 키 (.p8) | Apple Developer → Keys | Firebase → Apple 푸시 연동 |

---

## Android 앱 참고사항

- FCM 토큰은 `FirebaseMessaging.getInstance().token`으로 발급
- 토큰 갱신은 `FirebaseMessagingService.onNewToken()`에서 처리
- `data` 메시지 수신: `FirebaseMessagingService.onMessageReceived()`
- `notification` + `data` 함께 오므로, 앱이 포그라운드일 때는 `onMessageReceived()`에서 직접 알림 표시 필요
