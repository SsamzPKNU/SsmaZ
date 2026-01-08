# 📁 프로젝트 폴더 구조

```
project3/
│
├── 📄 README.md                    # 프로젝트 전체 문서
├── 📄 QUICKSTART.md                # 빠른 시작 가이드
├── 📄 .gitignore                   # Git 제외 파일 목록
│
├── 📂 backend/                     # Backend (FastAPI + MySQL)
│   │
│   ├── 📄 main.py                  # ⭐ FastAPI 앱 엔트리포인트
│   ├── 📄 requirements.txt         # Python 의존성 목록
│   ├── 📄 .env                     # 환경 변수 (gitignore)
│   ├── 📄 .env.example             # 환경 변수 예시
│   │
│   ├── 📂 app/                     # 애플리케이션 코드
│   │   │
│   │   ├── 📂 api/                 # API 엔드포인트
│   │   │   ├── __init__.py
│   │   │   └── 📄 auth.py          # ⭐ 인증 API (회원가입, 로그인)
│   │   │
│   │   ├── 📂 core/                # 핵심 설정
│   │   │   ├── __init__.py
│   │   │   ├── 📄 database.py      # ⭐ 데이터베이스 연결 설정
│   │   │   └── 📄 security.py      # ⭐ JWT 토큰, 비밀번호 암호화
│   │   │
│   │   ├── 📂 models/              # 데이터베이스 모델 (SQLAlchemy)
│   │   │   ├── __init__.py
│   │   │   └── 📄 user.py          # ⭐ User 테이블 모델
│   │   │
│   │   ├── 📂 schemas/             # Pydantic 스키마 (API 입출력)
│   │   │   ├── __init__.py
│   │   │   ├── 📄 user.py          # ⭐ User 관련 스키마
│   │   │   └── 📄 text_review.py   # 기존 리뷰 기능 스키마
│   │   │
│   │   └── 📂 services/            # 비즈니스 로직
│   │       ├── __init__.py
│   │       ├── 📄 auth_service.py  # ⭐ 인증 서비스 로직
│   │       └── 📂 text_review/     # 기존 리뷰 기능
│   │           ├── __init__.py
│   │           └── review_generator.py
│   │
│   └── 📂 tests/                   # 테스트 코드
│       └── test_text_review.py
│
└── 📂 frontend/                    # Frontend (React + Vite)
    │
    ├── 📄 package.json             # Node.js 의존성 및 스크립트
    ├── 📄 vite.config.js           # ⭐ Vite 설정 (프록시 포함)
    ├── 📄 tailwind.config.js       # Tailwind CSS 설정
    ├── 📄 postcss.config.js        # PostCSS 설정
    ├── 📄 index.html               # HTML 템플릿
    ├── 📄 .gitignore               # Git 제외 파일
    │
    └── 📂 src/                     # 소스 코드
        │
        ├── 📄 main.jsx             # ⭐ React 엔트리포인트
        ├── 📄 App.jsx              # ⭐ 라우팅 설정
        ├── 📄 index.css            # 전역 스타일 (Tailwind)
        │
        ├── 📂 pages/               # 페이지 컴포넌트
        │   ├── 📄 LoginPage.jsx    # ⭐ 로그인 페이지
        │   ├── 📄 SignupPage.jsx   # ⭐ 회원가입 페이지
        │   └── 📄 HomePage.jsx     # ⭐ 메인 대시보드
        │
        ├── 📂 services/            # API 통신
        │   └── 📄 api.js           # ⭐ Axios 설정 및 API 함수
        │
        ├── 📂 components/          # 재사용 컴포넌트 (향후 추가)
        │
        └── 📂 styles/              # 추가 스타일 (향후 추가)
```

## 📌 주요 파일 설명

### Backend

| 파일 | 역할 | 중요도 |
|------|------|--------|
| `main.py` | FastAPI 앱 시작점, 라우터 등록 | ⭐⭐⭐ |
| `app/models/user.py` | User 테이블 정의 (DB 스키마) | ⭐⭐⭐ |
| `app/schemas/user.py` | API 요청/응답 형식 정의 | ⭐⭐⭐ |
| `app/core/security.py` | JWT 토큰, 비밀번호 암호화 | ⭐⭐⭐ |
| `app/core/database.py` | MySQL 연결 설정 | ⭐⭐⭐ |
| `app/services/auth_service.py` | 회원가입/로그인 비즈니스 로직 | ⭐⭐⭐ |
| `app/api/auth.py` | 회원가입/로그인 API 엔드포인트 | ⭐⭐⭐ |

### Frontend

| 파일 | 역할 | 중요도 |
|------|------|--------|
| `src/App.jsx` | 라우팅 설정 (페이지 전환) | ⭐⭐⭐ |
| `src/services/api.js` | Backend API 통신 | ⭐⭐⭐ |
| `src/pages/LoginPage.jsx` | 로그인 UI | ⭐⭐⭐ |
| `src/pages/SignupPage.jsx` | 회원가입 UI | ⭐⭐⭐ |
| `src/pages/HomePage.jsx` | 메인 대시보드 UI | ⭐⭐ |
| `vite.config.js` | 개발 서버 및 프록시 설정 | ⭐⭐ |

## 🔄 데이터 흐름

### 회원가입 플로우
```
사용자 입력 (SignupPage.jsx)
    ↓
API 호출 (api.js - signup 함수)
    ↓
Backend API (auth.py - /auth/signup)
    ↓
비즈니스 로직 (auth_service.py - create_user)
    ↓
비밀번호 암호화 (security.py - hash_password)
    ↓
DB 저장 (user.py - User 모델)
    ↓
응답 반환 → 로그인 페이지로 이동
```

### 로그인 플로우
```
사용자 입력 (LoginPage.jsx)
    ↓
API 호출 (api.js - login 함수)
    ↓
Backend API (auth.py - /auth/login)
    ↓
인증 확인 (auth_service.py - authenticate_user)
    ↓
비밀번호 검증 (security.py - verify_password)
    ↓
JWT 토큰 생성 (security.py - create_access_token)
    ↓
토큰 + 사용자 정보 반환
    ↓
localStorage에 저장 (api.js)
    ↓
메인 페이지로 이동 (HomePage.jsx)
```

## 📝 파일 수정 시 참고사항

### Backend 수정 시
1. **모델 변경** (`models/user.py`)
   - 테이블 구조 변경 시 서버 재시작 필요
   - 기존 데이터와 충돌 가능성 주의

2. **API 추가** (`api/`)
   - 새 라우터 생성 후 `main.py`에 등록 필요
   - 스키마 정의 필수

3. **비즈니스 로직** (`services/`)
   - 복잡한 로직은 서비스 레이어에 작성
   - API 엔드포인트는 간결하게 유지

### Frontend 수정 시
1. **새 페이지 추가**
   - `src/pages/`에 컴포넌트 생성
   - `App.jsx`에 라우트 추가

2. **API 통신**
   - `services/api.js`에 함수 추가
   - 에러 처리 포함 필수

3. **스타일링**
   - Tailwind CSS 클래스 사용
   - `tailwind.config.js`에서 커스텀 색상 설정

## 🎯 코드 읽기 순서 (비전공자용)

### 1단계: 데이터 구조 이해
1. `backend/app/models/user.py` - DB 테이블 구조
2. `backend/app/schemas/user.py` - API 입출력 형식

### 2단계: 보안 로직 이해
3. `backend/app/core/security.py` - 암호화 및 토큰

### 3단계: 비즈니스 로직 이해
4. `backend/app/services/auth_service.py` - 회원가입/로그인 로직

### 4단계: API 엔드포인트 이해
5. `backend/app/api/auth.py` - API 정의

### 5단계: Frontend 이해
6. `frontend/src/services/api.js` - API 통신
7. `frontend/src/pages/LoginPage.jsx` - 로그인 UI
8. `frontend/src/pages/SignupPage.jsx` - 회원가입 UI
9. `frontend/src/App.jsx` - 라우팅

---

**💡 Tip**: ⭐ 표시가 있는 파일부터 읽으면 프로젝트 구조를 빠르게 이해할 수 있습니다!
