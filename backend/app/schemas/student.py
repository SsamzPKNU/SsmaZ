"""
학생 관련 Pydantic 스키마
API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class StudentStatus(str, Enum):
    """학생 상태"""
    ENROLLED = "재원"
    PAUSED = "휴원"
    GRADUATED = "졸업"


class StudentCreate(BaseModel):
    """학생 등록 요청 스키마"""
    name: str = Field(..., min_length=1, max_length=50, description="학생 이름")
    parent_phone: str = Field(..., max_length=20, description="학부모 전화번호")
    class_id: Optional[int] = Field(None, description="반 ID")
    status: Optional[StudentStatus] = Field(StudentStatus.ENROLLED, description="학생 상태")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "김철수",
                "parent_phone": "010-1234-5678",
                "class_id": 1,
                "status": "재원"
            }
        }


class StudentUpdate(BaseModel):
    """학생 정보 수정 요청 스키마"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="학생 이름")
    parent_phone: Optional[str] = Field(None, max_length=20, description="학부모 전화번호")
    class_id: Optional[int] = Field(None, description="반 ID")
    status: Optional[StudentStatus] = Field(None, description="학생 상태")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "김철수",
                "status": "휴원"
            }
        }


class StudentResponse(BaseModel):
    """학생 정보 응답 스키마"""
    student_id: int = Field(..., description="학생 고유 ID")
    academy_id: int = Field(..., description="학원 ID")
    class_id: Optional[int] = Field(None, description="반 ID")
    name: str = Field(..., description="학생 이름")
    parent_phone: str = Field(..., description="학부모 전화번호")
    status: Optional[str] = Field(None, description="학생 상태 (재원, 휴원, 졸업)")
    regdate: Optional[datetime] = Field(None, description="등록 시간")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "student_id": 1,
                "academy_id": 1,
                "class_id": 1,
                "name": "김철수",
                "parent_phone": "010-1234-5678",
                "status": "재원",
                "regdate": "2026-01-23T10:00:00"
            }
        }


class StudentListResponse(BaseModel):
    """학생 목록 응답 스키마"""
    total: int = Field(..., description="전체 학생 수")
    students: list[StudentResponse] = Field(..., description="학생 목록")
