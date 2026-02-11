"""
FCM 토큰 관리 API
앱에서 FCM 푸시 토큰을 등록/삭제하는 엔드포인트
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.fcm_token import (
    FCMTokenRegisterRequest,
    FCMTokenDeleteRequest,
    FCMTokenResponse,
)
from app.services.fcm_token_service import FCMTokenService

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
