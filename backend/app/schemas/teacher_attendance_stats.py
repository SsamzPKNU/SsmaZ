"""
선생님 출석 통계 응답 스키마
프론트엔드 camelCase 명세에 맞춤
"""

from pydantic import BaseModel
from typing import List


class MonthlyAttendanceData(BaseModel):
    month: str                # "2026-01" 형식
    presentCount: int
    lateCount: int
    absentCount: int
    dismissedCount: int


class ClassAttendanceData(BaseModel):
    classId: int
    className: str
    attendanceRate: float     # 출석률 (%)
    presentCount: int
    lateCount: int
    absentCount: int
    dismissedCount: int


class TeacherAttendanceStatsResponse(BaseModel):
    attendanceRate: float      # 전체 출석률 (%)
    presentCount: int          # 출석 수
    lateCount: int             # 지각 수
    absentCount: int           # 결석 수
    excusedCount: int = 0      # 사유결석 (DB ENUM에 없음, 항상 0)
    dismissedCount: int        # 조퇴 수
    monthlyData: List[MonthlyAttendanceData]
    classByClass: List[ClassAttendanceData]
