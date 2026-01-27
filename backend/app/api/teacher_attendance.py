"""
선생님 출퇴근 관리 API 엔드포인트
선생님 본인의 출퇴근 처리 및 기록 조회 기능 제공
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User, UserRole
from app.schemas.teacher_attendance import (
    TeacherCheckIn,
    TeacherCheckOut,
    TeacherAttendanceResponse,
    TeacherAttendanceListResponse,
    WorkHoursSummary
)
from app.services.teacher_attendance_service import TeacherAttendanceService
from datetime import date
from typing import Optional

router = APIRouter(
    prefix="/teachers",
    tags=["TeacherAttendance"]
)


def get_teacher_from_user(db: Session, user: User):
    """
    현재 사용자의 Teacher 정보 조회
    TEACHER 역할인 경우에만 Teacher 테이블에서 조회
    """
    if user.user_role != UserRole.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="선생님 권한이 필요합니다"
        )

    teacher = TeacherAttendanceService.get_teacher_by_user_id(db, user.user_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="선생님 정보를 찾을 수 없습니다. 관리자에게 문의하세요."
        )
    return teacher


@router.post(
    "/attendance/check-in",
    response_model=TeacherAttendanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="출근 처리"
)
async def check_in(
    check_in_data: TeacherCheckIn = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    선생님 출근 처리

    - 당일 중복 출근 방지
    - **date**: 근무일 (미입력 시 오늘)
    """
    teacher = get_teacher_from_user(db, current_user)

    target_date = None
    if check_in_data and check_in_data.work_date:
        target_date = check_in_data.work_date

    attendance = TeacherAttendanceService.check_in(
        db=db,
        teacher_id=teacher.teacher_id,
        target_date=target_date
    )
    return attendance


@router.post(
    "/attendance/check-out",
    response_model=TeacherAttendanceResponse,
    summary="퇴근 처리"
)
async def check_out(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    선생님 퇴근 처리

    - 당일 출근 기록이 있어야 퇴근 가능
    - 근무시간(분) 자동 계산
    """
    teacher = get_teacher_from_user(db, current_user)

    attendance = TeacherAttendanceService.check_out(
        db=db,
        teacher_id=teacher.teacher_id
    )
    return attendance


@router.get(
    "/{teacher_id}/attendance",
    response_model=TeacherAttendanceListResponse,
    summary="출퇴근 기록 조회"
)
async def get_attendance_list(
    teacher_id: int,
    start_date: Optional[date] = Query(None, description="조회 시작일"),
    end_date: Optional[date] = Query(None, description="조회 종료일"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    선생님 출퇴근 기록 조회

    - **teacher_id**: 선생님 ID
    - **start_date**: 조회 시작일 (선택)
    - **end_date**: 조회 종료일 (선택)
    - 본인 또는 관리자만 조회 가능
    """
    # 권한 체크: 본인이거나 관리자여야 함
    if current_user.user_role == UserRole.TEACHER:
        teacher = get_teacher_from_user(db, current_user)
        if teacher.teacher_id != teacher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="본인의 기록만 조회할 수 있습니다"
            )

    records, total = TeacherAttendanceService.get_attendance_list(
        db=db,
        teacher_id=teacher_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit
    )

    return TeacherAttendanceListResponse(
        records=records,
        total=total
    )


@router.get(
    "/{teacher_id}/work-summary",
    response_model=WorkHoursSummary,
    summary="근무시간 요약 조회"
)
async def get_work_summary(
    teacher_id: int,
    start_date: date = Query(..., description="조회 시작일"),
    end_date: date = Query(..., description="조회 종료일"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    선생님 근무시간 요약 및 예상 급여 조회

    - **teacher_id**: 선생님 ID
    - **start_date**: 조회 시작일
    - **end_date**: 조회 종료일
    - 비정규직(PART_TIME)인 경우 시급 기반 예상 급여 포함
    """
    # 권한 체크: 본인이거나 관리자여야 함
    if current_user.user_role == UserRole.TEACHER:
        teacher = get_teacher_from_user(db, current_user)
        if teacher.teacher_id != teacher_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="본인의 기록만 조회할 수 있습니다"
            )

    summary_data = TeacherAttendanceService.get_work_summary(
        db=db,
        teacher_id=teacher_id,
        start_date=start_date,
        end_date=end_date
    )

    return WorkHoursSummary(**summary_data)
