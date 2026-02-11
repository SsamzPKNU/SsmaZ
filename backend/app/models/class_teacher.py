"""
반-선생님 수준별 배정 모델
반 하나당 상(high)/중(mid)/하(low) 수준별 선생님 3명 배정
"""

from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, Boolean, TIMESTAMP, ForeignKey,
    Enum, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class TeacherLevel(str, PyEnum):
    """수준별 배정 레벨"""
    HIGH = "high"   # 상
    MID = "mid"     # 중
    LOW = "low"     # 하


class ClassTeacherAssignment(Base):
    """
    반-선생님 수준별 배정 테이블

    Classes 테이블의 teacher_id(레거시)와 병행 운영
    MID 레벨 배정 시 Classes.teacher_id와 자동 동기화

    컬럼 설명:
    - id: 배정 고유 ID (PK)
    - academy_id: 학원 ID
    - class_id: 반 ID (FK → Classes)
    - teacher_id: 선생님 ID (FK → Teachers)
    - level: 수준 (high, mid, low)
    - is_primary: 대표 선생님 여부
    - created_at: 배정 시간
    """
    __tablename__ = "ClassTeacherAssignments"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="배정 고유 ID"
    )

    academy_id = Column(
        Integer,
        nullable=False,
        comment="학원 ID"
    )

    class_id = Column(
        Integer,
        ForeignKey("Classes.class_id"),
        nullable=False,
        comment="반 ID"
    )

    teacher_id = Column(
        Integer,
        ForeignKey("Teachers.teacher_id"),
        nullable=False,
        comment="선생님 ID"
    )

    level = Column(
        Enum('high', 'mid', 'low', name='teacherlevel'),
        nullable=False,
        comment="수준 (high: 상, mid: 중, low: 하)"
    )

    is_primary = Column(
        Boolean,
        default=False,
        comment="대표 선생님 여부"
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        comment="배정 시간"
    )

    __table_args__ = (
        UniqueConstraint('class_id', 'level', name='uq_class_level'),
        Index('ix_cta_teacher', 'teacher_id'),
        Index('ix_cta_class', 'class_id'),
    )

    # Relationships
    class_obj = relationship("app.models.class_model.Class", backref="teacher_assignments")
    teacher = relationship("app.models.teacher.Teacher", backref="class_assignments")

    def __repr__(self):
        return f"<ClassTeacherAssignment(class_id={self.class_id}, teacher_id={self.teacher_id}, level='{self.level}')>"
