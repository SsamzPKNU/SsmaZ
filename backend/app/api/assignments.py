"""
과제 API 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.api.auth import get_current_user
from app.api.deps import get_admin_user
from app.models.user import User, UserRole
from app.models.assignment import Assignment, Question
from app.models.submission import Submission
from app.models.student import Student
from app.schemas.assignment import (
    AssignmentCreate, AssignmentUpdate, AssignmentResponse,
    AssignmentStudentResponse, AssignmentListItem, AssignmentListResponse,
    QuestionResponse, QuestionStudentResponse
)
from app.schemas.submission import SubmissionWithStudentItem, SubmissionWithStudentListResponse
from app.models.teacher import Teacher
from app.models.class_model import Class
from app.services.push_notification_service import PushNotificationService

import logging
logger = logging.getLogger(__name__)

router = APIRouter()


def get_teacher_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """TEACHER 또는 ADMIN 권한 체크"""
    if current_user.user_role not in [UserRole.ADMIN, UserRole.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="선생님 또는 관리자 권한이 필요합니다"
        )
    return current_user


@router.get("", response_model=AssignmentListResponse)
async def get_assignments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    assignment_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    과제 목록 조회
    - 본인 학원의 과제만 조회 가능
    """
    query = db.query(Assignment).filter(
        Assignment.academy_id == current_user.academy_id
    )

    if is_active is not None:
        query = query.filter(Assignment.is_active == is_active)

    if assignment_type:
        query = query.filter(Assignment.assignment_type == assignment_type)

    total = query.count()
    assignments = query.order_by(Assignment.created_at.desc()).offset(skip).limit(limit).all()

    items = []
    for a in assignments:
        question_count = db.query(Question).filter(
            Question.assignment_id == a.assignment_id
        ).count()

        items.append(AssignmentListItem(
            assignment_id=a.assignment_id,
            title=a.title,
            description=a.description,
            due_date=a.due_date,
            assignment_type=a.assignment_type,
            is_active=a.is_active,
            question_count=question_count,
            created_at=a.created_at
        ))

    return AssignmentListResponse(items=items, total=total)


@router.get("/{assignment_id}")
async def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    과제 상세 조회
    - 학생은 정답이 제외된 응답을 받음
    - 선생님/관리자는 정답 포함 응답을 받음
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

    questions = db.query(Question).filter(
        Question.assignment_id == assignment_id
    ).order_by(Question.question_number).all()

    # 학생인 경우 정답 제외
    if current_user.user_role == UserRole.STUDENT:
        question_list = [
            QuestionStudentResponse(
                question_id=q.question_id,
                question_number=q.question_number,
                question_text=q.question_text,
                question_type=q.question_type,
                options=q.options,
                points=q.points
            ) for q in questions
        ]
        return AssignmentStudentResponse(
            assignment_id=assignment.assignment_id,
            academy_id=assignment.academy_id,
            teacher_id=assignment.teacher_id,
            title=assignment.title,
            description=assignment.description,
            class_id=assignment.class_id,
            due_date=assignment.due_date,
            assignment_type=assignment.assignment_type,
            is_active=assignment.is_active,
            questions=question_list,
            created_at=assignment.created_at
        )
    else:
        question_list = [
            QuestionResponse(
                question_id=q.question_id,
                question_number=q.question_number,
                question_text=q.question_text,
                question_type=q.question_type,
                options=q.options,
                correct_answer=q.correct_answer,
                points=q.points,
                category=q.category,
                difficulty=q.difficulty
            ) for q in questions
        ]
        return AssignmentResponse(
            assignment_id=assignment.assignment_id,
            academy_id=assignment.academy_id,
            teacher_id=assignment.teacher_id,
            title=assignment.title,
            description=assignment.description,
            class_id=assignment.class_id,
            due_date=assignment.due_date,
            assignment_type=assignment.assignment_type,
            parent_assignment_id=assignment.parent_assignment_id,
            is_active=assignment.is_active,
            questions=question_list,
            created_at=assignment.created_at,
            updated_at=assignment.updated_at
        )


@router.post("", response_model=AssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_or_admin)
):
    """
    과제 생성 (TEACHER, ADMIN)
    """
    # teacher_id 조회
    teacher = db.query(Teacher).filter(
        Teacher.academy_id == current_user.academy_id,
        Teacher.user_id == current_user.user_id
    ).first()
    teacher_id_val = teacher.teacher_id if teacher else current_user.user_id

    # 과제 생성
    assignment = Assignment(
        academy_id=current_user.academy_id,
        teacher_id=teacher_id_val,
        title=data.title,
        description=data.description,
        class_id=data.class_id,
        due_date=data.due_date,
        assignment_type="NORMAL"
    )
    db.add(assignment)
    db.flush()

    # 문제 생성
    for q_data in data.questions:
        question = Question(
            assignment_id=assignment.assignment_id,
            question_number=q_data.question_number,
            question_text=q_data.question_text,
            question_type=q_data.question_type,
            options=q_data.options,
            correct_answer=q_data.correct_answer,
            points=q_data.points,
            category=q_data.category,
            difficulty=q_data.difficulty
        )
        db.add(question)

    db.commit()
    db.refresh(assignment)

    # 푸시 알림 발송
    try:
        if assignment.class_id:
            class_obj = db.query(Class).filter(Class.class_id == assignment.class_id).first()
            if class_obj:
                PushNotificationService.send_assignment_notification(
                    db, assignment, class_obj.class_name
                )
    except Exception as e:
        logger.error(f"[FCM] 과제 알림 발송 실패: {e}")

    # 응답 생성
    questions = db.query(Question).filter(
        Question.assignment_id == assignment.assignment_id
    ).order_by(Question.question_number).all()

    question_list = [
        QuestionResponse(
            question_id=q.question_id,
            question_number=q.question_number,
            question_text=q.question_text,
            question_type=q.question_type,
            options=q.options,
            correct_answer=q.correct_answer,
            points=q.points,
            category=q.category,
            difficulty=q.difficulty
        ) for q in questions
    ]

    return AssignmentResponse(
        assignment_id=assignment.assignment_id,
        academy_id=assignment.academy_id,
        teacher_id=assignment.teacher_id,
        title=assignment.title,
        description=assignment.description,
        class_id=assignment.class_id,
        due_date=assignment.due_date,
        assignment_type=assignment.assignment_type,
        parent_assignment_id=assignment.parent_assignment_id,
        is_active=assignment.is_active,
        questions=question_list,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at
    )


@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: int,
    data: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_or_admin)
):
    """
    과제 수정 (TEACHER, ADMIN)
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

    # 수정 가능 필드 업데이트
    if data.title is not None:
        assignment.title = data.title
    if data.description is not None:
        assignment.description = data.description
    if data.class_id is not None:
        assignment.class_id = data.class_id
    if data.due_date is not None:
        assignment.due_date = data.due_date
    if data.is_active is not None:
        assignment.is_active = data.is_active

    db.commit()
    db.refresh(assignment)

    questions = db.query(Question).filter(
        Question.assignment_id == assignment.assignment_id
    ).order_by(Question.question_number).all()

    question_list = [
        QuestionResponse(
            question_id=q.question_id,
            question_number=q.question_number,
            question_text=q.question_text,
            question_type=q.question_type,
            options=q.options,
            correct_answer=q.correct_answer,
            points=q.points,
            category=q.category,
            difficulty=q.difficulty
        ) for q in questions
    ]

    return AssignmentResponse(
        assignment_id=assignment.assignment_id,
        academy_id=assignment.academy_id,
        teacher_id=assignment.teacher_id,
        title=assignment.title,
        description=assignment.description,
        class_id=assignment.class_id,
        due_date=assignment.due_date,
        assignment_type=assignment.assignment_type,
        parent_assignment_id=assignment.parent_assignment_id,
        is_active=assignment.is_active,
        questions=question_list,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at
    )


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_or_admin)
):
    """
    과제 삭제 (TEACHER, ADMIN)
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

    db.delete(assignment)
    db.commit()

    return None


@router.get("/{assignment_id}/submissions", response_model=SubmissionWithStudentListResponse)
async def get_assignment_submissions(
    assignment_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_teacher_or_admin)
):
    """
    과제 제출 현황 조회 (TEACHER, ADMIN)

    특정 과제에 대한 학생들의 제출 현황을 조회합니다.
    학생 이름이 포함된 제출 목록을 반환합니다.

    Path Parameters:
        - assignment_id: 과제 ID

    Query Parameters:
        - skip: 페이지네이션 오프셋 (기본: 0)
        - limit: 페이지네이션 제한 (기본: 50)

    Headers:
        Authorization: Bearer {access_token}

    Returns:
        SubmissionWithStudentListResponse: 제출 목록 (학생 정보 포함)

    Raises:
        401: 인증되지 않은 사용자
        403: 권한 없음
        404: 과제를 찾을 수 없음

    사용 예시:
        GET /api/assignments/1/submissions
    """
    # 과제 확인
    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == assignment_id,
        Assignment.academy_id == current_user.academy_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="과제를 찾을 수 없습니다"
        )

    # 제출 목록 조회
    query = db.query(Submission).filter(
        Submission.assignment_id == assignment_id
    )

    total = query.count()
    submissions = query.order_by(Submission.submitted_at.desc()).offset(skip).limit(limit).all()

    items = []
    for s in submissions:
        # 학생 정보 조회
        student = db.query(Student).filter(
            Student.student_id == s.student_id
        ).first()

        items.append(SubmissionWithStudentItem(
            submission_id=s.submission_id,
            assignment_id=s.assignment_id,
            student_id=s.student_id,
            student_name=student.name if student else "Unknown",
            status=s.status,
            total_score=s.total_score,
            max_score=s.max_score,
            submitted_at=s.submitted_at,
            graded_at=s.graded_at
        ))

    return SubmissionWithStudentListResponse(items=items, total=total)
