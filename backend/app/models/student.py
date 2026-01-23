"""
Student 모델 정의
학원생 정보를 저장하는 테이블
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class StudentStatus(str, enum.Enum):
    """학생 상태"""
    ENROLLED = "enrolled"    # 재원 중
    PAUSED = "paused"        # 일시정지/휴원
    GRADUATED = "graduated"  # 수료/졸업


class Student(Base):
    """
    학생 정보 테이블
    
    User 테이블과 1:1 관계 (선택적)
    - User: 로그인 계정 정보 (학생용 앱 사용 시)
    - Student: 학생 전용 정보
    
    컬럼 설명:
    - student_id: 학생 고유 ID (PK)
    - user_id: User 테이블의 user_id (FK, nullable)
    - academy_id: 학원 ID
    - class_id: 반 ID (nullable)
    - name: 학생 이름
    - school: 학교명
    - grade: 학년
    - phone: 학생 전화번호
    - parent_phone: 학부모 전화번호 (알림 발송용)
    - enrollment_date: 등록일(입학일)
    - status: 학생 상태 (enrolled, paused, graduated)
    - regdate: 생성 시간
    """
    __tablename__ = "Students"

    student_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="학생 고유 ID"
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

    class_id = Column(
        Integer,
        nullable=True,
        comment="반 ID"
    )

    name = Column(
        String(50),
        nullable=False,
        comment="학생 이름"
    )
    
    school = Column(
        String(100),
        nullable=True,
        comment="학교명"
    )
    
    grade = Column(
        String(20),
        nullable=True,
        comment="학년 (예: 중1, 고2)"
    )
    
    phone = Column(
        String(20),
        nullable=True,
        comment="학생 전화번호"
    )

    parent_phone = Column(
        String(20),
        nullable=False,
        comment="학부모 전화번호"
    )
    
    enrollment_date = Column(
        Date,
        nullable=True,
        comment="등록일(입학일)"
    )

    status = Column(
        Enum(StudentStatus),
        default=StudentStatus.ENROLLED,
        nullable=False,
        comment="학생 상태 (enrolled, paused, graduated)"
    )

    regdate = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )
    
    # Relationships
    user = relationship("app.models.user.User", backref="student", uselist=False)

    def __repr__(self):
        return f"<Student(student_id={self.student_id}, name='{self.name}', grade='{self.grade}')>"
