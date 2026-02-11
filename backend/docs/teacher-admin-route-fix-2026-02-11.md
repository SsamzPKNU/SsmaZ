# Teacher/Admin 라우트 경로 수정 명세서

> **최종 수정일**: 2026-02-11
> **변경 사유**: Vite 프록시가 `/api` prefix를 제거 후 백엔드로 전달하므로, 백엔드 라우터 prefix에서 `/api`를 제거하여 404 해소

---

## 변경 요약

프론트엔드에서 `GET /api/teacher/assignments` 호출 시:
- **Vite 프록시**: `/api` 제거 → 백엔드에 `GET /teacher/assignments` 전달
- **변경 전**: 백엔드가 `/api/teacher/assignments`를 기대 → **404**
- **변경 후**: 백엔드가 `/teacher/assignments`를 기대 → **정상 응답**

**프론트엔드 코드 변경 불필요** - 기존 `/api/...` 호출 그대로 사용하면 됩니다.

---

## 1. 선생님 과제/채점 (`/teacher`)

| Method | URL | 설명 |
|--------|-----|------|
| `GET` | `/api/teacher/assignments` | 과제 목록 조회 |
| `GET` | `/api/teacher/assignments/{assignment_id}` | 과제 상세 조회 |
| `POST` | `/api/teacher/assignments` | 과제 생성 |
| `PUT` | `/api/teacher/assignments/{assignment_id}` | 과제 수정 |
| `DELETE` | `/api/teacher/assignments/{assignment_id}` | 과제 삭제 |
| `GET` | `/api/teacher/grading` | 채점 대기 목록 |
| `GET` | `/api/teacher/grading/{assignment_id}/submissions` | 과제별 제출 현황 |
| `GET` | `/api/teacher/grading/{assignment_id}/submissions/{student_id}` | 학생별 제출 상세 |
| `POST` | `/api/teacher/grading/{assignment_id}/submissions/{student_id}` | 채점 저장 |
| `POST` | `/api/teacher/grading/{assignment_id}/quick-grade` | 간편 채점 |

## 2. 선생님 메시지 (`/teacher/messages`)

| Method | URL | 설명 |
|--------|-----|------|
| `GET` | `/api/teacher/messages/templates` | 템플릿 목록 조회 |
| `POST` | `/api/teacher/messages/templates` | 템플릿 생성 |
| `PUT` | `/api/teacher/messages/templates/{template_id}` | 템플릿 수정 |
| `DELETE` | `/api/teacher/messages/templates/{template_id}` | 템플릿 삭제 |
| `POST` | `/api/teacher/messages/send` | 메시지 발송 |
| `GET` | `/api/teacher/messages/history` | 발송 내역 조회 |
| `GET` | `/api/teacher/messages/contacts` | 연락처 목록 조회 |

## 3. 선생님 오답 분석 (`/teacher/analysis`)

| Method | URL | 설명 |
|--------|-----|------|
| `GET` | `/api/teacher/analysis/questions` | 문항별 오답률 분석 |
| `GET` | `/api/teacher/analysis/students` | 학생별 취약점 분석 |
| `GET` | `/api/teacher/analysis/units` | 단원별 통계 |

## 4. 선생님 클리닉 (`/teacher/clinic`)

| Method | URL | 설명 |
|--------|-----|------|
| `GET` | `/api/teacher/clinic/wrong-answers` | 학생별 오답 문항 조회 |
| `POST` | `/api/teacher/clinic/assignments` | 클리닉 과제 생성 |
| `GET` | `/api/teacher/clinic/similar-questions` | 유사 문제 추천 |

## 5. 선생님 프린트 (`/teacher/print`)

| Method | URL | 설명 |
|--------|-----|------|
| `GET` | `/api/teacher/print/assignments` | 프린트용 과제 목록 |
| `GET` | `/api/teacher/print/exams` | 프린트용 시험 목록 |
| `GET` | `/api/teacher/print/reports` | 프린트용 리포트 목록 |
| `POST` | `/api/teacher/print/generate` | PDF 생성 |

## 6. 관리자 - 선생님 관리 (`/admin/teachers`)

| Method | URL | 설명 |
|--------|-----|------|
| `GET` | `/api/admin/teachers` | 선생님 목록 조회 |
| `GET` | `/api/admin/teachers/{teacher_id}` | 선생님 상세 조회 |
| `POST` | `/api/admin/teachers` | 선생님 등록 |
| `PUT` | `/api/admin/teachers/{teacher_id}` | 선생님 정보 수정 |
| `DELETE` | `/api/admin/teachers/{teacher_id}` | 선생님 퇴사 처리 |
| `GET` | `/api/admin/teachers/{teacher_id}/classes` | 담당반 목록 조회 |
| `POST` | `/api/admin/teachers/{teacher_id}/classes` | 반 배정 |
| `DELETE` | `/api/admin/teachers/{teacher_id}/classes/{class_id}` | 반 배정 해제 |

## 7. 관리자 - 클래스 관리 (`/admin/classes`)

| Method | URL | 설명 |
|--------|-----|------|
| `GET` | `/api/admin/classes` | 클래스 목록 조회 |
| `GET` | `/api/admin/classes/{class_id}` | 클래스 상세 조회 |
| `POST` | `/api/admin/classes` | 클래스 생성 |
| `PUT` | `/api/admin/classes/{class_id}` | 클래스 수정 |
| `DELETE` | `/api/admin/classes/{class_id}` | 클래스 삭제 |
| `GET` | `/api/admin/classes/{class_id}/students` | 반별 학생 목록 |
| `GET` | `/api/admin/classes/{class_id}/schedules` | 시간표 목록 |
| `POST` | `/api/admin/classes/{class_id}/schedules` | 시간표 생성 |
| `DELETE` | `/api/admin/classes/schedules/{schedule_id}` | 시간표 삭제 |

---

## 인증

모든 API에 인증 필요:
- **Header**: `Authorization: Bearer {token}`
- **Cookie**: httpOnly 쿠키 (로그인 시 자동 설정)

## 참고

- 모든 API는 인증 없이 호출 시 `401 Unauthorized` 반환
- Admin 전용 API(`/api/admin/...`)는 ADMIN 역할 필요, 그 외는 `403 Forbidden`
- 총 **44개 엔드포인트** (Teacher 27개 + Admin 17개)
