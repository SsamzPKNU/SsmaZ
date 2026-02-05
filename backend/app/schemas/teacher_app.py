"""
선생님용 앱 관련 Pydantic 스키마
API 요청/응답 데이터 검증 및 직렬화
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date as DateType
from enum import Enum


class AttendanceStatusEnum(str, Enum):
    """출결 상태"""
    PRESENT = "present"    # 출석
    LATE = "late"          # 지각
    ABSENT = "absent"      # 결석
    EXCUSED = "excused"    # 조퇴


class TeacherDashboardResponse(BaseModel):
    """선생님 대시보드 응답"""
    total_classes: int = Field(..., description="담당 반 수")
    total_students: int = Field(..., description="담당 학생 수")
    today_attendance_rate: float = Field(..., description="오늘 출석률 (%)")
    monthly_collection_rate: float = Field(..., description="이번 달 수납률 (%)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_classes": 3,
                "total_students": 45,
                "today_attendance_rate": 95.5,
                "monthly_collection_rate": 88.0
            }
        }


class TeacherClassResponse(BaseModel):
    """선생님 담당 반 응답"""
    id: int = Field(..., description="반 ID")
    name: str = Field(..., description="반 이름")
    student_count: int = Field(..., description="현재 학생 수")
    capacity: Optional[int] = Field(None, description="정원")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "수학 정규반 A",
                "student_count": 12,
                "capacity": 15
            }
        }


class TeacherStudentResponse(BaseModel):
    """선생님용 학생 목록 응답"""
    id: int = Field(..., description="학생 ID")
    name: str = Field(..., description="학생 이름")
    grade: Optional[str] = Field(None, description="학년")
    school: Optional[str] = Field(None, description="학교명")
    phone: Optional[str] = Field(None, description="학생 전화번호")
    parent_phone: str = Field(..., description="학부모 전화번호")
    class_name: Optional[str] = Field(None, description="소속 반 이름")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "김철수",
                "grade": "중1",
                "school": "SSamZ중학교",
                "phone": "010-1111-2222",
                "parent_phone": "010-3333-4444",
                "class_name": "수학 정규반 A"
            }
        }


class StudentDetailResponse(BaseModel):
    """학생 상세 정보 응답"""
    id: int = Field(..., description="학생 ID")
    name: str = Field(..., description="학생 이름")
    grade: Optional[str] = Field(None, description="학년")
    school: Optional[str] = Field(None, description="학교명")
    phone: Optional[str] = Field(None, description="학생 전화번호")
    parent_phone: str = Field(..., description="학부모 전화번호")
    enrollment_date: Optional[DateType] = Field(None, description="등록일")
    status: str = Field(..., description="학생 상태")
    class_id: Optional[int] = Field(None, description="반 ID")
    class_name: Optional[str] = Field(None, description="반 이름")
    attendance_rate: float = Field(..., description="출석률 (최근 30일)")
    recent_attendance: List[dict] = Field(default=[], description="최근 출결 기록 (5건)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "김철수",
                "grade": "중1",
                "school": "SSamZ중학교",
                "phone": "010-1111-2222",
                "parent_phone": "010-3333-4444",
                "enrollment_date": "2025-01-10",
                "status": "enrolled",
                "class_id": 1,
                "class_name": "수학 정규반 A",
                "attendance_rate": 95.5,
                "recent_attendance": [
                    {"date": "2026-01-23", "status": "present"},
                    {"date": "2026-01-22", "status": "present"}
                ]
            }
        }


class AttendanceRecordResponse(BaseModel):
    """출결 기록 응답"""
    id: int = Field(..., description="출결 기록 ID")
    student_id: int = Field(..., description="학생 ID")
    student_name: str = Field(..., description="학생 이름")
    attendance_date: DateType = Field(..., description="출결 날짜")
    status: str = Field(..., description="출결 상태")
    check_in_time: Optional[str] = Field(None, description="등원 시간")
    check_out_time: Optional[str] = Field(None, description="하원 시간")
    memo: Optional[str] = Field(None, description="메모")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "student_id": 1,
                "student_name": "김철수",
                "attendance_date": "2026-01-23",
                "status": "present",
                "check_in_time": "16:00",
                "check_out_time": "19:00",
                "memo": None
            }
        }


class AttendanceCreateRequest(BaseModel):
    """출결 등록 요청"""
    attendance_date: DateType = Field(..., description="출결 날짜")
    status: AttendanceStatusEnum = Field(..., description="출결 상태")
    check_in_time: Optional[str] = Field(None, description="등원 시간 (HH:MM)")
    check_out_time: Optional[str] = Field(None, description="하원 시간 (HH:MM)")
    memo: Optional[str] = Field(None, max_length=500, description="메모")

    class Config:
        json_schema_extra = {
            "example": {
                "attendance_date": "2026-01-23",
                "status": "present",
                "check_in_time": "16:00",
                "check_out_time": "19:00",
                "memo": "수업 태도 양호"
            }
        }


class AttendanceUpdateRequest(BaseModel):
    """출결 수정 요청"""
    status: Optional[AttendanceStatusEnum] = Field(None, description="출결 상태")
    check_in_time: Optional[str] = Field(None, description="등원 시간 (HH:MM)")
    check_out_time: Optional[str] = Field(None, description="하원 시간 (HH:MM)")
    memo: Optional[str] = Field(None, max_length=500, description="메모")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "late",
                "check_in_time": "16:30",
                "memo": "지각 (버스 지연)"
            }
        }


# ==================== 반 출결 현황 스키마 ====================

class ClassAttendanceStudentItem(BaseModel):
    """반 출결 현황 학생 항목"""
    student_id: int
    student_name: str
    status: Optional[str] = None
    check_in_at: Optional[str] = None
    check_out_at: Optional[str] = None
    memo: Optional[str] = None
    att_id: Optional[int] = None


class ClassAttendanceStatsDict(BaseModel):
    """반 출결 통계"""
    total: int
    present: int = 0
    late: int = 0
    absent: int = 0
    early: int = 0
    not_checked: int = 0


class ClassAttendanceResponse(BaseModel):
    """반 출결 현황 응답"""
    class_id: int
    class_name: str
    date: DateType
    stats: ClassAttendanceStatsDict
    students: List[ClassAttendanceStudentItem]


class ClassAttendanceBatchItem(BaseModel):
    """반 출결 일괄 처리 항목"""
    student_id: int
    status: AttendanceStatusEnum


class ClassAttendanceBatchRequest(BaseModel):
    """반 출결 일괄 처리 요청"""
    date: Optional[DateType] = Field(default=None, description="출결 날짜 (YYYY-MM-DD, 미입력 시 오늘)")
    items: List[ClassAttendanceBatchItem] = Field(..., description="출결 항목 목록")


class ClassAttendanceBatchResponse(BaseModel):
    """반 출결 일괄 처리 응답"""
    success_count: int
    fail_count: int
    failed_items: List[dict] = []


# ==================== 반 출결 통계 (기간별) 스키마 ====================

class StudentAttendanceSummaryItem(BaseModel):
    """학생별 출결 통계 항목"""
    student_id: int
    student_name: str
    attendance_rate: float
    present: int = 0
    late: int = 0
    absent: int = 0
    early: int = 0


class ClassAttendanceSummaryStats(BaseModel):
    """반 전체 출결 통계"""
    total_records: int
    avg_attendance_rate: float
    present: int = 0
    late: int = 0
    absent: int = 0
    early: int = 0


class ClassAttendanceSummaryResponse(BaseModel):
    """반 출결 통계 (기간별) 응답"""
    class_id: int
    class_name: str
    period_start: DateType
    period_end: DateType
    total_days: int
    stats: ClassAttendanceSummaryStats
    students: List[StudentAttendanceSummaryItem]
