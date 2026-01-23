"""
결제 관련 데이터베이스 모델
Payment 모델 정의
수납/결제 정보를 저장하는 테이블
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Enum, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


    - CASH: 현금 결제
class PaymentStatus(str, enum.Enum):
    """결제 상태"""
    UNPAID = "unpaid"      # 미납
    PAID = "paid"          # 납부 완료
    OVERDUE = "overdue"    # 연체


class PaymentMethod(str, enum.Enum):
    """결제 방법"""
    CARD = "card"          # 카드
    CASH = "cash"          # 현금
    TRANSFER = "transfer"  # 계좌이체


class Payment(Base):
    """
    - student_id: 학생 ID (Students 테이블 FK)
    토스페이먼츠 연동 추가 필드 (향후 마이그레이션 필요):
    - payment_key: 토스 결제 키 (토스 API 조회/취소 시 사용)
    __tablename__ = "Payments"
    
    # 기본 키
    수납/결제 정보 테이블
    
    Student와 N:1 관계
    - Student: 학생 정보
    - Payment: 해당 학생의 월별 수강료 납부 내역
    
    컬럼 설명:
    - payment_id: 결제 고유 ID (PK)
    - student_id: 학생 ID (FK)
    - academy_id: 학원 ID
    - amount: 납부 금액
    - due_date: 납부 기한일
    - paid_date: 실제 납부일
    - status: 결제 상태 (unpaid, paid, overdue)
    - method: 결제 방법 (card, cash, transfer)
    - memo: 메모
    - last_reminded: 마지막 독촉 문자 발송일
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
    
    due_date = Column(
        Date,
        nullable=False,
        comment="납부 기한일"
    )
    
    paid_date = Column(
        Date,
        nullable=True,
        comment="실제 납부일"
    )
    
    status = Column(
        Enum(PaymentStatus),
        default=PaymentStatus.UNPAID,
        nullable=False,
        comment="결제 상태 (unpaid, paid, overdue)"
    )
    
    method = Column(
        Enum(PaymentMethod),
        nullable=True,
        comment="결제 방법 (card, cash, transfer)"
    )
    
    memo = Column(
        Text,
        nullable=True,
        comment="메모"
    )
    
    last_reminded = Column(
        Date,
        nullable=True,
        comment="마지막 독촉 문자 발송일"
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
        return f"<Payment(payment_id={self.payment_id}, student_id={self.student_id}, amount={self.amount}, status={self.status})>"
