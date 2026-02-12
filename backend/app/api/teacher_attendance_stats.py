"""
선생님 출석 통계 API
프론트엔드 경로: GET /api/teacher/attendance/stats
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.models.user import User
from app.models.attendance import Attendance, AttendanceStatus
from app.models.student import Student
from app.models.class_model import Class
from app.api.auth import get_current_user
from app.services.teacher_app_service import TeacherAppService
from app.services.class_teacher_service import ClassTeacherService
from app.schemas.teacher_attendance_stats import (
    TeacherAttendanceStatsResponse,
    MonthlyAttendanceData,
    ClassAttendanceData,
)
from app.schemas.common import COMMON_RESPONSES


router = APIRouter(
    prefix="/teacher/attendance",
    tags=["선생님 - 출석통계"],
    responses=COMMON_RESPONSES,
)


@router.get("/stats", response_model=TeacherAttendanceStatsResponse)
async def get_attendance_stats(
    startDate: Optional[date] = Query(None, description="시작일 (YYYY-MM-DD)"),
    endDate: Optional[date] = Query(None, description="종료일 (YYYY-MM-DD)"),
    classId: Optional[int] = Query(None, description="반 ID (미지정 시 담당 반 전체)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    출석 통계 조회

    담당 반 학생들의 출석 현황을 집계합니다.
    - 전체 출석률 + 상태별 카운트
    - 월별 통계 (monthlyData)
    - 반별 통계 (classByClass)
    """
    teacher_id = TeacherAppService.get_teacher_id(
        db, current_user.user_id, current_user.academy_id
    )
    class_ids = ClassTeacherService.get_teacher_class_ids(db, teacher_id)

    # classId 파라미터가 있으면 해당 반만, 없으면 담당 반 전체
    if classId is not None:
        if classId in class_ids:
            class_ids = [classId]
        else:
            # 담당하지 않는 반이면 빈 결과 반환
            return TeacherAttendanceStatsResponse(
                attendanceRate=0,
                presentCount=0,
                lateCount=0,
                absentCount=0,
                excusedCount=0,
                dismissedCount=0,
                monthlyData=[],
                classByClass=[],
            )

    if not class_ids:
        return TeacherAttendanceStatsResponse(
            attendanceRate=0,
            presentCount=0,
            lateCount=0,
            absentCount=0,
            excusedCount=0,
            dismissedCount=0,
            monthlyData=[],
            classByClass=[],
        )

    # 기본 필터: 담당 반 학생의 출석 기록
    base_filter = [Student.class_id.in_(class_ids)]
    if startDate:
        base_filter.append(Attendance.attendance_date >= startDate)
    if endDate:
        base_filter.append(Attendance.attendance_date <= endDate)

    # ── 1) 전체 집계 ──
    totals = (
        db.query(
            func.count(Attendance.att_id).label("total"),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label("present"),
            func.sum(case((Attendance.status == AttendanceStatus.LATE, 1), else_=0)).label("late"),
            func.sum(case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)).label("absent"),
            func.sum(case((Attendance.status == AttendanceStatus.EARLY_LEAVE, 1), else_=0)).label("dismissed"),
        )
        .join(Student, Student.student_id == Attendance.student_id)
        .filter(*base_filter)
        .one()
    )

    total = totals.total or 0
    present = totals.present or 0
    late = totals.late or 0
    absent = totals.absent or 0
    dismissed = totals.dismissed or 0
    attendance_rate = round((present + late) / total * 100, 1) if total > 0 else 0

    # ── 2) 월별 집계 ──
    monthly_rows = (
        db.query(
            func.date_format(Attendance.attendance_date, "%Y-%m").label("month"),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label("present"),
            func.sum(case((Attendance.status == AttendanceStatus.LATE, 1), else_=0)).label("late"),
            func.sum(case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)).label("absent"),
            func.sum(case((Attendance.status == AttendanceStatus.EARLY_LEAVE, 1), else_=0)).label("dismissed"),
        )
        .join(Student, Student.student_id == Attendance.student_id)
        .filter(*base_filter)
        .group_by("month")
        .order_by("month")
        .all()
    )

    monthly_data = [
        MonthlyAttendanceData(
            month=row.month,
            presentCount=row.present or 0,
            lateCount=row.late or 0,
            absentCount=row.absent or 0,
            dismissedCount=row.dismissed or 0,
        )
        for row in monthly_rows
    ]

    # ── 3) 반별 집계 ──
    class_rows = (
        db.query(
            Class.class_id,
            Class.class_name,
            func.count(Attendance.att_id).label("total"),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label("present"),
            func.sum(case((Attendance.status == AttendanceStatus.LATE, 1), else_=0)).label("late"),
            func.sum(case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)).label("absent"),
            func.sum(case((Attendance.status == AttendanceStatus.EARLY_LEAVE, 1), else_=0)).label("dismissed"),
        )
        .join(Student, Student.class_id == Class.class_id)
        .join(Attendance, Attendance.student_id == Student.student_id)
        .filter(*base_filter)
        .group_by(Class.class_id, Class.class_name)
        .all()
    )

    class_by_class = []
    for row in class_rows:
        row_total = row.total or 0
        row_present = row.present or 0
        row_late = row.late or 0
        row_absent = row.absent or 0
        row_dismissed = row.dismissed or 0
        row_rate = round((row_present + row_late) / row_total * 100, 1) if row_total > 0 else 0

        class_by_class.append(
            ClassAttendanceData(
                classId=row.class_id,
                className=row.class_name,
                attendanceRate=row_rate,
                presentCount=row_present,
                lateCount=row_late,
                absentCount=row_absent,
                dismissedCount=row_dismissed,
            )
        )

    return TeacherAttendanceStatsResponse(
        attendanceRate=attendance_rate,
        presentCount=present,
        lateCount=late,
        absentCount=absent,
        excusedCount=0,
        dismissedCount=dismissed,
        monthlyData=monthly_data,
        classByClass=class_by_class,
    )
