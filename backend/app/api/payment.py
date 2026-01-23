"""
<<<<<<< Updated upstream
결제 관리 API 라우터
ADMIN 권한 전용 - 결제 조회, 취소, 로그 조회 기능 제공
=======
수납/결제 관리 관련 API 엔드포인트
수납 CRUD 및 통계 기능 제공
>>>>>>> Stashed changes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
<<<<<<< Updated upstream
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
=======
from app.core.database import get_db
from app.schemas.payment import (
    PaymentCreate,
    PaymentConfirm,
    PaymentResponse,
    PaymentSummary
)
from app.services.payment_service import PaymentService
from app.models.user import User
from app.api.auth import get_current_user
from typing import List, Optional
>>>>>>> Stashed changes


# API 라우터 생성
router = APIRouter(
<<<<<<< Updated upstream
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
=======
    prefix="/api/admin/payments",
    tags=["수납/결제 관리"]
)


@router.get("/summary", response_model=PaymentSummary)
async def get_payment_summary(
    month: str = Query(..., description="대상 월 (YYYY-MM 형식)", regex=r"^\d{4}-\d{2}$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    월별 수납 현황 조회
    
    특정 월의 수납 현황 요약 정보를 조회합니다.
    - 예상 총액
    - 실제 수납액
    - 수납률
    - 미납 인원 수
    
    Query Parameters:
        - month: 대상 월 (YYYY-MM 형식, 예: 2026-01)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        PaymentSummary:
            - month: 대상 월
            - total_expected: 예상 총액 (원)
            - total_collected: 실제 수납액 (원)
            - collection_rate: 수납률 (%)
            - unpaid_count: 미납 인원 수
    
    Raises:
        401: 인증되지 않은 사용자
        422: 잘못된 월 형식
    
    사용 예시:
        GET /api/admin/payments/summary?month=2026-01
    """
    academy_id = current_user.academy_id
    
    summary = PaymentService.get_monthly_summary(
        db=db,
        academy_id=academy_id,
        month_str=month
    )
    
    return summary


@router.get("", response_model=List[PaymentResponse])
async def get_payments(
    month: Optional[str] = Query(None, description="대상 월 (YYYY-MM)", regex=r"^\d{4}-\d{2}$"),
    status: Optional[str] = Query(None, description="상태 필터 (unpaid, paid, overdue)"),
    skip: int = Query(0, ge=0, description="페이지네이션 오프셋"),
    limit: int = Query(100, ge=1, le=1000, description="페이지네이션 제한"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    수납 내역 상세 목록 조회
    
    수납 내역 목록을 조회합니다.
    월별, 상태별로 필터링할 수 있습니다.
    
    Query Parameters:
        - month: 대상 월 필터 (YYYY-MM)
        - status: 상태 필터 (unpaid, paid, overdue)
        - skip: 페이지네이션 오프셋 (기본: 0)
        - limit: 페이지네이션 제한 (기본: 100)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        List[PaymentResponse]: 수납 내역 목록
    
    Response Fields:
        - id: 결제 ID
        - student_name: 학생 이름
        - parent_phone: 학부모 전화번호
        - amount: 납부 금액
        - due_date: 납부 기한일
        - status: 결제 상태
        - last_reminded: 마지막 독촉일
        - paid_date: 실제 납부일
        - method: 결제 방법
        - memo: 메모
    
    Raises:
        401: 인증되지 않은 사용자
    
    사용 예시:
        GET /api/admin/payments
        GET /api/admin/payments?month=2026-01
        GET /api/admin/payments?status=unpaid
        GET /api/admin/payments?month=2026-01&status=unpaid
    """
    academy_id = current_user.academy_id
    
    payments = PaymentService.get_payments(
        db=db,
        academy_id=academy_id,
        month=month,
        status=status,
        skip=skip,
        limit=limit
    )
    
    return [PaymentService.to_response(payment) for payment in payments]


@router.post("/{payment_id}/confirm", response_model=PaymentResponse)
async def confirm_payment(
    payment_id: int,
    confirm_data: PaymentConfirm,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    수납 처리 (관리자 수동 처리)
    
    미납 상태의 수납을 납부 완료 처리합니다.
    결제 방법, 납부일, 메모를 함께 기록합니다.
    
    Path Parameters:
        - payment_id: 결제 ID
    
    Request Body:
        - method: 결제 방법 (card, cash, transfer)
        - paid_date: 납부일 (YYYY-MM-DD)
        - memo: 메모 (선택)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        PaymentResponse: 수납 처리된 내역
    
    Raises:
        401: 인증되지 않은 사용자
        404: 수납 내역을 찾을 수 없음
        422: 입력 데이터 검증 실패
    
    사용 예시:
        POST /api/admin/payments/101/confirm
        {
            "method": "card",
            "paid_date": "2026-01-22",
            "memo": "방문 카드 결제"
        }
    """
    academy_id = current_user.academy_id
    
    confirmed_payment = PaymentService.confirm_payment(
        db=db,
        payment_id=payment_id,
        academy_id=academy_id,
        confirm_data=confirm_data
    )
    
    return PaymentService.to_response(confirmed_payment)


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    수납 항목 생성
    
    새로운 수납 항목을 생성합니다.
    월별 수강료나 추가 수업료 등을 등록할 때 사용합니다.
    
    Request Body:
        - student_id: 학생 ID (필수)
        - amount: 납부 금액 (필수)
        - due_date: 납부 기한일 (필수)
        - memo: 메모 (선택)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        PaymentResponse: 생성된 수납 내역
    
    Raises:
        401: 인증되지 않은 사용자
        404: 학생을 찾을 수 없음
        422: 입력 데이터 검증 실패
    
    사용 예시:
        POST /api/admin/payments
        {
            "student_id": 1,
            "amount": 300000,
            "due_date": "2026-02-05",
            "memo": "2월 수강료"
        }
    """
    academy_id = current_user.academy_id
    
    new_payment = PaymentService.create_payment(
        db=db,
        academy_id=academy_id,
        payment_data=payment_data
    )
    
    return PaymentService.to_response(new_payment)


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    수납 항목 삭제
    
    수납 항목을 삭제합니다.
    
    Path Parameters:
        - payment_id: 결제 ID
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        204 No Content (응답 바디 없음)
    
    Raises:
        401: 인증되지 않은 사용자
        404: 수납 내역을 찾을 수 없음
    
    사용 예시:
        DELETE /api/admin/payments/101
    """
    academy_id = current_user.academy_id
    
    PaymentService.delete_payment(
        db=db,
        payment_id=payment_id,
        academy_id=academy_id
    )
    
    return None
>>>>>>> Stashed changes
