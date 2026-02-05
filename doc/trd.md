# [TRD] 프로젝트3 - 시스템 설계서
> **최종 수정일**: 2026-02-03

## 1. 기술 스택 (Tech Stack)
- **Frontend**: React (Vite), 일반 CSS (TypeScript, Tailwind 미사용)
- **Backend**: FastAPI (Python 3.10+)
- **Database**: MySQL 5.5 (Engine: InnoDB)
- **Vector DB**: ChromaDB (FAQ 임베딩 저장)
- **LLM**: Ollama (llama31 모델, 로컬 실행)
- **Embedding**: SentenceTransformer (snunlp/KR-SBERT-V40K-klueNLI-augSTS)
- **Auth**: Native JWT (OAuth2 Password Flow) 기반 직접 로그인 (ID/PW)

> **참고**: 비전공자 팀원의 작업 편의를 위해 TypeScript와 Tailwind CSS를 제거하고 순수 JavaScript와 일반 CSS를 사용합니다.

## 2. 데이터베이스 설계 (ERD 요약)
- 모든 테이블은 **단일 Primary Key (`id`)**와 **AUTO_INCREMENT**를 사용함.
- **Multi-tenancy**: 모든 주요 데이터는 `academy_id`를 참조하여 학원별 데이터 격리.
- **삭제 정책**: 부모 데이터 삭제 시 자식 데이터 자동 삭제 (`ON DELETE CASCADE`).

### 핵심 테이블 구조
- `Academies`: 학원 기본 정보.
- `Users`: 로그인 정보 (username, password_hash, name, phone, role [ADMIN, TEACHER, STUDENT] 등).
- `LoginLogs`: 로그인 이력 기록 (login_time, ip_address, status [SUCCESS, FAIL], user_id).
- `Teachers`: 선생님 정보 (user_id FK, name, subject, employment_type, hourly_rate 등).
- `Students`: 학생 정보 및 `academy_id` 외래키 참조.
- `StudentContacts`: 학생 연락처 (student_id FK, phone, label, priority) - 다중 연락처 지원.
- `Attendance`: 학생 출결 기록 (status: [등교, 하교, 지각, 결석, 조퇴] ENUM 사용).
- `TeacherAttendances`: 선생님 출퇴근 기록 (teacher_id FK, check_in_time, check_out_time, worked_minutes, is_approved).
- `Payments`: 수납 관리 정보.
- `DailyLogs`: 학습 일지 및 문자 전송 상태.

## 3. 인증 및 보안 (Authentication & Security)
- **JWT (Json Web Token)**: 로그인 시 Access Token 발급 및 **httpOnly Cookie** 저장.
- **CSRF Protection**: 프론트엔드 API 요청 시 CSRF 토큰 검증 시스템 적용.
- **Security**: SHA-256 + Bcrypt 2단계 해싱을 통한 비밀번호 암호화 및 유효성 검증.
- **Audit Log**: `LoginLogService`를 통한 모든 인증 시도 추적.
- **Direct Login**: 자체 로그인 시스템만 구현 (소셜 로그인 미사용).

## 4. 핵심 모바일/웹 기능 구현
- **학생 출결 자동화 시스템**:
  - `AttendanceService`를 통한 등하교 관리.
  - 당일 중복 체크 방지 및 상태 히스토리 관리.
- **선생님 출퇴근 관리 시스템**:
  - `TeacherAttendanceService`를 통한 출퇴근 체크.
  - 당일 중복 출근 방지 및 퇴근 시 근무시간(분) 자동 계산.
  - 원장(ADMIN) 승인 기능 (`is_approved`, `approved_by`).
  - 비정규직(PART_TIME) 시급 기반 예상 급여 계산.
- **학생 연락처 다중 관리**:
  - `StudentContactService`를 통한 연락처 CRUD.
  - 우선순위(`priority`) 및 활성화(`is_active`) 상태 관리.
- **문자 리뷰 및 알림**:
  - `text_review` 모듈 연동.
  - `DailyLogs` 생성 시 혹은 `Attendance` 상태 변경 시 특정 훅(Hook)을 통해 문자 모델 호출.
  - `is_sent` 플래그를 통해 중복 발송 방지.
- **FAQ 챗봇 시스템**:
  - `ChatService`를 통한 RAG(Retrieval-Augmented Generation) 기반 FAQ 응답.
  - ChromaDB에 FAQ 임베딩 저장 및 유사도 검색.
  - Ollama(llama31)를 통한 자연어 답변 생성.
  - 환각 방지: 시스템 프롬프트 + 컨텍스트 제한 + 환각 키워드 감지.
- **FAQ 캐싱 최적화**:
  - `FAQCache` 클래스를 통한 응답 캐싱 (최대 100개).
  - 질문 정규화 및 MD5 해시 기반 캐시 키 생성.
  - 서버 시작 시 FAQ 20개 사전 캐싱 (Warm-up).
  - 캐시 히트 시 50ms 이내 응답, 미스 시 RAG 파이프라인 실행.

## 5. 개발 가이드 (For Antigravity & Team)
- **Branch 전략**: `main` (배포), `deploy/ 사람명` (개발용 브랜치).
- **Vibe Coding 규칙**:
  - 에이전트는 코드 작성 시 비전공자 팀원을 위해 상세한 **한글 주석**을 포함함.
  - API 에러 발생 시 프론트엔드에서 처리하기 쉽도록 명확한 에러 메시지(JSON)를 반환함.

## 6. 프로젝트 폴더 구조
project3/
├── backend/                # FastAPI 메인 백엔드
│   ├── app/
│   │   ├── api/            # API 엔드포인트
│   │   │   ├── auth.py         # 인증 API
│   │   │   ├── attendance.py   # 출결 API
│   │   │   └── chat.py         # FAQ 챗봇 API (신규)
│   │   ├── core/           # 보안(JWT), DB 연결 설정
│   │   ├── data/           # 정적 데이터 (신규)
│   │   │   └── faq_data.json   # FAQ 데이터 (20개 질문)
│   │   ├── models/         # SQLAlchemy 모델 (Users, Students, LoginLogs 등)
│   │   ├── schemas/        # Pydantic 데이터 검증 모델
│   │   │   └── chat.py         # 챗봇 스키마 (신규)
│   │   └── services/       # 비즈니스 로직
│   │       ├── chat_cache.py   # FAQ 캐싱 모듈 (신규)
│   │       ├── chat_service.py # FAQ 챗봇 서비스 (신규)
│   │       ├── faq_loader.py   # FAQ ChromaDB 로더 (신규)
│   │       └── text_review/    # 기존 문자 리뷰 로직 및 모델
│   ├── tests/              # API 테스트 코드
│   ├── .env                # DB_URL, JWT_SECRET, OLLAMA_URL 등 환경변수
│   ├── main.py             # 서버 실행 엔트리 포인트
│   └── requirements.txt
├── frontend/               # React 프로젝트 (Vite)
├── doc/                    # PRD, TRD 및 기술 문서
│   └── FAQ_CHATBOT_CACHING.md  # FAQ 챗봇 캐싱 최적화 문서 (신규)
└── .gitignore