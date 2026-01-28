"""
Schedule 모델 정의
시간표 정보를 저장하는 테이블
"""

from sqlalchemy import Column, Integer, String, Time, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Schedule(Base):
    """
    시간표 정보 테이블

    Class와 N:1 관계

    컬럼 설명:
    - schedule_id: 시간표 고유 ID (PK)
    - class_id: 반 ID (FK)
    - day_of_week: 요일 (월, 화, 수, 목, 금, 토, 일)
    - start_time: 시작 시간
    - end_time: 종료 시간
    - created_at: 생성 시간
    """
    __tablename__ = "Schedules"

    schedule_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="시간표 고유 ID"
    )

    class_id = Column(
        Integer,
        ForeignKey("Classes.class_id", ondelete="CASCADE"),
        nullable=False,
        comment="반 ID"
    )

    day_of_week = Column(
        String(10),
        nullable=False,
        comment="요일 (월, 화, 수, 목, 금, 토, 일)"
    )

    start_time = Column(
        Time,
        nullable=False,
        comment="시작 시간"
    )

    end_time = Column(
        Time,
        nullable=False,
        comment="종료 시간"
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )

    # Relationships
    class_obj = relationship("app.models.class_model.Class", backref="schedules")

    def __repr__(self):
        return f"<Schedule(schedule_id={self.schedule_id}, class_id={self.class_id}, day={self.day_of_week})>"
