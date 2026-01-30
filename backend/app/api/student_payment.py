"""
학생 결제 API 라우터
토스페이먼츠를 통한 학생/학부모 결제 엔드포인트
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.services.student_payment_service import StudentPaymentService
from app.schemas.toss_payment import (
    PaymentOrderRequest,
    PaymentOrderResponse,
    PaymentConfirmRequest,
    PaymentConfirmResponse,
    PayableInvoicesResponse,
    PaymentHistoryResponse
)

router = APIRouter(
    prefix="/api/payment",
    tags=["Student Payment"]
)


@router.get(
    "/invoices",
    response_model=PayableInvoicesResponse,
    summary="결제 가능한 청구서 목록 조회",
    description="현재 사용자에게 연결된 학생들의 미납 청구서 목록을 조회합니다."
)
async def get_payable_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    결제 가능한 청구서 목록 조회

    - 사용자에게 연결된 학생들의 청구서만 조회
    - PENDING, SENT, OVERDUE 상태의 청구서만 포함
    - 납부 기한 순으로 정렬
    """
    service = StudentPaymentService(db)
    result = service.get_payable_invoices(current_user)

    return PayableInvoicesResponse(
        invoices=result["invoices"],
        total=result["total"],
        total_amount=result["total_amount"]
    )


@router.post(
    "/request",
    response_model=PaymentOrderResponse,
    summary="결제 주문 생성",
    description="청구서에 대한 결제 주문을 생성하고, 토스 SDK 호출에 필요한 정보를 반환합니다."
)
async def create_payment_order(
    request: PaymentOrderRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    결제 주문 생성

    1. 청구서 유효성 및 권한 검증
    2. 주문 ID 생성
    3. PENDING 상태의 Payment 레코드 생성
    4. 프론트에서 토스 SDK 호출에 필요한 정보 반환

    프론트엔드에서는 반환된 정보로 토스 결제창을 호출합니다:
    ```javascript
    tossPayments.requestPayment('카드', {
        amount: response.amount,
        orderId: response.order_id,
        orderName: response.order_name,
        customerName: response.customer_name,
        successUrl: response.success_url,
        failUrl: response.fail_url
    });
    ```
    """
    service = StudentPaymentService(db)
    result = service.create_payment_order(current_user, request.invoice_id)

    return PaymentOrderResponse(
        order_id=result["order_id"],
        amount=result["amount"],
        order_name=result["order_name"],
        customer_name=result["customer_name"],
        success_url=result["success_url"],
        fail_url=result["fail_url"]
    )


@router.post(
    "/confirm",
    response_model=PaymentConfirmResponse,
    summary="결제 승인",
    description="토스 결제 완료 후 결제를 최종 승인합니다."
)
async def confirm_payment(
    request: PaymentConfirmRequest,
    db: Session = Depends(get_db)
):
    """
    결제 승인

    토스 결제창에서 결제 완료 후, successUrl로 리다이렉트될 때
    전달받은 정보(paymentKey, orderId, amount)로 결제를 최종 승인합니다.

    1. 주문 정보 검증 (order_id로 DB에서 payment 조회)
    2. 토스페이먼츠 결제 승인 API 호출
    3. Payment 상태를 DONE으로 업데이트
    4. 연결된 Invoice 상태를 PAID로 업데이트

    Note: 인증 없이 order_id 검증만으로 처리 (토스 리다이렉트 시 쿠키 전달 문제 해결)
    """
    service = StudentPaymentService(db)
    result = await service.confirm_payment(
        payment_key=request.payment_key,
        order_id=request.order_id,
        amount=request.amount
    )

    return PaymentConfirmResponse(
        success=result["success"],
        payment_id=result["payment_id"],
        payment_key=result["payment_key"],
        order_id=result["order_id"],
        amount=result["amount"],
        status=result["status"],
        approved_at=result["approved_at"],
        message=result["message"]
    )


@router.get(
    "/history",
    response_model=PaymentHistoryResponse,
    summary="결제 내역 조회",
    description="현재 사용자에게 연결된 학생들의 결제 내역을 조회합니다."
)
async def get_payment_history(
    limit: int = Query(50, ge=1, le=100, description="조회 개수"),
    offset: int = Query(0, ge=0, description="시작 위치"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    결제 내역 조회

    - 사용자에게 연결된 학생들의 결제 내역만 조회
    - 최신순으로 정렬
    - 페이지네이션 지원
    """
    service = StudentPaymentService(db)
    result = service.get_payment_history(current_user, limit, offset)

    return PaymentHistoryResponse(
        payments=result["payments"],
        total=result["total"]
    )
