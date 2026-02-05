"""
Class 모델 정의
반/수업 정보를 저장하는 테이블
"""

from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base


class ClassStatus(PyEnum):
    """클래스 상태 Enum"""
    ACTIVE = "active"       # 운영중
    INACTIVE = "inactive"   # 비활성
    PENDING = "pending"     # 대기
    CLOSED = "closed"       # 종료


class Class(Base):
    """
    반/수업 정보 테이블

    Teacher와 N:1 관계
    Student와 1:N 관계

    컬럼 설명:
    - class_id: 반 고유 ID (PK)
    - academy_id: 학원 ID
    - teacher_id: 담당 선생님 ID (FK)
    - class_name: 반 이름
    - capacity: 정원
    """
    __tablename__ = "Classes"

    class_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="반 고유 ID"
    )

    academy_id = Column(
        Integer,
        nullable=False,
        comment="학원 ID"
    )

    class_name = Column(
        String(50),
        nullable=False,
        comment="반 이름"
    )

    teacher_id = Column(
        Integer,
        ForeignKey("Teachers.teacher_id"),
        nullable=True,
        comment="담당 선생님 ID"
    )

    capacity = Column(
        Integer,
        nullable=True,
        comment="정원"
    )

    subject = Column(
        String(50),
        nullable=True,
        comment="과목"
    )

    grade_level = Column(
        String(30),
        nullable=True,
        comment="학년/레벨"
    )

    fee = Column(
        Integer,
        nullable=True,
        comment="수강료 (원)"
    )

    status = Column(
        Enum(ClassStatus),
        nullable=False,
        default=ClassStatus.ACTIVE,
        comment="반 상태"
    )

    # Relationships
    teacher = relationship("app.models.teacher.Teacher", backref="classes")

    @property
    def name(self) -> str:
        """class_name의 별칭 (호환성)"""
        return self.class_name

    def __repr__(self):
        return f"<Class(class_id={self.class_id}, name='{self.class_name}', teacher_id={self.teacher_id})>"
