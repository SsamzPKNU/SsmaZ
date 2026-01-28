"""
Clinic 관련 Pydantic 스키마
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class ClinicType(str, Enum):
    """클리닉 유형"""
    SAME = "SAME"          # 동일 문제
    SIMILAR = "SIMILAR"    # 유사 문제 (문제은행에서)


class ClinicGenerateRequest(BaseModel):
    """클리닉 과제 생성 요청"""
    submission_id: int = Field(..., description="원본 제출 ID")
    clinic_type: ClinicType = Field(default=ClinicType.SAME, description="클리닉 유형")
    title: Optional[str] = Field(default=None, max_length=200, description="클리닉 제목 (미입력시 자동 생성)")
    due_date: Optional[date] = Field(default=None, description="마감일")


class ClinicGenerateResponse(BaseModel):
    """클리닉 과제 생성 응답"""
    assignment_id: int
    title: str
    original_assignment_id: int
    original_assignment_title: str
    question_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class ClinicListItem(BaseModel):
    """클리닉 목록 항목"""
    assignment_id: int
    title: str
    original_assignment_title: str
    due_date: Optional[date]
    question_count: int
    is_completed: bool  # 학생이 완료했는지
    score: Optional[int]  # 완료시 점수
    max_score: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class ClinicListResponse(BaseModel):
    """클리닉 목록 응답"""
    items: List[ClinicListItem]
    total: int


class WrongQuestionInfo(BaseModel):
    """틀린 문제 정보"""
    question_id: int
    question_number: int
    question_text: str
    student_answer: Optional[str]
    correct_answer: str
    category: Optional[str]


class ClinicPreviewResponse(BaseModel):
    """클리닉 생성 미리보기"""
    submission_id: int
    assignment_title: str
    wrong_questions: List[WrongQuestionInfo]
    total_wrong_count: int
