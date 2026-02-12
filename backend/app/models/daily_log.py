"""
DailyLog 모델 정의
일일 기록(알림장) 테이블 - 학생별 태도 점수 및 학습 기록
"""

from sqlalchemy import Column, Integer, Text, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class DailyLog(Base):
    """
    일일 기록 테이블 (기존 DailyLogs 테이블 매핑)

    컬럼 설명:
    - log_id: 기록 고유 ID (PK)
    - student_id: 학생 ID (FK)
    - academy_id: 학원 ID
    - teacher_id: 작성 선생님 ID (FK, ALTER로 추가)
    - attitude_score: 태도 점수
    - study_note: 학습 기록/메모
    - is_sent: 학부모 발송 여부
    - regdate: 기록 날짜
    """
    __tablename__ = "DailyLogs"

    log_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="기록 고유 ID"
    )

    student_id = Column(
        Integer,
        ForeignKey("Students.student_id"),
        nullable=False,
        comment="학생 ID"
    )

    academy_id = Column(
        Integer,
        nullable=False,
        comment="학원 ID"
    )

    teacher_id = Column(
        Integer,
        ForeignKey("Teachers.teacher_id"),
        nullable=True,
        comment="작성 선생님 ID"
    )

    attitude_score = Column(
        Integer,
        nullable=True,
        comment="태도 점수"
    )

    study_note = Column(
        Text,
        nullable=True,
        comment="학습 기록/메모"
    )

    is_sent = Column(
        Boolean,
        default=False,
        comment="학부모 발송 여부"
    )

    regdate = Column(
        Date,
        nullable=False,
        comment="기록 날짜"
    )

    # Relationships
    student = relationship("app.models.student.Student", backref="daily_logs")
    teacher = relationship("app.models.teacher.Teacher", backref="daily_logs")

    def __repr__(self):
        return f"<DailyLog(log_id={self.log_id}, student_id={self.student_id}, date={self.regdate})>"
