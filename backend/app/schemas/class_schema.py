"""
클래스(반/수업) 관련 Pydantic 스키마
API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, Field
from typing import Optional


class ClassBase(BaseModel):
    """클래스 기본 정보 스키마"""
    name: str = Field(..., min_length=1, max_length=100, description="반 이름")
    teacher_id: Optional[int] = Field(None, description="담당 선생님 ID")
    schedule: Optional[str] = Field(None, max_length=100, description="수업 일정")
    capacity: Optional[int] = Field(None, gt=0, description="정원")


class ClassCreate(ClassBase):
    """클래스 생성 요청 스키마"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "영어 특강반",
                "teacher_id": 10,
                "schedule": "토 10:00",
                "capacity": 20
            }
        }


class ClassUpdate(BaseModel):
    """클래스 정보 수정 요청 스키마"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="반 이름")
    teacher_id: Optional[int] = Field(None, description="담당 선생님 ID")
    schedule: Optional[str] = Field(None, max_length=100, description="수업 일정")
    capacity: Optional[int] = Field(None, gt=0, description="정원")
    
    class Config:
        json_schema_extra = {
            "example": {
                "schedule": "화/목 17:00",
                "capacity": 25
            }
        }


class ClassResponse(ClassBase):
    """클래스 정보 응답 스키마"""
    id: int = Field(..., description="반 고유 ID")
    teacher_name: Optional[str] = Field(None, description="담당 선생님 이름")
    current_students: int = Field(default=0, description="현재 학생 수")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "수학 정규반 A",
                "teacher_id": 10,
                "teacher_name": "박선생",
                "schedule": "월/수/금 16:00",
                "capacity": 15,
                "current_students": 12
            }
        }


class ClassDetailResponse(ClassResponse):
    """클래스 상세 정보 응답 스키마"""
    students: list = Field(default=[], description="소속 학생 목록")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "수학 정규반 A",
                "teacher_id": 10,
                "teacher_name": "박선생",
                "schedule": "월/수/금 16:00",
                "capacity": 15,
                "current_students": 12,
                "students": [
                    {"id": 1, "name": "김철수"},
                    {"id": 2, "name": "이영희"}
                ]
            }
        }
