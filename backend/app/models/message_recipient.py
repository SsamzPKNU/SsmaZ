"""
MessageRecipient 모델 정의
메시지 수신자별 발송 상태를 저장하는 테이블
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, Enum, Index
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class RecipientStatus(str, enum.Enum):
    """수신자 발송 상태"""
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


class MessageRecipient(Base):
    """
    메시지 수신자 테이블

    메시지별 수신 학생과 발송 상태를 기록합니다.

    컬럼 설명:
    - recipient_id: 수신 레코드 ID (PK)
    - message_id: 메시지 ID (FK → Messages)
    - student_id: 수신 학생 ID (FK → Students)
    - status: 발송 상태 (sent, delivered, failed)
    - error_message: 실패 사유
    - created_at: 생성 시간
    """
    __tablename__ = "MessageRecipients"

    recipient_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="수신 레코드 ID"
    )

    message_id = Column(
        Integer,
        ForeignKey("Messages.message_id", ondelete="CASCADE"),
        nullable=False,
        comment="메시지 ID"
    )

    student_id = Column(
        Integer,
        ForeignKey("Students.student_id", ondelete="CASCADE"),
        nullable=False,
        comment="수신 학생 ID"
    )

    status = Column(
        Enum(RecipientStatus, values_callable=lambda x: [e.value for e in x]),
        default=RecipientStatus.SENT,
        nullable=False,
        comment="발송 상태 (sent, delivered, failed)"
    )

    error_message = Column(
        String(200),
        nullable=True,
        comment="실패 사유"
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )

    __table_args__ = (
        Index("idx_msg_recipient_message", "message_id"),
        Index("idx_msg_recipient_student", "student_id"),
    )

    def __repr__(self):
        return f"<MessageRecipient(recipient_id={self.recipient_id}, message_id={self.message_id}, student_id={self.student_id})>"
