"""
관리자용 학생 성적/과제 조회 스키마
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


# ========== 공통 Enum ==========

class StudentAssignmentStatusEnum(str, Enum):
    """학생별 과제 상태 (스키마용)"""
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    GRADED = "GRADED"


class AssignmentStatusFilterEnum(str, Enum):
    """과제 상태 필터"""
    COMPLETED = "completed"
    INCOMPLETE = "incomplete"


# ========== 성적 조회 스키마 ==========

class AdminGradeStats(BaseModel):
    """성적 통계"""
    total_count: int = Field(description="전체 성적 수")
    average_percentage: float = Field(description="평균 점수율 (%)")
    highest_percentage: float = Field(description="최고 점수율 (%)")
    lowest_percentage: float = Field(description="최저 점수율 (%)")


class AdminGradeItem(BaseModel):
    """성적 조회 항목"""
    submission_id: int
    student_id: int
    student_name: str
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    assignment_id: int
    assignment_title: str
    total_score: int
    max_score: int
    percentage: float = Field(description="점수율 (%)")
    status: str
    submitted_at: Optional[datetime] = None
    graded_at: Optional[datetime] = None


class AdminGradeListResponse(BaseModel):
    """성적 목록 응답"""
    records: List[AdminGradeItem]
    total: int
    page: int
    limit: int
    stats: AdminGradeStats


# ========== 과제 현황 스키마 ==========

class AdminAssignmentStats(BaseModel):
    """과제 현황 통계"""
    total_assignments: int = Field(description="전체 과제 수")
    active_count: int = Field(description="활성 과제 수")
    average_completion_rate: float = Field(description="평균 완료율 (%)")


class AdminAssignmentItem(BaseModel):
    """과제 현황 항목"""
    assignment_id: int
    title: str
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    teacher_id: int
    teacher_name: str
    due_date: Optional[date] = None
    is_active: bool
    total_students: int = Field(description="대상 학생 수")
    submitted_count: int = Field(description="제출 학생 수")
    graded_count: int = Field(description="채점 완료 수")
    completion_rate: float = Field(description="완료율 (%)")
    created_at: datetime


class AdminAssignmentListResponse(BaseModel):
    """과제 현황 목록 응답"""
    records: List[AdminAssignmentItem]
    total: int
    page: int
    limit: int
    stats: AdminAssignmentStats


# ========== 학생별 과제 상태 스키마 ==========

class AdminStudentAssignmentItem(BaseModel):
    """학생별 과제 상태 항목"""
    student_id: int
    student_name: str
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    assignment_id: int
    assignment_title: str
    due_date: Optional[date] = None
    status: str = Field(description="과제 상태 (NOT_STARTED, IN_PROGRESS, SUBMITTED, GRADED)")
    total_score: Optional[int] = None
    max_score: Optional[int] = None
    percentage: Optional[float] = Field(None, description="점수율 (채점 완료 시)")
    submitted_at: Optional[datetime] = None


class AdminStudentAssignmentStats(BaseModel):
    """학생별 과제 통계"""
    total_count: int = Field(description="전체 항목 수")
    completed_count: int = Field(description="완료 (제출+채점) 수")
    incomplete_count: int = Field(description="미완료 (미시작+진행중) 수")
    completion_rate: float = Field(description="완료율 (%)")


class AdminStudentAssignmentListResponse(BaseModel):
    """학생별 과제 상태 목록 응답"""
    records: List[AdminStudentAssignmentItem]
    total: int
    page: int
    limit: int
    stats: AdminStudentAssignmentStats
