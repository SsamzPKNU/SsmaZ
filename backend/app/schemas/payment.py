"""
수납/결제 관련 Pydantic 스키마
API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from enum import Enum


class PaymentStatus(str, Enum):
    """결제 상태"""
    UNPAID = "unpaid"
    PAID = "paid"
    OVERDUE = "overdue"


class PaymentMethod(str, Enum):
    """결제 방법"""
    CARD = "card"
    CASH = "cash"
    TRANSFER = "transfer"


class PaymentConfirm(BaseModel):
    """수납 처리 요청 스키마"""
    method: PaymentMethod = Field(..., description="결제 방법 (card, cash, transfer)")
    paid_date: date = Field(..., description="납부일")
    memo: Optional[str] = Field(None, description="메모")
    
    class Config:
        json_schema_extra = {
            "example": {
                "method": "card",
                "paid_date": "2026-01-22",
                "memo": "방문 카드 결제"
            }
        }


class PaymentCreate(BaseModel):
    """수납 항목 생성 요청 스키마"""
    student_id: int = Field(..., description="학생 ID")
    amount: int = Field(..., gt=0, description="납부 금액")
    due_date: date = Field(..., description="납부 기한일")
    memo: Optional[str] = Field(None, description="메모")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": 1,
                "amount": 300000,
                "due_date": "2026-02-05",
                "memo": "2월 수강료"
            }
        }


class PaymentResponse(BaseModel):
    """수납 내역 응답 스키마"""
    id: int = Field(..., description="결제 고유 ID")
    student_name: str = Field(..., description="학생 이름")
    parent_phone: str = Field(..., description="학부모 전화번호")
    amount: int = Field(..., description="납부 금액")
    due_date: date = Field(..., description="납부 기한일")
    status: str = Field(..., description="결제 상태")
    last_reminded: Optional[date] = Field(None, description="마지막 독촉일")
    paid_date: Optional[date] = Field(None, description="실제 납부일")
    method: Optional[str] = Field(None, description="결제 방법")
    memo: Optional[str] = Field(None, description="메모")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 101,
                "student_name": "최미납",
                "parent_phone": "010-xxxx-xxxx",
                "amount": 300000,
                "due_date": "2026-01-05",
                "status": "unpaid",
                "last_reminded": "2026-01-10"
            }
        }


class PaymentSummary(BaseModel):
    """월별 수납 현황 요약"""
    month: str = Field(..., description="대상 월 (YYYY-MM)")
    total_expected: int = Field(..., description="예상 총액 (원)")
    total_collected: int = Field(..., description="실제 수납액 (원)")
    collection_rate: float = Field(..., description="수납률 (%)")
    unpaid_count: int = Field(..., description="미납 인원 수")
    
    class Config:
        json_schema_extra = {
            "example": {
                "month": "2026-01",
                "total_expected": 50000000,
                "total_collected": 45000000,
                "collection_rate": 90.0,
                "unpaid_count": 15
            }
        }
