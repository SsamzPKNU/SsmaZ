"""
선생님용 앱 API 엔드포인트
선생님이 자신의 담당 반과 학생들을 관리하는 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.api.auth import get_current_user
from app.schemas.teacher_app import (
    TeacherDashboardResponse,
    TeacherClassResponse,
    TeacherStudentResponse,
    StudentDetailResponse,
    AttendanceRecordResponse,
    AttendanceCreateRequest,
    AttendanceUpdateRequest,
    ClassAttendanceResponse,
    ClassAttendanceBatchRequest,
    ClassAttendanceBatchResponse,
    ClassAttendanceSummaryResponse
)
from app.services.teacher_app_service import TeacherAppService
from app.schemas.support import NoticeResponse, NoticeListResponse
from app.services.support_service import NoticeService
from typing import List, Optional
from datetime import date


# API 라우터 생성
router = APIRouter(
    prefix="/api/teacher",
    tags=["선생님 앱"]
)


@router.get("/dashboard", response_model=TeacherDashboardResponse)
async def get_teacher_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    선생님 대시보드
    
    선생님의 요약 정보를 조회합니다:
    - 담당 반 수
    - 담당 학생 수
    - 오늘 출석률
    - 이번 달 수납률
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        TeacherDashboardResponse: 대시보드 요약 정보
    
    Raises:
        401: 인증되지 않은 사용자
        403: 선생님 권한이 아닌 경우
    """
    # TODO: 권한 체크 (TEACHER만)
    # if current_user.user_role != UserRole.TEACHER:
    #     raise HTTPException(status_code=403, detail="선생님 권한이 필요합니다")
    
    dashboard = TeacherAppService.get_teacher_dashboard(
        db=db,
        user_id=current_user.user_id,
        academy_id=current_user.academy_id
    )
    
    return dashboard


@router.get("/classes", response_model=List[TeacherClassResponse])
async def get_my_classes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내 담당 반 목록 조회
    
    현재 로그인한 선생님의 담당 반 목록을 조회합니다.
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        List[TeacherClassResponse]: 담당 반 목록
        
    Response Fields:
        - id: 반 ID
        - name: 반 이름
        - schedule: 수업 일정
        - student_count: 현재 학생 수
        - capacity: 정원
    
    Raises:
        401: 인증되지 않은 사용자
    """
    classes = TeacherAppService.get_teacher_classes(
        db=db,
        user_id=current_user.user_id,
        academy_id=current_user.academy_id
    )
    
    return classes


@router.get("/classes/{class_id}/students", response_model=List[TeacherStudentResponse])
async def get_class_students(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    특정 반의 학생 목록 조회
    
    선생님이 담당하는 특정 반의 학생 목록을 조회합니다.
    
    Path Parameters:
        - class_id: 반 ID
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        List[TeacherStudentResponse]: 학생 목록
    
    Raises:
        401: 인증되지 않은 사용자
        403: 해당 반의 담당 선생님이 아닌 경우
        404: 반을 찾을 수 없음
    """
    students = TeacherAppService.get_class_students(
        db=db,
        class_id=class_id,
        user_id=current_user.user_id,
        academy_id=current_user.academy_id
    )
    
    return students


@router.get("/students/{student_id}", response_model=StudentDetailResponse)
async def get_student_detail(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    학생 상세 정보 조회
    
    학생의 상세 정보를 조회합니다.
    선생님은 자신이 담당하는 학생만 조회할 수 있습니다.
    
    Path Parameters:
        - student_id: 학생 ID
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        StudentDetailResponse: 학생 상세 정보
    
    Raises:
        401: 인증되지 않은 사용자
        403: 해당 학생의 담당 선생님이 아닌 경우
        404: 학생을 찾을 수 없음
    """
    student = TeacherAppService.get_student_detail(
        db=db,
        student_id=student_id,
        user_id=current_user.user_id,
        academy_id=current_user.academy_id
    )
    
    return student


@router.get("/students/{student_id}/attendance", response_model=List[AttendanceRecordResponse])
async def get_student_attendance(
    student_id: int,
    start_date: Optional[date] = Query(None, description="시작일 (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="종료일 (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    학생 출결 기록 조회
    
    특정 학생의 출결 기록을 조회합니다.
    기간을 지정하지 않으면 최근 30일 기록을 반환합니다.
    
    Path Parameters:
        - student_id: 학생 ID
    
    Query Parameters:
        - start_date: 시작일 (선택)
        - end_date: 종료일 (선택)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        List[AttendanceRecordResponse]: 출결 기록 목록
    
    Raises:
        401: 인증되지 않은 사용자
        403: 해당 학생의 담당 선생님이 아닌 경우
        404: 학생을 찾을 수 없음
    """
    records = TeacherAppService.get_student_attendance(
        db=db,
        student_id=student_id,
        user_id=current_user.user_id,
        academy_id=current_user.academy_id,
        start_date=start_date,
        end_date=end_date
    )
    
    return records


@router.post("/students/{student_id}/attendance", response_model=AttendanceRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_attendance(
    student_id: int,
    attendance_data: AttendanceCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    출결 기록 등록
    
    학생의 출결을 기록합니다.
    
    Path Parameters:
        - student_id: 학생 ID
    
    Request Body:
        - attendance_date: 출결 날짜 (YYYY-MM-DD)
        - status: 출결 상태 (present, late, absent, excused)
        - memo: 메모 (선택)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        AttendanceRecordResponse: 등록된 출결 기록
    
    Raises:
        401: 인증되지 않은 사용자
        403: 해당 학생의 담당 선생님이 아닌 경우
        404: 학생을 찾을 수 없음
        422: 입력 데이터 검증 실패
    """
    record = TeacherAppService.create_attendance(
        db=db,
        student_id=student_id,
        user_id=current_user.user_id,
        academy_id=current_user.academy_id,
        attendance_data=attendance_data
    )
    
    return record


@router.get("/students", response_model=List[TeacherStudentResponse])
async def get_all_my_students(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    내가 담당하는 모든 학생 목록

    선생님이 담당하는 모든 반의 학생들을 조회합니다.

    Headers:
        Authorization: Bearer {access_token}

    Returns:
        List[TeacherStudentResponse]: 전체 학생 목록

    Raises:
        401: 인증되지 않은 사용자
    """
    students = TeacherAppService.get_all_teacher_students(
        db=db,
        user_id=current_user.user_id,
        academy_id=current_user.academy_id
    )

    return students


# ==================== 반 출결 관리 API ====================

@router.get("/classes/{class_id}/attendance", response_model=ClassAttendanceResponse)
async def get_class_attendance(
    class_id: int,
    target_date: Optional[date] = Query(None, description="조회 날짜 (미입력 시 오늘)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    반 출결 현황 조회

    담당하는 반의 특정일 출결 현황을 조회합니다.
    출결 기록이 없는 학생도 포함됩니다.

    Path Parameters:
        - class_id: 반 ID

    Query Parameters:
        - target_date: 조회 날짜 (미입력 시 오늘)

    Headers:
        Authorization: Bearer {access_token}

    Returns:
        ClassAttendanceResponse: 반 출결 현황

    Raises:
        401: 인증되지 않은 사용자
        403: 해당 반의 담당 선생님이 아닌 경우
        404: 반을 찾을 수 없음
    """
    result = TeacherAppService.get_class_attendance_status(
        db=db,
        class_id=class_id,
        user_id=current_user.user_id,
        academy_id=current_user.academy_id,
        target_date=target_date
    )

    return result


@router.post(
    "/classes/{class_id}/attendance/batch",
    response_model=ClassAttendanceBatchResponse,
    status_code=status.HTTP_201_CREATED
)
async def batch_check_class_attendance(
    class_id: int,
    batch_data: ClassAttendanceBatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    반 출결 일괄 처리

    담당하는 반의 학생들 출결을 일괄 처리합니다.

    Path Parameters:
        - class_id: 반 ID

    Request Body:
        - date: 출결 날짜 (미입력 시 오늘)
        - items: 출결 항목 목록 [{student_id, status}]

    Headers:
        Authorization: Bearer {access_token}

    Returns:
        ClassAttendanceBatchResponse: 일괄 처리 결과

    Raises:
        401: 인증되지 않은 사용자
        403: 해당 반의 담당 선생님이 아닌 경우
    """
    result = TeacherAppService.batch_check_class_attendance(
        db=db,
        class_id=class_id,
        user_id=current_user.user_id,
        academy_id=current_user.academy_id,
        items=batch_data.items,
        target_date=batch_data.date
    )

    return result


@router.patch(
    "/students/{student_id}/attendance/{att_id}",
    response_model=AttendanceRecordResponse
)
async def update_student_attendance(
    student_id: int,
    att_id: int,
    update_data: AttendanceUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    학생 출결 수정

    담당 학생의 출결 기록을 수정합니다.

    Path Parameters:
        - student_id: 학생 ID
        - att_id: 출결 기록 ID

    Request Body:
        - status: 출결 상태 (present, late, absent, excused)
        - check_in_time: 등원 시간 (HH:MM)
        - check_out_time: 하원 시간 (HH:MM)
        - memo: 메모

    Headers:
        Authorization: Bearer {access_token}

    Returns:
        AttendanceRecordResponse: 수정된 출결 기록

    Raises:
        401: 인증되지 않은 사용자
        403: 해당 학생의 담당 선생님이 아닌 경우
        404: 출결 기록을 찾을 수 없음
    """
    result = TeacherAppService.update_student_attendance(
        db=db,
        student_id=student_id,
        att_id=att_id,
        user_id=current_user.user_id,
        academy_id=current_user.academy_id,
        update_data=update_data
    )

    return result


@router.get("/classes/{class_id}/attendance/summary", response_model=ClassAttendanceSummaryResponse)
async def get_class_attendance_summary(
    class_id: int,
    start_date: Optional[date] = Query(None, description="시작일 (미입력 시 30일 전)"),
    end_date: Optional[date] = Query(None, description="종료일 (미입력 시 오늘)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    기간별 반 출결 통계

    담당하는 반의 기간별 출결 통계를 조회합니다.

    Path Parameters:
        - class_id: 반 ID

    Query Parameters:
        - start_date: 시작일 (미입력 시 30일 전)
        - end_date: 종료일 (미입력 시 오늘)

    Headers:
        Authorization: Bearer {access_token}

    Returns:
        ClassAttendanceSummaryResponse: 반 출결 통계

    Raises:
        401: 인증되지 않은 사용자
        403: 해당 반의 담당 선생님이 아닌 경우
        404: 반을 찾을 수 없음
    """
    result = TeacherAppService.get_class_attendance_summary(
        db=db,
        class_id=class_id,
        user_id=current_user.user_id,
        academy_id=current_user.academy_id,
        start_date=start_date,
        end_date=end_date
    )

    return result


# ==================== 공지사항 API ====================

@router.get("/notices", response_model=NoticeListResponse)
async def get_teacher_notices(
    skip: int = Query(0, ge=0, description="건너뛸 항목 수"),
    limit: int = Query(20, ge=1, le=100, description="조회할 항목 수"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    선생님용 공지사항 목록 조회

    선생님 대상(TEACHER) 및 전체 대상(ALL) 공지사항을 조회합니다.
    고정 공지가 먼저 표시되고, 최신순으로 정렬됩니다.

    Query Parameters:
        - skip: 건너뛸 항목 수 (기본: 0)
        - limit: 조회할 항목 수 (기본: 20, 최대: 100)

    Headers:
        Authorization: Bearer {access_token}

    Returns:
        NoticeListResponse: 공지사항 목록 및 총 개수

    Raises:
        401: 인증되지 않은 사용자
    """
    # TEACHER + ALL 대상 공지만 조회
    targets = ["TEACHER", "ALL"]
    notices, total = NoticeService.get_notices_for_targets(
        db=db,
        academy_id=current_user.academy_id,
        targets=targets,
        skip=skip,
        limit=limit
    )

    return NoticeListResponse(
        total=total,
        notices=[NoticeService.to_response(n) for n in notices]
    )


@router.get("/notices/{notice_id}", response_model=NoticeResponse)
async def get_teacher_notice_detail(
    notice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    선생님용 공지사항 상세 조회

    공지사항 상세 정보를 조회합니다.
    조회 시 조회수가 1 증가합니다.
    선생님 대상(TEACHER) 또는 전체 대상(ALL) 공지만 조회 가능합니다.

    Path Parameters:
        - notice_id: 공지사항 ID

    Headers:
        Authorization: Bearer {access_token}

    Returns:
        NoticeResponse: 공지사항 상세 정보

    Raises:
        401: 인증되지 않은 사용자
        403: 접근 권한이 없는 공지사항
        404: 공지사항을 찾을 수 없음
    """
    notice = NoticeService.get_notice(
        db=db,
        notice_id=notice_id,
        academy_id=current_user.academy_id,
        increment_view=True
    )

    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="공지사항을 찾을 수 없습니다"
        )

    # TEACHER 또는 ALL 대상이 아닌 경우 접근 거부
    allowed_targets = ["TEACHER", "ALL"]
    notice_target = notice.target.value if notice.target else "ALL"
    if notice_target not in allowed_targets:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="이 공지사항에 대한 접근 권한이 없습니다"
        )

    return NoticeService.to_response(notice)
