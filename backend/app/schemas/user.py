"""
사용자 관련 Pydantic 스키마
API 요청/응답 데이터 검증 및 직렬화
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum
import re


class UserRole(str, Enum):
    """사용자 역할"""
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"


class UserBase(BaseModel):
    """
    사용자 기본 정보 스키마
    회원가입/수정 시 공통으로 사용되는 필드
    """
    username: str = Field(..., min_length=3, max_length=50, description="로그인 ID")
    academy_id: int = Field(..., gt=0, description="소속 학원 ID")
    user_role: UserRole = Field(default=UserRole.TEACHER, description="사용자 역할")
    name: Optional[str] = Field(None, max_length=50, description="실명")
    phone: Optional[str] = Field(None, max_length=20, description="전화번호")
    
    @validator('username')
    def validate_username(cls, v):
        """
        username 검증
        - 영문, 숫자, 언더스코어만 허용
        """
        if not v.replace('_', '').isalnum():
            raise ValueError('username은 영문, 숫자, 언더스코어만 사용 가능합니다')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """
        전화번호 검증 (선택사항)
        - 숫자와 하이픈만 허용
        """
        if v is not None:
            cleaned = v.replace('-', '')
            if not cleaned.isdigit():
                raise ValueError('전화번호는 숫자와 하이픈만 사용 가능합니다')
        return v


class UserCreate(UserBase):
    """
    회원가입 요청 스키마
    비밀번호 필드 추가
    """
    password: str = Field(..., min_length=8, max_length=100, description="비밀번호")
    
    @validator('password')
    def validate_password(cls, v):
        """
        비밀번호 강도 검증
        - 최소 8자 이상
        - 영문자 포함 필수
        - 숫자 포함 필수
        """
        if len(v) < 8:
            raise ValueError('비밀번호는 최소 8자 이상이어야 합니다')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('비밀번호에 영문자가 포함되어야 합니다')
        if not re.search(r'[0-9]', v):
            raise ValueError('비밀번호에 숫자가 포함되어야 합니다')
        return v


class UserLogin(BaseModel):
    """
    로그인 요청 스키마
    """
    username: str = Field(..., description="로그인 ID")
    password: str = Field(..., description="비밀번호")


class UserResponse(UserBase):
    """
    사용자 정보 응답 스키마
    비밀번호는 제외하고 반환
    """
    user_id: int = Field(..., description="사용자 고유 ID")
    created_at: datetime = Field(..., description="계정 생성 시간")
    
    class Config:
        """Pydantic 설정"""
        from_attributes = True  # SQLAlchemy 모델을 Pydantic 모델로 변환 허용
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "username": "teacher_kim",
                "academy_id": 1,
                "user_role": "TEACHER",
                "name": "김선생",
                "phone": "010-1234-5678",
                "created_at": "2026-01-08T11:00:00"
            }
        }


class Token(BaseModel):
    """
    JWT 토큰 응답 스키마 (httpOnly 쿠키 + CSRF 토큰 방식)
    
    - access_token: httpOnly 쿠키로 저장됨
    - csrf_token: JavaScript에서 접근 가능 (헤더로 전송)
    """
    csrf_token: str = Field(..., description="CSRF 방지용 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")
    user: UserResponse = Field(..., description="사용자 정보")
    
    class Config:
        json_schema_extra = {
            "example": {
                "csrf_token": "abc123xyz...",
                "token_type": "bearer",
                "user": {
                    "user_id": 1,
                    "username": "teacher_kim",
                    "academy_id": 1,
                    "user_role": "TEACHER",
                    "name": "김선생",
                    "phone": "010-1234-5678",
                    "created_at": "2026-01-08T11:00:00"
                }
            }
        }
