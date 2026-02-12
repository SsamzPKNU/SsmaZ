"""
FCM 푸시 알림 발송 서비스
Firebase Admin SDK를 사용하여 푸시 알림을 발송합니다.
"""

import os
import logging
from typing import Optional, List
from datetime import datetime

from sqlalchemy.orm import Session

from app.services.fcm_token_service import FCMTokenService
from app.services.notification_history_service import NotificationHistoryService

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

        # 알림 유형 추출 (data 페이로드의 type 필드)
        notification_type = data.get("type") if data else None

        if not tokens:
            # 토큰이 없으면 skipped로 기록
            NotificationHistoryService.create_log(
                db=db,
                user_id=user_id,
                title=title,
                body=body,
                notification_type=notification_type,
                data=data,
                status="skipped"
            )
            return

        if not cls._initialized:
            # Firebase 미초기화 상태
            NotificationHistoryService.create_log(
                db=db,
                user_id=user_id,
                title=title,
                body=body,
                notification_type=notification_type,
                data=data,
                status="skipped"
            )
            for token in tokens:
                cls.send_push(db, token, title, body, data)
            return

        # 발송 시도
        any_success = False
        for token in tokens:
            result = cls.send_push(db, token, title, body, data)
            if result:
                any_success = True

        NotificationHistoryService.create_log(
            db=db,
            user_id=user_id,
            title=title,
            body=body,
            notification_type=notification_type,
            data=data,
            status="success" if any_success else "failed"
        )

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

    @classmethod
    def _get_user_ids_by_class(cls, db: Session, class_id: int) -> List[int]:
        """반 소속 학생들의 user_id 목록 반환 (user_id가 있는 학생만)"""
        from app.models.student import Student
        students = db.query(Student).filter(
            Student.class_id == class_id,
            Student.user_id.isnot(None)
        ).all()
        return [s.user_id for s in students]

    @classmethod
    def send_assignment_notification(
        cls,
        db: Session,
        assignment,
        class_name: str
    ):
        """과제 알림 발송 - 반 소속 학생들에게"""
        if not assignment.class_id:
            return

        user_ids = cls._get_user_ids_by_class(db, assignment.class_id)

        title = "새 과제가 등록되었습니다"
        body = f"{class_name} - {assignment.title}"
        data = {
            "type": "assignment",
            "assignmentId": str(assignment.assignment_id)
        }

        for user_id in user_ids:
            cls.send_to_user(db, user_id, title, body, data)

    @classmethod
    def send_schedule_notification(
        cls,
        db: Session,
        class_id: int,
        class_name: str,
        body_text: str,
        schedule_id: int
    ):
        """일정 변경 알림 발송 - 반 소속 학생들에게"""
        user_ids = cls._get_user_ids_by_class(db, class_id)

        title = "수업 일정이 변경되었습니다"
        data = {
            "type": "schedule",
            "scheduleId": str(schedule_id)
        }

        for user_id in user_ids:
            cls.send_to_user(db, user_id, title, body_text, data)

    @classmethod
    def send_payment_notification(
        cls,
        db: Session,
        student,
        title: str,
        body: str,
        payment_id: int
    ):
        """수납 알림 발송 - 개별 학생에게"""
        if not student.user_id:
            return

        data = {
            "type": "payment",
            "paymentId": str(payment_id)
        }

        cls.send_to_user(db, student.user_id, title, body, data)

    @classmethod
    def send_message_notification(
        cls,
        db: Session,
        student_ids: List[int],
        sender_name: str
    ):
        """메시지 알림 발송 - 대상 학생들에게"""
        from app.models.student import Student

        title = "새 메시지가 도착했습니다"
        body = f"{sender_name} 선생님이 메시지를 보냈습니다"
        data = {"type": "message"}

        for student_id in student_ids:
            student = db.query(Student).filter(
                Student.student_id == student_id
            ).first()
            if student and student.user_id:
                cls.send_to_user(db, student.user_id, title, body, data)
