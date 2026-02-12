# CLAUDE.md

## Language

한국어로 응답합니다.

## Project Overview

SsmaZ (학원 관리 서비스) - FastAPI 기반 학원 관리 백엔드.

## 작업 워크플로우

1. **계획**: Plan 모드에서 구현 방향 수립
2. **구현**: 코드 작성 (model → schema → service → api → main.py 등록)
3. **테스트**: curl로 API 동작 확인
4. **커밋/푸시**: 기능 단위로 commit & push

### DB 테이블 변경

- Claude가 SQL 쿼리를 작성하여 제공
- 사용자가 직접 DB에서 실행
- `Base.metadata.create_all()`로 자동 생성되는 경우도 있음

### 테스트

- curl을 사용하여 API 엔드포인트 테스트
- 서버는 http://localhost:8000 에서 실행
- 테스트 계정 정보: `test-accounts.md` 참조

## Architecture

```
app/
├── api/        # FastAPI 라우터
├── services/   # 비즈니스 로직
├── models/     # SQLAlchemy ORM 모델
├── schemas/    # Pydantic 스키마
├── data/       # 정적 데이터
└── core/       # DB, 보안 등 인프라
```

### 새 기능 추가 패턴

1. model → schema → service → api router → main.py 등록
2. 인증 필요 시: `Depends(get_current_user)` 또는 `Depends(get_admin_user)`

### 핵심 패턴

- 인증: JWT (httpOnly 쿠키 + Bearer 토큰)
- DB: SQLAlchemy ORM + MySQL
- 역할: ADMIN, TEACHER, STUDENT

## Development

```bash
conda activate ssmaz-backend
python main.py
```
