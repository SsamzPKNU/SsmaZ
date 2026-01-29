"""
토스페이먼츠 학생 결제 관련 Pydantic 스키마
결제 주문 요청/승인 API용
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from enum import Enum


class PaymentStatusEnum(str, Enum):
    """결제 상태"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CANCELED = "CANCELED"
    FAILED = "FAILED"


# ========== 결제 주문 요청/응답 ==========

class PaymentOrderRequest(BaseModel):
    """결제 주문 요청 스키마"""
    invoice_id: int = Field(..., description="청구서 ID")

    class Config:
        json_schema_extra = {
            "example": {
                "invoice_id": 1
            }
        }


class PaymentOrderResponse(BaseModel):
    """결제 주문 응답 스키마 (프론트에서 토스 SDK 호출에 사용)"""
    order_id: str = Field(..., description="토스페이먼츠 주문 ID")
    amount: int = Field(..., description="결제 금액")
    order_name: str = Field(..., description="주문명 (청구 내역)")
    customer_name: str = Field(..., description="결제자 이름 (학생명)")
    success_url: str = Field(..., description="결제 성공 시 리다이렉트 URL")
    fail_url: str = Field(..., description="결제 실패 시 리다이렉트 URL")

    class Config:
        json_schema_extra = {
            "example": {
                "order_id": "ORDER_20260129_abc123",
                "amount": 300000,
                "order_name": "2026년 1월 수강료",
                "customer_name": "김철수",
                "success_url": "https://example.com/payment/success",
                "fail_url": "https://example.com/payment/fail"
            }
        }


# ========== 결제 승인 요청/응답 ==========

class PaymentConfirmRequest(BaseModel):
    """결제 승인 요청 스키마 (토스 리다이렉트 후 호출)"""
    payment_key: str = Field(..., description="토스페이먼츠 결제 키")
    order_id: str = Field(..., description="주문 ID")
    amount: int = Field(..., description="결제 금액")

    class Config:
        json_schema_extra = {
            "example": {
                "payment_key": "tgen_202601291234567890",
                "order_id": "ORDER_20260129_abc123",
                "amount": 300000
            }
        }


class PaymentConfirmResponse(BaseModel):
    """결제 승인 응답 스키마"""
    success: bool = Field(..., description="성공 여부")
    payment_id: int = Field(..., description="결제 ID")
    payment_key: str = Field(..., description="토스페이먼츠 결제 키")
    order_id: str = Field(..., description="주문 ID")
    amount: int = Field(..., description="결제 금액")
    status: str = Field(..., description="결제 상태")
    approved_at: Optional[datetime] = Field(None, description="결제 승인 시간")
    message: str = Field(..., description="결과 메시지")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "payment_id": 101,
                "payment_key": "tgen_202601291234567890",
                "order_id": "ORDER_20260129_abc123",
                "amount": 300000,
                "status": "DONE",
                "approved_at": "2026-01-29T10:30:00",
                "message": "결제가 완료되었습니다"
            }
        }


# ========== 결제 가능 청구서 조회 ==========

class PayableInvoice(BaseModel):
    """결제 가능한 청구서 스키마"""
    invoice_id: int = Field(..., description="청구서 ID")
    student_id: int = Field(..., description="학생 ID")
    student_name: str = Field(..., description="학생 이름")
    amount: int = Field(..., description="청구 금액")
    description: Optional[str] = Field(None, description="청구 내역")
    due_date: date = Field(..., description="납부 기한")
    status: str = Field(..., description="청구서 상태")
    is_overdue: bool = Field(..., description="연체 여부")
    created_at: datetime = Field(..., description="생성 시간")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "invoice_id": 1,
                "student_id": 10,
                "student_name": "김철수",
                "amount": 300000,
                "description": "2026년 1월 수강료",
                "due_date": "2026-01-31",
                "status": "SENT",
                "is_overdue": False,
                "created_at": "2026-01-01T09:00:00"
            }
        }


class PayableInvoicesResponse(BaseModel):
    """결제 가능한 청구서 목록 응답"""
    invoices: List[PayableInvoice] = Field(..., description="청구서 목록")
    total: int = Field(..., description="전체 개수")
    total_amount: int = Field(..., description="전체 미납 금액")


# ========== 결제 내역 조회 ==========

class PaymentHistoryItem(BaseModel):
    """결제 내역 항목 스키마"""
    payment_id: int = Field(..., description="결제 ID")
    student_id: int = Field(..., description="학생 ID")
    student_name: str = Field(..., description="학생 이름")
    amount: int = Field(..., description="결제 금액")
    status: Optional[str] = Field(None, description="결제 상태")
    method: Optional[str] = Field(None, description="결제 방법")
    payment_date: Optional[date] = Field(None, description="결제일")
    order_id: Optional[str] = Field(None, description="주문 ID")
    invoice_description: Optional[str] = Field(None, description="청구 내역")
    created_at: datetime = Field(..., description="생성 시간")

    class Config:
        from_attributes = True


class PaymentHistoryResponse(BaseModel):
    """결제 내역 목록 응답"""
    payments: List[PaymentHistoryItem] = Field(..., description="결제 내역 목록")
    total: int = Field(..., description="전체 개수")
