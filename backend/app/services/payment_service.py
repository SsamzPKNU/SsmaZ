"""
수납/결제 관리 관련 비즈니스 로직
수납 CRUD 및 통계 기능 제공
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, extract, func
from fastapi import HTTPException, status as http_status
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.models.student import Student
from app.schemas.payment import (
    PaymentCreate,
    PaymentConfirm,
    PaymentResponse,
    PaymentSummary
)
from datetime import date, datetime
from typing import List, Optional, Tuple


class PaymentService:
    """수납/결제 관리 서비스 클래스"""
    
    @staticmethod
    def get_monthly_summary(db: Session, academy_id: int, month_str: str) -> PaymentSummary:
        """
        월별 수납 현황 요약 조회
        
        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            month_str: 대상 월 (YYYY-MM)
            
        Returns:
            PaymentSummary: 월별 수납 현황
        """
        # 년-월 파싱
        year, month = map(int, month_str.split('-'))
        
        # 해당 월의 모든 수납 내역
        payments = db.query(Payment).filter(
            and_(
                Payment.academy_id == academy_id,
                extract('year', Payment.due_date) == year,
                extract('month', Payment.due_date) == month
            )
        ).all()
        
        # 예상 총액
        total_expected = sum(p.amount for p in payments)
        
        # 실제 수납액 (paid 상태만)
        total_collected = sum(p.amount for p in payments if p.status == PaymentStatus.PAID)
        
        # 수납률 계산
        collection_rate = (total_collected / total_expected * 100) if total_expected > 0 else 0.0
        
        # 미납 인원수
        unpaid_count = sum(1 for p in payments if p.status != PaymentStatus.PAID)
        
        return PaymentSummary(
            month=month_str,
            total_expected=total_expected,
            total_collected=total_collected,
            collection_rate=round(collection_rate, 1),
            unpaid_count=unpaid_count
        )
    
    @staticmethod
    def get_payments(
        db: Session,
        academy_id: int,
        month: Optional[str] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """
        수납 내역 목록 조회
        
        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            month: 대상 월 필터 (YYYY-MM)
            status: 상태 필터
            skip: 페이지네이션 오프셋
            limit: 페이지네이션 제한
            
        Returns:
            List[Payment]: 수납 내역 목록
        """
        query = db.query(Payment).filter(Payment.academy_id == academy_id)
        
        # 월 필터
        if month:
            year, month_num = map(int, month.split('-'))
            query = query.filter(
                and_(
                    extract('year', Payment.due_date) == year,
                    extract('month', Payment.due_date) == month_num
                )
            )
        
        # 상태 필터
        if status:
            query = query.filter(Payment.status == status)
        
        # 정렬 및 페이지네이션
        payments = query.order_by(Payment.due_date.desc()).offset(skip).limit(limit).all()
        
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
            due_date=payment_data.due_date,
            status=PaymentStatus.UNPAID,
            memo=payment_data.memo
        )
        
        db.add(new_payment)
        db.commit()
        db.refresh(new_payment)
        
        return new_payment
    
    @staticmethod
    def confirm_payment(
        db: Session,
        payment_id: int,
        academy_id: int,
        confirm_data: PaymentConfirm
    ) -> Payment:
        """
        수납 처리 (관리자 수동 처리)
        
        Args:
            db: 데이터베이스 세션
            payment_id: 결제 ID
            academy_id: 학원 ID
            confirm_data: 수납 처리 정보
            
        Returns:
            Payment: 수납 처리된 내역
            
        Raises:
            HTTPException: 수납 내역을 찾을 수 없는 경우
        """
        payment = PaymentService.get_payment_by_id(db, payment_id, academy_id)
        
        if not payment:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="수납 내역을 찾을 수 없습니다"
            )
        
        # 수납 처리
        payment.status = PaymentStatus.PAID
        payment.paid_date = confirm_data.paid_date
        payment.method = confirm_data.method
        if confirm_data.memo:
            payment.memo = confirm_data.memo
        
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
            id=payment.payment_id,
            student_name=student.name if student else "Unknown",
            parent_phone=student.parent_phone if student else "Unknown",
            amount=payment.amount,
            due_date=payment.due_date,
            status=payment.status.value,
            last_reminded=payment.last_reminded,
            paid_date=payment.paid_date,
            method=payment.method.value if payment.method else None,
            memo=payment.memo
        )
