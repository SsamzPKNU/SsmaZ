# SSamZ Admin API - Quick Reference

## 🚀 빠른 시작

### 1. 로그인
```javascript
POST /auth/login-mobile

// Request
{
  "username": "admin",
  "password": "password123"
}

// Response
{
  "user": { "id": 1, "username": "admin", "name": "원장님", "user_role": "ADMIN", "academy_id": 1 },
  "access_token": "eyJhbG..."
}
```

### 2. 현재 사용자 정보
```javascript
GET /auth/me
Authorization: Bearer {token}

// Response
{
  "id": 1,
  "username": "admin",
  "name": "원장님",
  "avatar_seed": "admin",
  "user_role": "ADMIN"
}
```

---

## 📝 명세서 vs 실제 구현 매핑

| 명세서 | 실제 구현 | 비고 |
|--------|----------|------|
| `POST /auth/login` | `POST /auth/login-mobile` | 프론트엔드는 `-mobile` 사용 |
| `GET /auth/me` | `GET /auth/me` | ✅ 동일 |

---

## 💻 복사-붙여넣기 코드

### 로그인
```javascript
const { user, access_token } = await fetch('http://localhost:8000/auth/login-mobile', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username, password })
}).then(r => r.json());

localStorage.setItem('access_token', access_token);
localStorage.setItem('user', JSON.stringify(user));
```

### 인증된 API 호출
```javascript
const token = localStorage.getItem('access_token');
const data = await fetch('http://localhost:8000/auth/me', {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());
```

### 로그아웃
```javascript
localStorage.removeItem('access_token');
localStorage.removeItem('user');
```

---

## 🔑 인증 헤더

```javascript
headers: {
  'Authorization': `Bearer ${localStorage.getItem('access_token')}`
}
```

---

## ⚠️ 에러 처리

```javascript
try {
  const response = await fetch(url, options);
  if (response.status === 401) {
    // 토큰 만료 -> 로그아웃
    localStorage.clear();
    window.location.href = '/login';
  }
  return await response.json();
} catch (error) {
  console.error(error);
}
```

---

## 📚 상세 문서

- 프론트엔드 가이드: `FRONTEND_GUIDE.md`
- API 전체 명세서: `API_SPEC_LOGIN.md`
- Swagger UI: `http://localhost:8000/docs`
