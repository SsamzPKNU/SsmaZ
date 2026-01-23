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
    AttendanceCreateRequest
)
from app.services.teacher_app_service import TeacherAppService
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
