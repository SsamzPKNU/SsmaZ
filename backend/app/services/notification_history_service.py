from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.notification_history import NotificationHistory


class NotificationHistoryService:
    """알림 이력 관리 서비스"""

    @staticmethod
    def create_log(
        db: Session,
        user_id: int,
        title: str,
        body: Optional[str] = None,
        notification_type: Optional[str] = None,
        data: Optional[dict] = None,
        status: str = "success"
    ) -> NotificationHistory:
        """알림 이력 저장"""
        log = NotificationHistory(
            user_id=user_id,
            title=title,
            body=body,
            notification_type=notification_type,
            data=data,
            status=status
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def get_by_user_id(
        db: Session,
        user_id: int,
        page: int = 1,
        size: int = 20
    ) -> dict:
        """사용자별 알림 이력 조회 (페이지네이션)"""
        query = db.query(NotificationHistory).filter(
            NotificationHistory.user_id == user_id
        )
        total = query.count()
        items = query.order_by(NotificationHistory.created_at.desc()) \
            .offset((page - 1) * size) \
            .limit(size) \
            .all()

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size
        }
