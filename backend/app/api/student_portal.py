"""
학생 포털 API 라우터
학생용 대시보드, 출결, 수납, 스케줄, 성적 조회 엔드포인트
"""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_student_user
from app.models.user import User
from app.services.student_portal_service import StudentPortalService
from app.schemas.student_portal import (
    StudentAttendanceResponse,
    StudentDashboardResponse,
    StudentPaymentsResponse,
    StudentScheduleResponse,
    StudentGradesResponse,
    GradeAnalysisResponse
)

router = APIRouter(
    prefix="/api/student",
    tags=["Student Portal"]
)


@router.get(
    "/attendance",
    response_model=StudentAttendanceResponse,
    summary="학생 출결 조회",
    description="로그인한 사용자에게 연결된 학생의 월별 출결 기록을 조회합니다."
)
async def get_student_attendance(
    year: Optional[int] = Query(None, description="조회할 연도 (기본: 현재 연도)"),
    month: Optional[int] = Query(None, ge=1, le=12, description="조회할 월 (기본: 현재 월)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_student_user)
):
    """
    학생 출결 조회

    - 월별 출결 기록 및 통계 제공
    - 출석률은 지각/조퇴를 0.5로 계산
    - year, month 파라미터 생략 시 현재 연월 조회
    """
    service = StudentPortalService(db)
    result = service.get_attendance(current_user, year, month)
    return StudentAttendanceResponse(**result)


@router.get(
    "/dashboard",
    response_model=StudentDashboardResponse,
    summary="학생 대시보드",
    description="로그인한 사용자에게 연결된 학생의 대시보드 정보를 조회합니다."
)
async def get_student_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_student_user)
):
    """
    학생 대시보드

    - 이번 달 출결 통계
    - 최근 30일 과제 완료율
    - 오늘 예정된 수업 목록
    """
    service = StudentPortalService(db)
    result = service.get_dashboard(current_user)
    return StudentDashboardResponse(**result)


@router.get(
    "/payments",
    response_model=StudentPaymentsResponse,
    summary="학생 수납 조회",
    description="로그인한 사용자에게 연결된 학생의 연간 납부 현황을 조회합니다."
)
async def get_student_payments(
    year: Optional[int] = Query(None, description="조회할 연도 (기본: 현재 연도)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_student_user)
):
    """
    학생 수납 조회

    - 연간 월별 납부 현황
    - 완납/미납/부분납 상태 표시
    - 상세 청구서 목록
    """
    service = StudentPortalService(db)
    result = service.get_payments(current_user, year)
    return StudentPaymentsResponse(**result)


@router.get(
    "/schedule",
    response_model=StudentScheduleResponse,
    summary="학생 스케줄 조회",
    description="로그인한 사용자에게 연결된 학생의 시간표 및 일정을 조회합니다."
)
async def get_student_schedule(
    start_date: Optional[date] = Query(None, description="시작일 (기본: 오늘)"),
    end_date: Optional[date] = Query(None, description="종료일 (기본: 30일 후)"),
    type: str = Query("all", description="이벤트 유형 (all, assignment)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_student_user)
):
    """
    학생 스케줄 조회

    - 주간 정규 수업 시간표
    - 기간 내 과제 마감일 등 이벤트
    - type 파라미터로 이벤트 유형 필터링
    """
    service = StudentPortalService(db)
    result = service.get_schedule(current_user, start_date, end_date, type)
    return StudentScheduleResponse(**result)


@router.get(
    "/grades",
    response_model=StudentGradesResponse,
    summary="학생 성적 조회",
    description="로그인한 사용자에게 연결된 학생의 채점 완료된 성적을 조회합니다."
)
async def get_student_grades(
    subject: Optional[str] = Query(None, description="과목명 필터 (선택)"),
    start_date: Optional[date] = Query(None, description="시작일 (선택)"),
    end_date: Optional[date] = Query(None, description="종료일 (선택)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_student_user)
):
    """
    학생 성적 조회

    - 채점 완료된 과제 성적 목록
    - 과목명, 기간으로 필터링 가능
    - 평균 점수 통계 제공
    """
    service = StudentPortalService(db)
    result = service.get_grades(current_user, subject, start_date, end_date)
    return StudentGradesResponse(**result)


@router.get(
    "/grade-analysis",
    response_model=GradeAnalysisResponse,
    summary="학생 성적 분석",
    description="로그인한 사용자에게 연결된 학생의 성적 추이를 분석합니다."
)
async def get_student_grade_analysis(
    period: str = Query("3m", description="분석 기간 (3m, 6m, 1y)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_student_user)
):
    """
    학생 성적 분석

    - 월별 평균 점수 추이
    - 과목별 평균 및 추세 (상승/하락/유지)
    - 전체 평균 점수
    """
    service = StudentPortalService(db)
    result = service.get_grade_analysis(current_user, period)
    return GradeAnalysisResponse(**result)
