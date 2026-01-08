"""
User 모델 정의
학원 관리 시스템의 사용자 정보를 저장하는 테이블
"""

from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class UserRole(str, enum.Enum):
    """
    사용자 역할 정의
    - ADMIN: 관리자 (학원 전체 관리)
    - TEACHER: 선생님 (수업 및 학생 관리)
    - STUDENT: 학생 (본인 정보 조회)
    """
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"


class User(Base):
    """
    사용자 정보 테이블
    
    컬럼 설명:
    - user_id: 사용자 고유 ID (자동 증가)
    - academy_id: 소속 학원 ID (향후 Academy 테이블과 연결)
    - username: 로그인 ID (중복 불가)
    - password_hash: 암호화된 비밀번호
    - user_role: 사용자 역할 (ADMIN, TEACHER, STUDENT)
    - name: 실명
    - phone: 전화번호
    - created_at: 계정 생성 시간
    """
    __tablename__ = "users"
    
    # 기본 키
    user_id = Column(
        Integer, 
        primary_key=True, 
        index=True, 
        autoincrement=True,
        comment="사용자 고유 ID"
    )
    
    # 학원 ID (외래 키 - 향후 Academy 테이블 생성 시 연결)
    academy_id = Column(
        Integer,
        # ForeignKey('academies.academy_id'),  # Academy 테이블 생성 후 주석 해제
        nullable=False,
        comment="소속 학원 ID"
    )
    
    # 로그인 정보
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="로그인 ID (중복 불가)"
    )
    
    password_hash = Column(
        String(255),
        nullable=False,
        comment="bcrypt로 암호화된 비밀번호"
    )
    
    # 사용자 역할
    user_role = Column(
        Enum(UserRole),
        default=UserRole.TEACHER,
        nullable=False,
        comment="사용자 역할 (ADMIN/TEACHER/STUDENT)"
    )
    
    # 개인 정보
    name = Column(
        String(50),
        nullable=True,
        comment="사용자 실명"
    )
    
    phone = Column(
        String(20),
        nullable=True,
        comment="전화번호"
    )
    
    # 생성 시간 (자동 설정)
    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="계정 생성 시간"
    )
    
    def __repr__(self):
        """
        객체를 문자열로 표현 (디버깅용)
        """
        return f"<User(user_id={self.user_id}, username='{self.username}', role={self.user_role})>"
