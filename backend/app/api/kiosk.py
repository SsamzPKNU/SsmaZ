"""
키오스크 API 라우터
학원 태블릿 키오스크용 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.kiosk import (
    StudentLookupRequest,
    StudentLookupResponse,
    StudentInfo,
    AttendanceRequest,
    AttendanceResponse,
    AcademyInfoResponse,
    TeacherLookupRequest,
    TeacherLookupResponse,
    TeacherInfo
)
from app.services.kiosk_service import KioskService
from app.services.auth_service import AuthService


router = APIRouter(prefix="/api/kiosk", tags=["Kiosk"])


@router.post("/lookup", response_model=StudentLookupResponse)
def lookup_students(
    request: StudentLookupRequest,
    db: Session = Depends(get_db)
):
    """
    전화번호 뒷자리로 학생 조회

    - **academy_id**: 학원 ID
    - **phone_last_four**: 학부모 전화번호 뒷자리 4자리
    """
    students = KioskService.lookup_students_by_phone(
        db=db,
        academy_id=request.academy_id,
        phone_last_four=request.phone_last_four
    )

    if not students:
        return StudentLookupResponse(
            success=False,
            students=[],
            message="등록된 학생을 찾을 수 없습니다."
        )

    student_list = [
        StudentInfo(
            student_id=s.student_id,
            name=s.name
        )
        for s in students
    ]

    return StudentLookupResponse(
        success=True,
        students=student_list,
        message=None
    )


@router.post("/attendance", response_model=AttendanceResponse)
def process_attendance(
    request: AttendanceRequest,
    db: Session = Depends(get_db)
):
    """
    출결 처리 (등원/하원)

    - **student_id**: 학생 ID
    - **academy_id**: 학원 ID

    등원 기록이 없으면 등원 처리, 있으면 하원 처리
    """
    success, student_name, action, time = KioskService.process_attendance(
        db=db,
        student_id=request.student_id,
        academy_id=request.academy_id
    )

    if not success:
        return AttendanceResponse(
            success=False,
            action=None,
            student_name=None,
            time=None,
            message="학생 정보를 찾을 수 없습니다."
        )

    # 메시지 생성
    if action == "check_in":
        message = f"{student_name} 학생이 등원했습니다."
    elif action == "check_out":
        message = f"{student_name} 학생이 하원했습니다."
    else:  # already_done
        message = f"{student_name} 학생은 이미 하원 처리되었습니다."

    return AttendanceResponse(
        success=True,
        action=action,
        student_name=student_name,
        time=time,
        message=message
    )


@router.get("/academy/{academy_id}", response_model=AcademyInfoResponse)
def get_academy_info(
    academy_id: int,
    db: Session = Depends(get_db)
):
    """
    학원 정보 조회

    - **academy_id**: 학원 ID
    """
    academy = KioskService.get_academy_info(db=db, academy_id=academy_id)

    if not academy:
        return AcademyInfoResponse(
            success=False,
            academy_id=None,
            academy_name=None,
            message="학원 정보를 찾을 수 없습니다."
        )

    return AcademyInfoResponse(
        success=True,
        academy_id=academy.academy_id,
        academy_name=academy.academy_name,
        message=None
    )


@router.post("/teacher/lookup", response_model=TeacherLookupResponse)
def lookup_teachers(
    request: TeacherLookupRequest,
    db: Session = Depends(get_db)
):
    """
    전화번호 뒷자리로 선생님 조회

    - **academy_id**: 학원 ID
    - **phone_last_four**: 선생님 전화번호 뒷자리 4자리
    """
    teachers = KioskService.lookup_teachers_by_phone(
        db=db,
        academy_id=request.academy_id,
        phone_last_four=request.phone_last_four
    )

    if not teachers:
        return TeacherLookupResponse(
            success=False,
            teachers=[],
            message="등록된 선생님을 찾을 수 없습니다."
        )

    teacher_list = []
    for teacher in teachers:
        if teacher.user:
            access_token = AuthService.create_user_token(teacher.user)
            teacher_list.append(
                TeacherInfo(
                    teacher_id=teacher.teacher_id,
                    name=teacher.name,
                    access_token=access_token
                )
            )

    if not teacher_list:
        return TeacherLookupResponse(
            success=False,
            teachers=[],
            message="계정이 연결된 선생님을 찾을 수 없습니다."
        )

    return TeacherLookupResponse(
        success=True,
        teachers=teacher_list,
        message=None
    )
