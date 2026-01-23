# SSamZ Admin App - 로그인 API 명세서

## 개요

SSamZ 관리자 앱에서 사용할 수 있는 **두 가지 로그인 API**를 제공합니다:

1. **웹용 로그인** (`/auth/login`) - httpOnly 쿠키 + CSRF 토큰 (보안 강화)
2. **모바일/앱용 로그인** (`/auth/login-mobile`) - 응답 body에 토큰 포함 (명세서 형식)

---

## 1. 웹용 로그인 (권장)

### 📌 Endpoint
```
POST /auth/login
```

### 📥 Request Body
```json
{
  "username": "admin",
  "password": "password123"
}
```

### 📤 Response (200 OK)
```json
{
  "csrf_token": "a1b2c3d4e5f6...",
  "token_type": "bearer",
  "user": {
    "user_id": 1,
    "username": "admin",
    "name": "원장님",
    "user_role": "ADMIN",
    "academy_id": 1,
    "phone": "010-1234-5678",
    "created_at": "2026-01-23T10:00:00"
  }
}
```

### 🍪 Cookies (자동 설정됨)
```
Set-Cookie: access_token={JWT}; HttpOnly; Secure; SameSite=Strict; Max-Age=1800; Path=/
```

### 🔐 보안 특징
- ✅ **httpOnly 쿠키**: JavaScript에서 토큰 접근 불가 (XSS 공격 방지)
- ✅ **CSRF 토큰**: 모든 요청에 `X-CSRF-Token` 헤더 필요
- ✅ **Rate Limiting**: IP당 분당 5회 제한
- ✅ **로그인 기록**: IP, User-Agent 저장

### 📝 사용 방법 (프론트엔드)

```javascript
// 1. 로그인 요청
const response = await fetch('http://localhost:8000/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include',  // 쿠키 전송 허용
  body: JSON.stringify({
    username: 'admin',
    password: 'password123'
  })
});

const data = await response.json();

// 2. CSRF 토큰 저장 (localStorage 또는 state)
localStorage.setItem('csrf_token', data.csrf_token);
localStorage.setItem('user', JSON.stringify(data.user));

// 3. 이후 모든 API 요청 시 헤더 추가
fetch('http://localhost:8000/some-api', {
  headers: {
    'X-CSRF-Token': localStorage.getItem('csrf_token')
  },
  credentials: 'include'  // 쿠키 자동 전송
});
```

---

## 2. 모바일/앱용 로그인 (명세서 형식)

### 📌 Endpoint
```
POST /auth/login-mobile
```

### 📥 Request Body
```json
{
  "username": "admin",
  "password": "password123"
}
```

### 📤 Response (200 OK)
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "name": "원장님",
    "user_role": "ADMIN",
    "academy_id": 1
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInVzZXJfaWQiOjEsImFjYWRlbXlfaWQiOjEsInJvbGUiOiJBRE1JTiIsImV4cCI6MTY0MzAyNTYwMH0.abc123..."
}
```

### ⚠️ 주의사항
- 토큰이 **응답 body**에 포함되어 반환됩니다
- 클라이언트가 **직접 토큰을 저장하고 관리**해야 합니다
- httpOnly 쿠키 및 CSRF 토큰을 사용하지 않습니다
- 모바일 앱이나 토큰을 직접 관리하는 클라이언트에 적합합니다

### 📝 사용 방법 (모바일/React Native 등)

```javascript
// 1. 로그인 요청
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

// 2. 토큰과 사용자 정보 저장
await AsyncStorage.setItem('access_token', data.access_token);
await AsyncStorage.setItem('user', JSON.stringify(data.user));

// 3. 이후 모든 API 요청 시 Authorization 헤더 추가
const token = await AsyncStorage.getItem('access_token');
fetch('http://localhost:8000/some-api', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

---

## 3. 공통 에러 응답

### 401 Unauthorized (인증 실패)
```json
{
  "detail": "username 또는 password가 올바르지 않습니다"
}
```

### 429 Too Many Requests (Rate Limit 초과)
```json
{
  "detail": "Rate limit exceeded: 5 per 1 minute"
}
```

### 422 Validation Error (입력 데이터 오류)
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

---

## 4. 기타 인증 관련 API

### 4-1. 현재 사용자 정보 조회

#### Endpoint
```
GET /auth/me
```

#### Headers (웹용 - 쿠키 방식)
```
Cookie: access_token={JWT}
X-CSRF-Token: {csrf_token}
```

#### Headers (모바일/앱용 - Bearer 방식)
```
Authorization: Bearer {access_token}
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

**필드 설명:**
- `id`: 사용자 고유 ID
- `username`: 로그인 ID
- `name`: 사용자 실명
- `avatar_seed`: 아바타 생성용 시드 값 (username과 동일)
- `user_role`: 사용자 역할 (`ADMIN`, `TEACHER`, `STUDENT`)

---

### 4-2. 로그아웃 (웹용)

#### Endpoint
```
POST /auth/logout
```

#### Headers
```
Cookie: access_token={JWT}
```

#### Response (200 OK)
```json
{
  "message": "로그아웃 되었습니다"
}
```

- httpOnly 쿠키가 삭제됩니다
- 로그아웃 시간 및 세션 지속 시간이 기록됩니다

---

## 5. 사용자 역할 (UserRole)

| 역할 | 설명 |
|------|------|
| `ADMIN` | 관리자 (원장님) - 학원 전체 관리 |
| `TEACHER` | 선생님 - 수업 및 학생 관리 |
| `STUDENT` | 학생 - 본인 정보 조회 |

---

## 6. JWT 토큰 정보

### Payload 구조
```json
{
  "sub": "admin",          // username
  "user_id": 1,            // 사용자 ID
  "academy_id": 1,         // 소속 학원 ID
  "role": "ADMIN",         // 사용자 역할
  "exp": 1643025600        // 만료 시간 (Unix timestamp)
}
```

### 토큰 만료 시간
- **30분** (1800초)
- 만료 후 재로그인 필요

---

## 7. 테스트 방법

### Swagger UI 사용
1. 서버 실행: `uvicorn main:app --reload`
2. 브라우저에서 접속: `http://localhost:8000/docs`
3. `/auth/login-mobile` 또는 `/auth/login` 엔드포인트 테스트

### curl 사용

#### 모바일용 로그인 테스트
```bash
curl -X POST "http://localhost:8000/auth/login-mobile" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}'
```

#### 웹용 로그인 테스트
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password123"}' \
  -c cookies.txt  # 쿠키 저장
```

---

## 8. 어떤 API를 사용해야 할까요?

### 웹 브라우저 (React, Vue, Angular 등)
→ **`/auth/login`** 사용 권장
- 더 안전한 httpOnly 쿠키 방식
- XSS 공격으로부터 보호
- CSRF 토큰으로 추가 보안

### 모바일 앱 (React Native, Flutter 등)
→ **`/auth/login-mobile`** 사용 권장
- 명세서 형식에 맞는 응답
- 토큰을 직접 관리 가능
- AsyncStorage나 SecureStore에 저장

### 서버 간 통신 (API to API)
→ **`/auth/login-mobile`** 사용
- Bearer 토큰 방식이 더 간단
- 쿠키 관리 불필요

---

## 9. 보안 권장사항

1. **HTTPS 사용**: 프로덕션 환경에서는 반드시 HTTPS 사용
2. **토큰 저장 위치**:
   - 웹: httpOnly 쿠키 (자동 처리됨)
   - 모바일: SecureStore 또는 KeyChain 사용
   - ❌ localStorage에 토큰 저장 지양 (XSS 취약)
3. **Rate Limiting**: 로그인 시도 제한 (분당 5회)
4. **비밀번호 정책**: 최소 8자, 영문+숫자 포함

---

## 10. 문의 및 지원

API 관련 문의사항이 있으시면 개발팀에 문의해주세요.

- Swagger 문서: `http://localhost:8000/docs`
- ReDoc 문서: `http://localhost:8000/redoc`
