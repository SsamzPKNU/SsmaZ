# SSamZ Admin API - 선생님 관리 명세서

## 👨‍🏫 선생님 관리 API

### 3-1. 선생님 목록 조회

#### Endpoint
```
GET /api/admin/teachers
```

#### Query Parameters
| 파라미터 | 타입 | 설명 | 기본값 |
|---------|------|------|--------|
| status | String | 재직 상태 필터 (`active`, `leave`, `resigned`) | 전체 |
| skip | Integer | 페이지네이션 오프셋 | 0 |
| limit | Integer | 페이지네이션 제한 (최대: 1000) | 100 |

#### Headers
```
Authorization: Bearer {access_token}
```

#### Response (200 OK)
```json
[
  {
    "id": 10,
    "name": "박선생",
    "subject": "수학",
    "phone": "010-1234-5678",
    "email": "park@ssamz.com",
    "join_date": "2024-03-01",
    "status": "active",
    "assigned_classes": 3
  }
]
```

---

### 3-2. 선생님 등록

#### Endpoint
```
POST /api/admin/teachers
```

#### Headers
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

#### Request Body
```json
{
  "name": "새선생",
  "subject": "영어",
  "phone": "010-9999-8888",
  "email": "new@ssamz.com",
  "join_date": "2026-02-01"
}
```

**필드 설명:**
| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| name | String | ✅ | 선생님 이름 (1~50자) |
| subject | String | ❌ | 담당 과목 (최대 50자) |
| phone | String | ❌ | 전화번호 (최대 20자) |
| email | String | ❌ | 이메일 (유효한 이메일 형식) |
| join_date | String | ❌ | 입사일 (YYYY-MM-DD) |

#### Response (201 Created)
```json
{
  "id": 11,
  "name": "새선생",
  "subject": "영어",
  "phone": "010-9999-8888",
  "email": "new@ssamz.com",
  "join_date": "2026-02-01",
  "status": "active",
  "assigned_classes": 0
}
```

---

### 3-3. 선생님 정보 수정

#### Endpoint
```
PUT /api/admin/teachers/{teacherId}
```

#### Path Parameters
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| teacherId | Integer | 선생님 ID |

#### Headers
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

#### Request Body
```json
{
  "name": "박선생",
  "subject": "수학",
  "phone": "010-1234-5678",
  "email": "park@ssamz.com",
  "status": "active"
}
```

**필드 설명** (모두 선택사항):
| 필드 | 타입 | 설명 |
|------|------|------|
| name | String | 선생님 이름 |
| subject | String | 담당 과목 |
| phone | String | 전화번호 |
| email | String | 이메일 |
| join_date | String | 입사일 (YYYY-MM-DD) |
| status | String | 재직 상태 (`active`, `leave`, `resigned`) |

#### Response (200 OK)
```json
{
  "id": 10,
  "name": "박선생",
  "subject": "수학",
  "phone": "010-1234-5678",
  "email": "park@ssamz.com",
  "join_date": "2024-03-01",
  "status": "active",
  "assigned_classes": 3
}
```

---

### 3-4. 선생님 삭제

#### Endpoint
```
DELETE /api/admin/teachers/{teacherId}
```

#### Path Parameters
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| teacherId | Integer | 선생님 ID |

#### Headers
```
Authorization: Bearer {access_token}
```

#### Response (204 No Content)
응답 바디 없음

---

### 3-5. 선생님 정보 조회 (단일)

#### Endpoint
```
GET /api/admin/teachers/{teacherId}
```

#### Path Parameters
| 파라미터 | 타입 | 설명 |
|---------|------|------|
| teacherId | Integer | 선생님 ID |

#### Headers
```
Authorization: Bearer {access_token}
```

#### Response (200 OK)
```json
{
  "id": 10,
  "name": "박선생",
  "subject": "수학",
  "phone": "010-1234-5678",
  "email": "park@ssamz.com",
  "join_date": "2024-03-01",
  "status": "active",
  "assigned_classes": 3
}
```

---

## 📝 프론트엔드 사용 예시

### 선생님 목록 조회

```javascript
async function getTeachers(status = null) {
  const token = localStorage.getItem('access_token');
  const url = new URL('http://localhost:8000/api/admin/teachers');
  
  if (status) {
    url.searchParams.append('status', status);
  }
  
  const response = await fetch(url, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  return await response.json();
}

// 사용 예시
const allTeachers = await getTeachers();
const activeTeachers = await getTeachers('active');
```

### 선생님 등록

```javascript
async function createTeacher(teacherData) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch('http://localhost:8000/api/admin/teachers', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(teacherData)
  });
  
  if (!response.ok) {
    throw new Error('선생님 등록 실패');
  }
  
  return await response.json();
}

// 사용 예시
const newTeacher = await createTeacher({
  name: '새선생',
  subject: '영어',
  phone: '010-9999-8888',
  email: 'new@ssamz.com',
  join_date: '2026-02-01'
});
```

### 선생님 정보 수정

```javascript
async function updateTeacher(teacherId, updateData) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`http://localhost:8000/api/admin/teachers/${teacherId}`, {
    method: 'PUT',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(updateData)
  });
  
  if (!response.ok) {
    throw new Error('선생님 정보 수정 실패');
  }
  
  return await response.json();
}

// 사용 예시
const updated = await updateTeacher(10, {
  subject: '수학',
  status: 'active'
});
```

### 선생님 삭제

```javascript
async function deleteTeacher(teacherId) {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`http://localhost:8000/api/admin/teachers/${teacherId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (!response.ok) {
    throw new Error('선생님 삭제 실패');
  }
  
  return true;
}

// 사용 예시
await deleteTeacher(10);
```

---

## 🎨 React Component 예시

### 선생님 목록 컴포넌트

```jsx
import { useState, useEffect } from 'react';

function TeacherList() {
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, active, leave, resigned

  useEffect(() => {
    fetchTeachers();
  }, [filter]);

  const fetchTeachers = async () => {
    setLoading(true);
    try {
      const status = filter === 'all' ? null : filter;
      const data = await getTeachers(status);
      setTeachers(data);
    } catch (error) {
      console.error('선생님 목록 조회 실패:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (teacherId) => {
    if (!confirm('정말 삭제하시겠습니까?')) return;
    
    try {
      await deleteTeacher(teacherId);
      fetchTeachers(); // 목록 새로고침
    } catch (error) {
      alert('삭제 실패');
    }
  };

  if (loading) return <div>로딩 중...</div>;

  return (
    <div>
      <h1>선생님 관리</h1>
      
      {/* 필터 */}
      <div className="filters">
        <button onClick={() => setFilter('all')}>전체</button>
        <button onClick={() => setFilter('active')}>재직</button>
        <button onClick={() => setFilter('leave')}>휴직</button>
        <button onClick={() => setFilter('resigned')}>퇴사</button>
      </div>

      {/* 목록 */}
      <table>
        <thead>
          <tr>
            <th>이름</th>
            <th>과목</th>
            <th>전화번호</th>
            <th>이메일</th>
            <th>입사일</th>
            <th>상태</th>
            <th>담당 반</th>
            <th>관리</th>
          </tr>
        </thead>
        <tbody>
          {teachers.map(teacher => (
            <tr key={teacher.id}>
              <td>{teacher.name}</td>
              <td>{teacher.subject || '-'}</td>
              <td>{teacher.phone || '-'}</td>
              <td>{teacher.email || '-'}</td>
              <td>{teacher.join_date || '-'}</td>
              <td>
                <span className={`status-${teacher.status}`}>
                  {teacher.status === 'active' ? '재직' :
                   teacher.status === 'leave' ? '휴직' : '퇴사'}
                </span>
              </td>
              <td>{teacher.assigned_classes}</td>
              <td>
                <button onClick={() => handleEdit(teacher)}>수정</button>
                <button onClick={() => handleDelete(teacher.id)}>삭제</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

### 선생님 등록 폼 컴포넌트

```jsx
function TeacherForm({ onSuccess }) {
  const [formData, setFormData] = useState({
    name: '',
    subject: '',
    phone: '',
    email: '',
    join_date: ''
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      await createTeacher(formData);
      alert('선생님이 등록되었습니다');
      onSuccess();
    } catch (error) {
      alert('등록 실패');
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>이름 *</label>
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
        />
      </div>
      
      <div>
        <label>담당 과목</label>
        <input
          type="text"
          name="subject"
          value={formData.subject}
          onChange={handleChange}
        />
      </div>
      
      <div>
        <label>전화번호</label>
        <input
          type="tel"
          name="phone"
          value={formData.phone}
          onChange={handleChange}
        />
      </div>
      
      <div>
        <label>이메일</label>
        <input
          type="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
        />
      </div>
      
      <div>
        <label>입사일</label>
        <input
          type="date"
          name="join_date"
          value={formData.join_date}
          onChange={handleChange}
        />
      </div>
      
      <button type="submit">등록</button>
    </form>
  );
}
```

---

## 📊 응답 필드 상세 설명

### 선생님 정보 (TeacherResponse)

| 필드 | 타입 | 설명 | 예시 |
|------|------|------|------|
| id | Integer | 선생님 고유 ID | 10 |
| name | String | 선생님 이름 | "박선생" |
| subject | String\|null | 담당 과목 | "수학" |
| phone | String\|null | 전화번호 | "010-1234-5678" |
| email | String\|null | 이메일 | "park@ssamz.com" |
| join_date | String\|null | 입사일 (YYYY-MM-DD) | "2024-03-01" |
| status | String | 재직 상태 | "active" |
| assigned_classes | Integer | 담당 반 수 | 3 |

### 재직 상태 (Status)

| 값 | 설명 |
|----|------|
| `active` | 재직 중 |
| `leave` | 휴직 중 |
| `resigned` | 퇴사 |

---

## ⚠️ 주의사항

### 1. 담당 반 수 (assigned_classes)
현재 버전에서는 **Class 테이블이 구현되지 않아** 더미 데이터로 제공됩니다.
- 계산 방식: `(teacher_id % 5) + 1` (1~5 사이 값)
- **Class 테이블 구현 후** 실제 담당 반 수로 변경될 예정입니다.

### 2. User 계정 연동
현재는 **Teacher 테이블만** 별도로 관리됩니다.
- User 계정과의 연동 기능은 추후 구현 예정
- `user_id` 필드는 준비되어 있음

### 3. 권한 확인
인증된 모든 사용자가 선생님 관리 가능합니다.
- 필요시 ADMIN 권한만 허용하도록 수정 가능

---

## 🧪 테스트 방법

### curl 테스트

```bash
# 1. 로그인
TOKEN=$(curl -X POST "http://localhost:8000/auth/login-mobile" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}' \
  | jq -r '.access_token')

# 2. 선생님 목록 조회
curl -X GET "http://localhost:8000/api/admin/teachers" \
  -H "Authorization: Bearer ${TOKEN}" \
  | jq

# 3. 선생님 등록
curl -X POST "http://localhost:8000/api/admin/teachers" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "새선생",
    "subject": "영어",
    "phone": "010-9999-8888",
    "email": "new@ssamz.com",
    "join_date": "2026-02-01"
  }' \
  | jq

# 4. 선생님 정보 수정
curl -X PUT "http://localhost:8000/api/admin/teachers/1" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"subject": "수학"}' \
  | jq

# 5. 선생님 삭제
curl -X DELETE "http://localhost:8000/api/admin/teachers/1" \
  -H "Authorization: Bearer ${TOKEN}"
```

### Swagger UI
```
http://localhost:8000/docs
```

---

## 🎯 에러 응답

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 401 Unauthorized
```json
{
  "detail": "인증이 필요합니다"
}
```

### 404 Not Found
```json
{
  "detail": "선생님을 찾을 수 없습니다"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 📚 관련 문서

- 인증 API: `API_SPEC_LOGIN.md`
- 대시보드 API: `API_SPEC_DASHBOARD.md`
- 프론트엔드 가이드: `FRONTEND_GUIDE.md`

---

## 💡 향후 개선 사항

1. **User 계정 연동** - 선생님 등록 시 자동으로 로그인 계정 생성
2. **Class 테이블 구현** - 실제 담당 반 수 계산
3. **파일 업로드** - 프로필 사진, 이력서 첨부
4. **급여 관리** - 월급, 수당 등 급여 정보 관리
5. **근태 관리** - 출퇴근 시간 기록

---

## 문의

API 관련 문의나 이슈가 있으면 백엔드 팀에 문의해주세요.
