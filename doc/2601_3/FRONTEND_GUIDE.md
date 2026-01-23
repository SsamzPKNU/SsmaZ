# SSamZ Admin App - 프론트엔드 개발 가이드

## 🎯 개요

이 문서는 SSamZ 관리자 앱 프론트엔드 개발자를 위한 API 사용 가이드입니다.

---

## 1. 인증 API 사용법

### 1-1. 로그인

#### Endpoint
```
POST /auth/login-mobile
```

> 💡 **참고**: 명세서에는 `/auth/login`으로 되어 있지만, 실제 구현은 `/auth/login-mobile`입니다.
> 두 가지 로그인 방식을 지원하기 위해 엔드포인트를 분리했습니다.

#### Request
```javascript
const response = await fetch('http://localhost:8000/auth/login-mobile', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'admin',
    password: 'password123'
  })
});

const data = await response.json();
```

#### Response (200 OK)
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "name": "원장님",
    "user_role": "ADMIN",
    "academy_id": 1
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Error Response (401)
```json
{
  "detail": "username 또는 password가 올바르지 않습니다"
}
```

---

### 1-2. 현재 사용자 정보 조회

#### Endpoint
```
GET /auth/me
```

#### Request (with Bearer Token)
```javascript
const token = localStorage.getItem('access_token');

const response = await fetch('http://localhost:8000/auth/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const user = await response.json();
```

#### Response (200 OK)
```json
{
  "id": 1,
  "username": "admin",
  "name": "원장님",
  "avatar_seed": "admin",
  "user_role": "ADMIN"
}
```

#### Error Response (401)
```json
{
  "detail": "인증이 필요합니다"
}
```

---

## 2. 완전한 인증 플로우 예시

### React 예시

```javascript
import { useState, useEffect } from 'react';

// 1. 로그인 함수
async function login(username, password) {
  try {
    const response = await fetch('http://localhost:8000/auth/login-mobile', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '로그인 실패');
    }

    const data = await response.json();
    
    // 토큰과 사용자 정보 저장
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('user', JSON.stringify(data.user));
    
    return data;
  } catch (error) {
    console.error('로그인 에러:', error);
    throw error;
  }
}

// 2. 현재 사용자 정보 조회 함수
async function getCurrentUser() {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    throw new Error('토큰이 없습니다');
  }

  try {
    const response = await fetch('http://localhost:8000/auth/me', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      // 토큰이 만료되었거나 유효하지 않음
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      throw new Error('인증 실패');
    }

    const user = await response.json();
    localStorage.setItem('user', JSON.stringify(user));
    
    return user;
  } catch (error) {
    console.error('사용자 정보 조회 에러:', error);
    throw error;
  }
}

// 3. 로그아웃 함수
function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  // 로그인 페이지로 리다이렉트
  window.location.href = '/login';
}

// 4. 토큰 확인 함수
function isAuthenticated() {
  return !!localStorage.getItem('access_token');
}

// 5. React Hook 예시
function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUser = async () => {
      if (isAuthenticated()) {
        try {
          const currentUser = await getCurrentUser();
          setUser(currentUser);
        } catch (error) {
          console.error('사용자 로드 실패:', error);
          logout();
        }
      }
      setLoading(false);
    };

    loadUser();
  }, []);

  return { user, loading, login, logout, isAuthenticated };
}

// 사용 예시
function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    try {
      await login(username, password);
      window.location.href = '/dashboard';
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      {error && <div className="error">{error}</div>}
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="아이디"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="비밀번호"
      />
      <button type="submit">로그인</button>
    </form>
  );
}

export { login, getCurrentUser, logout, isAuthenticated, useAuth };
```

---

## 3. API 호출 유틸리티

### 인증이 필요한 API 호출 함수

```javascript
// api.js
const API_BASE_URL = 'http://localhost:8000';

async function apiCall(endpoint, options = {}) {
  const token = localStorage.getItem('access_token');
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // 토큰이 있으면 Authorization 헤더 추가
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    // 401 에러 시 자동 로그아웃
    if (response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
      throw new Error('인증이 만료되었습니다');
    }

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '요청 실패');
    }

    return await response.json();
  } catch (error) {
    console.error('API 호출 에러:', error);
    throw error;
  }
}

// 사용 예시
export async function getStudents() {
  return apiCall('/students');
}

export async function createStudent(studentData) {
  return apiCall('/students', {
    method: 'POST',
    body: JSON.stringify(studentData)
  });
}

export { apiCall };
```

---

## 4. 환경 변수 설정

### `.env` 파일 (Create React App)
```env
REACT_APP_API_URL=http://localhost:8000
```

### 사용
```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const response = await fetch(`${API_URL}/auth/login-mobile`, {
  // ...
});
```

---

## 5. CORS 설정 확인

백엔드에서 CORS가 설정되어 있습니다:

```python
# 허용된 Origins (backend/.env)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

프론트엔드가 다른 포트에서 실행되면 백엔드 `.env` 파일에 추가해야 합니다.

---

## 6. 아바타 이미지 생성

`avatar_seed`를 사용하여 사용자 아바타를 생성할 수 있습니다:

```javascript
function UserAvatar({ user }) {
  const avatarUrl = `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.avatar_seed}`;
  
  return (
    <img 
      src={avatarUrl} 
      alt={user.name} 
      className="avatar"
    />
  );
}

// 또는 다른 스타일
const avatarUrl = `https://api.dicebear.com/7.x/initials/svg?seed=${user.avatar_seed}`;
```

---

## 7. 보안 권장사항

### 1. 토큰 저장
- ✅ **localStorage**: 간단하지만 XSS 공격에 취약
- ✅ **sessionStorage**: 탭 닫으면 자동 삭제
- ⚠️ **주의**: 프로덕션에서는 httpOnly 쿠키 사용 권장

### 2. 토큰 만료 처리
- JWT 토큰은 **30분** 후 만료됩니다
- 401 에러 발생 시 자동으로 로그아웃 처리

### 3. HTTPS 사용
- 프로덕션 환경에서는 반드시 **HTTPS** 사용
- 토큰이 평문으로 전송되므로 중요합니다

---

## 8. 자주 묻는 질문 (FAQ)

### Q1. 명세서와 엔드포인트가 다른데 괜찮나요?
A. 네, 괜찮습니다. `/auth/login-mobile`을 사용하시면 됩니다. 명세서와 동일한 응답 형식을 제공합니다.

### Q2. 토큰이 만료되면 어떻게 되나요?
A. 30분 후 토큰이 만료되며, API 호출 시 401 에러가 발생합니다. 자동으로 로그아웃되고 다시 로그인해야 합니다.

### Q3. 웹용 로그인(`/auth/login`)을 사용해도 되나요?
A. 네, 가능합니다. 하지만 쿠키와 CSRF 토큰을 함께 관리해야 하므로 복잡합니다. 모바일용을 사용하는 것이 더 간단합니다.

### Q4. avatar_seed는 무엇인가요?
A. 사용자별로 고유한 아바타를 생성하기 위한 시드 값입니다. DiceBear와 같은 서비스에서 사용됩니다.

---

## 9. 테스트 계정

개발 중 테스트를 위한 계정:

```
Username: admin
Password: password123
```

---

## 10. 추가 리소스

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- 상세 API 명세서: `/doc/2601_3/API_SPEC_LOGIN.md`

---

## 문의

API 관련 문의나 이슈가 있으면 백엔드 팀에 문의해주세요.
