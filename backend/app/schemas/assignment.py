"""
Assignment 관련 Pydantic 스키마
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class QuestionType(str, Enum):
    """문제 유형"""
    CHOICE = "CHOICE"
    SHORT_ANSWER = "SHORT_ANSWER"
    ESSAY = "ESSAY"


class Difficulty(str, Enum):
    """난이도"""
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class AssignmentType(str, Enum):
    """과제 유형"""
    NORMAL = "NORMAL"
    CLINIC = "CLINIC"


# ========================================
# Question 스키마
# ========================================

class QuestionCreate(BaseModel):
    """문제 생성 요청"""
    question_number: int = Field(..., ge=1, description="문제 번호")
    question_text: str = Field(..., min_length=1, description="문제 내용")
    question_type: QuestionType = Field(default=QuestionType.CHOICE, description="문제 유형")
    options: Optional[List[str]] = Field(default=None, description="객관식 보기")
    correct_answer: str = Field(..., min_length=1, description="정답")
    points: int = Field(default=1, ge=1, description="배점")
    category: Optional[str] = Field(default=None, description="문제 유형 (클리닉용)")
    difficulty: Difficulty = Field(default=Difficulty.MEDIUM, description="난이도")


class QuestionUpdate(BaseModel):
    """문제 수정 요청"""
    question_text: Optional[str] = None
    question_type: Optional[QuestionType] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    points: Optional[int] = Field(default=None, ge=1)
    category: Optional[str] = None
    difficulty: Optional[Difficulty] = None


class QuestionResponse(BaseModel):
    """문제 응답 (정답 포함)"""
    question_id: int
    question_number: int
    question_text: str
    question_type: QuestionType
    options: Optional[List[str]]
    correct_answer: str
    points: int
    category: Optional[str]
    difficulty: Difficulty

    class Config:
        from_attributes = True


class QuestionStudentResponse(BaseModel):
    """문제 응답 (학생용 - 정답 제외)"""
    question_id: int
    question_number: int
    question_text: str
    question_type: QuestionType
    options: Optional[List[str]]
    points: int

    class Config:
        from_attributes = True


# ========================================
# Assignment 스키마
# ========================================

class AssignmentCreate(BaseModel):
    """과제 생성 요청"""
    title: str = Field(..., min_length=1, max_length=200, description="과제 제목")
    description: Optional[str] = Field(default=None, description="과제 설명")
    class_id: Optional[int] = Field(default=None, description="반 ID")
    due_date: Optional[date] = Field(default=None, description="마감일")
    questions: List[QuestionCreate] = Field(..., min_length=1, description="문제 목록")


class AssignmentUpdate(BaseModel):
    """과제 수정 요청"""
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = None
    class_id: Optional[int] = None
    due_date: Optional[date] = None
    is_active: Optional[bool] = None


class AssignmentResponse(BaseModel):
    """과제 상세 응답"""
    assignment_id: int
    academy_id: int
    teacher_id: int
    title: str
    description: Optional[str]
    class_id: Optional[int]
    due_date: Optional[date]
    assignment_type: AssignmentType
    parent_assignment_id: Optional[int]
    is_active: bool
    questions: List[QuestionResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssignmentStudentResponse(BaseModel):
    """과제 상세 응답 (학생용 - 정답 제외)"""
    assignment_id: int
    academy_id: int
    teacher_id: int
    title: str
    description: Optional[str]
    class_id: Optional[int]
    due_date: Optional[date]
    assignment_type: AssignmentType
    is_active: bool
    questions: List[QuestionStudentResponse]
    created_at: datetime

    class Config:
        from_attributes = True


class AssignmentListItem(BaseModel):
    """과제 목록 항목"""
    assignment_id: int
    title: str
    description: Optional[str]
    due_date: Optional[date]
    assignment_type: AssignmentType
    is_active: bool
    question_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class AssignmentListResponse(BaseModel):
    """과제 목록 응답"""
    items: List[AssignmentListItem]
    total: int
