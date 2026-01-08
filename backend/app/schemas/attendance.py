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

class TodayAttendanceResponse(BaseModel):
    date: date
    students: List[StudentAttendanceStatus]
