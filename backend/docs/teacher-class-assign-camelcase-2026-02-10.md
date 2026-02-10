# 강사 반 배정 API - Request Body camelCase 대응

**작성일:** 2026-02-10

---

## 개요

강사 반 배정 API(`POST /api/admin/teachers/{id}/classes`)의 Request Body가 **camelCase(`classIds`)와 snake_case(`class_ids`) 모두 수용**하도록 변경되었습니다.

프론트엔드에서 camelCase 컨벤션을 사용하므로, 별도 변환 없이 `classIds`로 바로 전송할 수 있습니다.

---

## 변경 대상 API

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/admin/teachers/{id}/classes` | 강사 반 배정 |

---

## Request Body 변경 사항

### Before (snake_case만 허용)

```json
{
  "class_ids": [1, 3, 5]
}
```

### After (camelCase + snake_case 모두 허용)

```json
// camelCase (권장)
{
  "classIds": [1, 3, 5]
}

// snake_case (하위 호환)
{
  "class_ids": [1, 3, 5]
}
```

### 필드 상세

| 필드명 | alias | 타입 | 필수 | 설명 |
|--------|-------|------|------|------|
| class_ids | classIds | `int[]` | O | 배정할 반 ID 목록 |

> **프론트엔드 권장:** `classIds` (camelCase) 사용

---

## 프론트엔드 적용 예시

```typescript
// 강사 반 배정
const assignClasses = async (teacherId: number, classIds: number[]) => {
  const response = await fetch(`/api/admin/teachers/${teacherId}/classes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ classIds }),  // camelCase 그대로 사용
  });
  return response.json();
};
```

---

## Response (변경 없음)

```json
{
  "message": "반 배정이 완료되었습니다",
  "teacher_id": 5,
  "assigned_classes": [1, 3, 5]
}
```

---

## 수정 파일

| 파일 경로 | 변경 내용 |
|----------|----------|
| `app/schemas/teacher.py` | `ClassAssign` 스키마에 `ConfigDict(populate_by_name=True)` 및 `alias="classIds"` 추가 |

---

## 기존 호환성

- snake_case(`class_ids`)로 전송해도 정상 동작 (하위 호환 유지)
- Response 형식은 변경 없음
