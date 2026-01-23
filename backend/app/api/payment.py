"""
수납/결제 관리 관련 API 엔드포인트
수납 CRUD 및 통계 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
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


# API 라우터 생성
router = APIRouter(
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
