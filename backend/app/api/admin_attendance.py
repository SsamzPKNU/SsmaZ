"""
원장(관리자)용 출퇴근 관리 API 엔드포인트
전체 선생님 출근현황 조회 및 승인 처리 기능 제공
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_admin_user
from app.models.user import User
from app.schemas.teacher_attendance import (
    TeacherAttendanceResponse,
    AdminAttendanceListResponse,
    AdminAttendanceResponse,
    ApproveRequest
)
from app.services.teacher_attendance_service import TeacherAttendanceService
from datetime import date
from typing import Optional

router = APIRouter(
    prefix="/admin",
    tags=["AdminAttendance"]
)


@router.get(
    "/teacher-attendance",
    response_model=AdminAttendanceListResponse,
    summary="전체 선생님 출근현황 조회"
)
async def get_all_teacher_attendance(
    target_date: Optional[date] = Query(None, description="조회 날짜 (미입력 시 오늘)"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    특정일 전체 선생님 출근현황 조회 (관리자 전용)

    - **target_date**: 조회 날짜 (미입력 시 오늘)
    - 해당 학원 소속 선생님만 조회
    """
    query_date = target_date or date.today()

    records = TeacherAttendanceService.get_all_attendance_by_date(
        db=db,
        academy_id=admin_user.academy_id,
        target_date=query_date
    )

    return AdminAttendanceListResponse(
        query_date=query_date,
        records=[AdminAttendanceResponse(**r) for r in records],
        total=len(records)
    )


@router.patch(
    "/attendance/{attendance_id}/approve",
    response_model=TeacherAttendanceResponse,
    summary="출퇴근 기록 승인"
)
async def approve_attendance(
    attendance_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    선생님 출퇴근 기록 승인 처리 (관리자 전용)

    - **attendance_id**: 출퇴근 기록 ID
    - 승인 시 승인자 ID와 승인 상태가 기록됨
    """
    attendance = TeacherAttendanceService.approve_attendance(
        db=db,
        attendance_id=attendance_id,
        admin_user_id=admin_user.user_id,
        academy_id=admin_user.academy_id
    )

    return attendance
