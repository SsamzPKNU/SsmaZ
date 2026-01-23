"""
Student 모델 정의
학원생 정보를 저장하는 테이블
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class StudentStatus(str, enum.Enum):
    """학생 상태"""
    ENROLLED = "재원"
    PAUSED = "휴원"
    GRADUATED = "졸업"


class Student(Base):
    """
    학생 정보 테이블

    컬럼 설명:
    - student_id: 학생 고유 ID (PK)
    - academy_id: 학원 ID
    - class_id: 반 ID (nullable)
    - name: 학생 이름
    - parent_phone: 학부모 전화번호 (알림 발송용)
    - status: 학생 상태 (재원, 휴원, 졸업)
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

    parent_phone = Column(
        String(20),
        nullable=False,
        comment="학부모 전화번호"
    )

    status = Column(
        Enum(StudentStatus, values_callable=lambda x: [e.value for e in x]),
        default=StudentStatus.ENROLLED,
        nullable=True,
        comment="학생 상태 (재원, 휴원, 졸업)"
    )

    regdate = Column(
        DateTime,
        server_default=func.now(),
        nullable=True,
        comment="생성 시간"
    )

    def __repr__(self):
        return f"<Student(student_id={self.student_id}, name='{self.name}')>"
