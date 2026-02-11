"""
선생님 클리닉 과제 API
오답 문항 조회, 클리닉 과제 생성, 유사 문제 추천 기능 제공
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.class_model import Class
from app.models.submission import Submission, Answer, SubmissionStatus
from app.models.assignment import Assignment, Question
from app.models.question_bank import QuestionBank
from app.api.auth import get_current_user
from app.services.class_teacher_service import ClassTeacherService
from app.services.teacher_app_service import TeacherAppService
from app.services.clinic_service import generate_clinic
from app.schemas.clinic import ClinicType, WrongQuestionInfo


from app.schemas.common import COMMON_RESPONSES

router = APIRouter(
    prefix="/teacher/clinic",
    tags=["선생님 - 클리닉생성"],
    responses=COMMON_RESPONSES
)


# ========== 스키마 ==========

class WrongAnswerItem(BaseModel):
    """학생별 오답 문항"""
    student_id: int
    student_name: str
    class_name: Optional[str] = None
    assignment_id: int
    assignment_title: str
    question_id: int
    question_number: int
    question_text: str
    category: Optional[str] = None
    student_answer: Optional[str] = None
    correct_answer: str
    submitted_at: Optional[str] = None


class WrongAnswersResponse(BaseModel):
    """오답 문항 목록 응답"""
    items: List[WrongAnswerItem]
    total: int


class ClinicCreateRequest(BaseModel):
    """클리닉 과제 생성 요청"""
    student_id: int = Field(..., description="학생 ID")
    question_ids: List[int] = Field(..., min_length=1, description="문제 ID 목록")
    clinic_type: ClinicType = Field(default=ClinicType.SAME, description="클리닉 유형 (SAME, SIMILAR)")
    title: Optional[str] = Field(None, max_length=200, description="클리닉 제목")
    due_date: Optional[date] = Field(None, description="마감일")


class ClinicCreateResponse(BaseModel):
    """클리닉 과제 생성 응답"""
    assignment_id: int
    title: str
    question_count: int
    student_id: int
    student_name: str


class SimilarQuestionItem(BaseModel):
    """유사 문제 항목"""
    question_bank_id: int
    question_text: str
    question_type: str
    category: str
    difficulty: str
    usage_count: int


class SimilarQuestionsResponse(BaseModel):
    """유사 문제 목록 응답"""
    category: str
    items: List[SimilarQuestionItem]
    total: int


# ========== API ==========

@router.get("/wrong-answers", response_model=WrongAnswersResponse)
async def get_wrong_answers(
    student_id: Optional[int] = Query(None, description="학생 ID"),
    class_id: Optional[int] = Query(None, description="반 ID"),
    assignment_id: Optional[int] = Query(None, description="과제 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    학생별 오답 문항 조회

    담당 반 학생들의 오답 문항을 조회합니다.

    Query Parameters:
    - student_id: 학생 ID (필터)
    - class_id: 반 ID (필터)
    - assignment_id: 과제 ID (필터)
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    # 담당 반 목록 (수준별 배정 + 레거시)
    classes = ClassTeacherService.get_teacher_classes(db, teacher_id)
    class_ids = [c.class_id for c in classes]
    class_map = {c.class_id: c.name for c in classes}

    if not class_ids:
        return WrongAnswersResponse(items=[], total=0)

    # 학생 필터
    student_query = db.query(Student).filter(
        and_(
            Student.academy_id == current_user.academy_id,
            Student.class_id.in_(class_ids)
        )
    )

    if student_id:
        student_query = student_query.filter(Student.student_id == student_id)

    if class_id:
        if class_id not in class_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="담당 반이 아닙니다"
            )
        student_query = student_query.filter(Student.class_id == class_id)

    students = student_query.all()
    student_ids = [s.student_id for s in students]
    student_map = {s.student_id: s for s in students}

    if not student_ids:
        return WrongAnswersResponse(items=[], total=0)

    # 오답 조회
    answer_query = db.query(Answer).join(Submission).filter(
        and_(
            Submission.student_id.in_(student_ids),
            Submission.status == SubmissionStatus.GRADED,
            Answer.is_correct == False
        )
    )

    if assignment_id:
        answer_query = answer_query.filter(Submission.assignment_id == assignment_id)

    wrong_answers = answer_query.all()

    items = []
    for ans in wrong_answers:
        submission = db.query(Submission).filter(
            Submission.submission_id == ans.submission_id
        ).first()

        question = db.query(Question).filter(
            Question.question_id == ans.question_id
        ).first()

        assignment = db.query(Assignment).filter(
            Assignment.assignment_id == submission.assignment_id
        ).first()

        student = student_map.get(submission.student_id)

        if student and question and assignment:
            items.append(WrongAnswerItem(
                student_id=student.student_id,
                student_name=student.name,
                class_name=class_map.get(student.class_id),
                assignment_id=assignment.assignment_id,
                assignment_title=assignment.title,
                question_id=question.question_id,
                question_number=question.question_number,
                question_text=question.question_text,
                category=question.category,
                student_answer=ans.student_answer,
                correct_answer=question.correct_answer,
                submitted_at=submission.submitted_at.isoformat() if submission.submitted_at else None
            ))

    return WrongAnswersResponse(items=items, total=len(items))


@router.post("/assignments", response_model=ClinicCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_clinic_assignment(
    data: ClinicCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    클리닉 과제 생성

    학생의 오답 문항을 기반으로 클리닉 과제를 생성합니다.

    Request Body:
    - student_id: 학생 ID
    - question_ids: 문제 ID 목록
    - clinic_type: 클리닉 유형 (SAME, SIMILAR)
    - title: 클리닉 제목 (선택)
    - due_date: 마감일 (선택)
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    # 학생 권한 확인
    if not TeacherAppService.verify_student_teacher(db, data.student_id, teacher_id, current_user.academy_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="담당 학생이 아닙니다"
        )

    student = db.query(Student).filter(
        Student.student_id == data.student_id
    ).first()

    # 문제 조회
    questions = db.query(Question).filter(
        Question.question_id.in_(data.question_ids)
    ).all()

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="선택한 문제가 없습니다"
        )

    # 첫 번째 문제의 과제 정보로 원본 확인
    first_assignment = db.query(Assignment).filter(
        Assignment.assignment_id == questions[0].assignment_id
    ).first()

    # 클리닉 과제 생성
    clinic_title = data.title or f"[클리닉] {student.name} - 오답 복습"

    clinic_assignment = Assignment(
        academy_id=current_user.academy_id,
        teacher_id=teacher_id,
        title=clinic_title,
        description=f"{student.name} 학생의 오답 클리닉",
        due_date=data.due_date,
        assignment_type="CLINIC",
        parent_assignment_id=first_assignment.assignment_id if first_assignment else None
    )
    db.add(clinic_assignment)
    db.flush()

    # 문제 복사/생성
    for idx, q in enumerate(questions, 1):
        if data.clinic_type == ClinicType.SAME:
            new_question = Question(
                assignment_id=clinic_assignment.assignment_id,
                question_number=idx,
                question_text=q.question_text,
                question_type=q.question_type,
                options=q.options,
                correct_answer=q.correct_answer,
                points=q.points,
                category=q.category,
                difficulty=q.difficulty
            )
        else:  # SIMILAR
            similar = db.query(QuestionBank).filter(
                and_(
                    QuestionBank.academy_id == current_user.academy_id,
                    QuestionBank.category == q.category,
                    QuestionBank.difficulty == q.difficulty
                )
            ).order_by(func.rand()).first()

            if similar:
                new_question = Question(
                    assignment_id=clinic_assignment.assignment_id,
                    question_number=idx,
                    question_text=similar.question_text,
                    question_type=similar.question_type,
                    options=similar.options,
                    correct_answer=similar.correct_answer,
                    points=q.points,
                    category=similar.category,
                    difficulty=similar.difficulty
                )
                similar.usage_count += 1
            else:
                new_question = Question(
                    assignment_id=clinic_assignment.assignment_id,
                    question_number=idx,
                    question_text=q.question_text,
                    question_type=q.question_type,
                    options=q.options,
                    correct_answer=q.correct_answer,
                    points=q.points,
                    category=q.category,
                    difficulty=q.difficulty
                )

        db.add(new_question)

    # 학생에게 제출 레코드 생성 (진행중 상태)
    from app.models.submission import Submission, SubmissionStatus
    new_submission = Submission(
        assignment_id=clinic_assignment.assignment_id,
        student_id=data.student_id,
        status=SubmissionStatus.IN_PROGRESS,
        total_score=0,
        max_score=sum(q.points for q in questions)
    )
    db.add(new_submission)

    db.commit()
    db.refresh(clinic_assignment)

    return ClinicCreateResponse(
        assignment_id=clinic_assignment.assignment_id,
        title=clinic_assignment.title,
        question_count=len(questions),
        student_id=data.student_id,
        student_name=student.name
    )


@router.get("/similar-questions", response_model=SimilarQuestionsResponse)
async def get_similar_questions(
    category: str = Query(..., description="문제 유형"),
    difficulty: Optional[str] = Query(None, description="난이도 (EASY, MEDIUM, HARD)"),
    limit: int = Query(10, ge=1, le=50, description="최대 개수"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    유사 문제 추천

    문제 은행에서 특정 카테고리의 유사 문제를 조회합니다.

    Query Parameters:
    - category: 문제 유형 (필수)
    - difficulty: 난이도 (선택)
    - limit: 최대 개수 (기본 10)
    """
    query = db.query(QuestionBank).filter(
        and_(
            QuestionBank.academy_id == current_user.academy_id,
            QuestionBank.category == category
        )
    )

    if difficulty:
        query = query.filter(QuestionBank.difficulty == difficulty)

    questions = query.order_by(QuestionBank.usage_count.asc()).limit(limit).all()

    items = [
        SimilarQuestionItem(
            question_bank_id=q.question_bank_id,
            question_text=q.question_text,
            question_type=q.question_type.value,
            category=q.category,
            difficulty=q.difficulty.value,
            usage_count=q.usage_count
        )
        for q in questions
    ]

    return SimilarQuestionsResponse(
        category=category,
        items=items,
        total=len(items)
    )
