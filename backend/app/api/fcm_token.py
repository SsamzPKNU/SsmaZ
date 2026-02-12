"""
FCM 토큰 관리 API
앱에서 FCM 푸시 토큰을 등록/삭제하는 엔드포인트
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.fcm_token import (
    FCMTokenRegisterRequest,
    FCMTokenDeleteRequest,
    FCMTokenResponse,
)
from app.schemas.notification_history import NotificationHistoryListResponse
from app.services.fcm_token_service import FCMTokenService
from app.services.notification_history_service import NotificationHistoryService

router = APIRouter(
    prefix="/api/student",
    tags=["FCM Token"]
)


@router.post("/fcm-token", response_model=FCMTokenResponse)
async def register_fcm_token(
    request: FCMTokenRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """FCM 푸시 토큰 등록"""
    device_info = request.device_info.model_dump() if request.device_info else None

    FCMTokenService.register_token(
        db=db,
        user_id=current_user.user_id,
        fcm_token=request.fcm_token,
        device_info=device_info
    )

    return FCMTokenResponse(
        success=True,
        message="FCM 토큰이 등록되었습니다."
    )


@router.delete("/fcm-token", response_model=FCMTokenResponse)
async def delete_fcm_token(
    request: FCMTokenDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """FCM 푸시 토큰 삭제 (로그아웃 시 호출)"""
    deleted = FCMTokenService.delete_token(
        db=db,
        user_id=current_user.user_id,
        fcm_token=request.fcm_token
    )

    if deleted:
        return FCMTokenResponse(
            success=True,
            message="FCM 토큰이 삭제되었습니다."
        )

    return FCMTokenResponse(
        success=False,
        message="해당 FCM 토큰을 찾을 수 없습니다."
    )


@router.get("/notifications", response_model=NotificationHistoryListResponse)
async def get_notifications(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    알림 이력 조회

    로그인한 사용자의 푸시 알림 이력을 조회합니다.

    Query Parameters:
        - page: 페이지 번호 (기본: 1)
        - size: 페이지 크기 (기본: 20)
    """
    result = NotificationHistoryService.get_by_user_id(
        db=db,
        user_id=current_user.user_id,
        page=page,
        size=size
    )

    return NotificationHistoryListResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        size=result["size"]
    )
