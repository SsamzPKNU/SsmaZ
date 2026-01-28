# 과제 시스템 API 명세서

> **작성일**: 2026-01-28
> **버전**: 1.0.0
> **Base URL**: `http://localhost:8000`

---

## 목차

1. [과제 API](#1-과제-api)
2. [제출/답안 API](#2-제출답안-api)
3. [클리닉 API](#3-클리닉-api)
4. [PDF API](#4-pdf-api)
5. [공통 사항](#5-공통-사항)

---

## 1. 과제 API

**Prefix**: `/api/assignments`

### 1.1 과제 목록 조회

```
GET /api/assignments
```

| 항목 | 내용 |
|------|------|
| 설명 | 본인 학원의 과제 목록을 조회합니다 |
| 권한 | ALL (ADMIN, TEACHER, STUDENT) |

**Query Parameters**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| skip | int | X | 0 | 건너뛸 개수 |
| limit | int | X | 20 | 조회 개수 (최대 100) |
| is_active | bool | X | - | 활성화 여부 필터 |
| assignment_type | string | X | - | 과제 유형 (NORMAL, CLINIC) |

**Response** `200 OK`

```json
{
  "items": [
    {
      "assignment_id": 1,
      "title": "1주차 영어 문법 테스트",
      "description": "현재완료 시제 문제",
      "due_date": "2026-02-05",
      "assignment_type": "NORMAL",
      "is_active": true,
      "question_count": 10,
      "created_at": "2026-01-28T10:00:00"
    }
  ],
  "total": 1
}
```

---

### 1.2 과제 상세 조회

```
GET /api/assignments/{assignment_id}
```

| 항목 | 내용 |
|------|------|
| 설명 | 과제 상세 정보와 문제 목록을 조회합니다 |
| 권한 | ALL |
| 참고 | 학생은 정답이 제외된 응답을 받습니다 |

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| assignment_id | int | O | 과제 ID |

**Response (TEACHER/ADMIN)** `200 OK`

```json
{
  "assignment_id": 1,
  "academy_id": 1,
  "teacher_id": 2,
  "title": "1주차 영어 문법 테스트",
  "description": "현재완료 시제 문제",
  "class_id": null,
  "due_date": "2026-02-05",
  "assignment_type": "NORMAL",
  "parent_assignment_id": null,
  "is_active": true,
  "questions": [
    {
      "question_id": 1,
      "question_number": 1,
      "question_text": "다음 중 현재완료 시제가 올바르게 사용된 문장은?",
      "question_type": "CHOICE",
      "options": ["I have see the movie", "I have seen the movie", "I has seen the movie", "I seen the movie"],
      "correct_answer": "I have seen the movie",
      "points": 2,
      "category": "현재완료",
      "difficulty": "MEDIUM"
    }
  ],
  "created_at": "2026-01-28T10:00:00",
  "updated_at": "2026-01-28T10:00:00"
}
```

**Response (STUDENT)** `200 OK`

```json
{
  "assignment_id": 1,
  "academy_id": 1,
  "teacher_id": 2,
  "title": "1주차 영어 문법 테스트",
  "description": "현재완료 시제 문제",
  "class_id": null,
  "due_date": "2026-02-05",
  "assignment_type": "NORMAL",
  "is_active": true,
  "questions": [
    {
      "question_id": 1,
      "question_number": 1,
      "question_text": "다음 중 현재완료 시제가 올바르게 사용된 문장은?",
      "question_type": "CHOICE",
      "options": ["I have see the movie", "I have seen the movie", "I has seen the movie", "I seen the movie"],
      "points": 2
    }
  ],
  "created_at": "2026-01-28T10:00:00"
}
```

---

### 1.3 과제 생성

```
POST /api/assignments
```

| 항목 | 내용 |
|------|------|
| 설명 | 새로운 과제를 생성합니다 |
| 권한 | TEACHER, ADMIN |

**Request Body**

```json
{
  "title": "1주차 영어 문법 테스트",
  "description": "현재완료 시제 문제",
  "class_id": null,
  "due_date": "2026-02-05",
  "questions": [
    {
      "question_number": 1,
      "question_text": "다음 중 현재완료 시제가 올바르게 사용된 문장은?",
      "question_type": "CHOICE",
      "options": ["I have see the movie", "I have seen the movie", "I has seen the movie", "I seen the movie"],
      "correct_answer": "I have seen the movie",
      "points": 2,
      "category": "현재완료",
      "difficulty": "MEDIUM"
    },
    {
      "question_number": 2,
      "question_text": "빈칸에 알맞은 단어를 쓰시오: I ___ (live) in Seoul for 10 years.",
      "question_type": "SHORT_ANSWER",
      "correct_answer": "have lived",
      "points": 3,
      "category": "현재완료",
      "difficulty": "MEDIUM"
    }
  ]
}
```

**Request Body Fields**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| title | string | O | 과제 제목 (최대 200자) |
| description | string | X | 과제 설명 |
| class_id | int | X | 반 ID (NULL이면 개인 과제) |
| due_date | date | X | 마감일 (YYYY-MM-DD) |
| questions | array | O | 문제 목록 (최소 1개) |

**Question Fields**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| question_number | int | O | 문제 번호 (1 이상) |
| question_text | string | O | 문제 내용 |
| question_type | enum | X | CHOICE, SHORT_ANSWER, ESSAY (기본: CHOICE) |
| options | array | X | 객관식 보기 |
| correct_answer | string | O | 정답 |
| points | int | X | 배점 (기본: 1) |
| category | string | X | 문제 유형 (클리닉용) |
| difficulty | enum | X | EASY, MEDIUM, HARD (기본: MEDIUM) |

**Response** `201 Created`

```json
{
  "assignment_id": 1,
  "academy_id": 1,
  "teacher_id": 2,
  "title": "1주차 영어 문법 테스트",
  "description": "현재완료 시제 문제",
  "class_id": null,
  "due_date": "2026-02-05",
  "assignment_type": "NORMAL",
  "parent_assignment_id": null,
  "is_active": true,
  "questions": [...],
  "created_at": "2026-01-28T10:00:00",
  "updated_at": "2026-01-28T10:00:00"
}
```

---

### 1.4 과제 수정

```
PUT /api/assignments/{assignment_id}
```

| 항목 | 내용 |
|------|------|
| 설명 | 과제 정보를 수정합니다 (문제 수정 불가) |
| 권한 | TEACHER, ADMIN |

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| assignment_id | int | O | 과제 ID |

**Request Body**

```json
{
  "title": "1주차 영어 문법 테스트 (수정)",
  "description": "현재완료 시제 문제 - 수정됨",
  "due_date": "2026-02-10",
  "is_active": true
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| title | string | X | 과제 제목 |
| description | string | X | 과제 설명 |
| class_id | int | X | 반 ID |
| due_date | date | X | 마감일 |
| is_active | bool | X | 활성화 여부 |

**Response** `200 OK`

```json
{
  "assignment_id": 1,
  "title": "1주차 영어 문법 테스트 (수정)",
  ...
}
```

---

### 1.5 과제 삭제

```
DELETE /api/assignments/{assignment_id}
```

| 항목 | 내용 |
|------|------|
| 설명 | 과제를 삭제합니다 (관련 문제, 제출도 함께 삭제) |
| 권한 | TEACHER, ADMIN |

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| assignment_id | int | O | 과제 ID |

**Response** `204 No Content`

---

## 2. 제출/답안 API

**Prefix**: `/api/submissions`

### 2.1 내 제출 목록 조회

```
GET /api/submissions/my
```

| 항목 | 내용 |
|------|------|
| 설명 | 로그인한 학생의 제출 목록을 조회합니다 |
| 권한 | STUDENT |

**Query Parameters**

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|----------|------|------|--------|------|
| skip | int | X | 0 | 건너뛸 개수 |
| limit | int | X | 20 | 조회 개수 |
| status | string | X | - | 상태 필터 (IN_PROGRESS, SUBMITTED, GRADED) |

**Response** `200 OK`

```json
{
  "items": [
    {
      "submission_id": 1,
      "assignment_id": 1,
      "assignment_title": "1주차 영어 문법 테스트",
      "status": "GRADED",
      "total_score": 8,
      "max_score": 10,
      "submitted_at": "2026-01-28T14:30:00",
      "graded_at": "2026-01-28T15:00:00"
    }
  ],
  "total": 1
}
```

---

### 2.2 과제별 제출 목록 조회

```
GET /api/submissions/assignment/{assignment_id}
```

| 항목 | 내용 |
|------|------|
| 설명 | 특정 과제의 모든 제출 목록을 조회합니다 |
| 권한 | TEACHER, ADMIN |

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| assignment_id | int | O | 과제 ID |

**Response** `200 OK`

```json
{
  "items": [
    {
      "submission_id": 1,
      "assignment_id": 1,
      "assignment_title": "1주차 영어 문법 테스트",
      "status": "GRADED",
      "total_score": 8,
      "max_score": 10,
      "submitted_at": "2026-01-28T14:30:00",
      "graded_at": "2026-01-28T15:00:00"
    }
  ],
  "total": 1
}
```

---

### 2.3 과제 시작

```
POST /api/submissions/{assignment_id}/start
```

| 항목 | 내용 |
|------|------|
| 설명 | 과제 풀이를 시작합니다. 이미 시작한 경우 기존 제출을 반환합니다 |
| 권한 | STUDENT |

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| assignment_id | int | O | 과제 ID |

**Response** `201 Created`

```json
{
  "submission_id": 1,
  "assignment_id": 1,
  "student_id": 5,
  "status": "IN_PROGRESS",
  "total_score": 0,
  "max_score": 0,
  "submitted_at": null,
  "graded_at": null,
  "created_at": "2026-01-28T14:00:00",
  "updated_at": "2026-01-28T14:00:00"
}
```

---

### 2.4 답안 저장

```
PUT /api/submissions/{submission_id}/answers
```

| 항목 | 내용 |
|------|------|
| 설명 | 답안을 저장합니다 (임시 저장 가능) |
| 권한 | STUDENT |
| 참고 | 제출 전(IN_PROGRESS)에만 수정 가능 |

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| submission_id | int | O | 제출 ID |

**Request Body**

```json
{
  "answers": [
    {
      "question_id": 1,
      "student_answer": "I have seen the movie"
    },
    {
      "question_id": 2,
      "student_answer": "have lived"
    }
  ]
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| answers | array | O | 답안 목록 |
| answers[].question_id | int | O | 문제 ID |
| answers[].student_answer | string | O | 학생 답안 |

**Response** `200 OK`

```json
{
  "submission_id": 1,
  "assignment_id": 1,
  "student_id": 5,
  "status": "IN_PROGRESS",
  ...
}
```

---

### 2.5 최종 제출

```
POST /api/submissions/{submission_id}/submit
```

| 항목 | 내용 |
|------|------|
| 설명 | 과제를 최종 제출합니다. 제출 후 수정 불가 |
| 권한 | STUDENT |

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| submission_id | int | O | 제출 ID |

**Response** `200 OK`

```json
{
  "submission_id": 1,
  "assignment_id": 1,
  "student_id": 5,
  "status": "SUBMITTED",
  "total_score": 0,
  "max_score": 0,
  "submitted_at": "2026-01-28T14:30:00",
  "graded_at": null,
  ...
}
```

---

### 2.6 자동 채점

```
POST /api/submissions/{submission_id}/grade
```

| 항목 | 내용 |
|------|------|
| 설명 | 제출된 과제를 자동 채점합니다 |
| 권한 | TEACHER, ADMIN |
| 참고 | 서술형(ESSAY)은 자동 채점 불가 |

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| submission_id | int | O | 제출 ID |

**Response** `200 OK`

```json
{
  "submission_id": 1,
  "total_score": 8,
  "max_score": 10,
  "percentage": 80.0,
  "correct_count": 4,
  "wrong_count": 1,
  "wrong_question_ids": [2]
}
```

---

### 2.7 채점 결과 조회

```
GET /api/submissions/{submission_id}/result
```

| 항목 | 내용 |
|------|------|
| 설명 | 채점 결과를 상세 조회합니다 |
| 권한 | ALL (학생은 본인 것만) |

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| submission_id | int | O | 제출 ID |

**Response** `200 OK`

```json
{
  "submission_id": 1,
  "assignment_title": "1주차 영어 문법 테스트",
  "student_name": "김민수",
  "total_score": 8,
  "max_score": 10,
  "percentage": 80.0,
  "answers": [
    {
      "answer_id": 1,
      "question_id": 1,
      "question_number": 1,
      "question_text": "다음 중 현재완료 시제가 올바르게 사용된 문장은?",
      "student_answer": "I have seen the movie",
      "correct_answer": "I have seen the movie",
      "is_correct": true,
      "points_earned": 2,
      "max_points": 2
    },
    {
      "answer_id": 2,
      "question_id": 2,
      "question_number": 2,
      "question_text": "빈칸에 알맞은 단어를 쓰시오...",
      "student_answer": "lived",
      "correct_answer": "have lived",
      "is_correct": false,
      "points_earned": 0,
      "max_points": 3
    }
  ],
  "graded_at": "2026-01-28T15:00:00"
}
```

---

## 3. 클리닉 API

**Prefix**: `/api/clinic`

### 3.1 클리닉 생성 미리보기

```
GET /api/clinic/preview/{submission_id}
```

| 항목 | 내용 |
|------|------|
| 설명 | 틀린 문제 목록을 미리 조회합니다 |
| 권한 | TEACHER, ADMIN |

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| submission_id | int | O | 제출 ID |

**Response** `200 OK`

```json
{
  "submission_id": 1,
  "assignment_title": "1주차 영어 문법 테스트",
  "wrong_questions": [
    {
      "question_id": 2,
      "question_number": 2,
      "question_text": "빈칸에 알맞은 단어를 쓰시오...",
      "student_answer": "lived",
      "correct_answer": "have lived",
      "category": "현재완료"
    }
  ],
  "total_wrong_count": 1
}
```

---

### 3.2 클리닉 과제 생성

```
POST /api/clinic/generate
```

| 항목 | 내용 |
|------|------|
| 설명 | 틀린 문제 기반으로 클리닉 과제를 생성합니다 |
| 권한 | TEACHER, ADMIN |

**Request Body**

```json
{
  "submission_id": 1,
  "clinic_type": "SAME",
  "title": "[클리닉] 김민수 - 현재완료 복습",
  "due_date": "2026-02-10"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| submission_id | int | O | 원본 제출 ID |
| clinic_type | enum | X | SAME(동일문제), SIMILAR(유사문제) - 기본: SAME |
| title | string | X | 클리닉 제목 (미입력시 자동 생성) |
| due_date | date | X | 마감일 |

**Response** `201 Created`

```json
{
  "assignment_id": 2,
  "title": "[클리닉] 김민수 - 현재완료 복습",
  "original_assignment_id": 1,
  "original_assignment_title": "1주차 영어 문법 테스트",
  "question_count": 1,
  "created_at": "2026-01-28T16:00:00"
}
```

---

### 3.3 학생별 클리닉 목록 조회

```
GET /api/clinic/student/{student_id}
```

| 항목 | 내용 |
|------|------|
| 설명 | 특정 학생의 클리닉 과제 목록을 조회합니다 |
| 권한 | ALL (같은 학원 소속) |

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| student_id | int | O | 학생 ID |

**Response** `200 OK`

```json
{
  "items": [
    {
      "assignment_id": 2,
      "title": "[클리닉] 김민수 - 현재완료 복습",
      "original_assignment_title": "1주차 영어 문법 테스트",
      "due_date": "2026-02-10",
      "question_count": 1,
      "is_completed": false,
      "score": null,
      "max_score": null,
      "created_at": "2026-01-28T16:00:00"
    }
  ],
  "total": 1
}
```

---

### 3.4 내 클리닉 목록 조회

```
GET /api/clinic/my
```

| 항목 | 내용 |
|------|------|
| 설명 | 로그인한 학생의 클리닉 목록을 조회합니다 |
| 권한 | STUDENT |

**Response** `200 OK`

```json
{
  "items": [...],
  "total": 1
}
```

---

## 4. PDF API

**Prefix**: `/api/pdf`

### 4.1 과제 문제지 PDF 다운로드

```
GET /api/pdf/assignment/{assignment_id}
```

| 항목 | 내용 |
|------|------|
| 설명 | 과제 문제지를 PDF로 다운로드합니다 |
| 권한 | ALL |
| Content-Type | application/pdf |

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| assignment_id | int | O | 과제 ID |

**Response** `200 OK`

- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename=assignment_{id}_{title}.pdf`

---

### 4.2 채점 결과지 PDF 다운로드

```
GET /api/pdf/result/{submission_id}
```

| 항목 | 내용 |
|------|------|
| 설명 | 채점 결과지를 PDF로 다운로드합니다 |
| 권한 | ALL (학생은 본인 것만) |
| Content-Type | application/pdf |

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| submission_id | int | O | 제출 ID |

**Response** `200 OK`

- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename=result_{id}_{student_name}.pdf`

---

## 5. 공통 사항

### 5.1 인증

모든 API는 인증이 필요합니다. 다음 중 하나의 방식으로 인증합니다:

1. **Cookie 기반 (권장)**
   - 로그인 시 발급된 `access_token` 쿠키 자동 전송

2. **Bearer Token**
   - Header: `Authorization: Bearer {token}`

### 5.2 권한

| 권한 | 설명 |
|------|------|
| ADMIN | 학원 관리자 - 모든 기능 사용 가능 |
| TEACHER | 선생님 - 과제 생성/채점 가능 |
| STUDENT | 학생 - 과제 풀이/결과 조회만 가능 |

### 5.3 에러 응답

```json
{
  "detail": "에러 메시지"
}
```

| 상태 코드 | 설명 |
|-----------|------|
| 400 | 잘못된 요청 |
| 401 | 인증 필요 |
| 403 | 권한 없음 |
| 404 | 리소스 없음 |
| 500 | 서버 에러 |

### 5.4 Enum 값

**AssignmentType (과제 유형)**
| 값 | 설명 |
|----|------|
| NORMAL | 일반 과제 |
| CLINIC | 클리닉 과제 |

**QuestionType (문제 유형)**
| 값 | 설명 |
|----|------|
| CHOICE | 객관식 |
| SHORT_ANSWER | 단답형 |
| ESSAY | 서술형 |

**Difficulty (난이도)**
| 값 | 설명 |
|----|------|
| EASY | 쉬움 |
| MEDIUM | 보통 |
| HARD | 어려움 |

**SubmissionStatus (제출 상태)**
| 값 | 설명 |
|----|------|
| IN_PROGRESS | 진행 중 |
| SUBMITTED | 제출됨 |
| GRADED | 채점 완료 |

**ClinicType (클리닉 유형)**
| 값 | 설명 |
|----|------|
| SAME | 동일 문제 |
| SIMILAR | 유사 문제 (문제은행에서) |

---

## 6. API 요약

| API | Method | Endpoint | 권한 |
|-----|--------|----------|------|
| 과제 목록 | GET | /api/assignments | ALL |
| 과제 상세 | GET | /api/assignments/{id} | ALL |
| 과제 생성 | POST | /api/assignments | TEACHER, ADMIN |
| 과제 수정 | PUT | /api/assignments/{id} | TEACHER, ADMIN |
| 과제 삭제 | DELETE | /api/assignments/{id} | TEACHER, ADMIN |
| 내 제출 목록 | GET | /api/submissions/my | STUDENT |
| 과제별 제출 목록 | GET | /api/submissions/assignment/{id} | TEACHER, ADMIN |
| 과제 시작 | POST | /api/submissions/{id}/start | STUDENT |
| 답안 저장 | PUT | /api/submissions/{id}/answers | STUDENT |
| 최종 제출 | POST | /api/submissions/{id}/submit | STUDENT |
| 자동 채점 | POST | /api/submissions/{id}/grade | TEACHER, ADMIN |
| 채점 결과 | GET | /api/submissions/{id}/result | ALL |
| 클리닉 미리보기 | GET | /api/clinic/preview/{id} | TEACHER, ADMIN |
| 클리닉 생성 | POST | /api/clinic/generate | TEACHER, ADMIN |
| 학생별 클리닉 | GET | /api/clinic/student/{id} | ALL |
| 내 클리닉 | GET | /api/clinic/my | STUDENT |
| 문제지 PDF | GET | /api/pdf/assignment/{id} | ALL |
| 결과지 PDF | GET | /api/pdf/result/{id} | ALL |
