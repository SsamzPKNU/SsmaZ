# Backend - 학원 자동화 시스템

FastAPI 기반의 학원 관리 시스템 백엔드입니다.

## 🚀 시작하기

### 1. 환경 설정
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 의존성 설치
pip install -r requirements.txt
```

### 2. Ollama 및 모델 설정
문자 리뷰 생성 기능을 위해 Ollama가 필요합니다.

```bash
# 모델 생성 (backend/app/services/text_review/model 디렉토리에서 실행)
cd app/services/text_review/model
ollama create student-review -f Modelfile
```

### 3. 서버 실행
```bash
python main.py
```

## 📂 폴더 구조
- `app/api/`: API 엔드포인트 (출결, 결제, 유저 등)
- `app/core/`: 보안(JWT), DB 설정
- `app/models/`: SQLAlchemy DB 모델
- `app/schemas/`: Pydantic 데이터 검증 모델
- `app/services/`: 비즈니스 로직
  - `text_review/`: 문자 리뷰 자동 생성 모듈
- `tests/`: 테스트 코드
