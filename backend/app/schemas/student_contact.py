"""
학생 연락처 관련 Pydantic 스키마
API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class StudentContactCreate(BaseModel):
    """학생 연락처 등록 요청 스키마"""
    phone: str = Field(..., max_length=20, description="전화번호")
    label: str = Field(..., max_length=50, description="관계 라벨 (엄마, 아빠, 할머니 등)")
    priority: int = Field(default=1, ge=1, description="알림 발송 우선순위 (1이 가장 먼저)")
    is_active: bool = Field(default=True, description="알림 수신 여부")

    class Config:
        json_schema_extra = {
            "example": {
                "phone": "010-1234-5678",
                "label": "엄마",
                "priority": 1,
                "is_active": True
            }
        }


class StudentContactUpdate(BaseModel):
    """학생 연락처 수정 요청 스키마"""
    phone: Optional[str] = Field(None, max_length=20, description="전화번호")
    label: Optional[str] = Field(None, max_length=50, description="관계 라벨")
    priority: Optional[int] = Field(None, ge=1, description="알림 발송 우선순위")
    is_active: Optional[bool] = Field(None, description="알림 수신 여부")

    class Config:
        json_schema_extra = {
            "example": {
                "phone": "010-9999-8888",
                "is_active": False
            }
        }


class StudentContactResponse(BaseModel):
    """학생 연락처 응답 스키마"""
    contact_id: int = Field(..., description="연락처 고유 ID")
    student_id: int = Field(..., description="학생 ID")
    phone: str = Field(..., description="전화번호")
    label: str = Field(..., description="관계 라벨")
    priority: int = Field(..., description="알림 발송 우선순위")
    is_active: bool = Field(..., description="알림 수신 여부")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: Optional[datetime] = Field(None, description="수정 시간")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "contact_id": 1,
                "student_id": 10,
                "phone": "010-1234-5678",
                "label": "엄마",
                "priority": 1,
                "is_active": True,
                "created_at": "2026-01-27T10:00:00",
                "updated_at": None
            }
        }


class StudentContactListResponse(BaseModel):
    """학생 연락처 목록 응답 스키마"""
    contacts: List[StudentContactResponse] = Field(..., description="연락처 목록")
    total: int = Field(..., description="전체 연락처 수")

    class Config:
        json_schema_extra = {
            "example": {
                "contacts": [
                    {
                        "contact_id": 1,
                        "student_id": 10,
                        "phone": "010-1234-5678",
                        "label": "엄마",
                        "priority": 1,
                        "is_active": True,
                        "created_at": "2026-01-27T10:00:00",
                        "updated_at": None
                    }
                ],
                "total": 1
            }
        }
