"""
Support 관련 Pydantic 스키마
문의, FAQ, 공지사항 API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


# ============================================
# Enum 정의 (스키마용)
# ============================================

class InquiryStatus(str, Enum):
    """문의 상태"""
    PENDING = "PENDING"
    ANSWERED = "ANSWERED"
    CLOSED = "CLOSED"


class NoticeTarget(str, Enum):
    """공지사항 대상"""
    ALL = "ALL"
    STUDENT = "STUDENT"
    PARENT = "PARENT"
    TEACHER = "TEACHER"


# ============================================
# 문의 (Inquiry) 스키마
# ============================================

class InquiryCreate(BaseModel):
    """문의 생성 요청"""
    title: str = Field(..., min_length=1, max_length=200, description="문의 제목")
    content: str = Field(..., min_length=1, description="문의 내용")


class InquiryAnswer(BaseModel):
    """문의 답변 요청"""
    answer: str = Field(..., min_length=1, description="답변 내용")


class InquiryResponse(BaseModel):
    """문의 응답"""
    inquiry_id: int
    academy_id: int
    user_id: int
    user_name: Optional[str] = None
    title: str
    content: str
    status: str
    answer: Optional[str] = None
    answered_by: Optional[int] = None
    answerer_name: Optional[str] = None
    answered_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InquiryListResponse(BaseModel):
    """문의 목록 응답"""
    total: int
    inquiries: List[InquiryResponse]


# ============================================
# FAQ 스키마
# ============================================

class FAQCreate(BaseModel):
    """FAQ 생성 요청"""
    question: str = Field(..., min_length=1, max_length=500, description="질문")
    answer: str = Field(..., min_length=1, description="답변")
    category: str = Field(default="일반", max_length=50, description="카테고리")
    display_order: int = Field(default=0, ge=0, description="표시 순서")


class FAQUpdate(BaseModel):
    """FAQ 수정 요청"""
    question: Optional[str] = Field(None, min_length=1, max_length=500)
    answer: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, max_length=50)
    display_order: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class FAQResponse(BaseModel):
    """FAQ 응답"""
    faq_id: int
    academy_id: int
    question: str
    answer: str
    category: str
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FAQListResponse(BaseModel):
    """FAQ 목록 응답"""
    total: int
    faqs: List[FAQResponse]


# ============================================
# 공지사항 (Notice) 스키마
# ============================================

class NoticeCreate(BaseModel):
    """공지사항 생성 요청"""
    title: str = Field(..., min_length=1, max_length=200, description="제목")
    content: str = Field(..., min_length=1, description="내용")
    is_pinned: bool = Field(default=False, description="상단 고정 여부")
    target: NoticeTarget = Field(default=NoticeTarget.ALL, description="대상")


class NoticeUpdate(BaseModel):
    """공지사항 수정 요청"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    is_pinned: Optional[bool] = None
    target: Optional[NoticeTarget] = None


class NoticeResponse(BaseModel):
    """공지사항 응답"""
    notice_id: int
    academy_id: int
    title: str
    content: str
    is_pinned: bool
    target: str
    view_count: int
    created_by: Optional[int] = None
    author_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NoticeListResponse(BaseModel):
    """공지사항 목록 응답"""
    total: int
    notices: List[NoticeResponse]
