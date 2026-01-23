"""
학생 관련 Pydantic 스키마
API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import date, datetime
from enum import Enum


class StudentStatus(str, Enum):
    """학생 상태"""
    ENROLLED = "enrolled"
    PAUSED = "paused"
    GRADUATED = "graduated"


class StudentBase(BaseModel):
    """학생 기본 정보 스키마"""
    name: str = Field(..., min_length=1, max_length=50, description="학생 이름")
    school: Optional[str] = Field(None, max_length=100, description="학교명")
    grade: Optional[str] = Field(None, max_length=20, description="학년 (예: 중1, 고2)")
    phone: Optional[str] = Field(None, max_length=20, description="학생 전화번호")
    parent_phone: str = Field(..., max_length=20, description="학부모 전화번호")
    enrollment_date: Optional[date] = Field(None, description="등록일")


class StudentCreate(StudentBase):
    """학생 등록 요청 스키마 (User 계정 포함)"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="로그인 ID (선택)")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="비밀번호 (선택)")
    
    @validator('username')
    def validate_username(cls, v):
        """username 검증"""
        if v is not None:
            if not v.replace('_', '').isalnum():
                raise ValueError('username은 영문, 숫자, 언더스코어만 사용 가능합니다')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "이학생",
                "school": "행복중",
                "grade": "중2",
                "phone": "010-5555-6666",
                "parent_phone": "010-7777-8888",
                "username": "student_lee",
                "password": "initial_password",
                "enrollment_date": "2026-01-23"
            }
        }


class StudentUpdate(BaseModel):
    """학생 정보 수정 요청 스키마"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="학생 이름")
    school: Optional[str] = Field(None, max_length=100, description="학교명")
    grade: Optional[str] = Field(None, max_length=20, description="학년")
    phone: Optional[str] = Field(None, max_length=20, description="학생 전화번호")
    parent_phone: Optional[str] = Field(None, max_length=20, description="학부모 전화번호")
    enrollment_date: Optional[date] = Field(None, description="등록일")
    status: Optional[StudentStatus] = Field(None, description="학생 상태")
    
    class Config:
        json_schema_extra = {
            "example": {
                "grade": "중3",
                "status": "enrolled"
            }
        }


class StudentResponse(StudentBase):
    """학생 정보 응답 스키마"""
    id: int = Field(..., description="학생 고유 ID")
    status: str = Field(..., description="학생 상태 (enrolled, paused, graduated)")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "김철수",
                "school": "SSamZ중학교",
                "grade": "중1",
                "phone": "010-1111-2222",
                "parent_phone": "010-3333-4444",
                "enrollment_date": "2025-01-10",
                "status": "enrolled"
            }
        }


class StudentListResponse(BaseModel):
    """학생 목록 응답 스키마 (페이지네이션)"""
    total: int = Field(..., description="전체 학생 수")
    page: int = Field(..., description="현재 페이지")
    students: list[StudentResponse] = Field(..., description="학생 목록")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 150,
                "page": 1,
                "students": [
                    {
                        "id": 1,
                        "name": "김철수",
                        "school": "SSamZ중학교",
                        "grade": "중1",
                        "phone": "010-1111-2222",
                        "parent_phone": "010-3333-4444",
                        "enrollment_date": "2025-01-10",
                        "status": "enrolled"
                    }
                ]
            }
        }
