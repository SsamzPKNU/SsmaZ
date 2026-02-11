from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.fcm_token import FCMToken
from app.models.student import Student


class FCMTokenService:
    """FCM 토큰 CRUD 서비스"""

    @staticmethod
    def register_token(
        db: Session,
        user_id: int,
        fcm_token: str,
        device_info: Optional[dict] = None
    ) -> FCMToken:
        """토큰 등록 (upsert: 같은 토큰이 있으면 업데이트)"""
        existing = db.query(FCMToken).filter(
            FCMToken.fcm_token == fcm_token
        ).first()

        if existing:
            existing.user_id = user_id
            existing.device_info = device_info
            db.commit()
            db.refresh(existing)
            return existing

        new_token = FCMToken(
            user_id=user_id,
            fcm_token=fcm_token,
            device_info=device_info
        )
        db.add(new_token)
        db.commit()
        db.refresh(new_token)
        return new_token

    @staticmethod
    def delete_token(db: Session, user_id: int, fcm_token: str) -> bool:
        """사용자의 특정 FCM 토큰 삭제"""
        result = db.query(FCMToken).filter(
            FCMToken.user_id == user_id,
            FCMToken.fcm_token == fcm_token
        ).delete()
        db.commit()
        return result > 0

    @staticmethod
    def get_tokens_by_user_id(db: Session, user_id: int) -> List[str]:
        """사용자의 모든 FCM 토큰 반환"""
        tokens = db.query(FCMToken.fcm_token).filter(
            FCMToken.user_id == user_id
        ).all()
        return [t[0] for t in tokens]

    @staticmethod
    def get_tokens_by_student_id(db: Session, student_id: int) -> List[str]:
        """학생에 연결된 user의 FCM 토큰 반환"""
        student = db.query(Student).filter(
            Student.student_id == student_id
        ).first()

        if not student or not student.user_id:
            return []

        return FCMTokenService.get_tokens_by_user_id(db, student.user_id)

    @staticmethod
    def delete_invalid_token(db: Session, fcm_token: str) -> None:
        """만료/무효 토큰 삭제 (발송 실패 시 호출)"""
        db.query(FCMToken).filter(
            FCMToken.fcm_token == fcm_token
        ).delete()
        db.commit()
