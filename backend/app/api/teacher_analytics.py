"""
선생님 오답 분석 API
문항별 오답률, 학생별 취약점, 단원별 통계 기능 제공
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.models.user import User
from app.api.auth import get_current_user
from app.services.teacher_app_service import TeacherAppService
from app.services.teacher_analytics_service import TeacherAnalyticsService
from app.schemas.teacher_analytics import (
    QuestionAnalysisResponse, StudentWeaknessResponse, UnitStatsResponse
)


router = APIRouter(
    prefix="/api/teacher/analysis",
    tags=["선생님 앱 - 오답 분석"]
)


@router.get("/questions", response_model=QuestionAnalysisResponse)
async def get_question_analysis(
    type: Optional[str] = Query(None, description="분석 유형 (normal, clinic)"),
    item_id: Optional[int] = Query(None, description="과제 ID"),
    class_id: Optional[int] = Query(None, description="반 ID"),
    start_date: Optional[date] = Query(None, description="시작일"),
    end_date: Optional[date] = Query(None, description="종료일"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    문항별 오답률 분석

    각 문항의 오답률과 자주 틀리는 오답을 분석합니다.

    Query Parameters:
    - type: 분석 유형 (normal, clinic)
    - item_id: 과제 ID
    - class_id: 반 ID
    - start_date: 시작일
    - end_date: 종료일
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    items = TeacherAnalyticsService.get_question_analysis(
        db=db,
        teacher_id=teacher_id,
        user_id=current_user.user_id,
        academy_id=current_user.academy_id,
        analysis_type=type,
        item_id=item_id,
        class_id=class_id,
        start_date=start_date,
        end_date=end_date
    )

    period = None
    if start_date and end_date:
        period = f"{start_date.isoformat()} ~ {end_date.isoformat()}"

    return QuestionAnalysisResponse(
        items=items,
        total=len(items),
        analysis_period=period
    )


@router.get("/students", response_model=StudentWeaknessResponse)
async def get_student_weakness(
    class_id: Optional[int] = Query(None, description="반 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    학생별 취약점 분석

    각 학생의 취약 유형을 분석합니다.

    Query Parameters:
    - class_id: 반 ID
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    items = TeacherAnalyticsService.get_student_weakness(
        db=db,
        teacher_id=teacher_id,
        academy_id=current_user.academy_id,
        class_id=class_id
    )

    return StudentWeaknessResponse(
        items=items,
        total=len(items)
    )


@router.get("/units", response_model=UnitStatsResponse)
async def get_unit_stats(
    class_id: Optional[int] = Query(None, description="반 ID"),
    start_date: Optional[date] = Query(None, description="시작일"),
    end_date: Optional[date] = Query(None, description="종료일"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    단원별 통계

    단원(카테고리)별 정답률/오답률 통계를 조회합니다.

    Query Parameters:
    - class_id: 반 ID
    - start_date: 시작일
    - end_date: 종료일
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    items = TeacherAnalyticsService.get_unit_stats(
        db=db,
        teacher_id=teacher_id,
        user_id=current_user.user_id,
        academy_id=current_user.academy_id,
        class_id=class_id,
        start_date=start_date,
        end_date=end_date
    )

    period = None
    if start_date and end_date:
        period = f"{start_date.isoformat()} ~ {end_date.isoformat()}"

    return UnitStatsResponse(
        items=items,
        total=len(items),
        analysis_period=period
    )
