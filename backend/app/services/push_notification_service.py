"""
FCM 푸시 알림 발송 서비스
Firebase Admin SDK를 사용하여 푸시 알림을 발송합니다.
"""

import os
import logging
from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Session

from app.services.fcm_token_service import FCMTokenService

logger = logging.getLogger(__name__)


class PushNotificationService:
    """Firebase Cloud Messaging 푸시 알림 서비스"""
    _initialized = False

    @classmethod
    def initialize(cls):
        """Firebase Admin SDK 초기화"""
        if cls._initialized:
            return

        credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        if not credentials_path or not os.path.exists(credentials_path):
            logger.warning(
                "[FCM] Firebase 서비스 계정 파일이 없습니다. "
                "FIREBASE_CREDENTIALS_PATH를 확인하세요. "
                "푸시 알림 기능이 비활성화됩니다."
            )
            return

        try:
            import firebase_admin
            from firebase_admin import credentials

            cred = credentials.Certificate(credentials_path)
            firebase_admin.initialize_app(cred)
            cls._initialized = True
            logger.info("[FCM] Firebase Admin SDK 초기화 완료")
        except Exception as e:
            logger.error(f"[FCM] Firebase 초기화 실패: {e}")

    @classmethod
    def send_push(
        cls,
        db: Session,
        token: str,
        title: str,
        body: str,
        data: Optional[dict] = None
    ) -> bool:
        """단일 기기에 푸시 알림 발송"""
        if not cls._initialized:
            logger.warning("[FCM] Firebase 미초기화 상태 - 푸시 발송 건너뜀")
            return False

        try:
            from firebase_admin import messaging

            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body
                ),
                data={k: str(v) for k, v in data.items()} if data else None,
                token=token
            )

            messaging.send(message)
            logger.info(f"[FCM] 푸시 발송 성공: {title}")
            return True

        except Exception as e:
            error_str = str(e)
            # 토큰 만료/무효 시 DB에서 삭제
            if "UNREGISTERED" in error_str or "INVALID_ARGUMENT" in error_str:
                logger.warning(f"[FCM] 무효 토큰 삭제: {token[:20]}...")
                FCMTokenService.delete_invalid_token(db, token)
            else:
                logger.error(f"[FCM] 푸시 발송 실패: {e}")
            return False

    @classmethod
    def send_to_user(
        cls,
        db: Session,
        user_id: int,
        title: str,
        body: str,
        data: Optional[dict] = None
    ):
        """사용자의 모든 기기에 푸시 알림 발송"""
        tokens = FCMTokenService.get_tokens_by_user_id(db, user_id)
        for token in tokens:
            cls.send_push(db, token, title, body, data)

    @classmethod
    def send_attendance_notification(
        cls,
        db: Session,
        student,
        action: str,
        time: datetime
    ):
        """출결 알림 발송"""
        if not student.user_id:
            return

        time_str = time.strftime("%H:%M")

        if action == "check_in":
            title = "등원 알림"
            body = f"{student.name} 학생이 등원했습니다. ({time_str})"
        elif action == "check_out":
            title = "하원 알림"
            body = f"{student.name} 학생이 하원했습니다. ({time_str})"
        else:
            return

        data = {
            "type": "attendance",
            "student_id": str(student.student_id),
            "action": action,
            "time": time_str
        }

        cls.send_to_user(db, student.user_id, title, body, data)
