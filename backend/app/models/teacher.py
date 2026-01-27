"""
Teacher 모델 정의
선생님 정보를 저장하는 테이블
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Date, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class TeacherStatus(str, enum.Enum):
    """선생님 상태"""
    ACTIVE = "active"      # 재직
    LEAVE = "leave"        # 휴직
    RESIGNED = "resigned"  # 퇴사


class Teacher(Base):
    """
    선생님 정보 테이블
    
    User 테이블과 1:1 관계
    - User: 로그인 계정 정보
    - Teacher: 선생님 전용 정보 (과목, 이메일, 상태 등)
    
    컬럼 설명:
    - teacher_id: 선생님 고유 ID (PK)
    - user_id: User 테이블의 user_id (FK, UNIQUE)
    - academy_id: 학원 ID
    - name: 선생님 이름
    - subject: 담당 과목
    - phone: 전화번호
    - email: 이메일
    - join_date: 입사일
    - status: 재직 상태 (active, leave, resigned)
    - created_at: 생성 시간
    """
    __tablename__ = "Teachers"
    
    teacher_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="선생님 고유 ID"
    )
    
    user_id = Column(
        Integer,
        ForeignKey("Users.user_id"),
        unique=True,
        nullable=True,
        comment="User 테이블의 user_id (로그인 계정 연결)"
    )
    
    academy_id = Column(
        Integer,
        nullable=False,
        comment="학원 ID"
    )
    
    name = Column(
        String(50),
        nullable=False,
        comment="선생님 이름"
    )
    
    subject = Column(
        String(50),
        nullable=True,
        comment="담당 과목"
    )
    
    phone = Column(
        String(20),
        nullable=True,
        comment="전화번호"
    )
    
    email = Column(
        String(100),
        nullable=True,
        comment="이메일"
    )
    
    join_date = Column(
        Date,
        nullable=True,
        comment="입사일"
    )
    
    status = Column(
        Enum(TeacherStatus),
        default=TeacherStatus.ACTIVE,
        nullable=False,
        comment="재직 상태 (active, leave, resigned)"
    )

    employment_type = Column(
        String(20),
        nullable=True,
        default="FULL_TIME",
        comment="고용 형태 (FULL_TIME: 정규직, PART_TIME: 비정규직)"
    )

    hourly_rate = Column(
        Integer,
        nullable=True,
        comment="시급 (비정규직용, 원 단위)"
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )
    
    # Relationships
    user = relationship("app.models.user.User", backref="teacher", uselist=False)
    
    def __repr__(self):
        return f"<Teacher(teacher_id={self.teacher_id}, name='{self.name}', subject='{self.subject}')>"
