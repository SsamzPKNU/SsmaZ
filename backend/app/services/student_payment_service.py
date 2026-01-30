"""
학생 결제 서비스
토스페이먼츠를 통한 학생 결제 처리 비즈니스 로직
"""

import uuid
import os
import logging
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.models.student import Student
from app.models.user import User
from app.services.toss_payment_client import TossPaymentClient

load_dotenv()


class StudentPaymentService:
    """
    학생 결제 서비스

    주요 기능:
    - 결제 주문 생성 (orderId 발급)
    - 결제 승인 처리
    - 결제 가능 청구서 조회
    - 결제 내역 조회
    """

    def __init__(self, db: Session):
        self.db = db
        self.toss_client = TossPaymentClient()
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

    def generate_order_id(self) -> str:
        """
        토스페이먼츠용 주문 ID 생성

        형식: ORDER_YYYYMMDD_UUID8
        예: ORDER_20260129_a1b2c3d4

        Returns:
            고유한 주문 ID 문자열
        """
        today = datetime.now().strftime("%Y%m%d")
        unique_id = uuid.uuid4().hex[:8]
        return f"ORDER_{today}_{unique_id}"

    def get_students_for_user(self, user: User) -> List[Student]:
        """
        사용자에게 연결된 학생 목록 조회

        Args:
            user: 현재 로그인한 사용자

        Returns:
            연결된 Student 목록
        """
        students = self.db.query(Student).filter(
            Student.user_id == user.user_id
        ).all()
        return students

    def get_payable_invoices(self, user: User) -> dict:
        """
        결제 가능한 청구서 목록 조회

        Args:
            user: 현재 로그인한 사용자

        Returns:
            청구서 목록, 개수, 총 금액
        """
        # 사용자에게 연결된 학생들의 ID 목록
        students = self.get_students_for_user(user)
        student_ids = [s.student_id for s in students]

        if not student_ids:
            return {
                "invoices": [],
                "total": 0,
                "total_amount": 0
            }

        # 결제 가능한 청구서 조회 (PENDING, SENT, OVERDUE 상태)
        payable_statuses = [InvoiceStatus.PENDING, InvoiceStatus.SENT, InvoiceStatus.OVERDUE]
        invoices = self.db.query(Invoice).filter(
            Invoice.student_id.in_(student_ids),
            Invoice.status.in_(payable_statuses)
        ).order_by(Invoice.due_date.asc()).all()

        today = date.today()
        result_invoices = []
        total_amount = 0

        for invoice in invoices:
            student = self.db.query(Student).filter(
                Student.student_id == invoice.student_id
            ).first()

            result_invoices.append({
                "invoice_id": invoice.invoice_id,
                "student_id": invoice.student_id,
                "student_name": student.name if student else "Unknown",
                "amount": invoice.amount,
                "description": invoice.description,
                "due_date": invoice.due_date,
                "status": invoice.status.value,
                "is_overdue": invoice.due_date < today,
                "created_at": invoice.created_at
            })
            total_amount += invoice.amount

        return {
            "invoices": result_invoices,
            "total": len(result_invoices),
            "total_amount": total_amount
        }

    def create_payment_order(self, user: User, invoice_id: int) -> dict:
        """
        결제 주문 생성

        1. 청구서 유효성 검증
        2. 주문 ID 생성
        3. Payment 레코드 생성 (PENDING 상태)
        4. 프론트에서 토스 SDK 호출에 필요한 정보 반환

        Args:
            user: 현재 로그인한 사용자
            invoice_id: 청구서 ID

        Returns:
            주문 정보 (orderId, amount, orderName 등)

        Raises:
            HTTPException: 청구서가 없거나 권한이 없는 경우
        """
        # 청구서 조회
        invoice = self.db.query(Invoice).filter(
            Invoice.invoice_id == invoice_id
        ).first()

        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="청구서를 찾을 수 없습니다"
            )

        # 권한 확인: 해당 학생이 사용자에게 연결되어 있는지
        student = self.db.query(Student).filter(
            Student.student_id == invoice.student_id,
            Student.user_id == user.user_id
        ).first()

        if not student:
            # 디버그: 왜 권한이 없는지 로깅
            invoice_student = self.db.query(Student).filter(
                Student.student_id == invoice.student_id
            ).first()
            logger.warning(
                f"결제 권한 없음 - user_id: {user.user_id}, "
                f"invoice.student_id: {invoice.student_id}, "
                f"student.user_id: {invoice_student.user_id if invoice_student else 'Student not found'}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"해당 청구서에 대한 결제 권한이 없습니다. (user_id: {user.user_id}, student_id: {invoice.student_id})"
            )

        # 이미 결제된 청구서인지 확인
        if invoice.status == InvoiceStatus.PAID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 결제 완료된 청구서입니다"
            )

        if invoice.status == InvoiceStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="취소된 청구서입니다"
            )

        # 주문 ID 생성
        order_id = self.generate_order_id()

        # Payment 레코드 생성 (PENDING 상태)
        payment = Payment(
            student_id=student.student_id,
            academy_id=invoice.academy_id,
            amount=invoice.amount,
            order_id=order_id,
            status=PaymentStatus.PENDING,
            invoice_id=invoice.invoice_id,
            method=PaymentMethod.CARD
        )
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)

        # 주문명 생성
        order_name = invoice.description or f"{student.name} 수강료"

        return {
            "order_id": order_id,
            "amount": invoice.amount,
            "order_name": order_name,
            "customer_name": student.name,
            "success_url": f"{self.frontend_url}/payment/success",
            "fail_url": f"{self.frontend_url}/payment/fail"
        }

    async def confirm_payment(
        self,
        payment_key: str,
        order_id: str,
        amount: int
    ) -> dict:
        """
        결제 승인 처리

        1. Payment 레코드 조회 및 검증 (order_id로 검증)
        2. 토스페이먼츠 결제 승인 API 호출
        3. Payment/Invoice 상태 업데이트

        Args:
            payment_key: 토스페이먼츠 결제 키
            order_id: 주문 ID
            amount: 결제 금액

        Returns:
            결제 승인 결과

        Raises:
            HTTPException: 주문이 없거나 금액이 일치하지 않는 경우
        """
        # Payment 조회
        payment = self.db.query(Payment).filter(
            Payment.order_id == order_id
        ).first()

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="주문 정보를 찾을 수 없습니다"
            )

        # 이미 처리된 결제인지 확인
        if payment.status == PaymentStatus.DONE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 완료된 결제입니다"
            )

        # 금액 검증
        if payment.amount != amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"결제 금액이 일치하지 않습니다. 예상: {payment.amount}, 실제: {amount}"
            )

        # 토스페이먼츠 결제 승인 API 호출
        try:
            toss_result = await self.toss_client.confirm_payment(
                payment_key=payment_key,
                order_id=order_id,
                amount=amount
            )
        except HTTPException:
            # 토스 API 호출 실패 시 결제 상태를 FAILED로 업데이트
            payment.status = PaymentStatus.FAILED
            self.db.commit()
            raise

        # Payment 업데이트
        payment.payment_key = payment_key
        payment.status = PaymentStatus.DONE
        payment.payment_date = date.today()

        # Invoice 업데이트 (있는 경우)
        if payment.invoice_id:
            invoice = self.db.query(Invoice).filter(
                Invoice.invoice_id == payment.invoice_id
            ).first()
            if invoice:
                invoice.status = InvoiceStatus.PAID
                invoice.paid_at = datetime.now()
                invoice.payment_id = payment.payment_id

        self.db.commit()
        self.db.refresh(payment)

        return {
            "success": True,
            "payment_id": payment.payment_id,
            "payment_key": payment_key,
            "order_id": order_id,
            "amount": amount,
            "status": payment.status.value,
            "approved_at": toss_result.get("approvedAt"),
            "message": "결제가 완료되었습니다"
        }

    def get_payment_history(self, user: User, limit: int = 50, offset: int = 0) -> dict:
        """
        결제 내역 조회

        Args:
            user: 현재 로그인한 사용자
            limit: 조회 개수
            offset: 시작 위치

        Returns:
            결제 내역 목록
        """
        # 사용자에게 연결된 학생들
        students = self.get_students_for_user(user)
        student_ids = [s.student_id for s in students]
        student_map = {s.student_id: s.name for s in students}

        if not student_ids:
            return {
                "payments": [],
                "total": 0
            }

        # 총 개수
        total = self.db.query(Payment).filter(
            Payment.student_id.in_(student_ids)
        ).count()

        # 결제 내역 조회
        payments = self.db.query(Payment).filter(
            Payment.student_id.in_(student_ids)
        ).order_by(Payment.created_at.desc()).offset(offset).limit(limit).all()

        result_payments = []
        for payment in payments:
            # 청구서 정보 조회
            invoice_desc = None
            if payment.invoice_id:
                invoice = self.db.query(Invoice).filter(
                    Invoice.invoice_id == payment.invoice_id
                ).first()
                if invoice:
                    invoice_desc = invoice.description

            result_payments.append({
                "payment_id": payment.payment_id,
                "student_id": payment.student_id,
                "student_name": student_map.get(payment.student_id, "Unknown"),
                "amount": payment.amount,
                "status": payment.status.value if payment.status else None,
                "method": payment.method.value if payment.method else None,
                "payment_date": payment.payment_date,
                "order_id": payment.order_id,
                "invoice_description": invoice_desc,
                "created_at": payment.created_at
            })

        return {
            "payments": result_payments,
            "total": total
        }
