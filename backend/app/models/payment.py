"""
Payment 모델 정의
수납/결제 정보를 저장하는 테이블
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Enum, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class PaymentMethod(str, enum.Enum):
    """결제 방법"""
    CARD = "CARD"
    CASH = "CASH"
    TRANSFER = "TRANSFER"


class Payment(Base):
    """
    수납/결제 정보 테이블

    Student와 N:1 관계
    - Student: 학생 정보
    - Payment: 해당 학생의 월별 수강료 납부 내역

    컬럼 설명:
    - payment_id: 결제 고유 ID (PK)
    - student_id: 학생 ID (FK)
    - academy_id: 학원 ID
    - amount: 납부 금액
    - payment_date: 납부일
    - next_payment_date: 다음 납부 예정일
    - method: 결제 방법 (CARD, CASH)
    - created_at: 생성 시간
    """
    __tablename__ = "Payments"

    payment_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="결제 고유 ID"
    )

    student_id = Column(
        Integer,
        ForeignKey("Students.student_id"),
        nullable=False,
        comment="학생 ID"
    )

    academy_id = Column(
        Integer,
        nullable=False,
        comment="학원 ID"
    )

    amount = Column(
        Integer,
        nullable=False,
        comment="납부 금액 (원)"
    )

    payment_date = Column(
        Date,
        nullable=True,
        comment="납부일"
    )

    next_payment_date = Column(
        Date,
        nullable=True,
        comment="다음 납부 예정일"
    )

    method = Column(
        Enum(PaymentMethod),
        nullable=True,
        comment="결제 방법 (CARD, CASH)"
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )

    # Relationships
    student = relationship("app.models.student.Student", backref="payments")

    def __repr__(self):
        return f"<Payment(payment_id={self.payment_id}, student_id={self.student_id}, amount={self.amount})>"
