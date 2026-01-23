"""
토스페이먼츠 연동 API 라우터
결제 조회, 취소 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.toss_payment_client import TossPaymentClient
from pydantic import BaseModel, Field
from typing import Optional


# API 라우터 생성
router = APIRouter(
    prefix="/api/admin/toss",
    tags=["토스페이먼츠 연동"]
)


# ==================== 스키마 ====================

class TossPaymentDetail(BaseModel):
    """토스페이먼츠 결제 상세 정보"""
    paymentKey: str
    orderId: str
    orderName: str
    status: str
    method: str
    totalAmount: int
    balanceAmount: int
    requestedAt: str
    approvedAt: Optional[str] = None


class RefundAccountInfo(BaseModel):
    """환불 계좌 정보"""
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
    success: bool
    message: str
    paymentKey: Optional[str] = None
    canceledAmount: Optional[int] = None
    canceledAt: Optional[str] = None


# ==================== API 엔드포인트 ====================

@router.get("/payments/{payment_key}", response_model=TossPaymentDetail)
async def get_toss_payment(
    payment_key: str,
    current_user: User = Depends(get_current_user)
):
    """
    토스페이먼츠 결제 조회
    
    토스페이먼츠 API를 통해 결제 상세 정보를 조회합니다.
    
    **주의**: 테스트 환경에서는 테스트 시크릿 키로 생성된 결제만 조회 가능합니다.
    
    Path Parameters:
        - payment_key: 토스페이먼츠 결제 키
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        TossPaymentDetail: 토스페이먼츠 결제 상세 정보
    
    Raises:
        404: 결제를 찾을 수 없는 경우
        503: 토스페이먼츠 API 연결 실패
    
    사용 예시:
        GET /api/admin/toss/payments/payment_key_abc123
    """
    client = TossPaymentClient()
    payment_data = await client.get_payment(payment_key)
    
    return TossPaymentDetail(**payment_data)


@router.post("/payments/{payment_key}/cancel", response_model=PaymentCancelResponse)
async def cancel_toss_payment(
    payment_key: str,
    cancel_request: PaymentCancelRequest,
    current_user: User = Depends(get_current_user)
):
    """
    토스페이먼츠 결제 취소/환불
    
    토스페이먼츠 API를 통해 결제를 취소하고 환불 처리합니다.
    
    **취소 유형**:
    - 전액 취소: cancelAmount를 지정하지 않음
    - 부분 취소: cancelAmount를 지정
    - 가상계좌 환불: refundReceiveAccount 필수
    
    **주의사항**:
    - 이미 취소된 결제는 다시 취소할 수 없습니다
    - 취소 가능 금액을 초과하면 실패합니다
    - 가상계좌 결제는 환불 계좌 정보가 필수입니다
    
    Path Parameters:
        - payment_key: 토스페이먼츠 결제 키
    
    Request Body:
        - cancelReason: 취소 사유 (필수)
        - cancelAmount: 취소 금액 (부분 취소 시)
        - refundReceiveAccount: 환불 계좌 정보 (가상계좌 환불 시 필수)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        PaymentCancelResponse: 취소 결과 정보
    
    Raises:
        400: 이미 취소된 결제, 취소 불가능한 결제 등
        404: 결제를 찾을 수 없는 경우
        503: 토스페이먼츠 API 연결 실패
    
    사용 예시:
        POST /api/admin/toss/payments/payment_key_abc123/cancel
        
        전액 취소:
        {
            "cancelReason": "고객 요청"
        }
        
        부분 취소:
        {
            "cancelReason": "부분 환불",
            "cancelAmount": 10000
        }
        
        가상계좌 환불:
        {
            "cancelReason": "환불 요청",
            "refundReceiveAccount": {
                "bank": "88",
                "accountNumber": "1002345678901",
                "holderName": "홍길동"
            }
        }
    """
    client = TossPaymentClient()
    
    # 환불 계좌 정보를 dict로 변환
    refund_account = None
    if cancel_request.refundReceiveAccount:
        refund_account = cancel_request.refundReceiveAccount.dict()
    
    # 토스페이먼츠 API 호출
    result = await client.cancel_payment(
        payment_key=payment_key,
        cancel_reason=cancel_request.cancelReason,
        cancel_amount=cancel_request.cancelAmount,
        refund_account=refund_account
    )
    
    # 취소 성공 응답
    return PaymentCancelResponse(
        success=True,
        message="결제가 성공적으로 취소되었습니다",
        paymentKey=result.get("paymentKey"),
        canceledAmount=result.get("cancels", [{}])[-1].get("cancelAmount") if result.get("cancels") else None,
        canceledAt=result.get("cancels", [{}])[-1].get("canceledAt") if result.get("cancels") else None
    )
