"""
원장(관리자)용 출결 관리 API 엔드포인트
전체 선생님/학생 출결현황 조회 및 수정 기능 제공
+ 학생 성적/과제 현황 조회 기능
"""

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.deps import get_admin_user
from app.models.user import User
from app.models.attendance import AttendanceStatus
from app.schemas.teacher_attendance import (
    TeacherAttendanceResponse,
    AdminAttendanceListResponse,
    AdminAttendanceResponse,
    ApproveRequest,
    AdminTeacherAttendancePeriodResponse,
    AdminTeacherAttendanceUpdate,
    AdminTeacherAttendanceItem,
    AdminTeacherAttendanceListResponse,
    ApproveSimpleResponse
)
from app.schemas.attendance import (
    AdminStudentAttendanceItem,
    AdminStudentAttendanceListResponse,
    AdminStudentAttendanceUpdate,
    AdminStudentAttendanceCreate
)
from app.schemas.admin_grade import (
    AdminGradeListResponse,
    AdminGradeItem,
    AdminGradeStats,
    AdminAssignmentListResponse,
    AdminAssignmentItem,
    AdminAssignmentStats,
    AdminStudentAssignmentListResponse,
    AdminStudentAssignmentItem,
    AdminStudentAssignmentStats
)
from app.services.teacher_attendance_service import TeacherAttendanceService
from app.services.attendance_service import AttendanceService, get_display_status
from app.services.admin_grade_service import AdminGradeService
from datetime import date
from typing import Optional

router = APIRouter(
    prefix="/admin",
    tags=["AdminAttendance"]
)


@router.get(
    "/teacher-attendance",
    response_model=AdminTeacherAttendanceListResponse,
    summary="전체 선생님 출근현황 조회"
)
async def get_all_teacher_attendance(
    target_date: Optional[date] = Query(None, alias="date", description="조회 날짜 (미입력 시 오늘)"),
    start_date: Optional[date] = Query(None, alias="startDate", description="기간 조회 시작일"),
    end_date: Optional[date] = Query(None, alias="endDate", description="기간 조회 종료일"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    전체 선생님 출근현황 조회 (관리자 전용)

    - **date**: 특정일 조회 (미입력 시 오늘). 미출근 강사는 absent로 포함
    - **startDate** + **endDate**: 기간 조회 (출결 기록이 있는 건만)
    """
    query_date = target_date or date.today()

    records = TeacherAttendanceService.get_all_attendance_by_date(
        db=db,
        academy_id=admin_user.academy_id,
        target_date=query_date,
        start_date=start_date,
        end_date=end_date
    )

    return AdminTeacherAttendanceListResponse(
        records=[AdminTeacherAttendanceItem(**r) for r in records],
        total=len(records)
    )


@router.patch(
    "/attendance/{attendance_id}/approve",
    response_model=ApproveSimpleResponse,
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
    TeacherAttendanceService.approve_attendance(
        db=db,
        attendance_id=attendance_id,
        admin_user_id=admin_user.user_id,
        academy_id=admin_user.academy_id
    )

    return ApproveSimpleResponse(success=True, message="승인되었습니다")


# ==================== 선생님 출퇴근 관리 (확장) ====================

@router.get(
    "/teacher-attendance/list",
    response_model=AdminTeacherAttendancePeriodResponse,
    summary="기간별 선생님 출퇴근 조회"
)
async def get_teacher_attendance_list(
    start_date: Optional[date] = Query(None, description="조회 시작일"),
    end_date: Optional[date] = Query(None, description="조회 종료일"),
    teacher_id: Optional[int] = Query(None, description="선생님 ID 필터"),
    is_approved: Optional[bool] = Query(None, description="승인 여부 필터"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    기간별 전체 선생님 출퇴근 기록 조회 (관리자 전용)

    - **start_date**: 조회 시작일
    - **end_date**: 조회 종료일
    - **teacher_id**: 특정 선생님만 필터
    - **is_approved**: 승인 여부로 필터
    - **page**: 페이지 번호
    - **limit**: 페이지당 항목 수
    """
    records, total = TeacherAttendanceService.get_attendance_list_by_period(
        db=db,
        academy_id=admin_user.academy_id,
        start_date=start_date,
        end_date=end_date,
        teacher_id=teacher_id,
        is_approved=is_approved,
        page=page,
        limit=limit
    )

    return AdminTeacherAttendancePeriodResponse(
        records=[AdminAttendanceResponse(**r) for r in records],
        total=total,
        page=page,
        limit=limit
    )


@router.patch(
    "/teacher-attendance/{attendance_id}",
    response_model=TeacherAttendanceResponse,
    summary="선생님 출퇴근 기록 수정"
)
async def update_teacher_attendance(
    attendance_id: int,
    update_data: AdminTeacherAttendanceUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    선생님 출퇴근 기록 수정 (관리자 전용)

    - **attendance_id**: 출퇴근 기록 ID
    - 출퇴근 시간, 승인 여부 수정 가능
    - 시간 수정 시 근무시간 자동 재계산
    """
    attendance = TeacherAttendanceService.admin_update_attendance(
        db=db,
        attendance_id=attendance_id,
        academy_id=admin_user.academy_id,
        check_in_time=update_data.check_in_time,
        check_out_time=update_data.check_out_time,
        is_approved=update_data.is_approved
    )

    return attendance


# ==================== 학생 출결 관리 ====================

@router.get(
    "/student-attendance/list",
    response_model=AdminStudentAttendanceListResponse,
    summary="기간별 학생 출결 조회"
)
async def get_student_attendance_list(
    start_date: Optional[date] = Query(None, description="조회 시작일"),
    end_date: Optional[date] = Query(None, description="조회 종료일"),
    class_id: Optional[int] = Query(None, description="반 ID 필터"),
    student_id: Optional[int] = Query(None, description="학생 ID 필터"),
    status_filter: Optional[str] = Query(None, alias="status", description="출결 상태 필터 (출석, 지각, 결석, 조퇴)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    기간별 학생 출결 기록 조회 (관리자 전용)

    - **start_date**: 조회 시작일
    - **end_date**: 조회 종료일
    - **class_id**: 특정 반만 필터
    - **student_id**: 특정 학생만 필터
    - **status**: 출결 상태 필터 (출석, 지각, 결석, 조퇴)
    - **page**: 페이지 번호
    - **limit**: 페이지당 항목 수
    """
    # 상태 필터 변환
    att_status = None
    if status_filter:
        try:
            att_status = AttendanceStatus(status_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"유효하지 않은 출결 상태입니다: {status_filter}"
            )

    records, total, stats = AttendanceService.get_student_attendance_list(
        db=db,
        academy_id=admin_user.academy_id,
        start_date=start_date,
        end_date=end_date,
        class_id=class_id,
        student_id=student_id,
        status=att_status,
        page=page,
        limit=limit
    )

    return AdminStudentAttendanceListResponse(
        records=[AdminStudentAttendanceItem(**r) for r in records],
        total=total,
        page=page,
        limit=limit,
        stats=stats
    )


@router.post(
    "/student-attendance",
    response_model=AdminStudentAttendanceItem,
    status_code=status.HTTP_201_CREATED,
    summary="학생 출결 생성"
)
async def create_student_attendance(
    data: AdminStudentAttendanceCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    학생 출결 기록 생성 (관리자 전용)

    - **student_id**: 학생 ID
    - **attendance_date**: 출결 날짜
    - **status**: 출결 상태 (출석, 지각, 결석, 조퇴)
    - **check_in_at**: 등원 시간 (선택)
    - **memo**: 메모 (선택)
    """
    # 스키마 Enum -> 모델 Enum 변환
    model_status = AttendanceStatus(data.status.value)

    try:
        attendance = AttendanceService.admin_create_attendance(
            db=db,
            academy_id=admin_user.academy_id,
            student_id=data.student_id,
            attendance_date=data.attendance_date,
            status=model_status,
            check_in_at=data.check_in_at,
            memo=data.memo
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # 학생 정보 조회
    from app.models.student import Student
    from app.models.class_model import Class

    student = db.query(Student).filter(Student.student_id == attendance.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="학생 정보를 찾을 수 없습니다"
        )

    class_obj = db.query(Class).filter(Class.class_id == student.class_id).first() if student.class_id else None

    return AdminStudentAttendanceItem(
        att_id=attendance.att_id,
        student_id=attendance.student_id,
        student_name=student.name,
        class_id=student.class_id,
        class_name=class_obj.class_name if class_obj else None,
        attendance_date=attendance.attendance_date,
        status=get_display_status(attendance.status.value, attendance.check_out_at),
        check_in_at=attendance.check_in_at,
        check_out_at=attendance.check_out_at,
        memo=attendance.memo
    )


@router.patch(
    "/student-attendance/{att_id}",
    response_model=AdminStudentAttendanceItem,
    summary="학생 출결 수정"
)
async def update_student_attendance(
    att_id: int,
    update_data: AdminStudentAttendanceUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    학생 출결 기록 수정 (관리자 전용)

    - **att_id**: 출결 기록 ID
    - 출결 상태, 등원/하원 시간, 메모 수정 가능
    """
    # 스키마 Enum -> 모델 Enum 변환 (status가 있는 경우에만)
    model_status = AttendanceStatus(update_data.status.value) if update_data.status else None

    try:
        attendance = AttendanceService.admin_update_attendance(
            db=db,
            att_id=att_id,
            academy_id=admin_user.academy_id,
            status=model_status,
            check_in_at=update_data.check_in_at,
            check_out_at=update_data.check_out_at,
            memo=update_data.memo
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    # 학생 정보 조회
    from app.models.student import Student
    from app.models.class_model import Class

    student = db.query(Student).filter(Student.student_id == attendance.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="학생 정보를 찾을 수 없습니다"
        )

    class_obj = db.query(Class).filter(Class.class_id == student.class_id).first() if student.class_id else None

    return AdminStudentAttendanceItem(
        att_id=attendance.att_id,
        student_id=attendance.student_id,
        student_name=student.name,
        class_id=student.class_id,
        class_name=class_obj.class_name if class_obj else None,
        attendance_date=attendance.attendance_date,
        status=get_display_status(attendance.status.value, attendance.check_out_at),
        check_in_at=attendance.check_in_at,
        check_out_at=attendance.check_out_at,
        memo=attendance.memo
    )


# ==================== 학생 성적/과제 관리 ====================

@router.get(
    "/student-grades",
    response_model=AdminGradeListResponse,
    summary="학생 성적 조회"
)
async def get_student_grades(
    student_id: Optional[int] = Query(None, description="학생 ID 필터"),
    class_id: Optional[int] = Query(None, description="반 ID 필터"),
    start_date: Optional[date] = Query(None, description="조회 시작일"),
    end_date: Optional[date] = Query(None, description="조회 종료일"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    학생 성적 조회 (관리자 전용)

    - **student_id**: 특정 학생만 필터
    - **class_id**: 특정 반만 필터
    - **start_date**: 조회 시작일
    - **end_date**: 조회 종료일
    - 통계: 평균, 최고, 최저 점수율 포함
    """
    records, total, stats = AdminGradeService.get_student_grades(
        db=db,
        academy_id=admin_user.academy_id,
        student_id=student_id,
        class_id=class_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        limit=limit
    )

    return AdminGradeListResponse(
        records=[AdminGradeItem(**r) for r in records],
        total=total,
        page=page,
        limit=limit,
        stats=AdminGradeStats(**stats)
    )


@router.get(
    "/assignments",
    response_model=AdminAssignmentListResponse,
    summary="과제 현황 조회"
)
async def get_assignments_overview(
    class_id: Optional[int] = Query(None, description="반 ID 필터"),
    teacher_id: Optional[int] = Query(None, description="선생님 ID 필터"),
    is_active: Optional[bool] = Query(None, description="활성화 여부 필터"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    과제 현황 조회 (관리자 전용)

    - **class_id**: 특정 반만 필터
    - **teacher_id**: 특정 선생님만 필터
    - **is_active**: 활성화 여부로 필터
    - 통계: 전체 과제 수, 활성 과제 수, 평균 완료율 포함
    """
    records, total, stats = AdminGradeService.get_assignments_overview(
        db=db,
        academy_id=admin_user.academy_id,
        class_id=class_id,
        teacher_id=teacher_id,
        is_active=is_active,
        page=page,
        limit=limit
    )

    return AdminAssignmentListResponse(
        records=[AdminAssignmentItem(**r) for r in records],
        total=total,
        page=page,
        limit=limit,
        stats=AdminAssignmentStats(**stats)
    )


@router.get(
    "/student-assignments",
    response_model=AdminStudentAssignmentListResponse,
    summary="학생별 과제 상태 조회"
)
async def get_student_assignments(
    student_id: Optional[int] = Query(None, description="학생 ID 필터"),
    class_id: Optional[int] = Query(None, description="반 ID 필터"),
    status_filter: Optional[str] = Query(
        None,
        alias="status",
        description="상태 필터 (completed: 제출/채점완료, incomplete: 미시작/진행중)"
    ),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    학생별 과제 상태 조회 (관리자 전용)

    - **student_id**: 특정 학생만 필터
    - **class_id**: 특정 반만 필터
    - **status**: 상태 필터
        - completed: SUBMITTED, GRADED (제출 완료)
        - incomplete: NOT_STARTED, IN_PROGRESS (미완료)
    - 통계: 완료/미완료 수, 완료율 포함
    """
    # 상태 필터 검증
    if status_filter and status_filter not in ["completed", "incomplete"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 상태 필터입니다. 'completed' 또는 'incomplete'만 허용됩니다."
        )

    records, total, stats = AdminGradeService.get_student_assignments(
        db=db,
        academy_id=admin_user.academy_id,
        student_id=student_id,
        class_id=class_id,
        status_filter=status_filter,
        page=page,
        limit=limit
    )

    return AdminStudentAssignmentListResponse(
        records=[AdminStudentAssignmentItem(**r) for r in records],
        total=total,
        page=page,
        limit=limit,
        stats=AdminStudentAssignmentStats(**stats)
    )
