from pydantic import BaseModel, model_validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum
from app.schemas.student import StudentResponse


# 스키마용 Enum (SQLAlchemy 모델 Enum과 분리하여 RecursionError 방지)
class AttendanceStatusSchema(str, Enum):
    """출결 상태 (스키마용)"""
    PRESENT = "출석"
    LATE = "지각"
    ABSENT = "결석"
    EARLY_LEAVE = "조퇴"


class AttendanceMethodSchema(str, Enum):
    """출결 방식 (스키마용)"""
    SELF = "SELF"
    MANUAL = "MANUAL"


class AttendanceBase(BaseModel):
    student_id: int
    status: AttendanceStatusSchema
    method: Optional[AttendanceMethodSchema] = AttendanceMethodSchema.MANUAL

class AttendanceCheckRequest(AttendanceBase):
    """
    출결 체크 요청 스키마
    - action: "CHECK_IN" (default) or "CHECK_OUT"
    """
    action: Optional[str] = "CHECK_IN"

class AttendanceResponse(AttendanceBase):
    att_id: int
    status: str  # AttendanceBase의 Enum을 str로 오버라이드 (하원 표시 지원)
    check_in_at: Optional[datetime]
    check_out_at: Optional[datetime]
    attendance_date: date
    is_notified: bool

    class Config:
        from_attributes = True

    @model_validator(mode='before')
    @classmethod
    def apply_display_status(cls, data):
        """check_out_at이 있으면 status를 '하원'으로 변환"""
        if hasattr(data, '__dict__'):  # ORM 객체인 경우
            check_out_at = getattr(data, 'check_out_at', None)
            status_val = getattr(data, 'status', None)
            if hasattr(status_val, 'value'):
                status_val = status_val.value
            if check_out_at is not None:
                return {
                    'att_id': data.att_id,
                    'student_id': data.student_id,
                    'status': '하원',
                    'method': data.method,
                    'check_in_at': data.check_in_at,
                    'check_out_at': data.check_out_at,
                    'attendance_date': data.attendance_date,
                    'is_notified': data.is_notified,
                }
        elif isinstance(data, dict):  # dict인 경우
            check_out_at = data.get('check_out_at')
            if check_out_at is not None:
                data['status'] = '하원'
        return data

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
    status: AttendanceStatusSchema


class AttendanceBatchRequest(BaseModel):
    """출결 일괄 처리 요청"""
    date: Optional[date] = None  # 기본값: 오늘
    items: List[AttendanceBatchItem]


class AttendanceBatchResponse(BaseModel):
    """출결 일괄 처리 응답"""
    success_count: int
    fail_count: int
    failed_items: List[dict] = []  # [{student_id, error}]


# ==================== 관리자용 스키마 ====================

class AdminStudentAttendanceItem(BaseModel):
    """관리자용 학생 출결 조회 항목"""
    att_id: int
    student_id: int
    student_name: str
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    attendance_date: date
    status: str
    check_in_at: Optional[datetime] = None
    check_out_at: Optional[datetime] = None
    memo: Optional[str] = None

    class Config:
        from_attributes = True


class AdminStudentAttendanceListResponse(BaseModel):
    """관리자용 학생 출결 목록 응답"""
    records: List[AdminStudentAttendanceItem]
    total: int
    page: int
    limit: int
    stats: AttendanceStats


class AdminStudentAttendanceUpdate(BaseModel):
    """관리자용 학생 출결 수정 요청"""
    status: Optional[AttendanceStatusSchema] = None
    check_in_at: Optional[datetime] = None
    check_out_at: Optional[datetime] = None
    memo: Optional[str] = None


class AdminStudentAttendanceCreate(BaseModel):
    """관리자용 학생 출결 생성 요청"""
    student_id: int
    attendance_date: date
    status: AttendanceStatusSchema
    check_in_at: Optional[datetime] = None
    memo: Optional[str] = None
