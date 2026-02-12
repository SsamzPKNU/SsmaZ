"""
선생님 일일 기록(알림장) API
학생별 태도 점수 및 학습 기록 CRUD
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date

from app.core.database import get_db
from app.models.user import User
from app.api.auth import get_current_user
from app.services.teacher_app_service import TeacherAppService
from app.services.class_teacher_service import ClassTeacherService
from app.services.daily_log_service import DailyLogService
from app.schemas.daily_log import (
    DailyLogListResponse,
    DailyLogCreateRequest,
    DailyLogUpdateRequest,
    DailyLogItem,
)
from app.schemas.common import COMMON_RESPONSES, NOT_FOUND_RESPONSE


router = APIRouter(
    prefix="/teacher/dailylogs",
    tags=["선생님 - 일일기록(알림장)"],
    responses=COMMON_RESPONSES,
)


@router.get("", response_model=DailyLogListResponse)
async def get_daily_logs(
    class_id: int = Query(..., description="반 ID"),
    date: date = Query(..., description="조회 날짜 (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    일일 기록 목록 조회

    해당 반 + 날짜의 학생별 일일 기록을 반환합니다.
    기록이 없는 학생도 빈 상태(id=0)로 포함됩니다.
    """
    teacher_id = TeacherAppService.get_teacher_id(
        db, current_user.user_id, current_user.academy_id
    )

    # 담당 반 확인
    class_ids = ClassTeacherService.get_teacher_class_ids(db, teacher_id)
    if class_id not in class_ids:
        return DailyLogListResponse(items=[], total=0)

    items = DailyLogService.get_daily_logs(
        db=db,
        class_id=class_id,
        log_date=date,
        academy_id=current_user.academy_id,
    )

    return DailyLogListResponse(items=items, total=len(items))


@router.post("", response_model=DailyLogItem, responses=NOT_FOUND_RESPONSE)
async def create_daily_log(
    req: DailyLogCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    일일 기록 생성 (학생 단위)

    - 학생 소속 반 확인
    - 동일 학생+날짜 중복 방지
    """
    teacher_id = TeacherAppService.get_teacher_id(
        db, current_user.user_id, current_user.academy_id
    )

    log = DailyLogService.create_daily_log(
        db=db,
        student_id=req.student_id,
        class_id=req.class_id,
        log_date=req.date,
        academy_id=current_user.academy_id,
        teacher_id=teacher_id,
        attitude_score=req.attitude_score,
        study_note=req.study_note,
    )

    # 학생 이름 조회
    from app.models.student import Student
    student = db.query(Student).filter(Student.student_id == log.student_id).first()

    return DailyLogItem(
        id=log.log_id,
        studentId=log.student_id,
        studentName=student.name if student else "",
        attitudeScore=log.attitude_score,
        studyNote=log.study_note,
        isSent=log.is_sent,
        date=log.regdate,
    )


@router.put("/{log_id}", response_model=DailyLogItem, responses=NOT_FOUND_RESPONSE)
async def update_daily_log(
    log_id: int,
    req: DailyLogUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    일일 기록 수정

    - 태도 점수, 학습 기록, 발송 여부 수정
    """
    log = DailyLogService.update_daily_log(
        db=db,
        log_id=log_id,
        academy_id=current_user.academy_id,
        attitude_score=req.attitude_score if req.attitude_score is not None else ...,
        study_note=req.study_note if req.study_note is not None else ...,
        is_sent=req.is_sent if req.is_sent is not None else ...,
    )

    # 학생 이름 조회
    from app.models.student import Student
    student = db.query(Student).filter(Student.student_id == log.student_id).first()

    return DailyLogItem(
        id=log.log_id,
        studentId=log.student_id,
        studentName=student.name if student else "",
        attitudeScore=log.attitude_score,
        studyNote=log.study_note,
        isSent=log.is_sent,
        date=log.regdate,
    )
