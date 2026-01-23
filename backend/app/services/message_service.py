"""
메시지 관리 관련 비즈니스 로직
단체 메시지 발송 및 이력 관리 기능 제공
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models.message import Message, MessageTargetGroup, MessageStatus
from app.models.student import Student
from app.models.user import User, UserRole
from app.schemas.message import (
    MessageSendRequest,
    MessageSendResponse,
    MessageHistoryResponse,
    MessageDetailResponse
)
from datetime import datetime
from typing import List
import json


class MessageService:
    """메시지 관리 서비스 클래스"""
    
    # SMS 단가 (예시: 1건당 20원)
    SMS_COST_PER_MESSAGE = 20
    
    @staticmethod
    def get_message_history(
        db: Session,
        academy_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Message]:
        """
        메시지 발송 이력 조회
        
        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            skip: 페이지네이션 오프셋
            limit: 페이지네이션 제한
            
        Returns:
            List[Message]: 메시지 발송 이력 목록
        """
        messages = db.query(Message).filter(
            Message.academy_id == academy_id
        ).order_by(
            Message.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return messages
    
    @staticmethod
    def send_bulk_message(
        db: Session,
        academy_id: int,
        message_data: MessageSendRequest
    ) -> MessageSendResponse:
        """
        단체 메시지 발송
        
        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            message_data: 메시지 발송 정보
            
        Returns:
            MessageSendResponse: 발송 결과
        """
        # 대상자 전화번호 목록 수집
        phone_numbers = MessageService._collect_phone_numbers(
            db=db,
            academy_id=academy_id,
            target_group=message_data.target_group,
            target_ids=message_data.target_ids
        )
        
        # 실제 발송 건수
        sent_count = len(phone_numbers)
        
        # TODO: 실제 SMS 발송 API 연동
        # 현재는 시뮬레이션만 수행
        success_count = sent_count  # 모두 성공으로 가정
        fail_count = 0
        
        # 예상 비용 계산
        estimated_cost = sent_count * MessageService.SMS_COST_PER_MESSAGE
        
        # 메시지 발송 기록 저장
        new_message = Message(
            academy_id=academy_id,
            target_group=message_data.target_group,
            target_ids=json.dumps(message_data.target_ids) if message_data.target_ids else None,
            title=message_data.title,
            content=message_data.content,
            sent_count=sent_count,
            success_count=success_count,
            fail_count=fail_count,
            status=MessageStatus.COMPLETED,
            sent_at=datetime.now()
        )
        
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        
        return MessageSendResponse(
            status="success",
            sent_count=sent_count,
            estimated_cost=estimated_cost,
            message_id=new_message.message_id
        )
    
    @staticmethod
    def _collect_phone_numbers(
        db: Session,
        academy_id: int,
        target_group: MessageTargetGroup,
        target_ids: List[int]
    ) -> List[str]:
        """
        대상 그룹에 따라 전화번호 목록 수집
        
        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            target_group: 대상 그룹
            target_ids: 특정 대상 ID 목록
            
        Returns:
            List[str]: 전화번호 목록
        """
        phone_numbers = []
        
        if target_group == MessageTargetGroup.PARENTS:
            # 학부모 전화번호 (학생 테이블의 parent_phone)
            query = db.query(Student.parent_phone).filter(
                Student.academy_id == academy_id
            )
            
            # 특정 학생 지정된 경우
            if target_ids:
                query = query.filter(Student.student_id.in_(target_ids))
            
            phone_numbers = [phone for (phone,) in query.all() if phone]
            
        elif target_group == MessageTargetGroup.STUDENTS:
            # 학생 전화번호
            query = db.query(Student.phone).filter(
                and_(
                    Student.academy_id == academy_id,
                    Student.phone.isnot(None)
                )
            )
            
            if target_ids:
                query = query.filter(Student.student_id.in_(target_ids))
            
            phone_numbers = [phone for (phone,) in query.all() if phone]
            
        elif target_group == MessageTargetGroup.TEACHERS:
            # 선생님 전화번호
            query = db.query(User.phone).filter(
                and_(
                    User.academy_id == academy_id,
                    User.user_role == UserRole.TEACHER,
                    User.phone.isnot(None)
                )
            )
            
            if target_ids:
                query = query.filter(User.user_id.in_(target_ids))
            
            phone_numbers = [phone for (phone,) in query.all() if phone]
        
        # TODO: SPECIFIC_CLASSES 구현 (Class 테이블 연동 후)
        
        # 중복 제거
        return list(set(phone_numbers))
    
    @staticmethod
    def to_history_response(message: Message) -> MessageHistoryResponse:
        """
        Message 모델을 MessageHistoryResponse로 변환
        
        Args:
            message: Message 모델 객체
            
        Returns:
            MessageHistoryResponse: 응답 스키마
        """
        return MessageHistoryResponse(
            id=message.message_id,
            summary=message.title,
            sent_count=message.sent_count,
            success_count=message.success_count,
            fail_count=message.fail_count,
            sent_at=message.sent_at.strftime("%Y-%m-%d %H:%M:%S") if message.sent_at else None
        )
    
    @staticmethod
    def to_detail_response(message: Message) -> MessageDetailResponse:
        """
        Message 모델을 MessageDetailResponse로 변환
        
        Args:
            message: Message 모델 객체
            
        Returns:
            MessageDetailResponse: 상세 응답 스키마
        """
        return MessageDetailResponse(
            id=message.message_id,
            target_group=message.target_group.value,
            title=message.title,
            content=message.content,
            sent_count=message.sent_count,
            success_count=message.success_count,
            fail_count=message.fail_count,
            status=message.status.value,
            sent_at=message.sent_at.strftime("%Y-%m-%d %H:%M:%S") if message.sent_at else None,
            created_at=message.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )
