# 반 수준별 선생님 배정 API 명세서

> **작성일**: 2026-02-11
> **대상**: 프론트엔드 개발자
> **요약**: 반 하나당 상(high)/중(mid)/하(low) 수준별 선생님 3명 배정 기능 추가

---

## 변경 개요

### 핵심 변경사항
- 기존: 반 1개 → 선생님 1명 (`teacher_id`)
- 변경: 반 1개 → 선생님 최대 3명 (상/중/하 수준별)

### 하위 호환성
- 기존 `teacher_id`, `teacher_name` 필드 **그대로 유지** (MID 선생님 기준)
- `level` 미지정 시 기본값 `"mid"` → 기존 프론트 코드 변경 없이도 동작
- 새 `teachers` 배열 필드가 응답에 추가됨 (사용 안 해도 무방)

---

## 1. 반(Class) API 변경사항

### 1-1. 반 목록 조회

```
GET /api/admin/classes
GET /api/admin/classes?teacher_id={id}
```

**응답 변경**: `teachers` 배열 추가

```jsonc
[
  {
    "id": 1,
    "name": "A반",
    "teacher_id": 10,          // 기존 유지 (MID 선생님)
    "teacher_name": "jason",   // 기존 유지
    "capacity": 20,
    "current_students": 4,
    "subject": "수학",
    "grade_level": "중1",
    "fee": 150000,
    "status": "active",
    // ✅ 새로 추가된 필드
    "teachers": [
      { "level": "high", "teacherId": 12, "teacherName": "jamie" },
      { "level": "mid",  "teacherId": 10, "teacherName": "jason" },
      { "level": "low",  "teacherId": 11, "teacherName": "jason" }
    ]
  }
]
```

> **`teacher_id` 필터 변경**: `?teacher_id=12` 조회 시, 해당 선생님이 **어떤 레벨이든** 배정된 반이 모두 조회됩니다. (기존에는 MID만 조회됨)

---

### 1-2. 반 상세 조회

```
GET /api/admin/classes/{class_id}
```

**응답**: 반 목록과 동일한 구조 + `students` 배열

```jsonc
{
  "id": 1,
  "name": "A반",
  "teacher_id": 10,
  "teacher_name": "jason",
  // ... 기존 필드 동일
  "teachers": [
    { "level": "high", "teacherId": 12, "teacherName": "jamie" },
    { "level": "mid",  "teacherId": 10, "teacherName": "jason" },
    { "level": "low",  "teacherId": 11, "teacherName": "jason" }
  ],
  "students": [
    { "id": 1, "name": "김철수" },
    { "id": 4, "name": "최다은" }
  ]
}
```

---

### 1-3. 반 생성

```
POST /api/admin/classes
```

**요청 변경**: `teachers_by_level` 필드 추가 (선택)

```jsonc
{
  "name": "영어 특강반",
  "teacher_id": 10,         // 기존 방식 (MID로 배정됨)
  "capacity": 20,
  "subject": "영어",
  "grade_level": "중2",
  "fee": 150000,
  "status": "active",
  // ✅ 새로 추가 (선택) - 수준별 선생님 일괄 배정
  "teachers_by_level": {
    "high": 12,   // 상 수준 선생님 ID
    "mid": 10,    // 중 수준 선생님 ID
    "low": 11     // 하 수준 선생님 ID
  }
}
```

> `teachers_by_level`과 `teacher_id`를 동시에 보내면 둘 다 적용됩니다.
> `teachers_by_level`만 보내도 MID 선생님이 자동으로 `teacher_id`에 동기화됩니다.

---

### 1-4. 반 수정

```
PUT /api/admin/classes/{class_id}
```

**요청 변경**: `teachers_by_level` 필드 추가 (선택)

```jsonc
{
  "teachers_by_level": {
    "high": 15,   // 상 수준 선생님 변경
    "mid": 10     // 일부만 변경 가능
  }
}
```

---

## 2. 선생님(Teacher) API 변경사항

### 2-1. 선생님 상세 조회

```
GET /api/admin/teachers/{teacher_id}
```

**응답 변경**: `classes` 배열에 `level` 필드 추가

```jsonc
{
  "id": 12,
  "name": "jamie",
  "subject": "상",
  "classCount": 1,
  // ... 기존 필드 동일
  "classes": [
    {
      "id": 1,
      "name": "A반",
      "subject": "수학",
      "grade": "중1",
      "level": "high",     // ✅ 새로 추가
      "assignedAt": null
    }
  ]
}
```

---

### 2-2. 선생님 담당반 목록

```
GET /api/admin/teachers/{teacher_id}/classes
```

**응답 변경**: 각 반에 `level` 필드 추가

```jsonc
{
  "classes": [
    {
      "id": 1,
      "name": "A반",
      "subject": "수학",
      "grade": "중1",
      "level": "high",     // ✅ 새로 추가 (null이면 레거시 배정)
      "assignedAt": null
    }
  ]
}
```

---

### 2-3. 선생님 반 배정

```
POST /api/admin/teachers/{teacher_id}/classes
```

**요청 변경**: `level` 필드 추가 (선택, 기본값 `"mid"`)

```jsonc
{
  "classIds": [1, 2],
  "level": "high"    // ✅ 새로 추가 (선택)
                     // "high" | "mid" | "low"
                     // 미지정 시 "mid" (기존 동작과 동일)
}
```

**level 값 설명**:

| 값 | 의미 | 비고 |
|-----|------|------|
| `"high"` | 상 수준 | |
| `"mid"` | 중 수준 | 기본값, `Classes.teacher_id`와 동기화 |
| `"low"` | 하 수준 | |

> 같은 반에 같은 레벨로 다른 선생님을 배정하면, 기존 배정이 **교체**됩니다.

---

### 2-4. 선생님 반 배정 해제

```
DELETE /api/admin/teachers/{teacher_id}/classes/{class_id}
DELETE /api/admin/teachers/{teacher_id}/classes/{class_id}?level=high
```

**Query Parameter 추가**: `level` (선택)

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `level` | string | N | `"high"` / `"mid"` / `"low"`. 미지정 시 해당 선생님의 **모든 레벨** 배정 해제 |

---

### 2-5. 선생님 퇴사 처리

```
DELETE /api/admin/teachers/{teacher_id}
```

변경 없음. 퇴사 시 해당 선생님의 **모든 수준별 배정이 자동 해제**됩니다.

---

## 3. `teachers` 배열 스키마

```typescript
// TypeScript 타입 정의

interface TeacherByLevel {
  level: "high" | "mid" | "low";  // 수준
  teacherId: number;               // 선생님 ID
  teacherName: string | null;      // 선생님 이름
}

// ClassResponse에 추가
interface ClassResponse {
  // ... 기존 필드
  teacher_id: number | null;       // 기존 유지 (MID 선생님)
  teacher_name: string | null;     // 기존 유지
  teachers: TeacherByLevel[];      // ✅ 새로 추가
}
```

---

## 4. 프론트엔드 적용 가이드

### 즉시 변경 불필요 (기존 코드 그대로 동작)
- `teacher_id`, `teacher_name` 필드 유지
- `classIds` 만으로 배정 (기본 MID)
- 기존 모든 페이지 정상 동작

### 수준별 배정 UI 구현 시

1. **반 상세 페이지**: `teachers` 배열로 상/중/하 선생님 표시
2. **선생님 배정 모달**: `level` 드롭다운 추가 (`high`/`mid`/`low`)
3. **반 생성/수정 폼**: `teachers_by_level` 객체 전송
4. **선생님 상세 페이지**: `classes[].level` 뱃지 표시

### 예시: 반 상세에서 수준별 선생님 표시

```tsx
// teachers 배열이 있으면 수준별 표시, 없으면 기존 teacher_name 표시
{classData.teachers.length > 0 ? (
  classData.teachers.map(t => (
    <div key={t.level}>
      <Badge>{t.level === 'high' ? '상' : t.level === 'mid' ? '중' : '하'}</Badge>
      <span>{t.teacherName}</span>
    </div>
  ))
) : (
  <span>{classData.teacher_name || '미배정'}</span>
)}
```
