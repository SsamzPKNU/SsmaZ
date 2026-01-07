from pydantic import BaseModel, Field
from typing import Optional


class ReviewRequest(BaseModel):
    """수업 리뷰 요청 모델"""
    student_name: str = Field(..., description="학생 이름", example="김민수")
    parent_name: Optional[str] = Field(None, description="학부모 이름 (없으면 학생 이름 사용)", example="김민수")
    learning_content: str = Field(..., description="학습 내용", example="영어 문법 - 현재완료 시제를 배웠습니다")
    attitude: str = Field(..., description="수업 태도", example="집중력이 좋았고 질문도 적극적으로 했습니다")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_name": "김민수",
                "parent_name": "김민수",
                "learning_content": "영어 문법 - 현재완료 시제를 배웠습니다",
                "attitude": "집중력이 좋았고 질문도 적극적으로 했습니다"
            }
        }


class ReviewResponse(BaseModel):
    """수업 리뷰 응답 모델"""
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="생성된 문자 메시지")
    error: Optional[str] = Field(None, description="에러 메시지")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "안녕하세요, 김민수 어머님! 오늘 민수는 영어 문법 중 현재완료 시제를 배웠습니다. 집중력이 좋았고 질문도 적극적으로 해서 개념을 잘 이해했습니다. 앞으로도 이런 적극적인 자세로 공부한다면 실력이 쑥쑥 늘 거예요. 감사합니다.",
                "error": None
            }
        }


class HealthResponse(BaseModel):
    """헬스체크 응답 모델"""
    status: str
    ollama_connected: bool
    model_name: str
