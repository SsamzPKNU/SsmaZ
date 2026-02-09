# 메시지 센터 API 명세

선생님용 메시지 센터 API입니다. 템플릿 관리, 메시지 발송, 발송 내역 조회, 반별 연락처 조회 기능을 제공합니다.

## 인증

모든 엔드포인트는 JWT 인증이 필요합니다.

```
Cookie: access_token=<JWT_TOKEN>
```

또는

```
Authorization: Bearer <JWT_TOKEN>
```

---

## 1. 템플릿 목록 조회

내 템플릿 + 학원 공용 템플릿을 조회합니다.

```
GET /api/teacher/messages/templates
```

### Query Parameters

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `category` | string | X | 카테고리 필터 (`출석`, `시험`, `성적`, `과제`, `공지`, `일반`) |

### Response `200 OK`

```json
{
  "items": [
    {
      "id": 1,
      "name": "출석 알림 템플릿",
      "content": "{student_name} 학생이 출석했습니다.",
      "category": "출석",
      "is_shared": false,
      "created_at": "2026-02-09T10:00:00",
      "updated_at": null
    }
  ],
  "total": 1
}
```

### Response Fields

| 필드 | 타입 | 설명 |
|------|------|------|
| `id` | int | 템플릿 ID |
| `name` | string | 템플릿 이름 |
| `content` | string | 템플릿 내용 |
| `category` | string \| null | 카테고리 (`출석`, `시험`, `성적`, `과제`, `공지`, `일반`) |
| `is_shared` | boolean | 학원 공용 여부 (`true`: 공용, `false`: 개인) |
| `created_at` | datetime | 생성 시간 |
| `updated_at` | datetime \| null | 수정 시간 |

---

## 2. 템플릿 생성

새 메시지 템플릿을 생성합니다.

```
POST /api/teacher/messages/templates
```

### Request Body

```json
{
  "name": "출석 알림 템플릿",
  "content": "{student_name} 학생이 {date} 출석했습니다.",
  "category": "출석"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `name` | string | O | 템플릿 이름 (최대 100자) |
| `content` | string | O | 템플릿 내용 |
| `category` | string | O | 카테고리 (`출석`, `시험`, `성적`, `과제`, `공지`, `일반`) |

### Response `201 Created`

```json
{
  "id": 1,
  "name": "출석 알림 템플릿",
  "content": "{student_name} 학생이 {date} 출석했습니다.",
  "category": "출석",
  "is_shared": false,
  "created_at": "2026-02-09T10:00:00",
  "updated_at": null
}
```

---

## 3. 템플릿 수정

본인이 생성한 템플릿만 수정할 수 있습니다.

```
PUT /api/teacher/messages/templates/{id}
```

### Path Parameters

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `id` | int | 템플릿 ID |

### Request Body

모든 필드는 선택입니다. 변경할 필드만 전송하세요.

```json
{
  "name": "수정된 템플릿 이름",
  "content": "수정된 내용",
  "category": "공지"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `name` | string | X | 템플릿 이름 (최대 100자) |
| `content` | string | X | 템플릿 내용 |
| `category` | string | X | 카테고리 |

### Response `200 OK`

수정된 템플릿 객체 반환 (템플릿 생성 응답과 동일 형식)

### Error `404 Not Found`

```json
{
  "detail": "템플릿을 찾을 수 없거나 수정 권한이 없습니다"
}
```

---

## 4. 템플릿 삭제

본인이 생성한 템플릿만 삭제할 수 있습니다.

```
DELETE /api/teacher/messages/templates/{id}
```

### Path Parameters

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `id` | int | 템플릿 ID |

### Response `200 OK`

```json
{
  "message": "템플릿이 삭제되었습니다"
}
```

### Error `404 Not Found`

```json
{
  "detail": "템플릿을 찾을 수 없거나 삭제 권한이 없습니다"
}
```

---

## 5. 메시지 발송

학생의 학부모에게 메시지를 발송합니다. (현재는 DB 기록만, SMS 연동은 추후)

```
POST /api/teacher/messages/send
```

### Request Body

```json
{
  "class_id": 1,
  "student_ids": [1, 2, 3],
  "type": "normal",
  "content": "안녕하세요. 내일 시험이 있습니다. 준비 잘 부탁드립니다.",
  "template_id": 1
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `class_id` | int | O | 대상 반 ID |
| `student_ids` | int[] | O | 대상 학생 ID 목록 (최소 1명) |
| `type` | string | O | 메시지 유형 (`normal`, `urgent`, `notice`) |
| `content` | string | O | 메시지 내용 (변수 치환 완료된 텍스트) |
| `template_id` | int | X | 사용한 템플릿 ID |

### Response `200 OK`

```json
{
  "message": "메시지 발송 완료 (성공: 3, 실패: 0)",
  "sent_count": 3,
  "failed_count": 0,
  "results": [
    {
      "student_id": 1,
      "status": "sent",
      "error": null
    },
    {
      "student_id": 2,
      "status": "sent",
      "error": null
    },
    {
      "student_id": 3,
      "status": "sent",
      "error": null
    }
  ]
}
```

### Response Fields

| 필드 | 타입 | 설명 |
|------|------|------|
| `message` | string | 발송 결과 요약 메시지 |
| `sent_count` | int | 발송 성공 건수 |
| `failed_count` | int | 발송 실패 건수 |
| `results` | array | 학생별 발송 결과 |
| `results[].student_id` | int | 학생 ID |
| `results[].status` | string | `sent` 또는 `failed` |
| `results[].error` | string \| null | 실패 시 오류 메시지 |

### Error `404 Not Found`

```json
{
  "detail": "반을 찾을 수 없습니다"
}
```

### Error `400 Bad Request`

```json
{
  "detail": "유효한 학생이 없습니다"
}
```

---

## 6. 발송 내역 조회

메시지 발송 내역을 페이지네이션으로 조회합니다.

```
GET /api/teacher/messages/history
```

### Query Parameters

| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|-------|------|
| `page` | int | X | 1 | 페이지 번호 (1 이상) |
| `limit` | int | X | 20 | 페이지 크기 (1~100) |
| `class_id` | int | X | - | 반 ID 필터 |
| `type` | string | X | - | 메시지 유형 필터 (`normal`, `urgent`, `notice`) |

### Response `200 OK`

```json
{
  "items": [
    {
      "id": 1,
      "type": "normal",
      "content": "안녕하세요. 내일 시험이 있습니다.",
      "class_id": 1,
      "class_name": "수학 A반",
      "recipients": [
        {
          "student_id": 1,
          "student_name": "김민수",
          "parent_phone": "010-1234-5678",
          "status": "sent"
        },
        {
          "student_id": 2,
          "student_name": "이영희",
          "parent_phone": "010-9876-5432",
          "status": "sent"
        }
      ],
      "sent_at": "2026-02-09T10:30:00",
      "sent_count": 2,
      "failed_count": 0
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20
}
```

### Response Fields

| 필드 | 타입 | 설명 |
|------|------|------|
| `items` | array | 발송 내역 목록 |
| `items[].id` | int | 메시지 ID |
| `items[].type` | string | 메시지 유형 (`normal`, `urgent`, `notice`) |
| `items[].content` | string | 메시지 내용 |
| `items[].class_id` | int \| null | 대상 반 ID |
| `items[].class_name` | string \| null | 대상 반 이름 |
| `items[].recipients` | array | 수신자 목록 |
| `items[].recipients[].student_id` | int | 학생 ID |
| `items[].recipients[].student_name` | string | 학생 이름 |
| `items[].recipients[].parent_phone` | string \| null | 학부모 연락처 |
| `items[].recipients[].status` | string | 발송 상태 (`sent`, `delivered`, `failed`) |
| `items[].sent_at` | datetime \| null | 발송 시간 |
| `items[].sent_count` | int | 성공 건수 |
| `items[].failed_count` | int | 실패 건수 |
| `total` | int | 전체 건수 |
| `page` | int | 현재 페이지 |
| `limit` | int | 페이지 크기 |

---

## 7. 반별 연락처 조회

특정 반의 학생-학부모 연락처 목록을 조회합니다.

```
GET /api/teacher/classes/{classId}/contacts
```

### Path Parameters

| 파라미터 | 타입 | 설명 |
|---------|------|------|
| `classId` | int | 반 ID |

### Response `200 OK`

```json
{
  "items": [
    {
      "student_id": 1,
      "student_name": "김민수",
      "parent_phone": "010-1234-5678"
    },
    {
      "student_id": 2,
      "student_name": "이영희",
      "parent_phone": "010-9876-5432"
    }
  ],
  "total": 2
}
```

### Response Fields

| 필드 | 타입 | 설명 |
|------|------|------|
| `items` | array | 연락처 목록 |
| `items[].student_id` | int | 학생 ID |
| `items[].student_name` | string | 학생 이름 |
| `items[].parent_phone` | string \| null | 학부모 연락처 (StudentContacts 우선, 없으면 Student.parent_phone 폴백) |
| `total` | int | 전체 건수 |

> **참고**: `parent_phone`은 `StudentContacts` 테이블에서 가장 우선순위 높은(priority=1) 활성 연락처의 phone을 사용합니다. 등록된 연락처가 없으면 `Student.parent_phone`으로 폴백합니다.

---

## Enum 참조

### 템플릿 카테고리 (`category`)

| 값 | 설명 |
|----|------|
| `출석` | 출석 관련 |
| `시험` | 시험 관련 |
| `성적` | 성적 관련 |
| `과제` | 과제 관련 |
| `공지` | 공지 관련 |
| `일반` | 일반 |

### 메시지 유형 (`type`)

| 값 | 설명 |
|----|------|
| `normal` | 일반 메시지 |
| `urgent` | 긴급 메시지 |
| `notice` | 공지 메시지 |

### 발송 상태 (`status`)

| 값 | 설명 |
|----|------|
| `sent` | 발송 완료 |
| `delivered` | 전달 완료 |
| `failed` | 발송 실패 |

---

## 에러 응답 형식

모든 에러는 다음 형식으로 반환됩니다:

```json
{
  "detail": "에러 메시지"
}
```

| HTTP 코드 | 설명 |
|-----------|------|
| `400` | 잘못된 요청 (유효하지 않은 데이터) |
| `401` | 인증 실패 (토큰 없음 또는 만료) |
| `404` | 리소스를 찾을 수 없음 |
| `422` | 유효성 검증 실패 (필수 필드 누락, 타입 오류 등) |
