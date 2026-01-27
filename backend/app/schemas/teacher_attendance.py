"""
선생님 출퇴근 관련 Pydantic 스키마
API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date


class TeacherCheckIn(BaseModel):
    """출근 요청 스키마"""
    work_date: Optional[date] = Field(None, description="근무일 (미입력 시 오늘)")

    class Config:
        json_schema_extra = {
            "example": {
                "work_date": "2026-01-27"
            }
        }


class TeacherCheckOut(BaseModel):
    """퇴근 요청 스키마 (빈 body)"""
    pass


class TeacherAttendanceResponse(BaseModel):
    """선생님 출퇴근 기록 응답 스키마"""
    id: int = Field(..., description="고유 ID")
    teacher_id: int = Field(..., description="선생님 ID")
    work_date: date = Field(..., description="근무일", alias="date")
    check_in_time: Optional[datetime] = Field(None, description="출근 시각")
    check_out_time: Optional[datetime] = Field(None, description="퇴근 시각")
    worked_minutes: int = Field(..., description="근무시간 (분)")
    is_approved: bool = Field(..., description="원장 승인 여부")
    approved_by: Optional[int] = Field(None, description="승인한 원장 ID")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: Optional[datetime] = Field(None, description="수정 시간")

    class Config:
        from_attributes = True
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "teacher_id": 5,
                "work_date": "2026-01-27",
                "check_in_time": "2026-01-27T09:00:00",
                "check_out_time": "2026-01-27T18:00:00",
                "worked_minutes": 540,
                "is_approved": True,
                "approved_by": 1,
                "created_at": "2026-01-27T09:00:00",
                "updated_at": "2026-01-27T18:00:00"
            }
        }


class TeacherAttendanceListResponse(BaseModel):
    """선생님 출퇴근 기록 목록 응답 스키마"""
    records: List[TeacherAttendanceResponse] = Field(..., description="출퇴근 기록 목록")
    total: int = Field(..., description="전체 기록 수")

    class Config:
        json_schema_extra = {
            "example": {
                "records": [
                    {
                        "id": 1,
                        "teacher_id": 5,
                        "work_date": "2026-01-27",
                        "check_in_time": "2026-01-27T09:00:00",
                        "check_out_time": "2026-01-27T18:00:00",
                        "worked_minutes": 540,
                        "is_approved": True,
                        "approved_by": 1,
                        "created_at": "2026-01-27T09:00:00",
                        "updated_at": None
                    }
                ],
                "total": 1
            }
        }


class WorkHoursSummary(BaseModel):
    """근무시간 요약 스키마"""
    teacher_id: int = Field(..., description="선생님 ID")
    teacher_name: str = Field(..., description="선생님 이름")
    period_start: date = Field(..., description="조회 시작일")
    period_end: date = Field(..., description="조회 종료일")
    total_minutes: int = Field(..., description="총 근무시간 (분)")
    total_hours: float = Field(..., description="총 근무시간 (시간)")
    total_days: int = Field(..., description="총 근무일수")
    employment_type: Optional[str] = Field(None, description="고용 형태")
    hourly_rate: Optional[int] = Field(None, description="시급")
    estimated_salary: Optional[int] = Field(None, description="예상 급여 (시급 * 시간)")

    class Config:
        json_schema_extra = {
            "example": {
                "teacher_id": 5,
                "teacher_name": "김선생",
                "period_start": "2026-01-01",
                "period_end": "2026-01-31",
                "total_minutes": 10800,
                "total_hours": 180.0,
                "total_days": 22,
                "employment_type": "PART_TIME",
                "hourly_rate": 15000,
                "estimated_salary": 2700000
            }
        }


class AdminAttendanceResponse(BaseModel):
    """관리자용 출퇴근 현황 응답 스키마"""
    id: int = Field(..., description="기록 ID")
    teacher_id: int = Field(..., description="선생님 ID")
    teacher_name: str = Field(..., description="선생님 이름")
    work_date: date = Field(..., description="근무일", alias="date")
    check_in_time: Optional[datetime] = Field(None, description="출근 시각")
    check_out_time: Optional[datetime] = Field(None, description="퇴근 시각")
    worked_minutes: int = Field(..., description="근무시간 (분)")
    is_approved: bool = Field(..., description="승인 여부")

    class Config:
        from_attributes = True
        populate_by_name = True


class AdminAttendanceListResponse(BaseModel):
    """관리자용 출퇴근 현황 목록 응답 스키마"""
    query_date: date = Field(..., description="조회 날짜")
    records: List[AdminAttendanceResponse] = Field(..., description="출퇴근 기록 목록")
    total: int = Field(..., description="전체 기록 수")


class ApproveRequest(BaseModel):
    """승인 요청 스키마"""
    pass
