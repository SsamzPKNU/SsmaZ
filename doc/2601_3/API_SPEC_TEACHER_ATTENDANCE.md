# SSamZ API - 선생님 출퇴근 관리 명세서

> **최종 수정일**: 2026-01-27

---

## 개요

선생님 출퇴근 관리를 위한 API입니다.
- 선생님 본인의 출퇴근 처리 및 기록 조회
- 원장(ADMIN)의 출근현황 조회 및 승인 처리
- 비정규직(PART_TIME) 시급 기반 예상 급여 계산

---

## 선생님용 API (`/teachers`)

### 1. 출근 처리

#### Endpoint
```
POST /teachers/attendance/check-in
```

#### Headers
```
Cookie: access_token=...
X-CSRF-Token: {csrf_token}
```

#### Request Body (선택)
```json
{
  "work_date": "2026-01-27"
}
```
> `work_date` 미입력 시 오늘 날짜로 자동 설정

#### Response (201 Created)
```json
{
  "id": 1,
  "teacher_id": 5,
  "work_date": "2026-01-27",
  "check_in_time": "2026-01-27T09:00:00",
  "check_out_time": null,
  "worked_minutes": 0,
  "is_approved": false,
  "approved_by": null,
  "created_at": "2026-01-27T09:00:00",
  "updated_at": null
}
```

#### Error Responses
| 상태 코드 | 설명 |
|----------|------|
| 400 | 이미 해당 날짜 출근 기록 존재 |
| 403 | 선생님 권한 필요 |
| 404 | 선생님 정보 없음 (Teachers 테이블 연결 필요) |

---

### 2. 퇴근 처리

#### Endpoint
```
POST /teachers/attendance/check-out
```

#### Headers
```
Cookie: access_token=...
X-CSRF-Token: {csrf_token}
```

#### Request Body
없음

#### Response (200 OK)
```json
{
  "id": 1,
  "teacher_id": 5,
  "work_date": "2026-01-27",
  "check_in_time": "2026-01-27T09:00:00",
  "check_out_time": "2026-01-27T18:00:00",
  "worked_minutes": 540,
  "is_approved": false,
  "approved_by": null,
  "created_at": "2026-01-27T09:00:00",
  "updated_at": "2026-01-27T18:00:00"
}
```

> `worked_minutes`는 출근~퇴근 시간 차이(분 단위)로 자동 계산

#### Error Responses
| 상태 코드 | 설명 |
|----------|------|
| 400 | 오늘 출근 기록 없음 / 이미 퇴근 처리됨 |
| 403 | 선생님 권한 필요 |

---

### 3. 출퇴근 기록 조회

#### Endpoint
```
GET /teachers/{teacher_id}/attendance
```

#### Path Parameters
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| teacher_id | Integer | 선생님 ID |

#### Query Parameters
| 파라미터 | 타입 | 설명 | 기본값 |
|---------|------|------|--------|
| start_date | Date | 조회 시작일 | 없음 |
| end_date | Date | 조회 종료일 | 없음 |
| page | Integer | 페이지 번호 | 1 |
| limit | Integer | 페이지당 항목 수 (1~100) | 20 |

#### Response (200 OK)
```json
{
  "records": [
    {
      "id": 1,
      "teacher_id": 5,
      "work_date": "2026-01-27",
      "check_in_time": "2026-01-27T09:00:00",
      "check_out_time": "2026-01-27T18:00:00",
      "worked_minutes": 540,
      "is_approved": true,
      "approved_by": 1,
      "created_at": "2026-01-27T09:00:00",
      "updated_at": "2026-01-27T18:00:00"
    }
  ],
  "total": 1
}
```

---

### 4. 근무시간 요약 조회

#### Endpoint
```
GET /teachers/{teacher_id}/work-summary
```

#### Path Parameters
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| teacher_id | Integer | 선생님 ID |

#### Query Parameters (필수)
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| start_date | Date | 조회 시작일 |
| end_date | Date | 조회 종료일 |

#### Response (200 OK)
```json
{
  "teacher_id": 5,
  "teacher_name": "김선생",
  "period_start": "2026-01-01",
  "period_end": "2026-01-31",
  "total_minutes": 10800,
  "total_hours": 180.0,
  "total_days": 22,
  "employment_type": "PART_TIME",
  "hourly_rate": 15000,
  "estimated_salary": 2700000
}
```

> `estimated_salary`는 비정규직(PART_TIME)이고 시급이 설정된 경우에만 계산됨

---

## 관리자용 API (`/admin`)

### 5. 전체 선생님 출근현황 조회

#### Endpoint
```
GET /admin/teacher-attendance
```

#### Query Parameters
| 파라미터 | 타입 | 설명 | 기본값 |
|---------|------|------|--------|
| target_date | Date | 조회 날짜 | 오늘 |

#### Response (200 OK)
```json
{
  "query_date": "2026-01-27",
  "records": [
    {
      "id": 1,
      "teacher_id": 5,
      "teacher_name": "김선생",
      "work_date": "2026-01-27",
      "check_in_time": "2026-01-27T09:00:00",
      "check_out_time": "2026-01-27T18:00:00",
      "worked_minutes": 540,
      "is_approved": false
    }
  ],
  "total": 1
}
```

---

### 6. 출퇴근 기록 승인

#### Endpoint
```
PATCH /admin/attendance/{attendance_id}/approve
```

#### Path Parameters
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| attendance_id | Integer | 출퇴근 기록 ID |

#### Response (200 OK)
```json
{
  "id": 1,
  "teacher_id": 5,
  "work_date": "2026-01-27",
  "check_in_time": "2026-01-27T09:00:00",
  "check_out_time": "2026-01-27T18:00:00",
  "worked_minutes": 540,
  "is_approved": true,
  "approved_by": 2,
  "created_at": "2026-01-27T09:00:00",
  "updated_at": "2026-01-27T18:05:00"
}
```

#### Error Responses
| 상태 코드 | 설명 |
|----------|------|
| 400 | 이미 승인된 기록 |
| 403 | 해당 출퇴근 기록에 대한 권한 없음 (다른 학원 소속) |
| 404 | 출퇴근 기록 없음 |

---

## 데이터베이스 스키마

### TeacherAttendances 테이블
```sql
CREATE TABLE TeacherAttendances (
    id INT PRIMARY KEY AUTO_INCREMENT,
    teacher_id INT NOT NULL,
    date DATE NOT NULL,
    check_in_time DATETIME,
    check_out_time DATETIME,
    worked_minutes INT DEFAULT 0,
    is_approved BOOLEAN DEFAULT FALSE,
    approved_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL,
    FOREIGN KEY (teacher_id) REFERENCES Teachers(teacher_id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES Users(user_id)
);
```

### Teachers 테이블 추가 컬럼
```sql
ALTER TABLE Teachers
ADD COLUMN employment_type VARCHAR(20) DEFAULT 'FULL_TIME' COMMENT '고용 형태 (FULL_TIME/PART_TIME)',
ADD COLUMN hourly_rate INT NULL COMMENT '시급 (비정규직용, 원 단위)';
```

---

## 권한 요약

| API | ADMIN | TEACHER |
|-----|-------|---------|
| 출근/퇴근 처리 | - | 본인만 |
| 기록/요약 조회 | 전체 | 본인만 |
| 출근현황 조회 | 소속 학원 전체 | - |
| 승인 처리 | 소속 학원 선생님만 | - |

---

## 관련 문서

- 선생님 관리 API: `API_SPEC_TEACHERS.md`
- 인증 API: `API_SPEC_LOGIN.md`
- 학생 연락처 API: `API_SPEC_STUDENT_CONTACT.md`
