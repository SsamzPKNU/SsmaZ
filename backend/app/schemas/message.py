"""
메시지 관련 Pydantic 스키마
API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class MessageTargetGroup(str, Enum):
    """메시지 대상 그룹"""
    PARENTS = "parents"
    STUDENTS = "students"
    TEACHERS = "teachers"
    SPECIFIC_CLASSES = "specific_classes"


class MessageSendRequest(BaseModel):
    """단체 메시지 발송 요청 스키마"""
    target_group: MessageTargetGroup = Field(..., description="대상 그룹")
    target_ids: List[int] = Field(default=[], description="특정 대상 ID 목록 (비어있으면 전체)")
    title: str = Field(..., min_length=1, max_length=200, description="제목")
    content: str = Field(..., min_length=1, description="내용")
    
    class Config:
        json_schema_extra = {
            "example": {
                "target_group": "parents",
                "target_ids": [],
                "title": "설 연휴 휴강 안내",
                "content": "SSamZ 학원입니다. 설 연휴 기간(1/28~1/30)은 휴강입니다."
            }
        }


class MessageSendResponse(BaseModel):
    """메시지 발송 응답 스키마"""
    status: str = Field(..., description="발송 상태 (success, failed)")
    sent_count: int = Field(..., description="발송 건수")
    estimated_cost: int = Field(..., description="예상 비용 (원)")
    message_id: Optional[int] = Field(None, description="메시지 ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "sent_count": 150,
                "estimated_cost": 3000,
                "message_id": 501
            }
        }


class MessageHistoryResponse(BaseModel):
    """메시지 발송 이력 응답 스키마"""
    id: int = Field(..., description="메시지 ID")
    summary: str = Field(..., description="제목 요약")
    sent_count: int = Field(..., description="발송 건수")
    success_count: int = Field(..., description="성공 건수")
    fail_count: int = Field(..., description="실패 건수")
    sent_at: Optional[str] = Field(None, description="발송 시간")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 501,
                "summary": "1월 수강료 안내",
                "sent_count": 145,
                "success_count": 142,
                "fail_count": 3,
                "sent_at": "2026-01-05 10:00:00"
            }
        }


class MessageDetailResponse(BaseModel):
    """메시지 상세 정보 응답 스키마"""
    id: int = Field(..., description="메시지 ID")
    target_group: str = Field(..., description="대상 그룹")
    title: str = Field(..., description="제목")
    content: str = Field(..., description="내용")
    sent_count: int = Field(..., description="발송 건수")
    success_count: int = Field(..., description="성공 건수")
    fail_count: int = Field(..., description="실패 건수")
    status: str = Field(..., description="발송 상태")
    sent_at: Optional[str] = Field(None, description="발송 시간")
    created_at: str = Field(..., description="생성 시간")
    
    class Config:
        from_attributes = True
