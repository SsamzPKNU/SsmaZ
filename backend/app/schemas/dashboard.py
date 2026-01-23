"""
대시보드 관련 Pydantic 스키마
API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


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


class DashboardResponse(BaseModel):
    """대시보드 전체 응답"""
    summary: SummaryStats = Field(..., description="전체 요약 통계")
    attendance_rate: AttendanceRate = Field(..., description="출석률")
    recent_activities: List[RecentActivity] = Field(..., description="최근 활동 내역")
    revenue_trend: List[RevenueTrend] = Field(..., description="최근 6개월 매출 추이")

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
