# 프론트엔드 전달용 - Classes API 변경사항

## 개요
Classes(반) 관련 API에 4개의 새 필드가 추가되었습니다.

---

## 추가된 필드

| 필드명 | 타입 | 필수 여부 | 기본값 | 설명 |
|--------|------|----------|--------|------|
| `subject` | string | 선택 | null | 과목 (최대 50자) |
| `grade_level` | string | 선택 | null | 학년/레벨 (최대 30자) |
| `fee` | integer | 선택 | null | 수강료 (원, 0 이상) |
| `status` | enum | 필수 | "active" | 반 상태 |

### status Enum 값
| 값 | 설명 |
|----|------|
| `active` | 운영중 |
| `inactive` | 비활성 |
| `pending` | 대기 |
| `closed` | 종료 |

---

## API 변경사항

### 1. 클래스 목록 조회
**GET** `/api/admin/classes`

#### 변경된 Query Parameters
| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| `status` | string | 선택 | 반 상태 필터 (`active`, `inactive`, `pending`, `closed`) |

#### 사용 예시
```
GET /api/admin/classes?status=active
GET /api/admin/classes?teacher_id=10&status=active
```

#### 응답 예시
```json
[
  {
    "id": 1,
    "name": "수학 정규반 A",
    "teacher_id": 10,
    "teacher_name": "박선생",
    "capacity": 15,
    "current_students": 12,
    "subject": "수학",
    "grade_level": "중3",
    "fee": 200000,
    "status": "active"
  }
]
```

---

### 2. 클래스 생성
**POST** `/api/admin/classes`

#### Request Body
```json
{
  "name": "영어 특강반",
  "teacher_id": 10,
  "capacity": 20,
  "subject": "영어",
  "grade_level": "중2",
  "fee": 150000,
  "status": "active"
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `name` | string | ✅ | 반 이름 (1-50자) |
| `teacher_id` | integer | ❌ | 담당 선생님 ID |
| `capacity` | integer | ❌ | 정원 (1 이상) |
| `subject` | string | ❌ | 과목 (최대 50자) |
| `grade_level` | string | ❌ | 학년/레벨 (최대 30자) |
| `fee` | integer | ❌ | 수강료 (0 이상) |
| `status` | string | ❌ | 반 상태 (기본값: "active") |

---

### 3. 클래스 수정
**PUT** `/api/admin/classes/{class_id}`

#### Request Body (모든 필드 선택)
```json
{
  "name": "수학 고급반",
  "capacity": 25,
  "subject": "수학",
  "grade_level": "중3",
  "fee": 200000,
  "status": "active"
}
```

---

### 4. 클래스 상세 조회
**GET** `/api/admin/classes/{class_id}`

#### 응답 예시
```json
{
  "id": 1,
  "name": "수학 정규반 A",
  "teacher_id": 10,
  "teacher_name": "박선생",
  "capacity": 15,
  "current_students": 12,
  "subject": "수학",
  "grade_level": "중3",
  "fee": 200000,
  "status": "active",
  "students": [
    {"id": 1, "name": "김철수"},
    {"id": 2, "name": "이영희"}
  ]
}
```

---

## 주의사항

1. **기존 데이터 호환**: `subject`, `grade_level`, `fee`는 기존 데이터에서 `null`일 수 있음
2. **status 기본값**: 생성 시 status를 지정하지 않으면 자동으로 `"active"` 설정
3. **fee 단위**: 원(KRW) 단위, 정수형
