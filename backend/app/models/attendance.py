"""
Attendance 모델 정의
출결 기록을 저장하는 테이블
"""

from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP, ForeignKey, Boolean, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class AttendanceStatus(str, enum.Enum):
    """
    출결 상태 (DB 테이블의 ENUM 설정과 일치시킴: '출석', '지각', '결석', '조퇴')
    """
    PRESENT = "출석"
    LATE = "지각"
    ABSENT = "결석"
    EARLY_LEAVE = "조퇴"

class AttendanceMethod(str, enum.Enum):
    """
    출결 방식
    """
    SELF = "SELF"
    MANUAL = "MANUAL"

class Attendance(Base):
    """
    출결 기록 테이블
    """
    __tablename__ = "Attendance"
    
    att_id = Column(
        Integer, 
        primary_key=True, 
        index=True, 
        autoincrement=True,
        comment="출결 ID"
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
    
    status = Column(
        Enum(AttendanceStatus, values_callable=lambda x: [e.value for e in x]), 
        nullable=False,
        comment="출결 상태 ('출석', '지각', '결석', '조퇴')"
    )
    
    check_in_at = Column(
        TIMESTAMP, 
        nullable=True,
        comment="등원 시간"
    )
    
    check_out_at = Column(
        TIMESTAMP, 
        nullable=True,
        comment="하원 시간"
    )
    
    attendance_date = Column(
        Date, 
        nullable=False,
        comment="출석 기준 날짜"
    )

    memo = Column(
        String(255),
        nullable=True,
        comment="비고"
    )
    
    is_notified = Column(
        Boolean, 
        default=False,
        comment="알림 발송 여부"
    )
    
    method = Column(
        Enum(AttendanceMethod), 
        default=AttendanceMethod.MANUAL,
        comment="처리 방식 (SELF/MANUAL)"
    )

    # Relationship
    student = relationship("app.models.student.Student", backref="attendances")

    def __repr__(self):
        return f"<Attendance(att_id={self.att_id}, student_id={self.student_id}, status={self.status}, date={self.attendance_date})>"
