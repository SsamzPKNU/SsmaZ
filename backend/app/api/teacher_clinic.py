"""
선생님 클리닉 과제 API
오답 문항 조회, 클리닉 과제 생성, 유사 문제 추천 기능 제공
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.submission import Submission, Answer, SubmissionStatus
from app.models.assignment import Assignment, Question, Difficulty
from app.models.question_bank import QuestionBank
from app.api.auth import get_current_user
from app.services.teacher_app_service import TeacherAppService

from app.schemas.common import COMMON_RESPONSES

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/teacher/clinic",
    tags=["선생님 - 클리닉생성"],
    responses=COMMON_RESPONSES
)


# ========== 스키마 ==========

class WrongAnswerItem(BaseModel):
    student_id: int
    student_name: str
    question_id: int
    question_text: str
    category: Optional[str] = None


class WrongAnswersResponse(BaseModel):
    items: List[WrongAnswerItem]


class SimilarQuestionItem(BaseModel):
    id: int
    content: str
    unit: Optional[str] = None
    original: int


class SimilarQuestionsResponse(BaseModel):
    items: List[SimilarQuestionItem]


class ClinicCreateRequest(BaseModel):
    student_ids: List[int] = Field(..., min_length=1)
    class_id: int
    title: str
    clinic_type: str  # "ORIGINAL" | "SIMILAR"
    question_ids: List[int] = Field(..., min_length=1)
    difficulty: str   # "easier" | "same" | "harder"


class ClinicCreateResponse(BaseModel):
    id: int
    title: str
    message: str


# ========== 난이도 매핑 헬퍼 ==========

DIFFICULTY_ORDER = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]


def map_relative_difficulty(base: Difficulty, direction: str) -> Difficulty:
    """상대적 난이도 방향을 절대 난이도로 변환"""
    idx = DIFFICULTY_ORDER.index(base)
    if direction == "easier":
        return DIFFICULTY_ORDER[max(0, idx - 1)]
    elif direction == "harder":
        return DIFFICULTY_ORDER[min(len(DIFFICULTY_ORDER) - 1, idx + 1)]
    else:  # "same"
        return base


# ========== API ==========

@router.get("/wrong-answers", response_model=WrongAnswersResponse)
async def get_wrong_answers(
    class_id: int = Query(..., description="반 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    반별 오답 문항 조회

    담당 반 학생들의 오답 문항을 조회합니다.
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    # 담당 반 권한 확인
    if not TeacherAppService.verify_class_teacher(db, class_id, teacher_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="담당 반이 아닙니다"
        )

    # JOIN으로 한 번에 조회 (N+1 방지)
    results = (
        db.query(
            Student.student_id,
            Student.name.label("student_name"),
            Question.question_id,
            Question.question_text,
            Question.category,
        )
        .join(Submission, Submission.student_id == Student.student_id)
        .join(Answer, Answer.submission_id == Submission.submission_id)
        .join(Question, Question.question_id == Answer.question_id)
        .filter(
            and_(
                Student.academy_id == current_user.academy_id,
                Student.class_id == class_id,
                Submission.status == SubmissionStatus.GRADED,
                Answer.is_correct == False,
            )
        )
        .all()
    )

    items = [
        WrongAnswerItem(
            student_id=r.student_id,
            student_name=r.student_name,
            question_id=r.question_id,
            question_text=r.question_text,
            category=r.category,
        )
        for r in results
    ]

    return WrongAnswersResponse(items=items)


@router.get("/similar-questions", response_model=SimilarQuestionsResponse)
async def get_similar_questions(
    question_ids: str = Query(..., description="원본 문항 ID (콤마 구분)"),
    difficulty: str = Query("same", description="상대 난이도 (easier/same/harder)"),
    limit: int = Query(10, ge=1, le=50, description="최대 개수"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    유사 문제 추천

    원본 문항 ID 기반으로 문제 은행에서 유사 문제를 조회합니다.
    """
    # question_ids 파싱
    try:
        qid_list = [int(x.strip()) for x in question_ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="question_ids 형식이 올바르지 않습니다"
        )

    if not qid_list:
        return SimilarQuestionsResponse(items=[])

    # 원본 문항 조회 (category, difficulty 확인)
    original_questions = db.query(Question).filter(
        Question.question_id.in_(qid_list)
    ).all()

    if not original_questions:
        return SimilarQuestionsResponse(items=[])

    original_map = {q.question_id: q for q in original_questions}

    # 각 원본 문항당 균등 분배
    per_question_limit = max(1, limit // len(qid_list))
    remainder = limit % len(qid_list)

    items: List[SimilarQuestionItem] = []

    for i, qid in enumerate(qid_list):
        orig = original_map.get(qid)
        if not orig:
            continue

        # 상대 난이도 → 절대 난이도 변환
        target_difficulty = map_relative_difficulty(orig.difficulty, difficulty)

        # 이 문항에 할당할 개수 (앞쪽 문항에 나머지 분배)
        current_limit = per_question_limit + (1 if i < remainder else 0)

        # QuestionBank에서 같은 category + 매핑된 difficulty로 검색
        similar = (
            db.query(QuestionBank)
            .filter(
                and_(
                    QuestionBank.academy_id == current_user.academy_id,
                    QuestionBank.category == orig.category,
                    QuestionBank.difficulty == target_difficulty,
                )
            )
            .order_by(QuestionBank.usage_count.asc())
            .limit(current_limit)
            .all()
        )

        for q in similar:
            items.append(SimilarQuestionItem(
                id=q.question_bank_id,
                content=q.question_text,
                unit=q.category,
                original=qid,
            ))

    return SimilarQuestionsResponse(items=items)


@router.post("/assignments", response_model=ClinicCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_clinic_assignment(
    data: ClinicCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    클리닉 과제 생성

    선택한 학생들에게 오답 기반 클리닉 과제를 생성합니다.
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    # 반 권한 확인
    if not TeacherAppService.verify_class_teacher(db, data.class_id, teacher_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="담당 반이 아닙니다"
        )

    # 문항 조회: Question 테이블 우선 → QuestionBank fallback
    source_questions = []
    found_ids = set()

    # 1) Question 테이블에서 검색
    questions_from_q = db.query(Question).filter(
        Question.question_id.in_(data.question_ids)
    ).all()
    for q in questions_from_q:
        source_questions.append({
            "question_text": q.question_text,
            "question_type": q.question_type,
            "options": q.options,
            "correct_answer": q.correct_answer,
            "points": q.points,
            "category": q.category,
            "difficulty": q.difficulty,
        })
        found_ids.add(q.question_id)

    # 2) 없는 ID는 QuestionBank에서 검색
    missing_ids = [qid for qid in data.question_ids if qid not in found_ids]
    if missing_ids:
        questions_from_qb = db.query(QuestionBank).filter(
            QuestionBank.question_bank_id.in_(missing_ids)
        ).all()
        for q in questions_from_qb:
            source_questions.append({
                "question_text": q.question_text,
                "question_type": q.question_type,
                "options": q.options,
                "correct_answer": q.correct_answer,
                "points": 1,
                "category": q.category,
                "difficulty": q.difficulty,
            })
            found_ids.add(q.question_bank_id)
            q.usage_count += 1

    if not source_questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="선택한 문제가 없습니다"
        )

    # Assignment 생성
    clinic_assignment = Assignment(
        academy_id=current_user.academy_id,
        class_id=data.class_id,
        teacher_id=teacher_id,
        title=data.title,
        assignment_type="CLINIC",
    )
    db.add(clinic_assignment)
    db.flush()

    # Question 레코드 복사 생성
    total_points = 0
    for idx, src in enumerate(source_questions, 1):
        new_question = Question(
            assignment_id=clinic_assignment.assignment_id,
            question_number=idx,
            question_text=src["question_text"],
            question_type=src["question_type"],
            options=src["options"],
            correct_answer=src["correct_answer"],
            points=src["points"],
            category=src["category"],
            difficulty=src["difficulty"],
        )
        db.add(new_question)
        total_points += src["points"]

    # 각 학생별 Submission 생성
    for student_id in data.student_ids:
        new_submission = Submission(
            assignment_id=clinic_assignment.assignment_id,
            student_id=student_id,
            status=SubmissionStatus.IN_PROGRESS,
            total_score=0,
            max_score=total_points,
        )
        db.add(new_submission)

    db.commit()
    db.refresh(clinic_assignment)

    student_count = len(data.student_ids)
    question_count = len(source_questions)

    return ClinicCreateResponse(
        id=clinic_assignment.assignment_id,
        title=clinic_assignment.title,
        message=f"{student_count}명의 학생에게 {question_count}문항 클리닉 과제가 생성되었습니다",
    )
