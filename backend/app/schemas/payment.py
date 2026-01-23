"""
<<<<<<< Updated upstream
결제 관련 Pydantic 스키마
API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from enum import Enum


class PaymentMethodEnum(str, Enum):
    """결제 수단"""
    CARD = "CARD"
    TRANSFER = "TRANSFER"
    CASH = "CASH"
    VIRTUAL_ACCOUNT = "VIRTUAL_ACCOUNT"


class PaymentStatusEnum(str, Enum):
    """
    토스페이먼츠 결제 상태
    """
    READY = "READY"  # 결제 대기
    IN_PROGRESS = "IN_PROGRESS"  # 결제 진행 중
    WAITING_FOR_DEPOSIT = "WAITING_FOR_DEPOSIT"  # 입금 대기 (가상계좌)
    DONE = "DONE"  # 결제 완료
    CANCELED = "CANCELED"  # 결제 취소
    PARTIAL_CANCELED = "PARTIAL_CANCELED"  # 부분 취소
    ABORTED = "ABORTED"  # 결제 중단
    EXPIRED = "EXPIRED"  # 결제 만료


# ==================== 결제 조회 ====================

class PaymentResponse(BaseModel):
    """결제 정보 응답 (DB 조회)"""
    payment_id: int = Field(..., description="결제 ID")
    student_id: int = Field(..., description="학생 ID")
    academy_id: int = Field(..., description="학원 ID")
    amount: Decimal = Field(..., description="결제 금액")
    payment_date: Optional[date] = Field(None, description="결제일")
    next_payment_date: Optional[date] = Field(None, description="다음 결제 예정일")
    method: Optional[str] = Field(None, description="결제 수단")
    created_at: datetime = Field(..., description="생성 시간")
    
    class Config:
        from_attributes = True  # Pydantic v2 (ORM 모드)


class PaymentListResponse(BaseModel):
    """결제 목록 응답"""
    total: int = Field(..., description="전체 결제 건수")
    payments: List[PaymentResponse] = Field(..., description="결제 목록")


# ==================== 토스페이먼츠 API ====================

class TossPaymentDetail(BaseModel):
    """토스페이먼츠 결제 상세 정보 (API 응답)"""
    paymentKey: str = Field(..., description="토스 결제 키")
    orderId: str = Field(..., description="주문 ID")
    orderName: str = Field(..., description="주문명")
    status: PaymentStatusEnum = Field(..., description="결제 상태")
    method: str = Field(..., description="결제 수단")
    totalAmount: int = Field(..., description="총 결제 금액")
    balanceAmount: int = Field(..., description="취소 가능 금액")
    requestedAt: str = Field(..., description="결제 요청 시간")
    approvedAt: Optional[str] = Field(None, description="결제 승인 시간")
    receipt: Optional[dict] = Field(None, description="영수증 정보")
    cancels: Optional[List[dict]] = Field(None, description="취소 내역")


class RefundAccountInfo(BaseModel):
    """환불 계좌 정보 (가상계좌 환불 시 필요)"""
    bank: str = Field(..., description="은행 코드", example="88")
    accountNumber: str = Field(..., description="계좌번호", example="1002345678901")
    holderName: str = Field(..., description="예금주명", example="홍길동")


class PaymentCancelRequest(BaseModel):
    """결제 취소 요청"""
    cancelReason: str = Field(..., description="취소 사유", min_length=1, max_length=200)
    cancelAmount: Optional[int] = Field(None, description="취소 금액 (부분 취소 시)", gt=0)
    refundReceiveAccount: Optional[RefundAccountInfo] = Field(
        None, 
        description="환불 계좌 정보 (가상계좌 환불 시 필수)"
    )


class PaymentCancelResponse(BaseModel):
    """결제 취소 응답"""
    success: bool = Field(..., description="취소 성공 여부")
    message: str = Field(..., description="응답 메시지")
    paymentKey: Optional[str] = Field(None, description="결제 키")
    canceledAmount: Optional[int] = Field(None, description="취소된 금액")
    canceledAt: Optional[str] = Field(None, description="취소 시간")


# ==================== 필터링 ====================

class PaymentFilterParams(BaseModel):
    """결제 목록 필터링 파라미터"""
    academy_id: Optional[int] = Field(None, description="학원 ID")
    student_id: Optional[int] = Field(None, description="학생 ID")
    method: Optional[PaymentMethodEnum] = Field(None, description="결제 수단")
    start_date: Optional[date] = Field(None, description="시작일 (payment_date 기준)")
    end_date: Optional[date] = Field(None, description="종료일 (payment_date 기준)")
    limit: int = Field(100, description="조회 개수", ge=1, le=1000)
    offset: int = Field(0, description="오프셋", ge=0)
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        """종료일이 시작일보다 이전인지 검증"""
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('종료일은 시작일보다 이후여야 합니다')
        return v
=======
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
>>>>>>> Stashed changes
