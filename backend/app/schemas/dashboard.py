"""
대시보드 관련 Pydantic 스키마
API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date


class SummaryStats(BaseModel):
    """전체 요약 통계"""
    total_students: int = Field(..., description="전체 수강생 수")
    total_teachers: int = Field(..., description="전체 강사 수")
    monthly_revenue: int = Field(..., description="이번 달 예상 매출")
    unpaid_amount: int = Field(..., description="현재 미납 총액")

    class Config:
        json_schema_extra = {
            "example": {
                "total_students": 150,
                "total_teachers": 8,
                "monthly_revenue": 45000000,
                "unpaid_amount": 2500000
            }
        }


class AttendanceRate(BaseModel):
    """출석률 통계"""
    today: float = Field(..., description="오늘 출석률 (%)")
    yesterday: float = Field(..., description="어제 출석률 (%)")

    class Config:
        json_schema_extra = {
            "example": {
                "today": 95.5,
                "yesterday": 94.0
            }
        }


class RecentActivity(BaseModel):
    """최근 활동 내역"""
    id: int = Field(..., description="활동 ID")
    type: str = Field(..., description="활동 타입 (payment, join, attendance 등)")
    message: str = Field(..., description="활동 메시지")
    time: str = Field(..., description="활동 시간")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "type": "payment",
                "message": "김철수 학생 1월 수강료 납부",
                "time": "10:30 AM"
            }
        }


class RevenueTrend(BaseModel):
    """월별 매출 추이"""
    month: str = Field(..., description="년-월 (YYYY-MM)")
    amount: int = Field(..., description="매출액")

    class Config:
        json_schema_extra = {
            "example": {
                "month": "2026-01",
                "amount": 45000000
            }
        }


class OverdueAssignment(BaseModel):
    """미제출 과제 정보"""
    assignment_id: int = Field(..., description="과제 ID")
    title: str = Field(..., description="과제 제목")
    due_date: date = Field(..., description="마감일")
    class_name: Optional[str] = Field(None, description="반 이름")
    not_submitted_count: int = Field(..., description="미제출 학생 수")

    class Config:
        json_schema_extra = {
            "example": {
                "assignment_id": 1,
                "title": "함수 문제 풀이",
                "due_date": "2026-01-27",
                "class_name": "중1-A",
                "not_submitted_count": 3
            }
        }


class TodayScheduleItem(BaseModel):
    """오늘 수업 스케줄"""
    schedule_id: int = Field(..., description="스케줄 ID")
    class_id: int = Field(..., description="반 ID")
    class_name: str = Field(..., description="반 이름")
    start_time: str = Field(..., description="시작 시간 (HH:MM)")
    end_time: str = Field(..., description="종료 시간 (HH:MM)")
    teacher_name: Optional[str] = Field(None, description="담당 선생님")
    student_count: int = Field(0, description="수강 학생 수")

    class Config:
        json_schema_extra = {
            "example": {
                "schedule_id": 1,
                "class_id": 1,
                "class_name": "중1-A",
                "start_time": "09:00",
                "end_time": "10:00",
                "teacher_name": "김선생",
                "student_count": 15
            }
        }


class DashboardResponse(BaseModel):
    """대시보드 전체 응답"""
    summary: SummaryStats = Field(..., description="전체 요약 통계")
    attendance_rate: AttendanceRate = Field(..., description="출석률")
    recent_activities: List[RecentActivity] = Field(..., description="최근 활동 내역")
    revenue_trend: List[RevenueTrend] = Field(..., description="최근 6개월 매출 추이")
    overdue_assignments: List[OverdueAssignment] = Field(default=[], description="미제출 과제 목록")
    today_schedule: List[TodayScheduleItem] = Field(default=[], description="오늘 수업 스케줄")

    class Config:
        json_schema_extra = {
            "example": {
                "summary": {
                    "total_students": 150,
                    "total_teachers": 8,
                    "monthly_revenue": 45000000,
                    "unpaid_amount": 2500000
                },
                "attendance_rate": {
                    "today": 95.5,
                    "yesterday": 94.0
                },
                "recent_activities": [
                    {
                        "id": 1,
                        "type": "payment",
                        "message": "김철수 학생 1월 수강료 납부",
                        "time": "10:30 AM"
                    },
                    {
                        "id": 2,
                        "type": "join",
                        "message": "신규 학생(이민호) 등록",
                        "time": "11:00 AM"
                    }
                ],
                "revenue_trend": [
                    {"month": "2025-08", "amount": 42000000},
                    {"month": "2025-09", "amount": 43500000},
                    {"month": "2025-10", "amount": 44000000},
                    {"month": "2025-11", "amount": 44500000},
                    {"month": "2025-12", "amount": 43000000},
                    {"month": "2026-01", "amount": 45000000}
                ]
            }
        }
