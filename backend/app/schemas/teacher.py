"""
선생님 관련 Pydantic 스키마
API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List


class TeacherCreate(BaseModel):
    """선생님 등록 요청 스키마 (User + Teacher 동시 생성)"""
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=50)
    subject: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    joinDate: Optional[str] = Field(None, description="입사일 (YYYY-MM-DD)")
    memo: Optional[str] = Field(None)


class TeacherUpdate(BaseModel):
    """선생님 정보 수정 요청 스키마"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    subject: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None, description="active | leave | resigned")
    joinDate: Optional[str] = Field(None, description="입사일 (YYYY-MM-DD)")
    memo: Optional[str] = Field(None)


class ClassAssign(BaseModel):
    """반 배정 요청 스키마"""
    model_config = ConfigDict(populate_by_name=True)
    class_ids: List[int] = Field(..., alias="classIds", description="배정할 반 ID 목록")
