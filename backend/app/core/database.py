"""
데이터베이스 연결 설정 파일
SQLAlchemy를 사용하여 MySQL 데이터베이스와 연결합니다.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# 데이터베이스 URL 가져오기
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy 엔진 생성
# pool_pre_ping=True: 연결이 유효한지 미리 확인
# echo=True: SQL 쿼리를 콘솔에 출력 (개발 시 유용, 프로덕션에서는 False로 설정)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=True
)

# 세션 로컬 클래스 생성
# autocommit=False: 자동 커밋 비활성화 (명시적으로 커밋해야 함)
# autoflush=False: 자동 플러시 비활성화
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성 (모든 모델이 이 클래스를 상속받음)
Base = declarative_base()

# 데이터베이스 세션을 가져오는 의존성 함수
def get_db():
    """
    FastAPI의 Depends에서 사용할 데이터베이스 세션 생성 함수
    
    사용 예시:
    @app.get("/users")
    def get_users(db: Session = Depends(get_db)):
        return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db  # 요청 처리 중에 세션 제공
    finally:
        db.close()  # 요청 완료 후 세션 닫기
