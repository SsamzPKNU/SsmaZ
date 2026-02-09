"""
Message 모델 정의
단체 메시지 발송 내역을 저장하는 테이블
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, Text, Enum, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class MessageTargetGroup(str, enum.Enum):
    """메시지 대상 그룹"""
    PARENTS = "parents"              # 학부모 전체
    STUDENTS = "students"            # 학생 전체
    TEACHERS = "teachers"            # 선생님 전체
    SPECIFIC_CLASSES = "specific_classes"  # 특정 반


class MessageType(str, enum.Enum):
    """메시지 유형"""
    NORMAL = "normal"
    URGENT = "urgent"
    NOTICE = "notice"


class MessageStatus(str, enum.Enum):
    """메시지 발송 상태"""
    PENDING = "pending"    # 대기 중
    SENDING = "sending"    # 발송 중
    COMPLETED = "completed"  # 발송 완료
    FAILED = "failed"      # 발송 실패


class Message(Base):
    """
    메시지 발송 내역 테이블
    
    단체 메시지 발송 기록을 저장합니다.
    - 발송 대상 그룹
    - 발송 성공/실패 건수
    - 발송 내용
    
    컬럼 설명:
    - message_id: 메시지 고유 ID (PK)
    - academy_id: 학원 ID
    - target_group: 대상 그룹 (parents, students, teachers, specific_classes)
    - target_ids: 특정 대상 ID 목록 (JSON 문자열)
    - title: 제목
    - content: 내용
    - sent_count: 발송 건수
    - success_count: 성공 건수
    - fail_count: 실패 건수
    - status: 발송 상태
    - sent_at: 발송 시간
    - created_at: 생성 시간
    """
    __tablename__ = "Messages"
    
    message_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="메시지 고유 ID"
    )
    
    academy_id = Column(
        Integer,
        nullable=False,
        comment="학원 ID"
    )

    teacher_id = Column(
        Integer,
        ForeignKey("Users.user_id"),
        nullable=True,
        comment="발송 교사 ID"
    )

    class_id = Column(
        Integer,
        nullable=True,
        comment="대상 반 ID"
    )

    target_group = Column(
        Enum(MessageTargetGroup),
        nullable=False,
        comment="대상 그룹 (parents, students, teachers, specific_classes)"
    )
    
    target_ids = Column(
        Text,
        nullable=True,
        comment="특정 대상 ID 목록 (JSON 배열 문자열)"
    )
    
    title = Column(
        String(200),
        nullable=False,
        comment="제목"
    )
    
    content = Column(
        Text,
        nullable=False,
        comment="내용"
    )

    message_type = Column(
        Enum(MessageType, values_callable=lambda x: [e.value for e in x]),
        default=MessageType.NORMAL,
        nullable=False,
        comment="메시지 유형 (normal, urgent, notice)"
    )

    template_id = Column(
        Integer,
        nullable=True,
        comment="사용한 템플릿 ID"
    )

    sent_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="발송 건수"
    )
    
    success_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="성공 건수"
    )
    
    fail_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="실패 건수"
    )
    
    status = Column(
        Enum(MessageStatus),
        default=MessageStatus.PENDING,
        nullable=False,
        comment="발송 상태 (pending, sending, completed, failed)"
    )
    
    sent_at = Column(
        TIMESTAMP,
        nullable=True,
        comment="발송 시간"
    )
    
    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )
    
    def __repr__(self):
        return f"<Message(message_id={self.message_id}, title='{self.title}', sent_count={self.sent_count})>"
