"""
일일 기록(알림장) 스키마
프론트엔드 camelCase 명세에 맞춤
"""

from pydantic import BaseModel
from typing import List, Optional
from datetime import date as date_type


# 목록 조회 응답 항목
class DailyLogItem(BaseModel):
    id: int                              # log_id (없으면 0)
    studentId: int
    studentName: str
    attitudeScore: Optional[int] = None  # 태도 점수
    studyNote: Optional[str] = None      # 학습 기록
    isSent: bool = False                 # 발송 여부
    date: date_type                      # regdate


# 목록 응답
class DailyLogListResponse(BaseModel):
    items: List[DailyLogItem]
    total: int


# 생성 요청
class DailyLogCreateRequest(BaseModel):
    student_id: int
    class_id: int                        # 검증용 (학생이 해당 반 소속인지)
    date: date_type
    attitude_score: Optional[int] = None
    study_note: Optional[str] = None


# 수정 요청
class DailyLogUpdateRequest(BaseModel):
    attitude_score: Optional[int] = None
    study_note: Optional[str] = None
    is_sent: Optional[bool] = None
