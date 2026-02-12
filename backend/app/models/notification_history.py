from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class NotificationHistory(Base):
    """FCM 푸시 알림 발송 이력 모델"""
    __tablename__ = "notification_history"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="알림 이력 고유 ID")
    user_id = Column(
        Integer,
        ForeignKey("Users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="수신 대상 사용자 ID"
    )
    title = Column(String(255), nullable=False, comment="알림 제목")
    body = Column(Text, nullable=True, comment="알림 본문")
    notification_type = Column(String(50), nullable=True, comment="알림 유형 (attendance, assignment, schedule, payment 등)")
    data = Column(JSON, nullable=True, comment="알림 data 페이로드")
    status = Column(String(20), nullable=False, server_default="success", comment="발송 상태 (success, failed, skipped)")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="생성 시간")
