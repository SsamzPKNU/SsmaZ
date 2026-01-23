"""
Class 모델 정의
반/수업 정보를 저장하는 테이블
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Class(Base):
    """
    반/수업 정보 테이블
    
    Teacher와 N:1 관계
    Student와 1:N 관계
    
    컬럼 설명:
    - class_id: 반 고유 ID (PK)
    - academy_id: 학원 ID
    - teacher_id: 담당 선생님 ID (FK)
    - name: 반 이름
    - schedule: 수업 일정 (예: 월/수/금 16:00)
    - capacity: 정원
    - created_at: 생성 시간
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
    
    teacher_id = Column(
        Integer,
        ForeignKey("Teachers.teacher_id"),
        nullable=True,
        comment="담당 선생님 ID"
    )
    
    name = Column(
        String(100),
        nullable=False,
        comment="반 이름"
    )
    
    schedule = Column(
        String(100),
        nullable=True,
        comment="수업 일정 (예: 월/수/금 16:00)"
    )
    
    capacity = Column(
        Integer,
        nullable=True,
        comment="정원"
    )
    
    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )
    
    # Relationships
    teacher = relationship("app.models.teacher.Teacher", backref="classes")
    
    def __repr__(self):
        return f"<Class(class_id={self.class_id}, name='{self.name}', teacher_id={self.teacher_id})>"
