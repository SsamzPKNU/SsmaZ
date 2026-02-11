# FCM 푸시 알림 API 명세서

> **Base URL**: `http://192.168.0.11:8000`
> **인증**: 모든 요청에 `Authorization: Bearer {token}` 헤더 또는 httpOnly 쿠키 필요
> **최종 수정일**: 2026-02-11

---

## 목차

1. [FCM 토큰 등록](#1-fcm-토큰-등록)
2. [FCM 토큰 삭제](#2-fcm-토큰-삭제)
3. [푸시 알림 수신 데이터 형식](#3-푸시-알림-수신-데이터-형식)
4. [연동 흐름](#4-연동-흐름)

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

## Android 앱 참고사항

- FCM 토큰은 `FirebaseMessaging.getInstance().token`으로 발급
- 토큰 갱신은 `FirebaseMessagingService.onNewToken()`에서 처리
- `data` 메시지 수신: `FirebaseMessagingService.onMessageReceived()`
- `notification` + `data` 함께 오므로, 앱이 포그라운드일 때는 `onMessageReceived()`에서 직접 알림 표시 필요
