from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from datetime import date
from typing import Optional
from app.schemas.attendance import (
    AttendanceCheckRequest,
    AttendanceResponse,
    TodayAttendanceResponse,
    AttendanceStats,
    AttendanceBatchRequest,
    AttendanceBatchResponse,
    AttendanceStatsResponse,
    AttendancePeriod,
)
from app.services.attendance_service import AttendanceService

router = APIRouter()


@router.get("/stats", response_model=AttendanceStatsResponse)
def get_attendance_stats(
    start_date: date = Query(..., description="조회 시작일 (YYYY-MM-DD)"),
    end_date: date = Query(..., description="조회 종료일 (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    기간별 출석 통계 조회 (대시보드용)
    - summary: 전체 기간 출석/지각/결석/조퇴 집계
    - daily_stats: 날짜별 통계 (차트용)
    - class_stats: 반별 출석률
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date는 end_date보다 이전이어야 합니다")

    academy_id = current_user.academy_id
    result = AttendanceService.get_attendance_stats(
        db=db,
        academy_id=academy_id,
        start_date=start_date,
        end_date=end_date
    )

    return AttendanceStatsResponse(
        period=AttendancePeriod(start_date=start_date, end_date=end_date),
        summary=result["summary"],
        daily_stats=result["daily_stats"],
        class_stats=result["class_stats"]
    )


@router.get("/today", response_model=TodayAttendanceResponse)
def get_today_attendance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    오늘의 출결 현황 조회
    모든 학생 목록과 그들의 오늘 출결 상태를 반환
    """
    academy_id = current_user.academy_id
    results, stats = AttendanceService.get_today_attendance(db, academy_id)
    return TodayAttendanceResponse(
        date=date.today(),
        stats=stats,
        students=results
    )


@router.post("/batch", response_model=AttendanceBatchResponse)
def check_attendance_batch(
    request: AttendanceBatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    출결 일괄 저장
    여러 학생의 출결을 한 번에 처리
    """
    academy_id = current_user.academy_id
    result = AttendanceService.check_attendance_batch(
        db=db,
        academy_id=academy_id,
        items=request.items,
        target_date=request.date
    )
    return AttendanceBatchResponse(**result)


@router.post("/check", response_model=AttendanceResponse)
def check_attendance(
    request: AttendanceCheckRequest,
    db: Session = Depends(get_db)
):
    """
    출결 체크 API
    - 등원/지각/조퇴/결석 등의 상태 변경 (action='CHECK_IN')
    - 하원 처리 (action='CHECK_OUT')
    """
    try:
        # action 처리: 'CHECK_OUT'인 경우 flag 설정
        is_checkout = False
        if request.action and request.action.upper() == "CHECK_OUT":
            is_checkout = True
            
        result = AttendanceService.check_attendance(
            db=db,
            student_id=request.student_id,
            status=request.status,
            method=request.method,
            is_checkout=is_checkout  # Service에 전달 (Service 수정 필요)
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
