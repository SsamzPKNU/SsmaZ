"""
Schedule 관련 Pydantic 스키마
시간표 API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import time, datetime


class ScheduleCreate(BaseModel):
    """시간표 생성 요청 스키마"""
    day_of_week: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="요일 (월, 화, 수, 목, 금, 토, 일)"
    )
    start_time: time = Field(..., description="시작 시간")
    end_time: time = Field(..., description="종료 시간")

    class Config:
        json_schema_extra = {
            "example": {
                "day_of_week": "월",
                "start_time": "16:00:00",
                "end_time": "18:00:00"
            }
        }


class ScheduleUpdate(BaseModel):
    """시간표 수정 요청 스키마"""
    day_of_week: Optional[str] = Field(None, min_length=1, max_length=10, description="요일 (월, 화, 수, 목, 금, 토, 일)")
    start_time: Optional[time] = Field(None, description="시작 시간")
    end_time: Optional[time] = Field(None, description="종료 시간")

    class Config:
        json_schema_extra = {
            "example": {
                "day_of_week": "화",
                "start_time": "17:00:00",
                "end_time": "19:00:00"
            }
        }


class ScheduleResponse(BaseModel):
    """시간표 응답 스키마"""
    schedule_id: int = Field(..., description="시간표 고유 ID")
    class_id: int = Field(..., description="반 ID")
    day_of_week: str = Field(..., description="요일")
    start_time: time = Field(..., description="시작 시간")
    end_time: time = Field(..., description="종료 시간")
    created_at: datetime = Field(..., description="생성 시간")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "schedule_id": 1,
                "class_id": 1,
                "day_of_week": "월",
                "start_time": "16:00:00",
                "end_time": "18:00:00",
                "created_at": "2025-01-28T10:00:00"
            }
        }


class ScheduleListResponse(BaseModel):
    """시간표 목록 응답 스키마"""
    items: List[ScheduleResponse]
    total: int = Field(..., description="총 시간표 수")
