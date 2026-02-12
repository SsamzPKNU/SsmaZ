from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class NotificationHistoryResponse(BaseModel):
    """알림 이력 단건 응답"""
    id: int
    user_id: int
    title: str
    body: Optional[str] = None
    notification_type: Optional[str] = None
    data: Optional[dict] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationHistoryListResponse(BaseModel):
    """알림 이력 목록 응답 (페이지네이션)"""
    items: List[NotificationHistoryResponse]
    total: int
    page: int
    size: int
