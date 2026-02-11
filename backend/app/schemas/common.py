"""
공통 응답 모델
에러 응답 등 여러 라우터에서 공유하는 스키마
"""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


COMMON_RESPONSES = {
    401: {"model": ErrorResponse, "description": "인증 필요 - 토큰 누락 또는 유효하지 않음"},
    403: {"model": ErrorResponse, "description": "권한 없음 - 해당 리소스 접근 불가"},
    422: {"description": "유효성 검사 실패 - 요청 파라미터 오류"},
}

NOT_FOUND_RESPONSE = {
    404: {"model": ErrorResponse, "description": "리소스를 찾을 수 없음"},
}
