from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class FCMToken(Base):
    """FCM 푸시 알림 토큰 저장 모델"""
    __tablename__ = "fcm_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="FCM 토큰 고유 ID")
    user_id = Column(
        Integer,
        ForeignKey("Users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="사용자 ID"
    )
    fcm_token = Column(
        String(255),
        nullable=False,
        unique=True,
        comment="FCM 토큰 문자열"
    )
    device_info = Column(
        JSON,
        nullable=True,
        comment="기기 정보 (platform, os_version, app_version, device_model)"
    )
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="생성 시간")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="수정 시간")
