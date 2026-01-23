"""
Student 모델 정의
학원생 정보를 저장하는 테이블
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base


class Student(Base):
    """
    학생 정보 테이블

    컬럼 설명:
    - student_id: 학생 고유 ID (PK)
    - academy_id: 학원 ID
    - class_id: 반 ID (nullable)
    - name: 학생 이름
    - parent_phone: 학부모 전화번호 (알림 발송용)
    - status: 학생 상태 (재원, 퇴원 등)
    - regdate: 등록일
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
        String(20),
        nullable=True,
        default="재원",
        comment="학생 상태 (재원, 퇴원 등)"
    )

    regdate = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=True,
        comment="등록일"
    )

    def __repr__(self):
        return f"<Student(student_id={self.student_id}, name='{self.name}')>"
