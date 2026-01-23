"""
키오스크 API 스키마 정의
학원 태블릿 키오스크용 API 요청/응답 모델
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# === 요청 스키마 ===

class StudentLookupRequest(BaseModel):
    """
    학생 조회 요청
    전화번호 뒷자리 4자리로 학생을 조회합니다.
    """
    academy_id: int = Field(..., description="학원 ID")
    phone_last_four: str = Field(
        ...,
        min_length=4,
        max_length=4,
        pattern=r"^\d{4}$",
        description="학부모 전화번호 뒷자리 4자리"
    )


class AttendanceRequest(BaseModel):
    """
    출결 처리 요청
    등원 또는 하원 처리를 수행합니다.
    """
    student_id: int = Field(..., description="학생 ID")
    academy_id: int = Field(..., description="학원 ID")


# === 응답 스키마 ===

class StudentInfo(BaseModel):
    """
    학생 정보 (조회 결과용)
    """
    student_id: int = Field(..., description="학생 ID")
    name: str = Field(..., description="학생 이름")
    # 개인정보 보호를 위해 전화번호 뒷자리만 포함

    class Config:
        from_attributes = True


class StudentLookupResponse(BaseModel):
    """
    학생 조회 응답
    """
    success: bool = Field(..., description="조회 성공 여부")
    students: List[StudentInfo] = Field(default=[], description="조회된 학생 목록")
    message: Optional[str] = Field(None, description="메시지 (에러 또는 안내)")


class AttendanceResponse(BaseModel):
    """
    출결 처리 응답
    """
    success: bool = Field(..., description="처리 성공 여부")
    action: Optional[str] = Field(None, description="처리 유형 (check_in 또는 check_out)")
    student_name: Optional[str] = Field(None, description="학생 이름")
    time: Optional[datetime] = Field(None, description="처리 시간")
    message: Optional[str] = Field(None, description="결과 메시지")


class AcademyInfoResponse(BaseModel):
    """
    학원 정보 조회 응답
    """
    success: bool = Field(..., description="조회 성공 여부")
    academy_id: Optional[int] = Field(None, description="학원 ID")
    academy_name: Optional[str] = Field(None, description="학원 이름")
    message: Optional[str] = Field(None, description="에러 메시지")
