# 강사 출결 관리 API 명세서

> **Base URL**: `http://localhost:8000`
> **인증**: 모든 요청에 `Authorization: Bearer {token}` 헤더 필요
> **최종 수정일**: 2026-02-10

---

## 목차

1. [출근 처리](#1-출근-처리)
2. [퇴근 처리](#2-퇴근-처리)
3. [출결 기록 조회](#3-출결-기록-조회)
4. [근무 요약 조회](#4-근무-요약-조회)
5. [관리자 - 전체 강사 출결 현황](#5-관리자---전체-강사-출결-현황)
6. [관리자 - 출결 승인](#6-관리자---출결-승인)
7. [공통 타입 정의](#7-공통-타입-정의)

---

## 1. 출근 처리

선생님 본인의 출근을 기록합니다.

| 항목 | 값 |
|------|-----|
| **Method** | `POST` |
| **URL** | `/teachers/attendance/check-in` |
| **권한** | TEACHER |
| **Status** | `201 Created` |

### Request Body (선택)

```json
{
  "work_date": "2026-02-10",
  "memo": "보충수업 예정"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `work_date` | `string (date)` | X | 근무일 (미입력 시 오늘) |
| `memo` | `string` | X | 출근 메모 |

> body 없이 `POST {}` 로 호출 가능 (오늘 날짜로 출근)

### Response

```json
{
  "id": 4,
  "teacher_id": 2,
  "date": "2026-02-10",
  "check_in_time": "2026-02-10T09:00:00",
  "check_out_time": null,
  "worked_minutes": 0,
  "is_approved": false,
  "approved_by": null,
  "created_at": "2026-02-10T09:00:00",
  "updated_at": null
}
```

### 에러

| Status | 상황 |
|--------|------|
| `400` | 당일 이미 출근 기록이 있음 |
| `403` | TEACHER 권한 아님 |
| `404` | 선생님 정보 없음 |

---

## 2. 퇴근 처리

선생님 본인의 퇴근을 기록합니다. 근무시간(분)이 자동 계산됩니다.

| 항목 | 값 |
|------|-----|
| **Method** | `POST` |
| **URL** | `/teachers/attendance/check-out` |
| **권한** | TEACHER |
| **Status** | `200 OK` |

### Request Body

없음 (빈 body)

### Response

```json
{
  "id": 4,
  "teacher_id": 2,
  "date": "2026-02-10",
  "check_in_time": "2026-02-10T09:00:00",
  "check_out_time": "2026-02-10T18:00:00",
  "worked_minutes": 540,
  "is_approved": false,
  "approved_by": null,
  "created_at": "2026-02-10T09:00:00",
  "updated_at": "2026-02-10T18:00:00"
}
```

### 에러

| Status | 상황 |
|--------|------|
| `400` | 오늘 출근 기록 없음 / 이미 퇴근 처리됨 |
| `403` | TEACHER 권한 아님 |

---

## 3. 출결 기록 조회

특정 강사의 기간별 출결 기록을 조회합니다.

| 항목 | 값 |
|------|-----|
| **Method** | `GET` |
| **URL** | `/teachers/{teacherId}/attendance` |
| **권한** | TEACHER (본인만) 또는 ADMIN |
| **Status** | `200 OK` |

### Path Parameters

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `teacherId` | `int` | 선생님 ID |

### Query Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `startDate` | `string (date)` | X | 조회 시작일 (예: `2026-02-01`) |
| `endDate` | `string (date)` | X | 조회 종료일 (예: `2026-02-28`) |
| `page` | `int` | X | 페이지 번호 (기본값: 1) |
| `limit` | `int` | X | 페이지당 항목 수 (기본값: 20, 최대: 100) |

### 요청 예시

```
GET /teachers/3/attendance?startDate=2026-02-01&endDate=2026-02-28
```

### Response

```json
{
  "records": [
    {
      "id": 4,
      "teacherId": 3,
      "teacherName": "김선생",
      "date": "2026-02-10",
      "check_in_at": "2026-02-10T09:00:00",
      "check_out_at": "2026-02-10T18:00:00",
      "status": "approved",
      "memo": "보충수업",
      "approved": true,
      "workedMinutes": 540
    }
  ],
  "total": 1
}
```

### Response 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `records` | `array` | 출결 기록 목록 |
| `records[].id` | `int` | 기록 ID |
| `records[].teacherId` | `int` | 선생님 ID |
| `records[].teacherName` | `string` | 선생님 이름 |
| `records[].date` | `string (date)` | 근무일 |
| `records[].check_in_at` | `string (datetime) \| null` | 출근 시각 |
| `records[].check_out_at` | `string (datetime) \| null` | 퇴근 시각 |
| `records[].status` | `string` | 출결 상태 ([status 값 참고](#status-값)) |
| `records[].memo` | `string \| null` | 메모 |
| `records[].approved` | `boolean` | 승인 여부 |
| `records[].workedMinutes` | `int` | 근무시간 (분) |
| `total` | `int` | 전체 기록 수 |

---

## 4. 근무 요약 조회

특정 강사의 기간 내 근무 통계를 조회합니다.

| 항목 | 값 |
|------|-----|
| **Method** | `GET` |
| **URL** | `/teachers/{teacherId}/work-summary` |
| **권한** | TEACHER (본인만) 또는 ADMIN |
| **Status** | `200 OK` |

### Path Parameters

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `teacherId` | `int` | 선생님 ID |

### Query Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `startDate` | `string (date)` | **O** | 조회 시작일 |
| `endDate` | `string (date)` | **O** | 조회 종료일 |

### 요청 예시

```
GET /teachers/3/work-summary?startDate=2026-02-01&endDate=2026-02-28
```

### Response

```json
{
  "teacherId": 3,
  "startDate": "2026-02-01",
  "endDate": "2026-02-28",
  "totalDays": 20,
  "totalHours": 160.0,
  "avgHours": 8.0,
  "lateCount": 2,
  "absentCount": 1
}
```

### Response 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `teacherId` | `int` | 선생님 ID |
| `startDate` | `string (date)` | 조회 시작일 |
| `endDate` | `string (date)` | 조회 종료일 |
| `totalDays` | `int` | 총 근무일수 |
| `totalHours` | `float` | 총 근무시간 (시간) |
| `avgHours` | `float` | 일 평균 근무시간 (시간) |
| `lateCount` | `int` | 지각 횟수 |
| `absentCount` | `int` | 결석 횟수 |

---

## 5. 관리자 - 전체 강사 출결 현황

관리자가 전체 강사의 출결 현황을 조회합니다. 두 가지 모드를 지원합니다.

| 항목 | 값 |
|------|-----|
| **Method** | `GET` |
| **URL** | `/admin/teacher-attendance` |
| **권한** | ADMIN |
| **Status** | `200 OK` |

### Query Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `date` | `string (date)` | X | 특정일 조회 (미입력 시 오늘). **미출근 강사도 absent로 포함** |
| `startDate` | `string (date)` | X | 기간 조회 시작일 |
| `endDate` | `string (date)` | X | 기간 조회 종료일 |

> **조회 모드**
> - `date`만 전달 → 해당일 전체 강사 현황 (미출근 = absent 포함)
> - `startDate` + `endDate` 전달 → 기간 내 출결 기록만 반환

### 요청 예시

```
# 특정일 현황 (미출근 강사 포함)
GET /admin/teacher-attendance?date=2026-02-10

# 기간 조회
GET /admin/teacher-attendance?startDate=2026-02-01&endDate=2026-02-10
```

### Response

```json
{
  "records": [
    {
      "id": 4,
      "teacherId": 2,
      "teacherName": "김선생",
      "subject": "수학",
      "date": "2026-02-10",
      "check_in_at": "2026-02-10T09:00:00",
      "check_out_at": "2026-02-10T18:00:00",
      "status": "approved",
      "memo": null,
      "approved": true,
      "workMinutes": 540,
      "workHours": 9.0
    },
    {
      "id": null,
      "teacherId": 3,
      "teacherName": "이선생",
      "subject": "영어",
      "date": "2026-02-10",
      "check_in_at": null,
      "check_out_at": null,
      "status": "absent",
      "memo": null,
      "approved": false,
      "workMinutes": 0,
      "workHours": 0.0
    }
  ],
  "total": 2
}
```

### Response 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `records` | `array` | 출결 현황 목록 |
| `records[].id` | `int \| null` | 기록 ID (미출근 시 `null`) |
| `records[].teacherId` | `int` | 선생님 ID |
| `records[].teacherName` | `string` | 선생님 이름 |
| `records[].subject` | `string \| null` | 담당 과목 |
| `records[].date` | `string (date)` | 근무일 |
| `records[].check_in_at` | `string (datetime) \| null` | 출근 시각 |
| `records[].check_out_at` | `string (datetime) \| null` | 퇴근 시각 |
| `records[].status` | `string` | 출결 상태 ([status 값 참고](#status-값)) |
| `records[].memo` | `string \| null` | 메모 |
| `records[].approved` | `boolean` | 승인 여부 |
| `records[].workMinutes` | `int` | 근무시간 (분) |
| `records[].workHours` | `float` | 근무시간 (시간, 소수점 2자리) |
| `total` | `int` | 전체 레코드 수 |

---

## 6. 관리자 - 출결 승인

관리자가 특정 출결 기록을 승인합니다.

| 항목 | 값 |
|------|-----|
| **Method** | `PATCH` |
| **URL** | `/admin/attendance/{attendanceId}/approve` |
| **권한** | ADMIN |
| **Status** | `200 OK` |

### Path Parameters

| 파라미터 | 타입 | 설명 |
|----------|------|------|
| `attendanceId` | `int` | 출결 기록 ID |

### Request Body

없음

### Response

```json
{
  "success": true,
  "message": "승인되었습니다"
}
```

### Response 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `success` | `boolean` | 성공 여부 |
| `message` | `string` | 결과 메시지 |

### 에러

| Status | 상황 |
|--------|------|
| `400` | 이미 승인된 기록 |
| `403` | 해당 기록에 대한 권한 없음 (다른 학원 소속) |
| `404` | 출결 기록을 찾을 수 없음 |

---

## 7. 공통 타입 정의

### status 값

출결 상태를 나타내는 문자열입니다.

| 값 | 설명 |
|----|------|
| `checked_in` | 출근 완료 (퇴근 전) |
| `checked_out` | 퇴근 완료 (미승인) |
| `late` | 지각 |
| `absent` | 결석 / 미출근 |
| `leave` | 휴가 |
| `approved` | 승인 완료 |
| `pending` | 대기 중 |

### 인증 방법

```
# 로그인
POST /auth/login-mobile
Content-Type: application/json

{ "username": "teacher_kim", "password": "password123" }

# 응답에서 access_token 추출 후 헤더에 사용
Authorization: Bearer {access_token}
```

### 날짜/시간 형식

| 타입 | 형식 | 예시 |
|------|------|------|
| `date` | `YYYY-MM-DD` | `2026-02-10` |
| `datetime` | `YYYY-MM-DDTHH:mm:ss` | `2026-02-10T09:00:00` |

### 필드명 규칙

| 위치 | 규칙 | 예시 |
|------|------|------|
| Query Parameter | camelCase | `startDate`, `endDate` |
| Response 필드 (ID/이름류) | camelCase | `teacherId`, `teacherName`, `workedMinutes` |
| Response 필드 (시간류) | snake_case | `check_in_at`, `check_out_at` |
| Response 필드 (단순) | 그대로 | `date`, `status`, `memo`, `approved` |
