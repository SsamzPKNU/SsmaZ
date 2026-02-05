"""
FAQ 챗봇 API 스키마
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """FAQ 챗봇 질문 요청"""
    question: str = Field(..., min_length=1, description="질문 내용", example="수업료는 얼마인가요?")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "수업료는 얼마인가요?"
            }
        }


class ChatErrorResponse(BaseModel):
    """FAQ 챗봇 에러 응답"""
    detail: str = Field(..., description="에러 메시지")
    error_code: str = Field(..., description="에러 코드")

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "ChromaDB 연결에 실패했습니다",
                "error_code": "CHROMADB_CONNECTION_ERROR"
            }
        }
