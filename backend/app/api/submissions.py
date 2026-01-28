"""
제출/답안 API 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User, UserRole
from app.models.assignment import Assignment, Question
from app.models.submission import Submission, Answer
from app.models.student import Student
from app.schemas.submission import (
    SubmissionStart, SubmissionAnswersUpdate, SubmissionResponse,
    SubmissionDetailResponse, SubmissionListItem, SubmissionListResponse,
    AnswerResponse, GradeResult, GradeDetailResult, AnswerDetailResponse
)
from app.services.grading_service import grade_submission

router = APIRouter()


def get_teacher_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """TEACHER 또는 ADMIN 권한 체크"""
    if current_user.user_role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="선생님 또는 관리자 권한이 필요합니다"
        )
    return current_user


def get_student_id_from_user(db: Session, user: User) -> int:
    """User에서 Student ID 조회"""
    student = db.query(Student).filter(
        Student.academy_id == user.academy_id,
        Student.name == user.name
    ).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="학생 정보를 찾을 수 없습니다"
        )
    return student.student_id


@router.get("/my", response_model=SubmissionListResponse)
async def get_my_submissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    내 제출 목록 조회 (STUDENT)
    """
    if current_user.user_role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="학생만 조회 가능합니다"
        )

    student_id = get_student_id_from_user(db, current_user)

    query = db.query(Submission).filter(
        Submission.student_id == student_id
    )

    if status_filter:
        query = query.filter(Submission.status == status_filter)

    total = query.count()
    submissions = query.order_by(Submission.created_at.desc()).offset(skip).limit(limit).all()

    items = []
    for s in submissions:
        assignment = db.query(Assignment).filter(
            Assignment.assignment_id == s.assignment_id
        ).first()

        items.append(SubmissionListItem(
            submission_id=s.submission_id,
            assignment_id=s.assignment_id,
            assignment_title=assignment.title if assignment else "",
            status=s.status,
            total_score=s.total_score,
            max_score=s.max_score,
            submitted_at=s.submitted_at,
            graded_at=s.graded_at
        ))

    return SubmissionListResponse(items=items, total=total)


@router.get("/assignment/{assignment_id}", response_model=SubmissionListResponse)
async def get_assignment_submissions(
    assignment_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_or_admin)
):
    """
    과제별 제출 목록 조회 (TEACHER, ADMIN)
    """
    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == assignment_id,
        Assignment.academy_id == current_user.academy_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="과제를 찾을 수 없습니다"
        )

    query = db.query(Submission).filter(
        Submission.assignment_id == assignment_id
    )

    total = query.count()
    submissions = query.order_by(Submission.submitted_at.desc()).offset(skip).limit(limit).all()

    items = []
    for s in submissions:
        items.append(SubmissionListItem(
            submission_id=s.submission_id,
            assignment_id=s.assignment_id,
            assignment_title=assignment.title,
            status=s.status,
            total_score=s.total_score,
            max_score=s.max_score,
            submitted_at=s.submitted_at,
            graded_at=s.graded_at
        ))

    return SubmissionListResponse(items=items, total=total)


@router.post("/{assignment_id}/start", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def start_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    과제 시작 (STUDENT)
    - 이미 시작한 과제가 있으면 기존 제출 반환
    """
    if current_user.user_role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="학생만 과제를 시작할 수 있습니다"
        )

    student_id = get_student_id_from_user(db, current_user)

    # 과제 확인
    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == assignment_id,
        Assignment.academy_id == current_user.academy_id,
        Assignment.is_active == True
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="과제를 찾을 수 없습니다"
        )

    # 기존 제출 확인
    existing = db.query(Submission).filter(
        Submission.assignment_id == assignment_id,
        Submission.student_id == student_id
    ).first()

    if existing:
        return SubmissionResponse(
            submission_id=existing.submission_id,
            assignment_id=existing.assignment_id,
            student_id=existing.student_id,
            status=existing.status,
            total_score=existing.total_score,
            max_score=existing.max_score,
            submitted_at=existing.submitted_at,
            graded_at=existing.graded_at,
            created_at=existing.created_at,
            updated_at=existing.updated_at
        )

    # 새 제출 생성
    submission = Submission(
        assignment_id=assignment_id,
        student_id=student_id,
        status="IN_PROGRESS"
    )
    db.add(submission)
    db.flush()

    # 빈 답안 생성
    questions = db.query(Question).filter(
        Question.assignment_id == assignment_id
    ).all()

    for q in questions:
        answer = Answer(
            submission_id=submission.submission_id,
            question_id=q.question_id
        )
        db.add(answer)

    db.commit()
    db.refresh(submission)

    return SubmissionResponse(
        submission_id=submission.submission_id,
        assignment_id=submission.assignment_id,
        student_id=submission.student_id,
        status=submission.status,
        total_score=submission.total_score,
        max_score=submission.max_score,
        submitted_at=submission.submitted_at,
        graded_at=submission.graded_at,
        created_at=submission.created_at,
        updated_at=submission.updated_at
    )


@router.put("/{submission_id}/answers", response_model=SubmissionResponse)
async def save_answers(
    submission_id: int,
    data: SubmissionAnswersUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    답안 저장 (STUDENT)
    - 제출 전 임시 저장 가능
    """
    if current_user.user_role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="학생만 답안을 저장할 수 있습니다"
        )

    student_id = get_student_id_from_user(db, current_user)

    submission = db.query(Submission).filter(
        Submission.submission_id == submission_id,
        Submission.student_id == student_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="제출 기록을 찾을 수 없습니다"
        )

    if submission.status.value != "IN_PROGRESS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 제출된 과제는 수정할 수 없습니다"
        )

    # 답안 저장
    for answer_input in data.answers:
        answer = db.query(Answer).filter(
            Answer.submission_id == submission_id,
            Answer.question_id == answer_input.question_id
        ).first()

        if answer:
            answer.student_answer = answer_input.student_answer

    db.commit()
    db.refresh(submission)

    return SubmissionResponse(
        submission_id=submission.submission_id,
        assignment_id=submission.assignment_id,
        student_id=submission.student_id,
        status=submission.status,
        total_score=submission.total_score,
        max_score=submission.max_score,
        submitted_at=submission.submitted_at,
        graded_at=submission.graded_at,
        created_at=submission.created_at,
        updated_at=submission.updated_at
    )


@router.post("/{submission_id}/submit", response_model=SubmissionResponse)
async def submit_assignment(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    최종 제출 (STUDENT)
    """
    if current_user.user_role != UserRole.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="학생만 제출할 수 있습니다"
        )

    student_id = get_student_id_from_user(db, current_user)

    submission = db.query(Submission).filter(
        Submission.submission_id == submission_id,
        Submission.student_id == student_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="제출 기록을 찾을 수 없습니다"
        )

    if submission.status.value != "IN_PROGRESS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 제출된 과제입니다"
        )

    submission.status = "SUBMITTED"
    submission.submitted_at = datetime.now()

    db.commit()
    db.refresh(submission)

    return SubmissionResponse(
        submission_id=submission.submission_id,
        assignment_id=submission.assignment_id,
        student_id=submission.student_id,
        status=submission.status,
        total_score=submission.total_score,
        max_score=submission.max_score,
        submitted_at=submission.submitted_at,
        graded_at=submission.graded_at,
        created_at=submission.created_at,
        updated_at=submission.updated_at
    )


@router.post("/{submission_id}/grade", response_model=GradeResult)
async def grade_submission_endpoint(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_or_admin)
):
    """
    자동 채점 (TEACHER, ADMIN)
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

    if submission.status.value == "IN_PROGRESS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="제출되지 않은 과제입니다"
        )

    try:
        result = grade_submission(db, submission_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{submission_id}/result", response_model=GradeDetailResult)
async def get_submission_result(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    채점 결과 조회
    """
    submission = db.query(Submission).filter(
        Submission.submission_id == submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="제출 기록을 찾을 수 없습니다"
        )

    # 권한 확인
    if current_user.user_role == UserRole.STUDENT:
        student_id = get_student_id_from_user(db, current_user)
        if submission.student_id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="권한이 없습니다"
            )
    else:
        assignment = db.query(Assignment).filter(
            Assignment.assignment_id == submission.assignment_id,
            Assignment.academy_id == current_user.academy_id
        ).first()
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="권한이 없습니다"
            )

    if submission.status.value != "GRADED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="아직 채점되지 않은 제출입니다"
        )

    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == submission.assignment_id
    ).first()

    student = db.query(Student).filter(
        Student.student_id == submission.student_id
    ).first()

    answers = db.query(Answer).filter(
        Answer.submission_id == submission_id
    ).all()

    answer_details = []
    for a in answers:
        question = db.query(Question).filter(
            Question.question_id == a.question_id
        ).first()

        if question:
            answer_details.append(AnswerDetailResponse(
                answer_id=a.answer_id,
                question_id=a.question_id,
                question_number=question.question_number,
                question_text=question.question_text,
                student_answer=a.student_answer,
                correct_answer=question.correct_answer,
                is_correct=a.is_correct,
                points_earned=a.points_earned,
                max_points=question.points
            ))

    percentage = round((submission.total_score / submission.max_score) * 100, 1) if submission.max_score > 0 else 0.0

    return GradeDetailResult(
        submission_id=submission.submission_id,
        assignment_title=assignment.title if assignment else "",
        student_name=student.name if student else "",
        total_score=submission.total_score,
        max_score=submission.max_score,
        percentage=percentage,
        answers=answer_details,
        graded_at=submission.graded_at
    )
