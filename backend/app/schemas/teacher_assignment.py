"""
선생님 과제/채점 관리 스키마
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import date, datetime
from enum import Enum


class AssignmentTypeEnum(str, Enum):
    """과제 유형"""
    NORMAL = "NORMAL"
    CLINIC = "CLINIC"


class QuestionTypeEnum(str, Enum):
    """문제 유형"""
    CHOICE = "CHOICE"
    SHORT_ANSWER = "SHORT_ANSWER"
    ESSAY = "ESSAY"


class DifficultyEnum(str, Enum):
    """문제 난이도"""
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


# ========== 문제 스키마 ==========

class QuestionCreateRequest(BaseModel):
    """문제 생성 요청"""
    question_number: int = Field(..., ge=1, description="문제 번호")
    question_text: str = Field(..., min_length=1, description="문제 내용")
    question_type: QuestionTypeEnum = Field(default=QuestionTypeEnum.CHOICE, description="문제 유형")
    options: Optional[List[str]] = Field(None, description="객관식 보기")
    correct_answer: str = Field(..., min_length=1, description="정답")
    points: int = Field(default=1, ge=1, description="배점")
    category: Optional[str] = Field(None, max_length=100, description="문제 유형 (클리닉용)")
    difficulty: DifficultyEnum = Field(default=DifficultyEnum.MEDIUM, description="난이도")


class QuestionResponse(BaseModel):
    """문제 응답"""
    question_id: int
    question_number: int
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    correct_answer: str
    points: int
    category: Optional[str] = None
    difficulty: str

    class Config:
        from_attributes = True


# ========== 과제 스키마 ==========

class AssignmentStats(BaseModel):
    """과제 통계"""
    total: int = Field(description="전체 과제 수")
    active: int = Field(description="진행 중인 과제 수")
    avg_submit_rate: float = Field(description="평균 제출률 (%)")


class AssignmentCreateRequest(BaseModel):
    """과제 생성 요청"""
    title: str = Field(..., min_length=1, max_length=200, description="과제 제목")
    description: Optional[str] = Field(None, description="과제 설명")
    class_id: Optional[int] = Field(None, description="반 ID (NULL이면 개인 과제)")
    due_date: Optional[date] = Field(None, description="마감일")
    assignment_type: AssignmentTypeEnum = Field(default=AssignmentTypeEnum.NORMAL, description="과제 유형")
    questions: List[QuestionCreateRequest] = Field(..., min_length=1, description="문제 목록")


class AssignmentUpdateRequest(BaseModel):
    """과제 수정 요청"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="과제 제목")
    description: Optional[str] = Field(None, description="과제 설명")
    due_date: Optional[date] = Field(None, description="마감일")
    is_active: Optional[bool] = Field(None, description="활성화 여부")


class AssignmentListItem(BaseModel):
    """과제 목록 항목"""
    assignment_id: int
    title: str
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    due_date: Optional[date] = None
    assignment_type: str
    is_active: bool
    question_count: int
    submission_count: int
    submit_rate: float = Field(description="제출률 (%)")
    created_at: datetime


class AssignmentListResponse(BaseModel):
    """과제 목록 응답"""
    items: List[AssignmentListItem]
    total: int
    stats: AssignmentStats


class AssignmentDetailResponse(BaseModel):
    """과제 상세 응답"""
    assignment_id: int
    title: str
    description: Optional[str] = None
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    due_date: Optional[date] = None
    assignment_type: str
    is_active: bool
    questions: List[QuestionResponse]
    submission_count: int
    submit_rate: float
    created_at: datetime
    updated_at: datetime


# ========== 채점 스키마 ==========

class GradingListItem(BaseModel):
    """채점 대기 목록 항목"""
    assignment_id: int
    title: str
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    due_date: Optional[date] = None
    pending_count: int = Field(description="채점 대기 제출 수")
    total_submissions: int = Field(description="전체 제출 수")


class GradingListResponse(BaseModel):
    """채점 대기 목록 응답"""
    items: List[GradingListItem]
    total: int
    total_pending: int = Field(description="전체 채점 대기 수")


class SubmissionListItem(BaseModel):
    """제출 현황 항목"""
    student_id: int
    student_name: str
    class_name: Optional[str] = None
    status: str
    submitted_at: Optional[datetime] = None
    total_score: Optional[int] = None
    max_score: int
    score_rate: Optional[float] = Field(None, description="점수율 (%)")


class SubmissionListResponse(BaseModel):
    """과제별 제출 현황 응답"""
    assignment_id: int
    assignment_title: str
    items: List[SubmissionListItem]
    total: int
    submitted_count: int
    graded_count: int


class AnswerDetail(BaseModel):
    """답안 상세"""
    answer_id: int
    question_id: int
    question_number: int
    question_text: str
    question_type: str
    correct_answer: str
    student_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    points: int
    points_earned: int


class StudentSubmissionDetail(BaseModel):
    """학생별 제출 상세"""
    submission_id: int
    student_id: int
    student_name: str
    status: str
    submitted_at: Optional[datetime] = None
    graded_at: Optional[datetime] = None
    total_score: int
    max_score: int
    answers: List[AnswerDetail]


class GradeAnswerRequest(BaseModel):
    """개별 답안 채점 요청"""
    answer_id: int
    points_earned: int = Field(..., ge=0, description="부여 점수")
    is_correct: bool = Field(..., description="정답 여부")


class GradeSubmissionRequest(BaseModel):
    """채점 저장 요청"""
    answers: List[GradeAnswerRequest] = Field(..., min_length=1, description="채점 결과 목록")
    feedback: Optional[str] = Field(None, description="전체 피드백 (선택)")


class GradeSubmissionResponse(BaseModel):
    """채점 저장 응답"""
    submission_id: int
    status: str
    total_score: int
    max_score: int
    graded_at: datetime


# ========== 간편 채점 스키마 ==========

class QuickGradeItem(BaseModel):
    """간편 채점 항목"""
    student_id: int
    score: int = Field(..., ge=0, description="획득 점수")
    max_score: int = Field(default=100, ge=1, description="최대 점수")
    wrong_questions: Optional[str] = Field(None, description="틀린 문항 번호")
    memo: Optional[str] = Field(None, description="메모")


class QuickGradeRequest(BaseModel):
    """간편 채점 요청"""
    grades: List[QuickGradeItem] = Field(..., min_length=1, description="성적 배열")


class QuickGradeResponse(BaseModel):
    """간편 채점 응답"""
    success: bool
    updated_count: int
    message: str
