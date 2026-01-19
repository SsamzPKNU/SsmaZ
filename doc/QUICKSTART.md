# 🚀 빠른 시작 가이드

이 문서는 SsmaZ 프로젝트를 처음 실행하는 분들을 위한 단계별 가이드입니다.

## ✅ 체크리스트

시작하기 전에 다음 항목들이 설치되어 있는지 확인하세요:

- [ ] Python 3.9 이상
- [ ] Node.js 18 이상
- [ ] MySQL 8.0 이상
- [ ] Git

## 📝 단계별 설정

### 1단계: MySQL 데이터베이스 생성

MySQL에 접속합니다:
```bash
mysql -u root -p
```

데이터베이스를 생성합니다:
```sql
CREATE DATABASE ssmaz_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;
```

### 2단계: Backend 설정

#### 2-1. 의존성 설치
```bash
cd backend
pip install -r requirements.txt
```

#### 2-2. 환경 변수 설정

`.env` 파일이 이미 생성되어 있습니다. 다음 내용을 수정하세요:

```bash
# .env 파일 열기
nano .env  # 또는 vi .env
```

**반드시 수정해야 할 항목:**

1. **DATABASE_URL**: MySQL 비밀번호 변경
   ```
   DATABASE_URL=mysql+pymysql://root:YOUR_MYSQL_PASSWORD@localhost:3306/ssmaz_db
   ```

2. **SECRET_KEY**: 보안 키 생성 및 변경
   ```bash
   # 새로운 SECRET_KEY 생성
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   
   생성된 키를 `.env` 파일의 `SECRET_KEY`에 붙여넣기:
   ```
   SECRET_KEY=생성된_키_여기에_붙여넣기
   ```

#### 2-3. Backend 서버 실행

```bash
# backend 폴더에서 실행
python main.py
```

✅ 성공 메시지:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

🌐 API 문서 확인: http://localhost:8000/docs

### 3단계: Frontend 설정

**새 터미널 창을 열고** 다음을 실행하세요:

#### 3-1. 의존성 설치
```bash
cd frontend
npm install
```

설치되는 주요 패키지:
- React 18 (UI 라이브러리)
- React Router (페이지 라우팅)
- Axios (API 통신)
- Vite (빌드 도구)

> **참고**: TypeScript와 Tailwind CSS는 제거되었습니다. 순수 JavaScript와 일반 CSS를 사용합니다.

설치 시간: 약 2-3분 소요

#### 3-2. Frontend 개발 서버 실행
```bash
npm run dev
```

✅ 성공 메시지:
```
  VITE v5.0.8  ready in 500 ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

🌐 웹 브라우저에서 http://localhost:3000 접속

## 🎯 첫 사용자 등록 및 로그인

### 1. 회원가입
1. http://localhost:3000/signup 접속
2. 다음 정보 입력:
   - **아이디**: test_teacher (예시)
   - **비밀번호**: test123 (예시)
   - **비밀번호 확인**: test123
   - **학원 ID**: 1
   - **역할**: 선생님 선택
   - **이름**: 테스트 (선택사항)
   - **전화번호**: 010-1234-5678 (선택사항)
3. "회원가입" 버튼 클릭

### 2. 로그인
1. 자동으로 로그인 페이지로 이동
2. 가입한 아이디/비밀번호 입력
3. "로그인" 버튼 클릭

### 3. 메인 페이지 확인
- 로그인 성공 시 자동으로 메인 페이지로 이동
- 사용자 정보 확인

## 🔍 동작 확인

### Backend 확인
```bash
# 새 터미널에서
curl http://localhost:8000/
```

예상 응답:
```json
{
  "message": "학원 관리 서비스 SsmaZ API",
  "version": "1.0.0",
  "endpoints": {
    "health": "/health",
    "signup": "/auth/signup",
    "login": "/auth/login",
    ...
  }
}
```

### Frontend 확인
브라우저에서 http://localhost:3000 접속 시 로그인 페이지가 표시되어야 합니다.

## ❌ 문제 해결

### Backend 오류

#### 1. "ModuleNotFoundError" 에러
```bash
# 해결: 가상환경 확인 및 재설치
cd backend
pip install -r requirements.txt
```

#### 2. "Can't connect to MySQL server" 에러
```bash
# MySQL 서비스 시작
# macOS
brew services start mysql

# 또는 MySQL 상태 확인
mysql.server status
```

#### 3. "Table doesn't exist" 에러
- 서버를 재시작하면 자동으로 테이블이 생성됩니다
- `Base.metadata.create_all(bind=engine)` 코드가 자동 실행됨

### Frontend 오류

#### 1. "npm install" 실패
```bash
# node_modules 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install
```

#### 2. "EADDRINUSE: address already in use" 에러
```bash
# 3000 포트를 사용 중인 프로세스 종료
lsof -ti:3000 | xargs kill -9

# 또는 다른 포트 사용
npm run dev -- --port 3001
```

#### 3. "Failed to fetch" 에러 (로그인/회원가입 시)
- Backend 서버가 실행 중인지 확인
- http://localhost:8000/docs 접속 가능한지 확인

## 🎓 다음 단계

1. **API 문서 탐색**: http://localhost:8000/docs
2. **코드 읽기**: README.md의 "팀원을 위한 가이드" 참고
3. **기능 추가**: 새로운 기능 구현 시작

## 💡 유용한 명령어

### Backend
```bash
# 서버 실행
python main.py

# 특정 포트로 실행
uvicorn main:app --port 8001 --reload

# 데이터베이스 초기화 (주의: 모든 데이터 삭제)
# MySQL에서 직접 실행
DROP DATABASE ssmaz_db;
CREATE DATABASE ssmaz_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Frontend
```bash
# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build

# 빌드 결과 미리보기
npm run preview
```

## 📞 도움이 필요하신가요?

- 이슈 생성: GitHub Issues
- 문서 확인: README.md
- API 문서: http://localhost:8000/docs

---

**축하합니다! 🎉 SsmaZ 프로젝트 설정이 완료되었습니다!**
