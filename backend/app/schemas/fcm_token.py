from typing import Optional
from pydantic import BaseModel


class DeviceInfo(BaseModel):
    """기기 정보"""
    platform: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    device_model: Optional[str] = None


class FCMTokenRegisterRequest(BaseModel):
    """FCM 토큰 등록 요청"""
    fcm_token: str
    device_info: Optional[DeviceInfo] = None


class FCMTokenDeleteRequest(BaseModel):
    """FCM 토큰 삭제 요청"""
    fcm_token: str


class FCMTokenResponse(BaseModel):
    """FCM 토큰 응답"""
    success: bool
    message: str
