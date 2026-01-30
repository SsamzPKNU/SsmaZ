"""
선생님 프린트 관리 스키마
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class PrintDocumentType(str, Enum):
    """프린트 문서 유형"""
    ASSIGNMENT = "assignment"
    EXAM = "exam"
    REPORT = "report"


class PrintLayoutType(str, Enum):
    """프린트 레이아웃"""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"


# ========== 과제 목록 ==========

class PrintAssignmentItem(BaseModel):
    """프린트용 과제 항목"""
    assignment_id: int
    title: str
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    due_date: Optional[date] = None
    question_count: int
    total_points: int
    assignment_type: str
    created_at: datetime


class PrintAssignmentListResponse(BaseModel):
    """프린트용 과제 목록 응답"""
    items: List[PrintAssignmentItem]
    total: int


# ========== 시험 목록 ==========

class PrintExamItem(BaseModel):
    """프린트용 시험 항목"""
    assignment_id: int
    title: str
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    due_date: Optional[date] = None
    question_count: int
    total_points: int
    submission_count: int
    avg_score: Optional[float] = None
    created_at: datetime


class PrintExamListResponse(BaseModel):
    """프린트용 시험 목록 응답"""
    items: List[PrintExamItem]
    total: int


# ========== 리포트 목록 ==========

class PrintReportItem(BaseModel):
    """프린트용 리포트 항목"""
    student_id: int
    student_name: str
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    assignment_count: int
    completed_count: int
    avg_score: Optional[float] = None
    last_activity: Optional[datetime] = None


class PrintReportListResponse(BaseModel):
    """프린트용 리포트 목록 응답"""
    items: List[PrintReportItem]
    total: int


# ========== PDF 생성 ==========

class PDFGenerateRequest(BaseModel):
    """PDF 생성 요청"""
    document_type: PrintDocumentType = Field(..., description="문서 유형")
    document_id: int = Field(..., description="문서 ID (과제 ID, 학생 ID 등)")
    show_answers: bool = Field(default=False, description="정답 표시 여부")
    show_points: bool = Field(default=True, description="배점 표시 여부")
    layout: PrintLayoutType = Field(default=PrintLayoutType.PORTRAIT, description="레이아웃")


class PDFGenerateResponse(BaseModel):
    """PDF 생성 응답"""
    success: bool
    file_name: str
    file_size: int = Field(description="파일 크기 (bytes)")
    download_url: str = Field(description="다운로드 URL")
