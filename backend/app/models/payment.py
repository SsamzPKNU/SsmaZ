"""
결제 관련 데이터베이스 모델
토스페이먼츠 API와 연동하여 결제 정보를 저장하는 테이블
"""

from sqlalchemy import Column, Integer, String, DECIMAL, DATE, TIMESTAMP, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class PaymentMethod(str, enum.Enum):
    """
    결제 수단 정의
    - CARD: 카드 결제
    - TRANSFER: 계좌이체
    - CASH: 현금 결제
    - VIRTUAL_ACCOUNT: 가상계좌
    """
    CARD = "CARD"
    TRANSFER = "TRANSFER"
    CASH = "CASH"
    VIRTUAL_ACCOUNT = "VIRTUAL_ACCOUNT"


class Payment(Base):
    """
    결제 정보 테이블 (기존 Payments 테이블 매핑)
    
    컬럼 설명:
    - payment_id: 결제 고유 ID (자동 증가)
    - student_id: 학생 ID (Students 테이블 FK)
    - academy_id: 학원 ID (Academies 테이블 FK)
    - amount: 결제 금액
    - payment_date: 결제일
    - next_payment_date: 다음 결제 예정일
    - method: 결제 수단 (CARD, TRANSFER, CASH, VIRTUAL_ACCOUNT)
    - created_at: 레코드 생성 시간
    
    토스페이먼츠 연동 추가 필드 (향후 마이그레이션 필요):
    - payment_key: 토스 결제 키 (토스 API 조회/취소 시 사용)
    - order_id: 주문 ID
    - order_name: 주문명
    - status: 결제 상태
    - approved_at: 결제 승인 시간
    - canceled_at: 취소 시간
    - cancel_reason: 취소 사유
    """
    __tablename__ = "Payments"
    
    # 기본 키
    payment_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="결제 고유 ID"
    )
    
    # 외래 키
    student_id = Column(
        Integer,
        # ForeignKey('Students.student_id'),  # Students 테이블과 연결
        nullable=False,
        comment="학생 ID"
    )
    
    academy_id = Column(
        Integer,
        # ForeignKey('Academies.academy_id'),  # Academies 테이블과 연결
        nullable=False,
        comment="학원 ID"
    )
    
    # 결제 정보
    amount = Column(
        DECIMAL(10, 2),
        nullable=False,
        comment="결제 금액"
    )
    
    payment_date = Column(
        DATE,
        nullable=True,
        comment="결제일"
    )
    
    next_payment_date = Column(
        DATE,
        nullable=True,
        comment="다음 결제 예정일"
    )
    
    method = Column(
        String(20),
        nullable=True,
        comment="결제 수단 (CARD, TRANSFER, CASH, VIRTUAL_ACCOUNT)"
    )
    
    # 생성 시간
    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="레코드 생성 시간"
    )
    
    # 토스페이먼츠 연동 필드 (향후 추가 예정)
    # payment_key = Column(String(200), nullable=True, unique=True, comment="토스 결제 키")
    # order_id = Column(String(100), nullable=True, comment="주문 ID")
    # order_name = Column(String(100), nullable=True, comment="주문명")
    # status = Column(String(50), nullable=True, comment="결제 상태")
    # approved_at = Column(TIMESTAMP, nullable=True, comment="결제 승인 시간")
    # canceled_at = Column(TIMESTAMP, nullable=True, comment="취소 시간")
    # cancel_reason = Column(Text, nullable=True, comment="취소 사유")
    
    def __repr__(self):
        """
        객체를 문자열로 표현 (디버깅용)
        """
        return f"<Payment(payment_id={self.payment_id}, student_id={self.student_id}, amount={self.amount}, method='{self.method}')>"
