# SSamZ API - 학생 연락처 관리 명세서

> **최종 수정일**: 2026-01-27

---

## 개요

학생별 다중 연락처 관리를 위한 API입니다.
- 학생당 여러 연락처 등록 가능 (엄마, 아빠, 할머니 등)
- 우선순위(priority) 설정으로 알림 발송 순서 지정
- 활성화(is_active) 상태로 연락처 사용 여부 관리

---

## API 엔드포인트

### 1. 연락처 추가

#### Endpoint
```
POST /students/{student_id}/contacts
```

#### Path Parameters
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| student_id | Integer | 학생 ID |

#### Headers
```
Cookie: access_token=...
X-CSRF-Token: {csrf_token}
Content-Type: application/json
```

#### Request Body
```json
{
  "phone": "01012345678",
  "label": "엄마",
  "priority": 1,
  "is_active": true
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| phone | String | O | 전화번호 (최대 20자) |
| label | String | X | 연락처 라벨 (최대 50자) |
| priority | Integer | X | 알림 우선순위 (1이 가장 먼저, 기본값: 1) |
| is_active | Boolean | X | 활성화 여부 (기본값: true) |

#### Response (201 Created)
```json
{
  "contact_id": 1,
  "student_id": 10,
  "phone": "01012345678",
  "label": "엄마",
  "priority": 1,
  "is_active": true,
  "created_at": "2026-01-27T10:00:00",
  "updated_at": null
}
```

---

### 2. 연락처 목록 조회

#### Endpoint
```
GET /students/{student_id}/contacts
```

#### Path Parameters
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| student_id | Integer | 학생 ID |

#### Query Parameters
| 파라미터 | 타입 | 설명 | 기본값 |
|---------|------|------|--------|
| active_only | Boolean | 활성 연락처만 조회 | false |

#### Response (200 OK)
```json
{
  "contacts": [
    {
      "contact_id": 1,
      "student_id": 10,
      "phone": "01012345678",
      "label": "엄마",
      "priority": 1,
      "is_active": true,
      "created_at": "2026-01-27T10:00:00",
      "updated_at": null
    },
    {
      "contact_id": 2,
      "student_id": 10,
      "phone": "01098765432",
      "label": "아빠",
      "priority": 2,
      "is_active": true,
      "created_at": "2026-01-27T10:05:00",
      "updated_at": null
    }
  ],
  "total": 2
}
```

> 결과는 `priority` 오름차순으로 정렬됨 (1이 가장 먼저)

---

### 3. 연락처 수정

#### Endpoint
```
PUT /students/contacts/{contact_id}
```

#### Path Parameters
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| contact_id | Integer | 연락처 ID |

#### Request Body
```json
{
  "phone": "01011112222",
  "label": "엄마 (직장)",
  "priority": 1,
  "is_active": true
}
```

> 모든 필드 선택사항

#### Response (200 OK)
```json
{
  "contact_id": 1,
  "student_id": 10,
  "phone": "01011112222",
  "label": "엄마 (직장)",
  "priority": 1,
  "is_active": true,
  "created_at": "2026-01-27T10:00:00",
  "updated_at": "2026-01-27T11:00:00"
}
```

---

### 4. 연락처 삭제

#### Endpoint
```
DELETE /students/contacts/{contact_id}
```

#### Path Parameters
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| contact_id | Integer | 연락처 ID |

#### Response (204 No Content)
응답 바디 없음

---

## 데이터베이스 스키마

### StudentContacts 테이블
```sql
CREATE TABLE StudentContacts (
    contact_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    phone VARCHAR(20) NOT NULL,
    label VARCHAR(50),
    priority INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE
);
```

---

## 사용 예시

### 학생 연락처 등록 (JavaScript)
```javascript
async function addContact(studentId, contactData) {
  const response = await fetch(`/students/${studentId}/contacts`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': csrfToken
    },
    credentials: 'include',
    body: JSON.stringify(contactData)
  });
  return await response.json();
}

// 사용 예시
await addContact(10, {
  phone: '01012345678',
  label: '엄마',
  priority: 1
});
```

### 활성 연락처만 조회
```javascript
async function getActiveContacts(studentId) {
  const response = await fetch(
    `/students/${studentId}/contacts?active_only=true`,
    { credentials: 'include' }
  );
  return await response.json();
}
```

---

## 에러 응답

### 404 Not Found
```json
{
  "detail": "학생을 찾을 수 없습니다"
}
```

```json
{
  "detail": "연락처를 찾을 수 없습니다"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "phone"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 관련 문서

- 학생 관리 API: 별도 문서 참조
- 선생님 출퇴근 API: `API_SPEC_TEACHER_ATTENDANCE.md`
