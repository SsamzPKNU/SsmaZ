# StudentContacts API 권한 변경 안내

> **변경일**: 2026-02-05
> **변경 사항**: 학부모 연락처 API 접근 권한 제한

---

## 변경 요약

학생 연락처(StudentContacts) API가 **관리자/선생님 전용**으로 변경되었습니다.

| 변경 전 | 변경 후 |
|--------|--------|
| 모든 인증된 사용자 접근 가능 | ADMIN, TEACHER만 접근 가능 |

---

## 영향받는 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/students/{student_id}/contacts` | 연락처 추가 |
| GET | `/students/{student_id}/contacts` | 연락처 목록 조회 |
| PUT | `/students/contacts/{contact_id}` | 연락처 수정 |
| DELETE | `/students/contacts/{contact_id}` | 연락처 삭제 |

---

## 권한별 응답

| 사용자 권한 | HTTP 상태 | 응답 |
|------------|-----------|------|
| 비인증 | 401 | `{"detail": "Not authenticated"}` |
| STUDENT | **403** | `{"detail": "관리자 또는 선생님 권한이 필요합니다. 현재 권한: STUDENT"}` |
| TEACHER | 200/201/204 | 정상 응답 |
| ADMIN | 200/201/204 | 정상 응답 |

---

## 프론트엔드 대응 가이드

### 1. 학생 포털에서 연락처 API 호출 제거

학생 계정으로 로그인한 경우, 해당 API를 호출하지 않도록 처리해야 합니다.

```javascript
// 권한 체크 예시
if (userRole === 'ADMIN' || userRole === 'TEACHER') {
  // 연락처 API 호출 가능
  const contacts = await fetchStudentContacts(studentId);
} else {
  // 학생은 연락처 관리 UI 숨김
}
```

### 2. 403 에러 핸들링 추가

```javascript
try {
  const response = await fetch(`/students/${studentId}/contacts`, {
    credentials: 'include'
  });

  if (response.status === 403) {
    // 권한 없음 처리
    alert('연락처 조회 권한이 없습니다.');
    return;
  }

  const data = await response.json();
} catch (error) {
  console.error('API 호출 실패:', error);
}
```

### 3. UI 조건부 렌더링

학생 권한일 경우 연락처 관리 메뉴/버튼을 숨기는 것을 권장합니다.

```jsx
// React 예시
{(userRole === 'ADMIN' || userRole === 'TEACHER') && (
  <ContactManagementSection studentId={studentId} />
)}
```

---

## 기존 API 스펙 (변경 없음)

### Request/Response 형식은 동일

**연락처 추가 예시:**
```json
// POST /students/{student_id}/contacts
// Request Body
{
  "phone": "010-1234-5678",
  "label": "엄마",
  "priority": 1,
  "is_active": true
}

// Response (201 Created)
{
  "contact_id": 1,
  "student_id": 10,
  "phone": "010-1234-5678",
  "label": "엄마",
  "priority": 1,
  "is_active": true,
  "created_at": "2026-02-05T10:00:00",
  "updated_at": null
}
```

---

## 문의

API 관련 문의사항은 백엔드 팀에 연락해주세요.
