"""
선생님 메시지 센터 스키마
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MessageTargetType(str, Enum):
    """메시지 대상 유형"""
    PARENTS = "parents"
    STUDENTS = "students"
    CLASS = "class"


# ========== 템플릿 스키마 ==========

class TemplateCreateRequest(BaseModel):
    """템플릿 생성 요청"""
    name: str = Field(..., min_length=1, max_length=100, description="템플릿 이름")
    content: str = Field(..., min_length=1, description="템플릿 내용")


class TemplateUpdateRequest(BaseModel):
    """템플릿 수정 요청"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="템플릿 이름")
    content: Optional[str] = Field(None, min_length=1, description="템플릿 내용")


class TemplateResponse(BaseModel):
    """템플릿 응답"""
    template_id: int
    name: str
    content: str
    is_shared: bool = Field(description="학원 공용 여부")
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    """템플릿 목록 응답"""
    items: List[TemplateResponse]
    total: int


# ========== 메시지 발송 스키마 ==========

class MessageSendRequest(BaseModel):
    """메시지 발송 요청"""
    target_type: MessageTargetType = Field(..., description="대상 유형 (parents, students, class)")
    target_ids: List[int] = Field(..., min_length=1, description="대상 ID 목록 (학생 ID 또는 반 ID)")
    title: str = Field(..., min_length=1, max_length=200, description="메시지 제목")
    content: str = Field(..., min_length=1, description="메시지 내용")
    template_id: Optional[int] = Field(None, description="사용한 템플릿 ID (선택)")


class MessageSendResponse(BaseModel):
    """메시지 발송 응답"""
    message_id: int
    sent_count: int
    success_count: int
    fail_count: int
    status: str


class MessageHistoryItem(BaseModel):
    """메시지 발송 내역 항목"""
    message_id: int
    title: str
    content: str
    target_type: str
    sent_count: int
    success_count: int
    fail_count: int
    status: str
    sent_at: Optional[datetime] = None
    created_at: datetime


class MessageHistoryResponse(BaseModel):
    """메시지 발송 내역 응답"""
    items: List[MessageHistoryItem]
    total: int
    page: int
    page_size: int


# ========== 연락처 스키마 ==========

class ContactItem(BaseModel):
    """연락처 항목"""
    student_id: int
    student_name: str
    grade: Optional[str] = None
    school: Optional[str] = None
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    phone: Optional[str] = None
    parent_phone: Optional[str] = None


class ContactListResponse(BaseModel):
    """연락처 목록 응답"""
    items: List[ContactItem]
    total: int
