"""
선생님 메시지 센터 스키마
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class TemplateCategoryEnum(str, Enum):
    """템플릿 카테고리 (스키마용)"""
    ATTENDANCE = "출석"
    EXAM = "시험"
    GRADE = "성적"
    ASSIGNMENT = "과제"
    NOTICE = "공지"
    GENERAL = "일반"


class MessageTypeEnum(str, Enum):
    """메시지 유형 (스키마용)"""
    NORMAL = "normal"
    URGENT = "urgent"
    NOTICE = "notice"


# ========== 템플릿 스키마 ==========

class TemplateCreateRequest(BaseModel):
    """템플릿 생성 요청"""
    name: str = Field(..., min_length=1, max_length=100, description="템플릿 이름")
    content: str = Field(..., min_length=1, description="템플릿 내용")
    category: TemplateCategoryEnum = Field(..., description="템플릿 카테고리")


class TemplateUpdateRequest(BaseModel):
    """템플릿 수정 요청"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="템플릿 이름")
    content: Optional[str] = Field(None, min_length=1, description="템플릿 내용")
    category: Optional[TemplateCategoryEnum] = Field(None, description="템플릿 카테고리")


class TemplateResponse(BaseModel):
    """템플릿 응답"""
    id: int = Field(description="템플릿 ID")
    name: str
    content: str
    category: Optional[str] = None
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
    class_id: int = Field(..., description="대상 반 ID")
    student_ids: List[int] = Field(..., min_length=1, description="대상 학생 ID 목록")
    type: MessageTypeEnum = Field(..., description="메시지 유형 (normal, urgent, notice)")
    content: str = Field(..., min_length=1, description="메시지 내용")
    template_id: Optional[int] = Field(None, description="사용한 템플릿 ID (선택)")


class SendResultItem(BaseModel):
    """발송 결과 항목"""
    student_id: int
    status: str
    error: Optional[str] = None


class MessageSendResponse(BaseModel):
    """메시지 발송 응답"""
    message: str
    sent_count: int
    failed_count: int
    results: List[SendResultItem]


# ========== 히스토리 스키마 ==========

class RecipientItem(BaseModel):
    """수신자 항목"""
    student_id: int
    student_name: str
    parent_phone: Optional[str] = None
    status: str


class MessageHistoryItem(BaseModel):
    """메시지 발송 내역 항목"""
    id: int
    type: str
    content: str
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    recipients: List[RecipientItem] = []
    sent_at: Optional[datetime] = None
    sent_count: int
    failed_count: int


class MessageHistoryResponse(BaseModel):
    """메시지 발송 내역 응답"""
    items: List[MessageHistoryItem]
    total: int
    page: int
    limit: int


# ========== 연락처 스키마 ==========

class ContactItem(BaseModel):
    """연락처 항목"""
    student_id: int
    student_name: str
    parent_phone: Optional[str] = None


class ContactListResponse(BaseModel):
    """연락처 목록 응답"""
    items: List[ContactItem]
    total: int
