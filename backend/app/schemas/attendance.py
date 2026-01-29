from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from app.models.attendance import AttendanceStatus, AttendanceMethod
from app.schemas.student import StudentResponse

class AttendanceBase(BaseModel):
    student_id: int
    status: AttendanceStatus
    method: Optional[AttendanceMethod] = AttendanceMethod.MANUAL

class AttendanceCheckRequest(AttendanceBase):
    """
    출결 체크 요청 스키마
    - action: "CHECK_IN" (default) or "CHECK_OUT"
    """
    action: Optional[str] = "CHECK_IN"

class AttendanceResponse(AttendanceBase):
    att_id: int
    check_in_at: Optional[datetime]
    check_out_at: Optional[datetime]
    attendance_date: date
    is_notified: bool

    class Config:
        from_attributes = True

class AttendanceUpdate(BaseModel):
    check_out_at: Optional[datetime] = None
    is_notified: Optional[bool] = None

class StudentAttendanceStatus(BaseModel):
    student: StudentResponse
    attendance: Optional[AttendanceResponse] = None # None if no record yet today

    class Config:
        from_attributes = True


class AttendanceStats(BaseModel):
    """출결 통계"""
    total: int = 0        # 전체 학생 수
    present: int = 0      # 출석
    late: int = 0         # 지각
    absent: int = 0       # 결석
    early: int = 0        # 조퇴


class TodayAttendanceResponse(BaseModel):
    date: date
    stats: AttendanceStats
    students: List[StudentAttendanceStatus]


class AttendanceBatchItem(BaseModel):
    """출결 일괄 처리 항목"""
    student_id: int
    status: AttendanceStatus


class AttendanceBatchRequest(BaseModel):
    """출결 일괄 처리 요청"""
    date: Optional[date] = None  # 기본값: 오늘
    items: List[AttendanceBatchItem]


class AttendanceBatchResponse(BaseModel):
    """출결 일괄 처리 응답"""
    success_count: int
    fail_count: int
    failed_items: List[dict] = []  # [{student_id, error}]
