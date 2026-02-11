"""
클래스(반/수업) 관련 Pydantic 스키마
API 요청/응답 데이터 검증 및 직렬화
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class ClassStatus(str, Enum):
    """클래스 상태 Enum (스키마용)"""
    ACTIVE = "active"       # 운영중
    INACTIVE = "inactive"   # 비활성
    PENDING = "pending"     # 대기
    CLOSED = "closed"       # 종료


class ClassBase(BaseModel):
    """클래스 기본 정보 스키마"""
    name: str = Field(..., min_length=1, max_length=50, description="반 이름")
    teacher_id: Optional[int] = Field(None, description="담당 선생님 ID")
    capacity: Optional[int] = Field(None, gt=0, description="정원")
    subject: Optional[str] = Field(None, max_length=50, description="과목")
    grade_level: Optional[str] = Field(None, max_length=30, description="학년/레벨")
    fee: Optional[int] = Field(None, ge=0, description="수강료 (원)")


class TeacherByLevel(BaseModel):
    """수준별 선생님 정보"""
    level: str = Field(..., description="수준 (high/mid/low)")
    teacherId: int = Field(..., description="선생님 ID")
    teacherName: Optional[str] = Field(None, description="선생님 이름")


class ClassCreate(ClassBase):
    """클래스 생성 요청 스키마"""
    status: ClassStatus = Field(default=ClassStatus.ACTIVE, description="반 상태")
    teachers_by_level: Optional[Dict[str, int]] = Field(
        None,
        description="수준별 선생님 배정 (예: {\"high\": 11, \"mid\": 10, \"low\": 12})"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "영어 특강반",
                "teacher_id": 10,
                "capacity": 20,
                "subject": "영어",
                "grade_level": "중2",
                "fee": 150000,
                "status": "active",
                "teachers_by_level": {"high": 11, "mid": 10, "low": 12}
            }
        }


class ClassUpdate(BaseModel):
    """클래스 정보 수정 요청 스키마"""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="반 이름")
    teacher_id: Optional[int] = Field(None, description="담당 선생님 ID")
    capacity: Optional[int] = Field(None, gt=0, description="정원")
    subject: Optional[str] = Field(None, max_length=50, description="과목")
    grade_level: Optional[str] = Field(None, max_length=30, description="학년/레벨")
    fee: Optional[int] = Field(None, ge=0, description="수강료 (원)")
    status: Optional[ClassStatus] = Field(None, description="반 상태")
    teachers_by_level: Optional[Dict[str, int]] = Field(
        None,
        description="수준별 선생님 배정 (예: {\"high\": 11, \"mid\": 10, \"low\": 12})"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "수학 고급반",
                "capacity": 25,
                "subject": "수학",
                "fee": 200000,
                "status": "active",
                "teachers_by_level": {"high": 11, "mid": 10, "low": 12}
            }
        }


class ClassResponse(ClassBase):
    """클래스 정보 응답 스키마"""
    id: int = Field(..., description="반 고유 ID")
    teacher_name: Optional[str] = Field(None, description="담당 선생님 이름")
    current_students: int = Field(default=0, description="현재 학생 수")
    status: ClassStatus = Field(default=ClassStatus.ACTIVE, description="반 상태")
    teachers: List[TeacherByLevel] = Field(default=[], description="수준별 선생님 목록")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "수학 정규반 A",
                "teacher_id": 10,
                "teacher_name": "박선생",
                "capacity": 15,
                "current_students": 12,
                "subject": "수학",
                "grade_level": "중3",
                "fee": 200000,
                "status": "active",
                "teachers": [
                    {"level": "high", "teacherId": 11, "teacherName": "김상급"},
                    {"level": "mid", "teacherId": 10, "teacherName": "박선생"},
                    {"level": "low", "teacherId": 12, "teacherName": "이기초"}
                ]
            }
        }


class ClassDetailResponse(ClassResponse):
    """클래스 상세 정보 응답 스키마"""
    students: list = Field(default=[], description="소속 학생 목록")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "수학 정규반 A",
                "teacher_id": 10,
                "teacher_name": "박선생",
                "capacity": 15,
                "current_students": 12,
                "subject": "수학",
                "grade_level": "중3",
                "fee": 200000,
                "status": "active",
                "students": [
                    {"id": 1, "name": "김철수"},
                    {"id": 2, "name": "이영희"}
                ]
            }
        }
