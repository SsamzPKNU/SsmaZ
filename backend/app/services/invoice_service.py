"""
Invoice 관련 비즈니스 로직
청구서 CRUD 및 발송 처리
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, date
from typing import List, Optional, Tuple

from app.models.invoice import Invoice, InvoiceStatus
from app.models.student import Student
from app.schemas.invoice import (
    InvoiceCreate, InvoiceBulkCreate, InvoiceResponse
)


class InvoiceService:
    """청구서 관련 서비스"""

    @staticmethod
    def get_invoices(
        db: Session,
        academy_id: int,
        status: Optional[str] = None,
        student_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Invoice], int]:
        """청구서 목록 조회"""
        query = db.query(Invoice).filter(Invoice.academy_id == academy_id)

        if status:
            query = query.filter(Invoice.status == status)
        if student_id:
            query = query.filter(Invoice.student_id == student_id)

        total = query.count()
        invoices = query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit).all()

        return invoices, total

    @staticmethod
    def get_invoice(db: Session, invoice_id: int, academy_id: int) -> Optional[Invoice]:
        """청구서 상세 조회"""
        return db.query(Invoice).filter(
            and_(
                Invoice.invoice_id == invoice_id,
                Invoice.academy_id == academy_id
            )
        ).first()

    @staticmethod
    def create_invoice(db: Session, academy_id: int, data: InvoiceCreate) -> Invoice:
        """청구서 단건 생성"""
        # 학생 확인
        student = db.query(Student).filter(
            and_(
                Student.student_id == data.student_id,
                Student.academy_id == academy_id
            )
        ).first()
        if not student:
            raise ValueError("학생을 찾을 수 없습니다")

        invoice = Invoice(
            academy_id=academy_id,
            student_id=data.student_id,
            amount=data.amount,
            description=data.description,
            due_date=data.due_date,
            status=InvoiceStatus.PENDING
        )
        db.add(invoice)
        db.commit()
        db.refresh(invoice)
        return invoice

    @staticmethod
    def create_invoices_bulk(
        db: Session,
        academy_id: int,
        data: InvoiceBulkCreate
    ) -> List[Invoice]:
        """청구서 일괄 생성"""
        invoices = []

        for student_id in data.student_ids:
            # 학생 확인
            student = db.query(Student).filter(
                and_(
                    Student.student_id == student_id,
                    Student.academy_id == academy_id
                )
            ).first()
            if not student:
                continue

            invoice = Invoice(
                academy_id=academy_id,
                student_id=student_id,
                amount=data.amount,
                description=data.description,
                due_date=data.due_date,
                status=InvoiceStatus.PENDING
            )
            db.add(invoice)
            invoices.append(invoice)

        db.commit()

        # 생성된 청구서들 새로고침
        for invoice in invoices:
            db.refresh(invoice)

        return invoices

    @staticmethod
    def send_invoices(
        db: Session,
        academy_id: int,
        invoice_ids: List[int]
    ) -> Tuple[int, List[int]]:
        """
        청구서 발송

        Returns:
            Tuple[int, List[int]]: (발송 성공 수, 실패한 청구서 ID 목록)
        """
        sent_count = 0
        failed_ids = []
        now = datetime.now()

        for invoice_id in invoice_ids:
            invoice = InvoiceService.get_invoice(db, invoice_id, academy_id)
            if not invoice:
                failed_ids.append(invoice_id)
                continue

            if invoice.status != InvoiceStatus.PENDING:
                failed_ids.append(invoice_id)
                continue

            # TODO: 실제 SMS/알림톡 발송 로직 구현
            # 현재는 상태만 변경
            invoice.status = InvoiceStatus.SENT
            invoice.sent_at = now
            sent_count += 1

        db.commit()

        return sent_count, failed_ids

    @staticmethod
    def mark_as_paid(
        db: Session,
        invoice_id: int,
        academy_id: int,
        payment_id: Optional[int] = None
    ) -> Optional[Invoice]:
        """청구서 납부 완료 처리"""
        invoice = InvoiceService.get_invoice(db, invoice_id, academy_id)
        if not invoice:
            return None

        if invoice.status == InvoiceStatus.PAID:
            raise ValueError("이미 납부 완료된 청구서입니다")

        if invoice.status == InvoiceStatus.CANCELLED:
            raise ValueError("취소된 청구서입니다")

        invoice.status = InvoiceStatus.PAID
        invoice.paid_at = datetime.now()
        if payment_id:
            invoice.payment_id = payment_id

        db.commit()
        db.refresh(invoice)
        return invoice

    @staticmethod
    def cancel_invoice(db: Session, invoice_id: int, academy_id: int) -> Optional[Invoice]:
        """청구서 취소"""
        invoice = InvoiceService.get_invoice(db, invoice_id, academy_id)
        if not invoice:
            return None

        if invoice.status == InvoiceStatus.PAID:
            raise ValueError("이미 납부된 청구서는 취소할 수 없습니다")

        invoice.status = InvoiceStatus.CANCELLED
        db.commit()
        db.refresh(invoice)
        return invoice

    @staticmethod
    def check_overdue_invoices(db: Session, academy_id: int) -> int:
        """연체 청구서 상태 업데이트"""
        today = date.today()
        updated_count = db.query(Invoice).filter(
            and_(
                Invoice.academy_id == academy_id,
                Invoice.status == InvoiceStatus.SENT,
                Invoice.due_date < today
            )
        ).update({Invoice.status: InvoiceStatus.OVERDUE})

        db.commit()
        return updated_count

    @staticmethod
    def to_response(invoice: Invoice) -> InvoiceResponse:
        """Invoice 모델을 InvoiceResponse로 변환"""
        return InvoiceResponse(
            invoice_id=invoice.invoice_id,
            academy_id=invoice.academy_id,
            student_id=invoice.student_id,
            student_name=invoice.student.name if invoice.student else None,
            amount=invoice.amount,
            description=invoice.description,
            due_date=invoice.due_date,
            status=invoice.status.value if invoice.status else "PENDING",
            sent_at=invoice.sent_at,
            paid_at=invoice.paid_at,
            payment_id=invoice.payment_id,
            created_at=invoice.created_at
        )
