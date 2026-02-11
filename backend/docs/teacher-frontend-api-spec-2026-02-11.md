# Teacher 화면 API 명세서 (Frontend)

> **Base URL**: `http://localhost:8000`
> **Prefix**: 모든 요청에 `/api` prefix 사용
> **인증**: `Authorization: Bearer {token}` 헤더 또는 httpOnly 쿠키
> **최종 수정일**: 2026-02-11

---

## 공통 사항

### 인증
모든 엔드포인트는 로그인(Teacher 권한)이 필요합니다.

### 공통 에러 응답

| Status | 설명 | 응답 예시 |
|--------|------|----------|
| `401` | 인증 필요 - 토큰 누락 또는 유효하지 않음 | `{"detail": "인증이 필요합니다"}` |
| `403` | 권한 없음 - 해당 리소스 접근 불가 | `{"detail": "담당 반이 아닙니다"}` |
| `404` | 리소스를 찾을 수 없음 | `{"detail": "과제를 찾을 수 없습니다"}` |
| `422` | 유효성 검사 실패 - 요청 파라미터 오류 | `{"detail": [...]}` |

### Swagger 태그

| 태그 | 화면 |
|------|------|
| `선생님 - 채점관리` | 과제/채점 관리 |
| `선생님 - 오답분석` | 오답 분석 |
| `선생님 - 클리닉생성` | 클리닉 과제 생성 |

### Enum 값 정리

| Enum | 값 | 설명 |
|------|-----|------|
| `assignment_type` | `NORMAL`, `CLINIC` | 과제 유형 |
| `question_type` | `CHOICE`, `SHORT_ANSWER`, `ESSAY` | 문제 유형 |
| `difficulty` | `EASY`, `MEDIUM`, `HARD` | 난이도 |
| `clinic_type` | `SAME`, `SIMILAR` | 클리닉 유형 |
| `status_filter` | `active`, `inactive` | 과제 상태 필터 |
| `type` (분석) | `normal`, `clinic` | 분석 유형 필터 |

---

## 1. 채점관리 (10개 엔드포인트)

### 1-1. 과제 목록 조회

| 항목 | 값 |
|------|-----|
| **Method** | `GET` |
| **URL** | `/api/teacher/assignments` |
| **Status** | `200 OK` |

#### Query Parameters

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `class_id` | `int` | X | 반 ID 필터 |
| `status_filter` | `string` | X | 상태 필터 (`active`, `inactive`) |

#### Response

```json
{
  "items": [
    {
      "assignment_id": 1,
      "title": "유리수 분류 연습",
      "class_id": 3,
      "class_name": "중1-A반",
      "due_date": "2026-02-20",
      "assignment_type": "NORMAL",
      "is_active": true,
      "question_count": 5,
      "submission_count": 12,
      "submit_rate": 80.0,
      "created_at": "2026-02-10T14:30:00"
    }
  ],
  "total": 1,
  "stats": {
    "total": 10,
    "active": 7,
    "avg_submit_rate": 75.5
  }
}
```

---

### 1-2. 과제 상세 조회

| 항목 | 값 |
|------|-----|
| **Method** | `GET` |
| **URL** | `/api/teacher/assignments/{assignment_id}` |
| **Status** | `200 OK`, `404 Not Found` |

#### Response

```json
{
  "assignment_id": 1,
  "title": "유리수 분류 연습",
  "description": "분수/소수 분류",
  "class_id": 3,
  "class_name": "중1-A반",
  "due_date": "2026-02-20",
  "assignment_type": "NORMAL",
  "is_active": true,
  "questions": [
    {
      "question_id": 10,
      "question_number": 1,
      "question_text": "-2/3은 어떤 수인가?",
      "question_type": "SHORT_ANSWER",
      "options": null,
      "correct_answer": "정수가아닌유리수",
      "points": 1,
      "category": "유리수",
      "difficulty": "MEDIUM"
    }
  ],
  "submission_count": 12,
  "submit_rate": 80.0,
  "created_at": "2026-02-10T14:30:00",
  "updated_at": "2026-02-10T14:30:00"
}
```

---

### 1-3. 과제 생성

| 항목 | 값 |
|------|-----|
| **Method** | `POST` |
| **URL** | `/api/teacher/assignments` |
| **Status** | `201 Created` |

#### Request Body

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `title` | `string` | O | 과제 제목 (1~200자) |
| `description` | `string` | X | 과제 설명 |
| `class_id` | `int` | X | 반 ID (null이면 개인 과제) |
| `due_date` | `string` | X | 마감일 (`YYYY-MM-DD`) |
| `assignment_type` | `string` | X | `NORMAL`(기본) / `CLINIC` |
| `questions` | `array` | O | 문제 목록 (최소 1개) |

**questions[] 항목:**

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `question_number` | `int` | O | 문제 번호 (1 이상) |
| `question_text` | `string` | O | 문제 내용 |
| `question_type` | `string` | X | `CHOICE`(기본) / `SHORT_ANSWER` / `ESSAY` |
| `options` | `string[]` | X | 객관식 보기 |
| `correct_answer` | `string` | O | 정답 |
| `points` | `int` | X | 배점 (기본 1) |
| `category` | `string` | X | 문제 유형 |
| `difficulty` | `string` | X | `EASY` / `MEDIUM`(기본) / `HARD` |

#### Request 예시

```json
{
  "title": "유리수 분류 연습",
  "description": "분수/소수 분류",
  "class_id": 3,
  "due_date": "2026-02-20",
  "assignment_type": "NORMAL",
  "questions": [
    {
      "question_number": 1,
      "question_text": "-2/3은 어떤 수인가?",
      "question_type": "SHORT_ANSWER",
      "correct_answer": "정수가아닌유리수",
      "points": 1,
      "category": "유리수",
      "difficulty": "MEDIUM"
    }
  ]
}
```

#### Response: `AssignmentDetailResponse` (1-2와 동일)

---

### 1-4. 과제 수정

| 항목 | 값 |
|------|-----|
| **Method** | `PUT` |
| **URL** | `/api/teacher/assignments/{assignment_id}` |
| **Status** | `200 OK`, `404 Not Found` |

#### Request Body

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `title` | `string` | X | 과제 제목 |
| `description` | `string` | X | 과제 설명 |
| `due_date` | `string` | X | 마감일 (`YYYY-MM-DD`) |
| `is_active` | `boolean` | X | 활성화 여부 |

#### Response: `AssignmentDetailResponse` (1-2와 동일)

---

### 1-5. 과제 삭제

| 항목 | 값 |
|------|-----|
| **Method** | `DELETE` |
| **URL** | `/api/teacher/assignments/{assignment_id}` |
| **Status** | `204 No Content`, `404 Not Found` |

Response Body 없음.

---

### 1-6. 채점 대기 목록 조회

| 항목 | 값 |
|------|-----|
| **Method** | `GET` |
| **URL** | `/api/teacher/grading` |
| **Status** | `200 OK` |

#### Response

```json
{
  "items": [
    {
      "assignment_id": 1,
      "title": "유리수 분류 연습",
      "class_id": 3,
      "class_name": "중1-A반",
      "due_date": "2026-02-20",
      "pending_count": 5,
      "total_submissions": 12
    }
  ],
  "total": 1,
  "total_pending": 5
}
```

---

### 1-7. 과제별 제출 현황 조회

| 항목 | 값 |
|------|-----|
| **Method** | `GET` |
| **URL** | `/api/teacher/grading/{assignment_id}/submissions` |
| **Status** | `200 OK`, `404 Not Found` |

#### Response

```json
{
  "assignment_id": 1,
  "assignment_title": "유리수 분류 연습",
  "items": [
    {
      "student_id": 101,
      "student_name": "홍길동",
      "class_name": "중1-A반",
      "status": "SUBMITTED",
      "submitted_at": "2026-02-15T10:30:00",
      "total_score": null,
      "max_score": 5,
      "score_rate": null
    }
  ],
  "total": 15,
  "submitted_count": 12,
  "graded_count": 7
}
```

---

### 1-8. 학생별 제출 상세 조회

| 항목 | 값 |
|------|-----|
| **Method** | `GET` |
| **URL** | `/api/teacher/grading/{assignment_id}/submissions/{student_id}` |
| **Status** | `200 OK`, `404 Not Found` |

#### Response

```json
{
  "submission_id": 50,
  "student_id": 101,
  "student_name": "홍길동",
  "status": "SUBMITTED",
  "submitted_at": "2026-02-15T10:30:00",
  "graded_at": null,
  "total_score": 0,
  "max_score": 5,
  "answers": [
    {
      "answer_id": 200,
      "question_id": 10,
      "question_number": 1,
      "question_text": "-2/3은 어떤 수인가?",
      "question_type": "SHORT_ANSWER",
      "correct_answer": "정수가아닌유리수",
      "student_answer": "유리수",
      "is_correct": null,
      "points": 1,
      "points_earned": 0
    }
  ]
}
```

---

### 1-9. 채점 저장

| 항목 | 값 |
|------|-----|
| **Method** | `POST` |
| **URL** | `/api/teacher/grading/{assignment_id}/submissions/{student_id}` |
| **Status** | `200 OK`, `404 Not Found` |

#### Request Body

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `answers` | `array` | O | 채점 결과 (최소 1개) |
| `answers[].answer_id` | `int` | O | 답안 ID |
| `answers[].points_earned` | `int` | O | 부여 점수 (0 이상) |
| `answers[].is_correct` | `boolean` | O | 정답 여부 |
| `feedback` | `string` | X | 전체 피드백 |

#### Request 예시

```json
{
  "answers": [
    { "answer_id": 200, "points_earned": 1, "is_correct": true },
    { "answer_id": 201, "points_earned": 0, "is_correct": false }
  ],
  "feedback": "유리수 개념을 다시 복습하세요"
}
```

#### Response

```json
{
  "submission_id": 50,
  "status": "GRADED",
  "total_score": 3,
  "max_score": 5,
  "graded_at": "2026-02-15T15:00:00"
}
```

---

### 1-10. 간편 채점 (총점 직접 입력)

| 항목 | 값 |
|------|-----|
| **Method** | `POST` |
| **URL** | `/api/teacher/grading/{assignment_id}/quick-grade` |
| **Status** | `200 OK`, `404 Not Found` |

#### Request Body

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `grades` | `array` | O | 성적 배열 (최소 1개) |
| `grades[].student_id` | `int` | O | 학생 ID |
| `grades[].score` | `int` | O | 획득 점수 (0 이상) |
| `grades[].max_score` | `int` | X | 최대 점수 (기본 100) |
| `grades[].wrong_questions` | `string` | X | 틀린 문항 번호 |
| `grades[].memo` | `string` | X | 메모 |

#### Request 예시

```json
{
  "grades": [
    { "student_id": 101, "score": 85, "max_score": 100 },
    { "student_id": 102, "score": 92, "max_score": 100, "wrong_questions": "3,7" }
  ]
}
```

#### Response

```json
{
  "success": true,
  "updated_count": 2,
  "message": "2명의 채점이 완료되었습니다"
}
```

---

## 2. 오답분석 (3개 엔드포인트)

### 2-1. 문항별 오답률 분석

| 항목 | 값 |
|------|-----|
| **Method** | `GET` |
| **URL** | `/api/teacher/analysis/questions` |
| **Status** | `200 OK` |

#### Query Parameters

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `type` | `string` | X | 분석 유형 (`normal`, `clinic`) |
| `item_id` | `int` | X | 과제 ID |
| `class_id` | `int` | X | 반 ID |
| `start_date` | `string` | X | 시작일 (`YYYY-MM-DD`) |
| `end_date` | `string` | X | 종료일 (`YYYY-MM-DD`) |

#### Response

```json
{
  "items": [
    {
      "question_id": 10,
      "question_number": 1,
      "question_text": "-2/3은 어떤 수인가?",
      "category": "유리수",
      "difficulty": "MEDIUM",
      "total_attempts": 15,
      "wrong_count": 8,
      "wrong_rate": 53.3,
      "common_wrong_answers": ["정수", "자연수", "소수"]
    }
  ],
  "total": 1,
  "analysis_period": "2026-01-12 ~ 2026-02-11"
}
```

---

### 2-2. 학생별 취약점 분석

| 항목 | 값 |
|------|-----|
| **Method** | `GET` |
| **URL** | `/api/teacher/analysis/students` |
| **Status** | `200 OK` |

#### Query Parameters

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `class_id` | `int` | X | 반 ID |

#### Response

```json
{
  "items": [
    {
      "student_id": 101,
      "student_name": "홍길동",
      "class_id": 3,
      "class_name": "중1-A반",
      "total_questions": 50,
      "total_wrong": 15,
      "overall_wrong_rate": 30.0,
      "weak_categories": [
        {
          "category": "유리수",
          "total_questions": 10,
          "wrong_count": 6,
          "wrong_rate": 60.0
        }
      ]
    }
  ],
  "total": 1
}
```

---

### 2-3. 단원별 통계

| 항목 | 값 |
|------|-----|
| **Method** | `GET` |
| **URL** | `/api/teacher/analysis/units` |
| **Status** | `200 OK` |

#### Query Parameters

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `type` | `string` | X | 분석 유형 (`normal`, `clinic`) |
| `class_id` | `int` | X | 반 ID |
| `start_date` | `string` | X | 시작일 (`YYYY-MM-DD`) |
| `end_date` | `string` | X | 종료일 (`YYYY-MM-DD`) |

#### Response

```json
{
  "items": [
    {
      "category": "유리수",
      "total_questions": 20,
      "total_attempts": 100,
      "correct_count": 65,
      "wrong_count": 35,
      "correct_rate": 65.0,
      "wrong_rate": 35.0,
      "avg_difficulty": "MEDIUM"
    }
  ],
  "total": 1,
  "analysis_period": "2026-01-12 ~ 2026-02-11"
}
```

---

## 3. 클리닉생성 (3개 엔드포인트)

### 3-1. 학생별 오답 문항 조회

| 항목 | 값 |
|------|-----|
| **Method** | `GET` |
| **URL** | `/api/teacher/clinic/wrong-answers` |
| **Status** | `200 OK` |

#### Query Parameters

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `student_id` | `int` | X | 학생 ID |
| `class_id` | `int` | X | 반 ID |
| `assignment_id` | `int` | X | 과제 ID |

#### Response

```json
{
  "items": [
    {
      "student_id": 101,
      "student_name": "홍길동",
      "class_name": "중1-A반",
      "assignment_id": 1,
      "assignment_title": "유리수 분류 연습",
      "question_id": 10,
      "question_number": 1,
      "question_text": "-2/3은 어떤 수인가?",
      "category": "유리수",
      "student_answer": "정수",
      "correct_answer": "정수가아닌유리수",
      "submitted_at": "2026-02-15T10:30:00"
    }
  ],
  "total": 1
}
```

---

### 3-2. 클리닉 과제 생성

| 항목 | 값 |
|------|-----|
| **Method** | `POST` |
| **URL** | `/api/teacher/clinic/assignments` |
| **Status** | `201 Created` |

#### Request Body

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `student_id` | `int` | O | 학생 ID |
| `question_ids` | `int[]` | O | 문제 ID 목록 (최소 1개) |
| `clinic_type` | `string` | X | `SAME`(기본) / `SIMILAR` |
| `title` | `string` | X | 클리닉 제목 (미입력시 자동 생성) |
| `due_date` | `string` | X | 마감일 (`YYYY-MM-DD`) |

#### Request 예시

```json
{
  "student_id": 101,
  "question_ids": [10, 11, 15],
  "clinic_type": "SAME",
  "title": "[클리닉] 홍길동 - 유리수 오답 복습",
  "due_date": "2026-02-25"
}
```

#### Response

```json
{
  "assignment_id": 502,
  "title": "[클리닉] 홍길동 - 유리수 오답 복습",
  "question_count": 3,
  "student_id": 101,
  "student_name": "홍길동"
}
```

---

### 3-3. 유사 문제 추천

| 항목 | 값 |
|------|-----|
| **Method** | `GET` |
| **URL** | `/api/teacher/clinic/similar-questions` |
| **Status** | `200 OK` |

#### Query Parameters

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `category` | `string` | **O** | 문제 유형 |
| `difficulty` | `string` | X | 난이도 (`EASY`, `MEDIUM`, `HARD`) |
| `limit` | `int` | X | 최대 개수 (기본 10, 최대 50) |

#### Response

```json
{
  "category": "유리수",
  "items": [
    {
      "question_bank_id": 301,
      "question_text": "1/4는 어떤 수의 분류에 속하는가?",
      "question_type": "SHORT_ANSWER",
      "category": "유리수",
      "difficulty": "MEDIUM",
      "usage_count": 2
    }
  ],
  "total": 1
}
```

---

## 엔드포인트 요약

| # | Method | URL | 화면 | 설명 |
|---|--------|-----|------|------|
| 1 | `GET` | `/api/teacher/assignments` | 채점관리 | 과제 목록 |
| 2 | `GET` | `/api/teacher/assignments/{id}` | 채점관리 | 과제 상세 |
| 3 | `POST` | `/api/teacher/assignments` | 채점관리 | 과제 생성 |
| 4 | `PUT` | `/api/teacher/assignments/{id}` | 채점관리 | 과제 수정 |
| 5 | `DELETE` | `/api/teacher/assignments/{id}` | 채점관리 | 과제 삭제 |
| 6 | `GET` | `/api/teacher/grading` | 채점관리 | 채점 대기 목록 |
| 7 | `GET` | `/api/teacher/grading/{id}/submissions` | 채점관리 | 제출 현황 |
| 8 | `GET` | `/api/teacher/grading/{id}/submissions/{sid}` | 채점관리 | 학생 제출 상세 |
| 9 | `POST` | `/api/teacher/grading/{id}/submissions/{sid}` | 채점관리 | 채점 저장 |
| 10 | `POST` | `/api/teacher/grading/{id}/quick-grade` | 채점관리 | 간편 채점 |
| 11 | `GET` | `/api/teacher/analysis/questions` | 오답분석 | 문항별 오답률 |
| 12 | `GET` | `/api/teacher/analysis/students` | 오답분석 | 학생별 취약점 |
| 13 | `GET` | `/api/teacher/analysis/units` | 오답분석 | 단원별 통계 |
| 14 | `GET` | `/api/teacher/clinic/wrong-answers` | 클리닉생성 | 오답 문항 조회 |
| 15 | `POST` | `/api/teacher/clinic/assignments` | 클리닉생성 | 클리닉 과제 생성 |
| 16 | `GET` | `/api/teacher/clinic/similar-questions` | 클리닉생성 | 유사 문제 추천 |

---

## Swagger UI

`http://localhost:8000/docs` 에서 위 모든 엔드포인트를 확인하고 테스트할 수 있습니다.
