"""
클리닉 API 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User, UserRole
from app.models.assignment import Assignment
from app.models.submission import Submission
from app.models.student import Student
from app.schemas.clinic import (
    ClinicGenerateRequest, ClinicGenerateResponse,
    ClinicListResponse, ClinicListItem, ClinicPreviewResponse
)
from app.services.clinic_service import generate_clinic, get_wrong_questions, get_student_clinics
from app.models.teacher import Teacher

router = APIRouter()


def get_teacher_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """TEACHER 또는 ADMIN 권한 체크"""
    if current_user.user_role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="선생님 또는 관리자 권한이 필요합니다"
        )
    return current_user


@router.get("/preview/{submission_id}", response_model=ClinicPreviewResponse)
async def preview_clinic(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_or_admin)
):
    """
    클리닉 생성 미리보기 (TEACHER, ADMIN)
    - 틀린 문제 목록 조회
    """
    submission = db.query(Submission).filter(
        Submission.submission_id == submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="제출 기록을 찾을 수 없습니다"
        )

    # 학원 확인
    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == submission.assignment_id,
        Assignment.academy_id == current_user.academy_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다"
        )

    try:
        wrong_questions = get_wrong_questions(db, submission_id)

        return ClinicPreviewResponse(
            submission_id=submission_id,
            assignment_title=assignment.title,
            wrong_questions=wrong_questions,
            total_wrong_count=len(wrong_questions)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/generate", response_model=ClinicGenerateResponse, status_code=status.HTTP_201_CREATED)
async def create_clinic(
    data: ClinicGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_or_admin)
):
    """
    클리닉 과제 생성 (TEACHER, ADMIN)
    """
    submission = db.query(Submission).filter(
        Submission.submission_id == data.submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="제출 기록을 찾을 수 없습니다"
        )

    # 학원 확인
    original_assignment = db.query(Assignment).filter(
        Assignment.assignment_id == submission.assignment_id,
        Assignment.academy_id == current_user.academy_id
    ).first()

    if not original_assignment:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다"
        )

    try:
        # teacher_id 조회
        teacher = db.query(Teacher).filter(
            Teacher.academy_id == current_user.academy_id,
            Teacher.user_id == current_user.user_id
        ).first()
        teacher_id_val = teacher.teacher_id if teacher else current_user.user_id

        clinic_assignment = generate_clinic(
            db=db,
            submission_id=data.submission_id,
            clinic_type=data.clinic_type,
            teacher_id=teacher_id_val,
            title=data.title,
            due_date=data.due_date
        )

        question_count = len(clinic_assignment.questions)

        return ClinicGenerateResponse(
            assignment_id=clinic_assignment.assignment_id,
            title=clinic_assignment.title,
            original_assignment_id=original_assignment.assignment_id,
            original_assignment_title=original_assignment.title,
            question_count=question_count,
            created_at=clinic_assignment.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/student/{student_id}", response_model=ClinicListResponse)
async def get_student_clinic_list(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    학생별 클리닉 목록 조회
    """
    # 학생 확인
    student = db.query(Student).filter(
        Student.student_id == student_id
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="학생을 찾을 수 없습니다"
        )

    # 권한 확인: 같은 학원 소속이어야 함
    if student.academy_id != current_user.academy_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다"
        )

    clinics = get_student_clinics(db, student_id, current_user.academy_id)

    items = [
        ClinicListItem(
            assignment_id=c["assignment_id"],
            title=c["title"],
            original_assignment_title=c["original_assignment_title"],
            due_date=c["due_date"],
            question_count=c["question_count"],
            is_completed=c["is_completed"],
            score=c["score"],
            max_score=c["max_score"],
            created_at=c["created_at"]
        ) for c in clinics
    ]

    return ClinicListResponse(items=items, total=len(items))


@router.get("/my", response_model=ClinicListResponse)
async def get_my_clinics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    내 클리닉 목록 조회 (STUDENT)
    """
    if current_user.user_role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="학생만 조회 가능합니다"
        )

    # Student ID 조회
    student = db.query(Student).filter(
        Student.academy_id == current_user.academy_id,
        Student.name == current_user.name
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="학생 정보를 찾을 수 없습니다"
        )

    clinics = get_student_clinics(db, student.student_id, current_user.academy_id)

    items = [
        ClinicListItem(
            assignment_id=c["assignment_id"],
            title=c["title"],
            original_assignment_title=c["original_assignment_title"],
            due_date=c["due_date"],
            question_count=c["question_count"],
            is_completed=c["is_completed"],
            score=c["score"],
            max_score=c["max_score"],
            created_at=c["created_at"]
        ) for c in clinics
    ]

    return ClinicListResponse(items=items, total=len(items))
