# SsmaZ - 학원 관리 서비스

학원 관리를 위한 Full-stack 웹 애플리케이션입니다.

## 📋 기술 스택

### Backend
- **FastAPI**: Python 웹 프레임워크
- **MySQL**: 데이터베이스
- **SQLAlchemy**: ORM
- **JWT**: 인증 토큰
- **bcrypt**: 비밀번호 암호화

### Frontend
- **React 18**: UI 라이브러리
- **Vite**: 빌드 도구
- **React Router**: 라우팅
- **Axios**: HTTP 클라이언트
- **일반 CSS**: 스타일링 (TypeScript, Tailwind 없음)

> **참고**: 비전공자 팀원의 작업 편의를 위해 TypeScript와 Tailwind CSS를 제거하고 순수 JavaScript와 일반 CSS를 사용합니다.

## 🚀 시작하기

### 1. 사전 요구사항

- Python 3.9 이상
- Node.js 18 이상
- MySQL 8.0 이상

### 2. 데이터베이스 설정

MySQL에 데이터베이스를 생성합니다:

```sql
CREATE DATABASE ssmaz_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Backend 설정

#### 3.1 의존성 설치

```bash
cd backend
pip install -r requirements.txt
```

#### 3.2 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 수정합니다:

```bash
cp .env.example .env
```

`.env` 파일 내용:

```env
# 데이터베이스 설정
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/ssmaz_db

# JWT 설정
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Ollama 서버 설정 (기존 기능)
OLLAMA_URL=http://localhost:11434
MODEL_NAME=student-review
```

**중요**: `SECRET_KEY`는 반드시 변경하세요! 다음 명령으로 생성할 수 있습니다:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 3.3 서버 실행

```bash
cd backend
python main.py
```

서버가 `http://localhost:8000`에서 실행됩니다.

API 문서는 `http://localhost:8000/docs`에서 확인할 수 있습니다.

### 4. Frontend 설정

#### 4.1 의존성 설치

```bash
cd frontend
npm install
```

#### 4.2 개발 서버 실행

```bash
npm run dev
```

프론트엔드가 `http://localhost:3000`에서 실행됩니다.

## 📁 프로젝트 구조

```
project3/
├── backend/                    # Backend (FastAPI)
│   ├── app/
│   │   ├── api/               # API 엔드포인트
│   │   │   ├── auth.py        # 인증 API (회원가입, 로그인)
│   │   │   └── attendance.py  # 출결 API
│   │   ├── core/              # 핵심 설정
│   │   │   ├── database.py    # 데이터베이스 연결
│   │   │   └── security.py    # 보안 (JWT, 비밀번호 해싱)
│   │   ├── models/            # 데이터베이스 모델
│   │   │   └── user.py        # User 모델
│   │   ├── schemas/           # Pydantic 스키마
│   │   │   └── user.py        # User 스키마
│   │   └── services/          # 비즈니스 로직
│   │       └── auth_service.py # 인증 서비스
│   ├── main.py                # FastAPI 앱 엔트리포인트
│   ├── requirements.txt       # Python 의존성
│   └── .env                   # 환경 변수 (gitignore)
│
└── frontend/                   # Frontend (React)
    ├── index.html             # HTML 템플릿
    ├── package.json           # Node.js 의존성 (간소화됨)
    ├── vite.config.js         # Vite 설정
    └── src/
        ├── main.jsx           # React 엔트리포인트
        ├── App.jsx            # 라우팅 설정
        ├── index.css          # 전역 CSS 스타일
        ├── pages/             # 페이지 컴포넌트
        │   ├── LoginPage.jsx  # 로그인 페이지
        │   ├── SignupPage.jsx # 회원가입 페이지
        │   ├── HomePage.jsx   # 메인 페이지
        │   └── AttendanceDashboard.jsx  # 출결 대시보드
        └── services/          # API 통신
            └── api.js         # Axios 설정 및 API 함수
```

## 📦 Frontend 의존성

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.2"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.8"
  }
}
```

## 🎨 CSS 클래스 사용법

모든 스타일은 `src/index.css`에 정의되어 있습니다.

### 주요 클래스

| 클래스 | 용도 | 예시 |
|--------|------|------|
| `page-wrapper` | 페이지 전체 배경 | `<div className="page-wrapper">` |
| `card-lg` | 큰 카드 컴포넌트 | `<div className="card-lg">` |
| `btn btn-primary` | 주요 버튼 | `<button className="btn btn-primary">` |
| `input` | 입력 필드 | `<input className="input" />` |
| `form-group` | 폼 그룹 | `<div className="form-group">` |
| `alert-error` | 에러 메시지 | `<div className="alert alert-error">` |
| `table` | 테이블 | `<table className="table">` |

### 텍스트 스타일

```jsx
<p className="text-gray">회색 텍스트</p>
<p className="text-primary">파란색 텍스트</p>
<p className="font-bold">굵은 텍스트</p>
<p className="text-2xl">큰 텍스트</p>
```

## 🔐 데이터베이스 스키마

### users 테이블

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| user_id | INT (PK, AI) | 사용자 고유 ID |
| academy_id | INT | 소속 학원 ID |
| username | VARCHAR(50) | 로그인 ID (중복 불가) |
| password_hash | VARCHAR(255) | 암호화된 비밀번호 |
| user_role | ENUM | 사용자 역할 (ADMIN/TEACHER/STUDENT) |
| name | VARCHAR(50) | 실명 (선택) |
| phone | VARCHAR(20) | 전화번호 (선택) |
| created_at | TIMESTAMP | 계정 생성 시간 |

## 📝 API 엔드포인트

### 인증 API

#### 1. 회원가입
```http
POST /auth/signup
Content-Type: application/json

{
  "username": "teacher_kim",
  "password": "secure123",
  "academy_id": 1,
  "user_role": "TEACHER",
  "name": "김선생",
  "phone": "010-1234-5678"
}
```

**응답:**
```json
{
  "user_id": 1,
  "username": "teacher_kim",
  "academy_id": 1,
  "user_role": "TEACHER",
  "name": "김선생",
  "phone": "010-1234-5678",
  "created_at": "2026-01-08T11:00:00"
}
```

#### 2. 로그인
```http
POST /auth/login
Content-Type: application/json

{
  "username": "teacher_kim",
  "password": "secure123"
}
```

**응답:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "user_id": 1,
    "username": "teacher_kim",
    "academy_id": 1,
    "user_role": "TEACHER",
    "name": "김선생",
    "phone": "010-1234-5678",
    "created_at": "2026-01-08T11:00:00"
  }
}
```

### 출결 API

#### 1. 오늘 출결 조회
```http
GET /attendance/today
```

#### 2. 출결 체크
```http
POST /attendance/check
Content-Type: application/json

{
  "student_id": 1,
  "status": "출석",
  "action": "CHECK_IN"
}
```

## 🔒 보안 기능

### 비밀번호 암호화
- **bcrypt** 알고리즘 사용
- 솔트(salt) 자동 생성
- 단방향 해싱으로 원본 비밀번호 복구 불가

### JWT 토큰
- **HS256** 알고리즘 사용
- 토큰에 사용자 정보 포함 (user_id, username, academy_id, role)
- 기본 만료 시간: 30분
- localStorage에 저장

### API 보안
- 요청 인터셉터: 모든 요청에 JWT 토큰 자동 추가
- 응답 인터셉터: 401 에러 시 자동 로그아웃 및 로그인 페이지 이동

## 🎨 Frontend 주요 기능

### 1. 로그인 페이지 (`/login`)
- 아이디/비밀번호 입력
- 에러 메시지 표시
- 로딩 상태 표시
- 회원가입 링크

### 2. 회원가입 페이지 (`/signup`)
- 모든 필드 입력 (필수/선택 구분)
- 비밀번호 확인
- 실시간 유효성 검증
- 성공 시 자동 로그인 페이지 이동

### 3. 메인 페이지 (`/`)
- 사용자 정보 대시보드
- 로그아웃 기능
- 출결 관리 바로가기
- 보호된 라우트 (로그인 필요)

### 4. 출결 대시보드 (`/attendance`)
- 학생 목록 및 출결 상태
- 출석/지각/조퇴/하원 버튼
- 실시간 상태 업데이트

### 라우트 보호
- **PublicRoute**: 로그인하지 않은 사용자만 접근 (로그인, 회원가입)
- **ProtectedRoute**: 로그인한 사용자만 접근 (메인 페이지, 출결)

## 🧪 테스트 방법

### 1. Backend API 테스트

FastAPI Swagger UI 사용:
```
http://localhost:8000/docs
```

### 2. Frontend 테스트

1. 회원가입 테스트:
   - `http://localhost:3000/signup` 접속
   - 정보 입력 후 가입

2. 로그인 테스트:
   - `http://localhost:3000/login` 접속
   - 가입한 계정으로 로그인

3. 메인 페이지 확인:
   - 로그인 성공 시 자동 이동
   - 사용자 정보 확인

## 🐛 문제 해결

### Backend 실행 오류

**문제**: `ModuleNotFoundError`
```bash
# 해결: 의존성 재설치
pip install -r requirements.txt
```

**문제**: 데이터베이스 연결 오류
```bash
# 해결: MySQL 서비스 확인
# macOS
brew services start mysql

# .env 파일의 DATABASE_URL 확인
```

### Frontend 실행 오류

**문제**: `npm install` 실패
```bash
# 해결: node_modules 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install
```

**문제**: CORS 에러
```bash
# 해결: backend의 CORS 설정 확인
# main.py에서 allow_origins 설정 확인
```

## 📚 추가 학습 자료

### Backend
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [SQLAlchemy 문서](https://docs.sqlalchemy.org/)
- [JWT 소개](https://jwt.io/introduction)

### Frontend
- [React 공식 문서](https://react.dev/)
- [Vite 가이드](https://vitejs.dev/guide/)
- [MDN CSS 가이드](https://developer.mozilla.org/ko/docs/Web/CSS)

## 👥 팀원을 위한 가이드

### 코드 읽기 순서

#### Backend
1. `backend/app/models/user.py` - 데이터 구조 이해
2. `backend/app/schemas/user.py` - API 입출력 형식
3. `backend/app/core/security.py` - 보안 로직
4. `backend/app/services/auth_service.py` - 비즈니스 로직
5. `backend/app/api/auth.py` - API 엔드포인트

#### Frontend
1. `frontend/src/index.css` - CSS 클래스 확인
2. `frontend/src/services/api.js` - API 통신 방법
3. `frontend/src/pages/LoginPage.jsx` - 로그인 UI
4. `frontend/src/pages/SignupPage.jsx` - 회원가입 UI
5. `frontend/src/App.jsx` - 라우팅 구조

### 주석 설명
- 모든 파일에 상세한 한글 주석 포함
- 각 파일 상단에 파일 설명 주석 제공
- 함수마다 설명과 사용 예시 제공
- 복잡한 로직은 단계별로 주석 작성

### 파일 수정 시 참고
각 JSX 파일 상단의 주석 형식:
```jsx
/**
 * 📄 파일명: [파일명].jsx
 * 📝 설명: [이 파일이 하는 일]
 * 🔗 API: [사용하는 API 엔드포인트]
 * ✏️ 수정 시 주의: [주의사항]
 */
```

## 📄 라이선스

MIT License

## 🤝 기여

이슈나 PR은 언제든 환영합니다!
