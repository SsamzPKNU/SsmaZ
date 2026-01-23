"""
수납/결제 관리 관련 비즈니스 로직
수납 CRUD 기능 제공
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status as http_status
from app.models.payment import Payment, PaymentMethod
from app.models.student import Student
from app.schemas.payment import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse
)
from typing import List, Optional


class PaymentService:
    """수납/결제 관리 서비스 클래스"""

    @staticmethod
    def get_payments(
        db: Session,
        academy_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """
        수납 내역 목록 조회

        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            skip: 페이지네이션 오프셋
            limit: 페이지네이션 제한

        Returns:
            List[Payment]: 수납 내역 목록
        """
        query = db.query(Payment).filter(Payment.academy_id == academy_id)
        payments = query.order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()
        return payments

    @staticmethod
    def get_payment_by_id(db: Session, payment_id: int, academy_id: int) -> Optional[Payment]:
        """
        수납 내역 조회 (ID로)

        Args:
            db: 데이터베이스 세션
            payment_id: 결제 ID
            academy_id: 학원 ID

        Returns:
            Optional[Payment]: 수납 내역 또는 None
        """
        return db.query(Payment).filter(
            and_(
                Payment.payment_id == payment_id,
                Payment.academy_id == academy_id
            )
        ).first()

    @staticmethod
    def create_payment(
        db: Session,
        academy_id: int,
        payment_data: PaymentCreate
    ) -> Payment:
        """
        수납 항목 생성

        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            payment_data: 수납 정보

        Returns:
            Payment: 생성된 수납 내역

        Raises:
            HTTPException: 학생을 찾을 수 없는 경우
        """
        # 학생 존재 여부 확인
        student = db.query(Student).filter(
            and_(
                Student.student_id == payment_data.student_id,
                Student.academy_id == academy_id
            )
        ).first()

        if not student:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="학생을 찾을 수 없습니다"
            )

        # Payment 객체 생성
        new_payment = Payment(
            student_id=payment_data.student_id,
            academy_id=academy_id,
            amount=payment_data.amount,
            payment_date=payment_data.payment_date,
            next_payment_date=payment_data.next_payment_date,
            method=payment_data.method
        )

        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)

        return new_payment

    @staticmethod
    def update_payment(
        db: Session,
        payment_id: int,
        academy_id: int,
        update_data: PaymentUpdate
    ) -> Payment:
        """
        수납 내역 수정

        Args:
            db: 데이터베이스 세션
            payment_id: 결제 ID
            academy_id: 학원 ID
            update_data: 수정할 정보

        Returns:
            Payment: 수정된 수납 내역

        Raises:
            HTTPException: 수납 내역을 찾을 수 없는 경우
        """
        payment = PaymentService.get_payment_by_id(db, payment_id, academy_id)

        if not payment:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="수납 내역을 찾을 수 없습니다"
            )

        # 수정할 필드만 업데이트
        if update_data.amount is not None:
            payment.amount = update_data.amount
        if update_data.payment_date is not None:
            payment.payment_date = update_data.payment_date
        if update_data.next_payment_date is not None:
            payment.next_payment_date = update_data.next_payment_date
        if update_data.method is not None:
            payment.method = update_data.method

        db.commit()
        db.refresh(payment)

        return payment

    @staticmethod
    def delete_payment(db: Session, payment_id: int, academy_id: int) -> bool:
        """
        수납 항목 삭제

        Args:
            db: 데이터베이스 세션
            payment_id: 결제 ID
            academy_id: 학원 ID

        Returns:
            bool: 삭제 성공 여부

        Raises:
            HTTPException: 수납 내역을 찾을 수 없는 경우
        """
        payment = PaymentService.get_payment_by_id(db, payment_id, academy_id)

        if not payment:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="수납 내역을 찾을 수 없습니다"
            )

        db.delete(payment)
        db.commit()

        return True

    @staticmethod
    def to_response(payment: Payment) -> PaymentResponse:
        """
        Payment 모델을 PaymentResponse로 변환

        Args:
            payment: Payment 모델 객체

        Returns:
            PaymentResponse: 응답 스키마
        """
        student = payment.student

        return PaymentResponse(
            payment_id=payment.payment_id,
            student_id=payment.student_id,
            student_name=student.name if student else None,
            academy_id=payment.academy_id,
            amount=payment.amount,
            payment_date=payment.payment_date,
            next_payment_date=payment.next_payment_date,
            method=payment.method.value if payment.method else None,
            created_at=payment.created_at
        )
