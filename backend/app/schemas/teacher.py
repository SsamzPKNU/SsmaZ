"""
선생님 관련 Pydantic 스키마
API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import date, datetime
from enum import Enum


class TeacherStatus(str, Enum):
    """선생님 상태"""
    ACTIVE = "active"
    LEAVE = "leave"
    RESIGNED = "resigned"


class TeacherBase(BaseModel):
    """선생님 기본 정보 스키마"""
    name: str = Field(..., min_length=1, max_length=50, description="선생님 이름")
    subject: Optional[str] = Field(None, max_length=50, description="담당 과목")
    phone: Optional[str] = Field(None, max_length=20, description="전화번호")
    email: Optional[EmailStr] = Field(None, description="이메일")
    join_date: Optional[date] = Field(None, description="입사일")


class TeacherCreate(TeacherBase):
    """선생님 등록 요청 스키마"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "새선생",
                "subject": "영어",
                "phone": "010-9999-8888",
                "email": "new@ssamz.com",
                "join_date": "2026-02-01"
            }
        }


class TeacherUpdate(BaseModel):
    """선생님 정보 수정 요청 스키마"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="선생님 이름")
    subject: Optional[str] = Field(None, max_length=50, description="담당 과목")
    phone: Optional[str] = Field(None, max_length=20, description="전화번호")
    email: Optional[EmailStr] = Field(None, description="이메일")
    join_date: Optional[date] = Field(None, description="입사일")
    status: Optional[TeacherStatus] = Field(None, description="재직 상태")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "박선생",
                "subject": "수학",
                "phone": "010-1234-5678",
                "email": "park@ssamz.com",
                "status": "active"
            }
        }


class TeacherResponse(TeacherBase):
    """선생님 정보 응답 스키마"""
    id: int = Field(..., description="선생님 고유 ID")
    status: str = Field(..., description="재직 상태 (active, leave, resigned)")
    assigned_classes: int = Field(default=0, description="담당 반 수")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 10,
                "name": "박선생",
                "subject": "수학",
                "phone": "010-1234-5678",
                "email": "park@ssamz.com",
                "join_date": "2024-03-01",
                "status": "active",
                "assigned_classes": 3
            }
        }


class TeacherListResponse(BaseModel):
    """선생님 목록 응답 스키마"""
    teachers: list[TeacherResponse] = Field(..., description="선생님 목록")
    total: int = Field(..., description="전체 선생님 수")
    
    class Config:
        json_schema_extra = {
            "example": {
                "teachers": [
                    {
                        "id": 10,
                        "name": "박선생",
                        "subject": "수학",
                        "phone": "010-1234-5678",
                        "email": "park@ssamz.com",
                        "join_date": "2024-03-01",
                        "status": "active",
                        "assigned_classes": 3
                    }
                ],
                "total": 1
            }
        }
