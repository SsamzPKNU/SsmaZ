"""
수납/결제 관련 Pydantic 스키마
API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from enum import Enum


class PaymentMethod(str, Enum):
    """결제 방법"""
    CARD = "CARD"
    CASH = "CASH"
    TRANSFER = "TRANSFER"


class PaymentCreate(BaseModel):
    """수납 항목 생성 요청 스키마"""
    student_id: int = Field(..., description="학생 ID")
    amount: int = Field(..., gt=0, description="납부 금액")
    payment_date: Optional[date] = Field(None, description="납부일")
    next_payment_date: Optional[date] = Field(None, description="다음 납부 예정일")
    method: Optional[PaymentMethod] = Field(None, description="결제 방법 (CARD, CASH)")

    class Config:
        json_schema_extra = {
            "example": {
                "student_id": 1,
                "amount": 300000,
                "payment_date": "2026-01-23",
                "next_payment_date": "2026-02-23",
                "method": "CARD"
            }
        }


class PaymentUpdate(BaseModel):
    """수납 항목 수정 요청 스키마"""
    amount: Optional[int] = Field(None, gt=0, description="납부 금액")
    payment_date: Optional[date] = Field(None, description="납부일")
    next_payment_date: Optional[date] = Field(None, description="다음 납부 예정일")
    method: Optional[PaymentMethod] = Field(None, description="결제 방법 (CARD, CASH)")

    class Config:
        json_schema_extra = {
            "example": {
                "amount": 350000,
                "method": "CASH"
            }
        }


class PaymentResponse(BaseModel):
    """수납 내역 응답 스키마"""
    payment_id: int = Field(..., description="결제 고유 ID")
    student_id: int = Field(..., description="학생 ID")
    student_name: Optional[str] = Field(None, description="학생 이름")
    academy_id: int = Field(..., description="학원 ID")
    amount: int = Field(..., description="납부 금액")
    payment_date: Optional[date] = Field(None, description="납부일")
    next_payment_date: Optional[date] = Field(None, description="다음 납부 예정일")
    method: Optional[str] = Field(None, description="결제 방법")
    created_at: Optional[datetime] = Field(None, description="생성 시간")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "payment_id": 101,
                "student_id": 1,
                "student_name": "김철수",
                "academy_id": 1,
                "amount": 300000,
                "payment_date": "2026-01-23",
                "next_payment_date": "2026-02-23",
                "method": "CARD"
            }
        }


class PaymentNotifyRequest(BaseModel):
    """수납 알림 발송 요청 스키마"""
    title: Optional[str] = Field(None, description="알림 제목 (기본: '수납 안내')")
    body: Optional[str] = Field(None, description="알림 본문 (기본: '수강료 납부 안내가 등록되었습니다')")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "수납 안내",
                "body": "이번 달 수강료 납부를 확인해주세요"
            }
        }


class PaymentListResponse(BaseModel):
    """수납 목록 응답 스키마"""
    payments: list[PaymentResponse] = Field(..., description="수납 목록")
    total: int = Field(..., description="전체 개수")
