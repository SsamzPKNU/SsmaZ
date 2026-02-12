"""
수납/결제 관리 관련 API 엔드포인트
수납 CRUD 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
    PaymentListResponse,
    PaymentNotifyRequest
)
from app.services.payment_service import PaymentService
from app.services.push_notification_service import PushNotificationService
from app.models.user import User
from app.models.student import Student
from app.api.auth import get_current_user
from typing import List

import logging
logger = logging.getLogger(__name__)


# API 라우터 생성
router = APIRouter(
    prefix="/api/admin/payments",
    tags=["수납/결제 관리"]
)


@router.get("", response_model=PaymentListResponse)
async def get_payments(
    skip: int = Query(0, ge=0, description="페이지네이션 오프셋"),
    limit: int = Query(100, ge=1, le=1000, description="페이지네이션 제한"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    수납 내역 목록 조회

    Query Parameters:
        - skip: 페이지네이션 오프셋 (기본: 0)
        - limit: 페이지네이션 제한 (기본: 100)

    Returns:
        PaymentListResponse: 수납 내역 목록
    """
    academy_id = current_user.academy_id

    payments = PaymentService.get_payments(
        db=db,
        academy_id=academy_id,
        skip=skip,
        limit=limit
    )

    return PaymentListResponse(
        payments=[PaymentService.to_response(p) for p in payments],
        total=len(payments)
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    수납 내역 단건 조회

    Path Parameters:
        - payment_id: 결제 ID

    Returns:
        PaymentResponse: 수납 내역
    """
    academy_id = current_user.academy_id

    payment = PaymentService.get_payment_by_id(db, payment_id, academy_id)

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="수납 내역을 찾을 수 없습니다"
        )

    return PaymentService.to_response(payment)


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    수납 항목 생성

    Request Body:
        - student_id: 학생 ID (필수)
        - amount: 납부 금액 (필수)
        - payment_date: 납부일 (선택)
        - next_payment_date: 다음 납부 예정일 (선택)
        - method: 결제 방법 (CARD, CASH)

    Returns:
        PaymentResponse: 생성된 수납 내역
    """
    academy_id = current_user.academy_id

    new_payment = PaymentService.create_payment(
        db=db,
        academy_id=academy_id,
        payment_data=payment_data
    )

    # 푸시 알림 발송
    try:
        student = db.query(Student).filter(
            Student.student_id == payment_data.student_id
        ).first()
        if student:
            PushNotificationService.send_payment_notification(
                db, student,
                title="수납 안내",
                body="수강료 납부 안내가 등록되었습니다",
                payment_id=new_payment.payment_id
            )
    except Exception as e:
        logger.error(f"[FCM] 수납 알림 발송 실패: {e}")

    return PaymentService.to_response(new_payment)


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int,
    update_data: PaymentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    수납 내역 수정

    Path Parameters:
        - payment_id: 결제 ID

    Request Body:
        - amount: 납부 금액 (선택)
        - payment_date: 납부일 (선택)
        - next_payment_date: 다음 납부 예정일 (선택)
        - method: 결제 방법 (선택)

    Returns:
        PaymentResponse: 수정된 수납 내역
    """
    academy_id = current_user.academy_id

    updated_payment = PaymentService.update_payment(
        db=db,
        payment_id=payment_id,
        academy_id=academy_id,
        update_data=update_data
    )

    return PaymentService.to_response(updated_payment)


@router.post("/{payment_id}/notify")
async def send_payment_notification(
    payment_id: int,
    notify_data: PaymentNotifyRequest = PaymentNotifyRequest(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    수납 알림 수동 발송

    Path Parameters:
        - payment_id: 결제 ID

    Request Body (선택):
        - title: 알림 제목 (기본: "수납 안내")
        - body: 알림 본문 (기본: "수강료 납부 안내가 등록되었습니다")
    """
    academy_id = current_user.academy_id

    payment = PaymentService.get_payment_by_id(db, payment_id, academy_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="수납 내역을 찾을 수 없습니다"
        )

    student = db.query(Student).filter(
        Student.student_id == payment.student_id
    ).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="학생을 찾을 수 없습니다"
        )

    title = notify_data.title or "수납 안내"
    body = notify_data.body or "수강료 납부 안내가 등록되었습니다"

    PushNotificationService.send_payment_notification(
        db, student, title=title, body=body, payment_id=payment_id
    )

    return {"success": True, "message": "수납 알림이 발송되었습니다"}


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    수납 항목 삭제

    Path Parameters:
        - payment_id: 결제 ID

    Returns:
        204 No Content
    """
    academy_id = current_user.academy_id

    PaymentService.delete_payment(
        db=db,
        payment_id=payment_id,
        academy_id=academy_id
    )

    return None
