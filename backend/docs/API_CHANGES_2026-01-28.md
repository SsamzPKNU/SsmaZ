# API 변경사항 명세서

**작성일:** 2026-01-28
**버전:** 1.1.0

---

## 목차

1. [시간표 API](#1-시간표-api)
2. [반별 학생 목록 API](#2-반별-학생-목록-api)
3. [과제 제출 현황 API](#3-과제-제출-현황-api)
4. [과제 채점 API (PUT)](#4-과제-채점-api-put)

---

## 1. 시간표 API

### 1.1 시간표 목록 조회

클래스의 시간표 목록을 조회합니다.

- **URL:** `GET /api/admin/classes/{class_id}/schedules`
- **인증:** Bearer Token (Cookie)
- **권한:** 로그인 사용자

#### Path Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| class_id | int | O | 반 ID |

#### Response (200 OK)

```json
{
  "items": [
    {
      "schedule_id": 1,
      "class_id": 1,
      "day_of_week": "월",
      "start_time": "16:00:00",
      "end_time": "18:00:00",
      "created_at": "2026-01-28T10:00:00"
    }
  ],
  "total": 1
}
```

#### Error Responses

| 상태 코드 | 설명 |
|-----------|------|
| 401 | 인증되지 않은 사용자 |
| 404 | 클래스를 찾을 수 없음 |

---

### 1.2 시간표 생성

클래스에 새로운 시간표를 추가합니다.

- **URL:** `POST /api/admin/classes/{class_id}/schedules`
- **인증:** Bearer Token (Cookie)
- **권한:** 로그인 사용자

#### Path Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| class_id | int | O | 반 ID |

#### Request Body

```json
{
  "day_of_week": "월",
  "start_time": "16:00:00",
  "end_time": "18:00:00"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| day_of_week | string | O | 요일 (월, 화, 수, 목, 금, 토, 일) |
| start_time | time | O | 시작 시간 (HH:MM:SS) |
| end_time | time | O | 종료 시간 (HH:MM:SS) |

#### Response (201 Created)

```json
{
  "schedule_id": 1,
  "class_id": 1,
  "day_of_week": "월",
  "start_time": "16:00:00",
  "end_time": "18:00:00",
  "created_at": "2026-01-28T10:00:00"
}
```

#### Error Responses

| 상태 코드 | 설명 |
|-----------|------|
| 401 | 인증되지 않은 사용자 |
| 404 | 클래스를 찾을 수 없음 |
| 422 | 입력 데이터 검증 실패 |

---

### 1.3 시간표 삭제

시간표를 삭제합니다.

- **URL:** `DELETE /api/admin/classes/schedules/{schedule_id}`
- **인증:** Bearer Token (Cookie)
- **권한:** 로그인 사용자

#### Path Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| schedule_id | int | O | 시간표 ID |

#### Response (204 No Content)

응답 바디 없음

#### Error Responses

| 상태 코드 | 설명 |
|-----------|------|
| 401 | 인증되지 않은 사용자 |
| 403 | 권한 없음 (다른 학원의 시간표) |
| 404 | 시간표를 찾을 수 없음 |

---

## 2. 반별 학생 목록 API

### 2.1 반별 학생 목록 조회

특정 반에 소속된 학생 목록을 조회합니다.

- **URL:** `GET /api/admin/classes/{class_id}/students`
- **인증:** Bearer Token (Cookie)
- **권한:** 로그인 사용자

#### Path Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| class_id | int | O | 반 ID |

#### Response (200 OK)

```json
{
  "class_id": 1,
  "class_name": "수학 정규반 A",
  "students": [
    {
      "student_id": 1,
      "name": "김철수",
      "status": "재원"
    },
    {
      "student_id": 2,
      "name": "이영희",
      "status": "재원"
    }
  ],
  "total": 2
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| class_id | int | 반 ID |
| class_name | string | 반 이름 |
| students | array | 학생 목록 |
| students[].student_id | int | 학생 ID |
| students[].name | string | 학생 이름 |
| students[].status | string | 학생 상태 (재원, 휴원, 졸업) |
| total | int | 총 학생 수 |

#### Error Responses

| 상태 코드 | 설명 |
|-----------|------|
| 401 | 인증되지 않은 사용자 |
| 404 | 클래스를 찾을 수 없음 |

---

## 3. 과제 제출 현황 API

### 3.1 과제 제출 현황 조회

특정 과제에 대한 학생들의 제출 현황을 조회합니다.

- **URL:** `GET /api/assignments/{assignment_id}/submissions`
- **인증:** Bearer Token (Cookie)
- **권한:** TEACHER, ADMIN

#### Path Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| assignment_id | int | O | 과제 ID |

#### Query Parameters

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| skip | int | X | 0 | 페이지네이션 오프셋 |
| limit | int | X | 50 | 페이지네이션 제한 (1-100) |

#### Response (200 OK)

```json
{
  "items": [
    {
      "submission_id": 1,
      "assignment_id": 1,
      "student_id": 1,
      "student_name": "김철수",
      "status": "GRADED",
      "total_score": 85,
      "max_score": 100,
      "submitted_at": "2026-01-28T14:30:00",
      "graded_at": "2026-01-28T15:00:00"
    }
  ],
  "total": 1
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| items | array | 제출 목록 |
| items[].submission_id | int | 제출 ID |
| items[].assignment_id | int | 과제 ID |
| items[].student_id | int | 학생 ID |
| items[].student_name | string | 학생 이름 |
| items[].status | string | 상태 (IN_PROGRESS, SUBMITTED, GRADED) |
| items[].total_score | int | 획득 점수 |
| items[].max_score | int | 만점 |
| items[].submitted_at | datetime | 제출 시간 |
| items[].graded_at | datetime | 채점 시간 |
| total | int | 총 제출 수 |

#### Error Responses

| 상태 코드 | 설명 |
|-----------|------|
| 401 | 인증되지 않은 사용자 |
| 403 | 권한 없음 (학생 계정) |
| 404 | 과제를 찾을 수 없음 |

---

## 4. 과제 채점 API (PUT)

### 4.1 과제 채점 (PUT)

기존 `POST /api/submissions/{submission_id}/grade`와 동일한 기능을 PUT 메서드로 제공합니다.

- **URL:** `PUT /api/submissions/{submission_id}/grade`
- **인증:** Bearer Token (Cookie)
- **권한:** TEACHER, ADMIN

#### Path Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| submission_id | int | O | 제출 ID |

#### Response (200 OK)

```json
{
  "submission_id": 1,
  "total_score": 85,
  "max_score": 100,
  "percentage": 85.0,
  "correct_count": 17,
  "wrong_count": 3,
  "wrong_question_ids": [5, 12, 18]
}
```

| 필드 | 타입 | 설명 |
|------|------|------|
| submission_id | int | 제출 ID |
| total_score | int | 획득 점수 |
| max_score | int | 만점 |
| percentage | float | 정답률 (%) |
| correct_count | int | 정답 수 |
| wrong_count | int | 오답 수 |
| wrong_question_ids | array[int] | 오답 문제 ID 목록 |

#### Error Responses

| 상태 코드 | 설명 |
|-----------|------|
| 400 | 제출되지 않은 과제 (IN_PROGRESS 상태) |
| 401 | 인증되지 않은 사용자 |
| 403 | 권한 없음 |
| 404 | 제출 기록을 찾을 수 없음 |

---

## 변경된 파일 목록

### 신규 파일

| 파일 경로 | 설명 |
|-----------|------|
| `app/models/schedule.py` | Schedule 테이블 모델 |
| `app/schemas/schedule.py` | Schedule Pydantic 스키마 |
| `app/services/schedule_service.py` | Schedule CRUD 서비스 |

### 수정된 파일

| 파일 경로 | 변경 내용 |
|-----------|-----------|
| `app/api/class_api.py` | 시간표 CRUD + 학생 목록 API 추가 |
| `app/api/assignments.py` | 과제 제출 현황 조회 API 추가 |
| `app/api/submissions.py` | PUT grade 메서드 추가 |
| `app/schemas/submission.py` | `SubmissionWithStudentItem`, `SubmissionWithStudentListResponse` 스키마 추가 |
| `main.py` | Schedule 모델 import 추가 |

---

## 데이터베이스 변경사항

### 신규 테이블: Schedules

```sql
CREATE TABLE Schedules (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    class_id INT NOT NULL,
    day_of_week VARCHAR(10) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES Classes(class_id) ON DELETE CASCADE
);
```

| 컬럼 | 타입 | 설명 |
|------|------|------|
| schedule_id | INT | 시간표 고유 ID (PK) |
| class_id | INT | 반 ID (FK) |
| day_of_week | VARCHAR(10) | 요일 |
| start_time | TIME | 시작 시간 |
| end_time | TIME | 종료 시간 |
| created_at | TIMESTAMP | 생성 시간 |
