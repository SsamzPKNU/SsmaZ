"""
선생님 오답 분석 스키마
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class AnalysisTypeEnum:
    """분석 대상 유형"""
    ASSIGNMENT = "assignment"
    EXAM = "exam"


# ========== 문항별 오답률 ==========

class QuestionAnalysisItem(BaseModel):
    """문항별 오답 분석 항목"""
    question_id: int
    question_number: int
    question_text: str
    category: Optional[str] = None
    difficulty: str
    total_attempts: int = Field(description="총 응시 수")
    wrong_count: int = Field(description="오답 수")
    wrong_rate: float = Field(description="오답률 (%)")
    common_wrong_answers: List[str] = Field(description="자주 틀리는 오답")


class QuestionAnalysisResponse(BaseModel):
    """문항별 오답 분석 응답"""
    items: List[QuestionAnalysisItem]
    total: int
    analysis_period: Optional[str] = None


# ========== 학생별 취약점 ==========

class StudentWeaknessCategory(BaseModel):
    """학생 취약 유형"""
    category: str
    total_questions: int
    wrong_count: int
    wrong_rate: float


class StudentWeaknessItem(BaseModel):
    """학생별 취약점 항목"""
    student_id: int
    student_name: str
    class_id: Optional[int] = None
    class_name: Optional[str] = None
    total_questions: int = Field(description="총 풀이 문제 수")
    total_wrong: int = Field(description="총 오답 수")
    overall_wrong_rate: float = Field(description="전체 오답률 (%)")
    weak_categories: List[StudentWeaknessCategory] = Field(description="취약 유형 목록")


class StudentWeaknessResponse(BaseModel):
    """학생별 취약점 응답"""
    items: List[StudentWeaknessItem]
    total: int


# ========== 단원별 통계 ==========

class UnitStatsItem(BaseModel):
    """단원별 통계 항목"""
    category: str = Field(description="단원/유형명")
    total_questions: int = Field(description="총 문제 수")
    total_attempts: int = Field(description="총 응시 수")
    correct_count: int = Field(description="정답 수")
    wrong_count: int = Field(description="오답 수")
    correct_rate: float = Field(description="정답률 (%)")
    wrong_rate: float = Field(description="오답률 (%)")
    avg_difficulty: str = Field(description="평균 난이도")


class UnitStatsResponse(BaseModel):
    """단원별 통계 응답"""
    items: List[UnitStatsItem]
    total: int
    analysis_period: Optional[str] = None
