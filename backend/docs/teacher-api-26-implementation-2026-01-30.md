# 선생님 API 26개 구현 완료 문서

**작성일:** 2026-01-30
**버전:** 1.0.0

---

## 개요

프론트엔드에서 필요한 선생님용 API 26개를 구현했습니다.
기존 `teacher_app.py` 패턴과 일관성을 유지하며 `/api/teacher/` prefix를 사용합니다.

---

## 파일 변경 내역

### 신규 생성 파일 (13개)

| 파일 경로 | 설명 |
|----------|------|
| `app/models/message_template.py` | MessageTemplate 모델 |
| `app/schemas/teacher_assignment.py` | 과제/채점 스키마 |
| `app/schemas/teacher_analytics.py` | 오답 분석 스키마 |
| `app/schemas/teacher_message.py` | 메시지 스키마 |
| `app/schemas/teacher_print.py` | 프린트 스키마 |
| `app/services/teacher_assignment_service.py` | 과제/채점 서비스 |
| `app/services/teacher_analytics_service.py` | 오답 분석 서비스 |
| `app/services/teacher_message_service.py` | 메시지 서비스 |
| `app/api/teacher_assignment.py` | 과제/채점 라우터 (9개 API) |
| `app/api/teacher_analytics.py` | 오답 분석 라우터 (3개 API) |
| `app/api/teacher_clinic.py` | 클리닉 라우터 (3개 API) |
| `app/api/teacher_message.py` | 메시지 라우터 (7개 API) |
| `app/api/teacher_print.py` | 프린트 라우터 (4개 API) |

### 수정 파일 (1개)

| 파일 경로 | 변경 내용 |
|----------|----------|
| `main.py` | 5개 신규 라우터 등록 + MessageTemplate 모델 import |

---

## API 엔드포인트 상세

### Phase 1: 과제 관리 (5개)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/teacher/assignments` | 과제 목록 조회 (담당 반 필터) |
| GET | `/api/teacher/assignments/{id}` | 과제 상세 조회 |
| POST | `/api/teacher/assignments` | 과제 생성 |
| PUT | `/api/teacher/assignments/{id}` | 과제 수정 |
| DELETE | `/api/teacher/assignments/{id}` | 과제 삭제 |

**Query Parameters (GET /assignments):**
- `class_id`: 반 ID (필터)
- `status_filter`: 상태 필터 (active, inactive)

**Request Body (POST /assignments):**
```json
{
  "title": "과제 제목",
  "description": "과제 설명",
  "class_id": 1,
  "due_date": "2026-02-15",
  "assignment_type": "NORMAL",
  "questions": [
    {
      "question_number": 1,
      "question_text": "문제 내용",
      "question_type": "CHOICE",
      "options": ["보기1", "보기2", "보기3", "보기4"],
      "correct_answer": "보기1",
      "points": 10,
      "category": "수학",
      "difficulty": "MEDIUM"
    }
  ]
}
```

---

### Phase 2: 채점 관리 (4개)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/teacher/grading` | 채점 대기 목록 |
| GET | `/api/teacher/grading/{assignmentId}/submissions` | 과제별 제출 현황 |
| GET | `/api/teacher/grading/{assignmentId}/submissions/{studentId}` | 학생별 제출 상세 |
| POST | `/api/teacher/grading/{assignmentId}/submissions/{studentId}` | 채점 저장 |

**Request Body (POST 채점 저장):**
```json
{
  "answers": [
    {
      "answer_id": 1,
      "points_earned": 10,
      "is_correct": true
    },
    {
      "answer_id": 2,
      "points_earned": 0,
      "is_correct": false
    }
  ],
  "feedback": "전체 피드백"
}
```

---

### Phase 3: 오답 분석 (3개)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/teacher/analysis/questions` | 문항별 오답률 |
| GET | `/api/teacher/analysis/students` | 학생별 취약점 |
| GET | `/api/teacher/analysis/units` | 단원별 통계 |

**Query Parameters:**
- `type`: 분석 유형 (normal, clinic)
- `item_id`: 과제 ID
- `class_id`: 반 ID
- `start_date`: 시작일 (YYYY-MM-DD)
- `end_date`: 종료일 (YYYY-MM-DD)

---

### Phase 4: 클리닉 과제 (3개)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/teacher/clinic/wrong-answers` | 학생별 오답 문항 |
| POST | `/api/teacher/clinic/assignments` | 클리닉 과제 생성 |
| GET | `/api/teacher/clinic/similar-questions` | 유사 문제 추천 |

**Request Body (POST 클리닉 생성):**
```json
{
  "student_id": 1,
  "question_ids": [1, 2, 3],
  "clinic_type": "SAME",
  "title": "클리닉 과제 제목",
  "due_date": "2026-02-20"
}
```

**clinic_type:**
- `SAME`: 동일 문제
- `SIMILAR`: 유사 문제 (문제은행에서)

---

### Phase 5: 메시지 센터 (7개)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/teacher/messages/templates` | 템플릿 목록 |
| POST | `/api/teacher/messages/templates` | 템플릿 생성 |
| PUT | `/api/teacher/messages/templates/{id}` | 템플릿 수정 |
| DELETE | `/api/teacher/messages/templates/{id}` | 템플릿 삭제 |
| POST | `/api/teacher/messages/send` | 메시지 발송 |
| GET | `/api/teacher/messages/history` | 발송 내역 |
| GET | `/api/teacher/messages/contacts` | 연락처 목록 |

**Request Body (POST 메시지 발송):**
```json
{
  "target_type": "parents",
  "target_ids": [1, 2, 3],
  "title": "메시지 제목",
  "content": "메시지 내용",
  "template_id": 1
}
```

**target_type:**
- `parents`: 학부모
- `students`: 학생
- `class`: 반별

---

### Phase 6: 프린트 관리 (4개)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/teacher/print/assignments` | 과제 목록 |
| GET | `/api/teacher/print/exams` | 시험 목록 |
| GET | `/api/teacher/print/reports` | 리포트 목록 |
| POST | `/api/teacher/print/generate` | PDF 생성 |

**Request Body (POST PDF 생성):**
```json
{
  "document_type": "assignment",
  "document_id": 1,
  "show_answers": false,
  "show_points": true,
  "layout": "portrait"
}
```

**document_type:**
- `assignment`: 과제
- `exam`: 시험
- `report`: 리포트

---

## 데이터베이스 모델

### MessageTemplate (신규)

```sql
CREATE TABLE MessageTemplates (
    template_id INT AUTO_INCREMENT PRIMARY KEY,
    academy_id INT NOT NULL,
    teacher_id INT NULL,
    name VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    INDEX idx_message_template_academy (academy_id),
    INDEX idx_message_template_teacher (teacher_id),

    FOREIGN KEY (academy_id) REFERENCES Academies(academy_id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES Users(user_id) ON DELETE SET NULL
);
```

---

## 공통 패턴

### 인증
모든 API는 JWT 인증이 필요합니다.
```
Authorization: Bearer {access_token}
```

### 권한 확인
- `TeacherAppService.get_teacher_id()` - Teacher 테이블에서 teacher_id 조회
- `TeacherAppService.verify_class_teacher()` - 담당 반 확인
- `TeacherAppService.verify_student_teacher()` - 담당 학생 확인

### 에러 응답
```json
{
  "detail": "에러 메시지"
}
```

| 상태 코드 | 설명 |
|----------|------|
| 401 | 인증 필요 |
| 403 | 권한 없음 |
| 404 | 리소스 없음 |
| 422 | 입력 검증 실패 |

---

## 검증 방법

1. **서버 시작:**
   ```bash
   python main.py
   ```

2. **Swagger 확인:**
   http://localhost:8000/docs

3. **주요 API 테스트:**
   - 과제 목록: `GET /api/teacher/assignments`
   - 채점 저장: `POST /api/teacher/grading/{id}/submissions/{studentId}`
   - 메시지 발송: `POST /api/teacher/messages/send`

---

## 기존 코드 재사용

| 기능 | 재사용 모듈 |
|------|------------|
| 클리닉 생성 | `app/services/clinic_service.py` |
| PDF 생성 | `app/services/pdf_service.py` |
| 권한 확인 | `app/services/teacher_app_service.py` |

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-01-30 | 1.0.0 | 초기 구현 (26개 API) |
