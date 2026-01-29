"""
Invoice 관련 Pydantic 스키마
청구서 API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from enum import Enum


class InvoiceStatus(str, Enum):
    """청구서 상태"""
    PENDING = "PENDING"
    SENT = "SENT"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


class InvoiceCreate(BaseModel):
    """청구서 단건 생성 요청"""
    student_id: int = Field(..., description="학생 ID")
    amount: int = Field(..., gt=0, description="청구 금액 (원)")
    description: Optional[str] = Field(None, max_length=500, description="청구 내역 설명")
    due_date: date = Field(..., description="납부 기한")


class InvoiceBulkCreate(BaseModel):
    """청구서 일괄 생성 요청"""
    student_ids: List[int] = Field(..., min_length=1, description="학생 ID 목록")
    amount: int = Field(..., gt=0, description="청구 금액 (원)")
    description: Optional[str] = Field(None, max_length=500, description="청구 내역 설명")
    due_date: date = Field(..., description="납부 기한")


class InvoiceSendRequest(BaseModel):
    """청구서 발송 요청"""
    invoice_ids: List[int] = Field(..., min_length=1, description="청구서 ID 목록")


class InvoiceMarkPaidRequest(BaseModel):
    """청구서 납부 완료 처리 요청"""
    payment_id: Optional[int] = Field(None, description="연결할 결제 ID")


class InvoiceResponse(BaseModel):
    """청구서 응답"""
    invoice_id: int
    academy_id: int
    student_id: int
    student_name: Optional[str] = None
    amount: int
    description: Optional[str] = None
    due_date: date
    status: str
    sent_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    payment_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    """청구서 목록 응답"""
    total: int
    invoices: List[InvoiceResponse]


class InvoiceBulkCreateResponse(BaseModel):
    """청구서 일괄 생성 응답"""
    success_count: int
    invoices: List[InvoiceResponse]


class InvoiceSendResponse(BaseModel):
    """청구서 발송 응답"""
    sent_count: int
    failed_count: int
    failed_ids: List[int] = []
