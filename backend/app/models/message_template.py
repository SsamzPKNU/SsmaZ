"""
MessageTemplate 모델 정의
메시지 템플릿을 저장하는 테이블
"""

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Index
from sqlalchemy.sql import func
from app.core.database import Base


class MessageTemplate(Base):
    """
    메시지 템플릿 테이블

    학원 또는 선생님별 메시지 템플릿을 저장합니다.

    컬럼 설명:
    - template_id: 템플릿 고유 ID (PK)
    - academy_id: 학원 ID
    - teacher_id: 선생님 ID (NULL이면 학원 공용)
    - name: 템플릿 이름
    - content: 템플릿 내용
    - created_at: 생성 시간
    - updated_at: 수정 시간
    """
    __tablename__ = "MessageTemplates"

    template_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="템플릿 고유 ID"
    )

    academy_id = Column(
        Integer,
        ForeignKey("Academies.academy_id", ondelete="CASCADE"),
        nullable=False,
        comment="학원 ID"
    )

    teacher_id = Column(
        Integer,
        ForeignKey("Users.user_id", ondelete="SET NULL"),
        nullable=True,
        comment="선생님 ID (NULL이면 학원 공용)"
    )

    name = Column(
        String(100),
        nullable=False,
        comment="템플릿 이름"
    )

    content = Column(
        Text,
        nullable=False,
        comment="템플릿 내용"
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )

    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        comment="수정 시간"
    )

    __table_args__ = (
        Index("idx_message_template_academy", "academy_id"),
        Index("idx_message_template_teacher", "teacher_id"),
    )

    def __repr__(self):
        return f"<MessageTemplate(template_id={self.template_id}, name='{self.name}')>"
