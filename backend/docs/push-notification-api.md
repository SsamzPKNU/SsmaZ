# 푸시 알림 발송 기능 API 명세서

> **Base URL**: `http://192.168.0.11:8000`
> **인증**: 모든 요청에 `Authorization: Bearer {token}` 헤더 또는 httpOnly 쿠키 필요
> **최종 수정일**: 2026-02-12

---

## 목차

1. [개요 - 알림 유형 및 자동 발송](#1-개요---알림-유형-및-자동-발송)
2. [푸시 알림 수신 데이터 형식](#2-푸시-알림-수신-데이터-형식)
3. [알림 이력 조회 API](#3-알림-이력-조회-api)
4. [일정 수정 API](#4-일정-수정-api)
5. [수납 알림 수동 발송 API](#5-수납-알림-수동-발송-api)
6. [앱 알림 화면 구현 가이드](#6-앱-알림-화면-구현-가이드)

---

## 1. 개요 - 알림 유형 및 자동 발송

기존 출결 알림에 더해 4가지 알림 유형이 추가되었습니다.
**자동 발송**은 별도의 프론트엔드 호출 없이, 관련 API 호출 시 백엔드가 자동으로 푸시를 발송합니다.

| 알림 유형 | `data.type` | 트리거 시점 | 발송 대상 |
|-----------|-------------|-------------|-----------|
| 출결 | `attendance` | 키오스크 출석 체크 시 | 해당 학생의 user_id |
| **과제** | `assignment` | 과제 생성 시 (자동) | 반 소속 전체 학생 |
| **일정 변경** | `schedule` | 시간표 수정 시 (자동) | 반 소속 전체 학생 |
| **수납** | `payment` | 수납 생성 시 (자동) + 수동 발송 API | 해당 학생 개별 |
| **메시지** | `message` | 선생님 메시지 발송 시 (자동) | 메시지 수신 학생들 |

### 자동 발송 트리거 API

| 알림 유형 | 트리거 API | 비고 |
|-----------|-----------|------|
| 과제 | `POST /api/assignments` | class_id가 있는 경우만 발송 |
| 과제 | `POST /api/teacher/assignments` | class_id가 있는 경우만 발송 |
| 일정 변경 | `PUT /api/admin/classes/schedules/{schedule_id}` | 변경된 내용을 body에 조합 |
| 수납 | `POST /api/admin/payments` | 해당 학생에게 자동 발송 |
| 메시지 | `POST /api/teacher/messages/send` | 수신 학생들에게 자동 발송 |

> 모든 자동 발송은 `try/except`로 감싸져 있어, 푸시 실패해도 본 기능(과제 생성, 수납 등)은 정상 처리됩니다.

---

## 2. 푸시 알림 수신 데이터 형식

앱에서 FCM 메시지를 수신할 때 아래 형식으로 데이터가 전달됩니다.

### 2-1. 과제 알림

과제가 생성되면 해당 반의 학생들에게 발송됩니다.

```json
{
  "notification": {
    "title": "새 과제가 등록되었습니다",
    "body": "A반 - 중간고사 대비 문제풀이"
  },
  "data": {
    "type": "assignment",
    "assignmentId": "21"
  }
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `data.type` | `string` | `"assignment"` 고정 |
| `data.assignmentId` | `string` | 과제 ID (상세 조회 시 사용) |

### 2-2. 일정 변경 알림

시간표가 수정되면 해당 반의 학생들에게 발송됩니다.

```json
{
  "notification": {
    "title": "수업 일정이 변경되었습니다",
    "body": "A반 - 15:00 → 17:00, ~16:30 → ~19:00"
  },
  "data": {
    "type": "schedule",
    "scheduleId": "2"
  }
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `data.type` | `string` | `"schedule"` 고정 |
| `data.scheduleId` | `string` | 시간표 ID |

### 2-3. 수납 알림

수납이 등록되거나 수동 발송 시 해당 학생에게 발송됩니다.

```json
{
  "notification": {
    "title": "수납 안내",
    "body": "수강료 납부 안내가 등록되었습니다"
  },
  "data": {
    "type": "payment",
    "paymentId": "71"
  }
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `data.type` | `string` | `"payment"` 고정 |
| `data.paymentId` | `string` | 수납 ID |

### 2-4. 메시지 알림

선생님이 메시지를 발송하면 대상 학생들에게 발송됩니다.

```json
{
  "notification": {
    "title": "새 메시지가 도착했습니다",
    "body": "윤도이 선생님이 메시지를 보냈습니다"
  },
  "data": {
    "type": "message"
  }
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `data.type` | `string` | `"message"` 고정 |

> 메시지 본문은 보안을 위해 push body에 포함되지 않습니다. 앱 안에서 메시지 목록 API를 통해 확인하세요.

### data.type 요약

| `data.type` | 알림 종류 | 앱 이동 화면 (권장) |
|-------------|----------|-------------------|
| `attendance` | 출결 알림 | 출결 현황 화면 |
| `assignment` | 과제 알림 | 과제 상세 화면 (`assignmentId` 활용) |
| `schedule` | 일정 변경 | 시간표 화면 |
| `payment` | 수납 알림 | 수납 내역 화면 (`paymentId` 활용) |
| `message` | 메시지 알림 | 메시지 목록 화면 |

---

## 3. 알림 이력 조회 API

로그인한 사용자의 푸시 알림 이력을 조회합니다. 앱 내 "알림 목록" 화면에 사용합니다.

| 항목 | 값 |
|------|-----|
| **Method** | `GET` |
| **URL** | `/api/student/notifications` |
| **권한** | 로그인 사용자 (ADMIN, TEACHER, STUDENT 모두 가능) |
| **Status** | `200 OK` |

### Query Parameters

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| `page` | `int` | X | `1` | 페이지 번호 (1부터 시작) |
| `size` | `int` | X | `20` | 페이지당 항목 수 (최대 100) |

### Request 예시

```
GET /api/student/notifications?page=1&size=20
Authorization: Bearer {token}
```

### Response

```json
{
  "items": [
    {
      "id": 15,
      "user_id": 23,
      "title": "새 과제가 등록되었습니다",
      "body": "A반 - 중간고사 대비 문제풀이",
      "notification_type": "assignment",
      "data": {
        "type": "assignment",
        "assignmentId": "21"
      },
      "status": "success",
      "created_at": "2026-02-12T14:12:38"
    },
    {
      "id": 14,
      "user_id": 23,
      "title": "등원 알림",
      "body": "김철수 학생이 등원했습니다. (14:30)",
      "notification_type": "attendance",
      "data": {
        "type": "attendance",
        "student_id": "1",
        "action": "check_in",
        "time": "14:30"
      },
      "status": "success",
      "created_at": "2026-02-12T14:00:00"
    }
  ],
  "total": 25,
  "page": 1,
  "size": 20
}
```

### Response 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `items` | `array` | 알림 이력 목록 |
| `items[].id` | `int` | 알림 이력 고유 ID |
| `items[].user_id` | `int` | 수신 사용자 ID |
| `items[].title` | `string` | 알림 제목 |
| `items[].body` | `string\|null` | 알림 본문 |
| `items[].notification_type` | `string\|null` | 알림 유형 (`attendance`, `assignment`, `schedule`, `payment`, `message`) |
| `items[].data` | `object\|null` | 알림 data 페이로드 (푸시 수신 시 data와 동일) |
| `items[].status` | `string` | 발송 상태 (`success`, `failed`, `skipped`) |
| `items[].created_at` | `string` | 발송 시각 (ISO 8601) |
| `total` | `int` | 전체 알림 수 |
| `page` | `int` | 현재 페이지 |
| `size` | `int` | 페이지 크기 |

### status 값 설명

| 값 | 의미 |
|----|------|
| `success` | 1개 이상의 기기에 발송 성공 |
| `failed` | 모든 기기 발송 실패 |
| `skipped` | FCM 토큰 미등록 또는 Firebase 미설정 |

---

## 4. 일정 수정 API

시간표를 수정합니다. 수정 시 해당 반 학생들에게 일정 변경 알림이 자동 발송됩니다.

| 항목 | 값 |
|------|-----|
| **Method** | `PUT` |
| **URL** | `/api/admin/classes/schedules/{schedule_id}` |
| **권한** | 로그인 사용자 (ADMIN) |
| **Status** | `200 OK` |

### Path Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `schedule_id` | `int` | O | 시간표 ID |

### Request Body

```json
{
  "day_of_week": "화",
  "start_time": "17:00:00",
  "end_time": "19:00:00"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `day_of_week` | `string` | X | 요일 (월, 화, 수, 목, 금, 토, 일) |
| `start_time` | `string` | X | 시작 시간 (HH:MM:SS) |
| `end_time` | `string` | X | 종료 시간 (HH:MM:SS) |

> 변경할 필드만 보내면 됩니다. 보내지 않은 필드는 기존 값이 유지됩니다.

### Response

```json
{
  "schedule_id": 2,
  "class_id": 1,
  "day_of_week": "화",
  "start_time": "17:00:00",
  "end_time": "19:00:00",
  "created_at": "2026-01-30T14:32:41"
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| `schedule_id` | `int` | 시간표 ID |
| `class_id` | `int` | 반 ID |
| `day_of_week` | `string` | 요일 |
| `start_time` | `string` | 시작 시간 |
| `end_time` | `string` | 종료 시간 |
| `created_at` | `string` | 생성 시간 |

### 에러 응답

| Status | 상황 |
|--------|------|
| `401` | 인증 토큰 없음/만료 |
| `403` | 다른 학원의 시간표 수정 시도 |
| `404` | 존재하지 않는 schedule_id |

---

## 5. 수납 알림 수동 발송 API

특정 수납 건에 대해 해당 학생에게 수동으로 푸시 알림을 발송합니다.
수납 생성 시 자동 발송되지만, 미납 독촉 등의 용도로 재발송할 때 사용합니다.

| 항목 | 값 |
|------|-----|
| **Method** | `POST` |
| **URL** | `/api/admin/payments/{payment_id}/notify` |
| **권한** | 로그인 사용자 (ADMIN) |
| **Status** | `200 OK` |

### Path Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `payment_id` | `int` | O | 수납 ID |

### Request Body (선택)

```json
{
  "title": "수납 독촉",
  "body": "이번 달 수강료 납부를 확인해주세요"
}
```

| 필드 | 타입 | 필수 | 기본값 | 설명 |
|------|------|------|--------|------|
| `title` | `string` | X | `"수납 안내"` | 알림 제목 |
| `body` | `string` | X | `"수강료 납부 안내가 등록되었습니다"` | 알림 본문 |

> Request Body를 생략하면 기본값으로 발송됩니다.

### Response

```json
{
  "success": true,
  "message": "수납 알림이 발송되었습니다"
}
```

### 에러 응답

| Status | 상황 |
|--------|------|
| `401` | 인증 토큰 없음/만료 |
| `404` | 존재하지 않는 payment_id 또는 학생 정보 없음 |

---

## 6. 앱 알림 화면 구현 가이드

### 알림 목록 화면

```
┌─────────────────────────────────────┐
│  알림                          전체  │
├─────────────────────────────────────┤
│                                     │
│  📚 새 과제가 등록되었습니다           │
│  A반 - 중간고사 대비 문제풀이          │
│  2분 전                              │
│                                     │
│  📅 수업 일정이 변경되었습니다          │
│  A반 - 15:00 → 17:00                │
│  1시간 전                            │
│                                     │
│  💰 수납 안내                        │
│  수강료 납부 안내가 등록되었습니다       │
│  3시간 전                            │
│                                     │
│  ✅ 등원 알림                        │
│  김철수 학생이 등원했습니다. (14:30)    │
│  어제                                │
│                                     │
└─────────────────────────────────────┘
```

### 구현 포인트

1. **알림 목록**: `GET /api/student/notifications` 호출하여 이력 표시
2. **무한 스크롤/페이지네이션**: `page` 파라미터로 추가 로드
3. **알림 터치 시 화면 이동**: `notification_type` (또는 `data.type`)에 따라 분기
   - `attendance` → 출결 현황 화면
   - `assignment` → 과제 상세 (data의 `assignmentId` 활용)
   - `schedule` → 시간표 화면
   - `payment` → 수납 내역 (data의 `paymentId` 활용)
   - `message` → 메시지 목록
4. **푸시 수신 시**: `onMessageReceived()`에서 `data.type`으로 분기하여 적절한 화면으로 이동

### 푸시 수신 처리 흐름 (앱)

```
FCM 메시지 수신
  ├─ 앱 포그라운드: onMessageReceived()에서 직접 알림 표시
  └─ 앱 백그라운드: 시스템 알림 자동 표시
       └─ 알림 터치 시: data.type으로 화면 이동 분기

data.type 분기:
  ├─ "attendance"  → 출결 현황
  ├─ "assignment"  → 과제 상세 (assignmentId)
  ├─ "schedule"    → 시간표
  ├─ "payment"     → 수납 내역 (paymentId)
  └─ "message"     → 메시지 목록
```
