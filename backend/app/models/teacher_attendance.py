"""
TeacherAttendance 모델 정의
선생님 출퇴근 기록을 저장하는 테이블
"""

from sqlalchemy import Column, Integer, Boolean, TIMESTAMP, ForeignKey, Date, DateTime, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class TeacherAttendance(Base):
    """
    선생님 출퇴근 기록 테이블

    선생님의 일별 출퇴근 기록을 저장하고,
    근무시간 계산 및 원장 승인 기능을 제공합니다.

    컬럼 설명:
    - id: 고유 ID (PK)
    - teacher_id: 선생님 ID (FK → Teachers)
    - date: 근무일
    - check_in_time: 출근 시각
    - check_out_time: 퇴근 시각
    - worked_minutes: 계산된 근무시간 (분)
    - is_approved: 원장 승인 여부
    - approved_by: 승인한 원장 ID (FK → Users)
    - created_at: 생성 시간
    - updated_at: 수정 시간
    """
    __tablename__ = "TeacherAttendances"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="고유 ID"
    )

    teacher_id = Column(
        Integer,
        ForeignKey("Teachers.teacher_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="선생님 ID"
    )

    date = Column(
        Date,
        nullable=False,
        index=True,
        comment="근무일"
    )

    check_in_time = Column(
        DateTime,
        nullable=True,
        comment="출근 시각"
    )

    check_out_time = Column(
        DateTime,
        nullable=True,
        comment="퇴근 시각"
    )

    status = Column(
        String(20),
        nullable=False,
        default="pending",
        comment="출결 상태 (checked_in, checked_out, late, absent, leave, approved, pending)"
    )

    worked_minutes = Column(
        Integer,
        nullable=False,
        default=0,
        comment="계산된 근무시간 (분)"
    )

    memo = Column(
        Text,
        nullable=True,
        comment="출근 메모"
    )

    is_approved = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="원장 승인 여부"
    )

    approved_by = Column(
        Integer,
        ForeignKey("Users.user_id"),
        nullable=True,
        comment="승인한 원장 ID"
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )

    updated_at = Column(
        TIMESTAMP,
        nullable=True,
        onupdate=func.now(),
        comment="수정 시간"
    )

    # Relationships (lazy loading으로 순환 참조 방지)
    teacher = relationship("app.models.teacher.Teacher", backref="teacher_attendances", lazy="select")
    approver = relationship("app.models.user.User", backref="approved_attendances", lazy="select")

    def __repr__(self):
        return f"<TeacherAttendance(id={self.id}, teacher_id={self.teacher_id}, date={self.date})>"
