"""
결제 관리 API 라우터
ADMIN 권한 전용 - 결제 조회, 취소, 로그 조회 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.api.deps import get_admin_user
from app.models.user import User
from app.models.payment import Payment
from app.schemas.payment import (
    PaymentResponse,
    PaymentListResponse,
    PaymentCancelRequest,
    PaymentCancelResponse,
    TossPaymentDetail,
    PaymentFilterParams
)
from app.services.toss_payment_client import TossPaymentClient


# API 라우터 생성
router = APIRouter(
    prefix="/payments",
    tags=["결제 관리 (ADMIN)"]
)


@router.get("/logs", response_model=PaymentListResponse)
async def get_payment_logs(
    academy_id: Optional[int] = Query(None, description="학원 ID"),
    student_id: Optional[int] = Query(None, description="학생 ID"),
    method: Optional[str] = Query(None, description="결제 수단"),
    start_date: Optional[date] = Query(None, description="시작일 (payment_date 기준)"),
    end_date: Optional[date] = Query(None, description="종료일 (payment_date 기준)"),
    limit: int = Query(100, ge=1, le=1000, description="조회 개수"),
    offset: int = Query(0, ge=0, description="오프셋"),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    결제 로그 목록 조회 (ADMIN 전용)
    
    DB에 저장된 결제 로그를 날짜별/상태별로 필터링하여 반환합니다.
    
    **권한**: ADMIN만 접근 가능
    
    **필터링 옵션**:
    - academy_id: 특정 학원의 결제만 조회
    - student_id: 특정 학생의 결제만 조회
    - method: 결제 수단 필터 (CARD, TRANSFER, CASH, VIRTUAL_ACCOUNT)
    - start_date, end_date: 결제일 범위 필터
    - limit, offset: 페이징
    
    **사용 예시**:
    ```
    GET /payments/logs?academy_id=1&start_date=2026-01-01&end_date=2026-01-31&limit=50
    ```
    
    Returns:
        결제 목록 및 전체 개수
    """
    # 쿼리 빌더
    query = db.query(Payment)
    
    # 필터 적용
    filters = []
    
    if academy_id is not None:
        filters.append(Payment.academy_id == academy_id)
    
    if student_id is not None:
        filters.append(Payment.student_id == student_id)
    
    if method is not None:
        filters.append(Payment.method == method)
    
    if start_date is not None:
        filters.append(Payment.payment_date >= start_date)
    
    if end_date is not None:
        filters.append(Payment.payment_date <= end_date)
    
    # 필터 적용
    if filters:
        query = query.filter(and_(*filters))
    
    # 전체 개수 조회
    total = query.count()
    
    # 페이징 및 정렬 (최신순)
    payments = query.order_by(Payment.created_at.desc()).offset(offset).limit(limit).all()
    
    return PaymentListResponse(
        total=total,
        payments=[PaymentResponse.from_orm(p) for p in payments]
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment_by_id(
    payment_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    결제 단건 조회 (DB) (ADMIN 전용)
    
    DB에 저장된 결제 정보를 payment_id로 조회합니다.
    
    **권한**: ADMIN만 접근 가능
    
    Args:
        payment_id: 결제 ID
        
    Returns:
        결제 상세 정보
        
    Raises:
        404: 결제 정보를 찾을 수 없는 경우
    """
    payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"결제 ID {payment_id}를 찾을 수 없습니다"
        )
    
    return PaymentResponse.from_orm(payment)


@router.get("/toss/{payment_key}", response_model=TossPaymentDetail)
async def get_toss_payment(
    payment_key: str,
    admin_user: User = Depends(get_admin_user)
):
    """
    토스페이먼츠 결제 조회 (ADMIN 전용)
    
    토스페이먼츠 API를 통해 결제 상세 정보를 조회합니다.
    
    **권한**: ADMIN만 접근 가능
    
    **주의**: 이 API는 토스페이먼츠 서버에 직접 요청하므로,
    테스트 환경에서는 테스트 시크릿 키로 생성된 결제만 조회 가능합니다.
    
    Args:
        payment_key: 토스페이먼츠 결제 키
        
    Returns:
        토스페이먼츠 결제 상세 정보
        
    Raises:
        404: 결제를 찾을 수 없는 경우
        503: 토스페이먼츠 API 연결 실패
    """
    client = TossPaymentClient()
    payment_data = await client.get_payment(payment_key)
    
    return TossPaymentDetail(**payment_data)


@router.post("/toss/{payment_key}/cancel", response_model=PaymentCancelResponse)
async def cancel_toss_payment(
    payment_key: str,
    cancel_request: PaymentCancelRequest,
    admin_user: User = Depends(get_admin_user)
):
    """
    토스페이먼츠 결제 취소/환불 (ADMIN 전용)
    
    토스페이먼츠 API를 통해 결제를 취소하고 환불 처리합니다.
    
    **권한**: ADMIN만 접근 가능
    
    **취소 유형**:
    - 전액 취소: cancelAmount를 지정하지 않음
    - 부분 취소: cancelAmount를 지정
    - 가상계좌 환불: refundReceiveAccount 필수
    
    **주의사항**:
    - 이미 취소된 결제는 다시 취소할 수 없습니다
    - 취소 가능 금액을 초과하면 실패합니다
    - 가상계좌 결제는 환불 계좌 정보가 필수입니다
    
    Args:
        payment_key: 토스페이먼츠 결제 키
        cancel_request: 취소 요청 정보
            - cancelReason: 취소 사유 (필수)
            - cancelAmount: 취소 금액 (부분 취소 시)
            - refundReceiveAccount: 환불 계좌 정보 (가상계좌 환불 시 필수)
        
    Returns:
        취소 결과 정보
        
    Raises:
        400: 이미 취소된 결제, 취소 불가능한 결제 등
        404: 결제를 찾을 수 없는 경우
        503: 토스페이먼츠 API 연결 실패
        
    사용 예시:
    ```json
    // 전액 취소
    {
        "cancelReason": "고객 요청"
    }
    
    // 부분 취소
    {
        "cancelReason": "부분 환불",
        "cancelAmount": 10000
    }
    
    // 가상계좌 환불
    {
        "cancelReason": "환불 요청",
        "refundReceiveAccount": {
            "bank": "88",
            "accountNumber": "1002345678901",
            "holderName": "홍길동"
        }
    }
    ```
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


@router.get("/", response_model=dict)
async def payment_root(
    admin_user: User = Depends(get_admin_user)
):
    """
    결제 API 루트 엔드포인트 (ADMIN 전용)
    
    사용 가능한 엔드포인트 목록을 반환합니다.
    """
    return {
        "message": "결제 관리 API (ADMIN 전용)",
        "endpoints": {
            "결제 로그 목록": "GET /payments/logs",
            "결제 단건 조회 (DB)": "GET /payments/{payment_id}",
            "토스 결제 조회": "GET /payments/toss/{payment_key}",
            "토스 결제 취소": "POST /payments/toss/{payment_key}/cancel"
        }
    }
