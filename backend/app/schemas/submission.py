"""
Submission 관련 Pydantic 스키마
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SubmissionStatus(str, Enum):
    """제출 상태"""
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    GRADED = "GRADED"


# ========================================
# Answer 스키마
# ========================================

class AnswerInput(BaseModel):
    """답안 입력"""
    question_id: int = Field(..., description="문제 ID")
    student_answer: str = Field(..., description="학생 답안")


class AnswerResponse(BaseModel):
    """답안 응답"""
    answer_id: int
    question_id: int
    student_answer: Optional[str]
    is_correct: Optional[bool]
    points_earned: int

    class Config:
        from_attributes = True


class AnswerDetailResponse(BaseModel):
    """답안 상세 응답 (문제 정보 포함)"""
    answer_id: int
    question_id: int
    question_number: int
    question_text: str
    student_answer: Optional[str]
    correct_answer: str
    is_correct: Optional[bool]
    points_earned: int
    max_points: int

    class Config:
        from_attributes = True


# ========================================
# Submission 스키마
# ========================================

class SubmissionStart(BaseModel):
    """과제 시작 요청"""
    assignment_id: int = Field(..., description="과제 ID")


class SubmissionAnswersUpdate(BaseModel):
    """답안 저장 요청"""
    answers: List[AnswerInput] = Field(..., min_length=1, description="답안 목록")


class SubmissionResponse(BaseModel):
    """제출 기록 응답"""
    submission_id: int
    assignment_id: int
    student_id: int
    status: SubmissionStatus
    total_score: int
    max_score: int
    submitted_at: Optional[datetime]
    graded_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubmissionDetailResponse(BaseModel):
    """제출 상세 응답 (답안 포함)"""
    submission_id: int
    assignment_id: int
    assignment_title: str
    student_id: int
    student_name: str
    status: SubmissionStatus
    total_score: int
    max_score: int
    submitted_at: Optional[datetime]
    graded_at: Optional[datetime]
    answers: List[AnswerResponse]
    created_at: datetime

    class Config:
        from_attributes = True


class SubmissionListItem(BaseModel):
    """제출 목록 항목"""
    submission_id: int
    assignment_id: int
    assignment_title: str
    status: SubmissionStatus
    total_score: int
    max_score: int
    submitted_at: Optional[datetime]
    graded_at: Optional[datetime]

    class Config:
        from_attributes = True


class SubmissionWithStudentItem(BaseModel):
    """제출 목록 항목 (학생 정보 포함)"""
    submission_id: int
    assignment_id: int
    student_id: int
    student_name: str
    status: SubmissionStatus
    total_score: int
    max_score: int
    submitted_at: Optional[datetime]
    graded_at: Optional[datetime]

    class Config:
        from_attributes = True


class SubmissionWithStudentListResponse(BaseModel):
    """제출 목록 응답 (학생 정보 포함)"""
    items: List[SubmissionWithStudentItem]
    total: int


class SubmissionListResponse(BaseModel):
    """제출 목록 응답"""
    items: List[SubmissionListItem]
    total: int


# ========================================
# 채점 결과 스키마
# ========================================

class GradeResult(BaseModel):
    """채점 결과"""
    submission_id: int
    total_score: int
    max_score: int
    percentage: float
    correct_count: int
    wrong_count: int
    wrong_question_ids: List[int]


class GradeDetailResult(BaseModel):
    """채점 상세 결과"""
    submission_id: int
    assignment_title: str
    student_name: str
    total_score: int
    max_score: int
    percentage: float
    answers: List[AnswerDetailResponse]
    graded_at: datetime

    class Config:
        from_attributes = True
