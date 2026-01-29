"""
Invoice 모델 정의
청구서 정보를 저장하는 테이블
"""

from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class InvoiceStatus(str, enum.Enum):
    """청구서 상태"""
    PENDING = "PENDING"        # 발송 대기
    SENT = "SENT"             # 발송됨
    PAID = "PAID"             # 납부 완료
    OVERDUE = "OVERDUE"       # 연체
    CANCELLED = "CANCELLED"   # 취소


class Invoice(Base):
    """
    청구서 테이블

    Student와 N:1 관계
    Payment와 1:1 관계 (납부 완료 시)

    컬럼 설명:
    - invoice_id: 청구서 고유 ID (PK)
    - academy_id: 학원 ID
    - student_id: 학생 ID (FK)
    - amount: 청구 금액
    - description: 청구 내역 설명
    - due_date: 납부 기한
    - status: 상태 (PENDING, SENT, PAID, OVERDUE, CANCELLED)
    - sent_at: 발송 시간
    - paid_at: 납부 시간
    - payment_id: 연결된 결제 ID (FK)
    - created_at: 생성 시간
    """
    __tablename__ = "Invoices"

    invoice_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="청구서 고유 ID"
    )

    academy_id = Column(
        Integer,
        nullable=False,
        comment="학원 ID"
    )

    student_id = Column(
        Integer,
        ForeignKey("Students.student_id", ondelete="CASCADE"),
        nullable=False,
        comment="학생 ID"
    )

    amount = Column(
        Integer,
        nullable=False,
        comment="청구 금액 (원)"
    )

    description = Column(
        String(500),
        nullable=True,
        comment="청구 내역 설명"
    )

    due_date = Column(
        Date,
        nullable=False,
        comment="납부 기한"
    )

    status = Column(
        Enum(InvoiceStatus, values_callable=lambda x: [e.value for e in x]),
        default=InvoiceStatus.PENDING,
        nullable=False,
        comment="상태 (PENDING, SENT, PAID, OVERDUE, CANCELLED)"
    )

    sent_at = Column(
        TIMESTAMP,
        nullable=True,
        comment="발송 시간"
    )

    paid_at = Column(
        TIMESTAMP,
        nullable=True,
        comment="납부 시간"
    )

    payment_id = Column(
        Integer,
        ForeignKey("Payments.payment_id", ondelete="SET NULL"),
        nullable=True,
        comment="연결된 결제 ID"
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )

    # Relationships
    student = relationship("app.models.student.Student", backref="invoices")
    payment = relationship("app.models.payment.Payment", backref="invoice")

    def __repr__(self):
        return f"<Invoice(invoice_id={self.invoice_id}, student_id={self.student_id}, amount={self.amount})>"
