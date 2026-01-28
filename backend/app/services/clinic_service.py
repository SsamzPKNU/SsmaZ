"""
클리닉 과제 생성 서비스
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.submission import Submission, Answer
from app.models.assignment import Assignment, Question
from app.models.question_bank import QuestionBank
from app.schemas.clinic import ClinicType, WrongQuestionInfo


def get_wrong_questions(db: Session, submission_id: int) -> List[WrongQuestionInfo]:
    """
    틀린 문제 목록 조회
    """
    submission = db.query(Submission).filter(
        Submission.submission_id == submission_id
    ).first()

    if not submission:
        raise ValueError("제출 기록을 찾을 수 없습니다")

    if submission.status.value != "GRADED":
        raise ValueError("채점 완료된 제출만 조회 가능합니다")

    wrong_answers = db.query(Answer).filter(
        Answer.submission_id == submission_id,
        Answer.is_correct == False
    ).all()

    wrong_questions = []
    for answer in wrong_answers:
        question = db.query(Question).filter(
            Question.question_id == answer.question_id
        ).first()

        if question:
            wrong_questions.append(WrongQuestionInfo(
                question_id=question.question_id,
                question_number=question.question_number,
                question_text=question.question_text,
                student_answer=answer.student_answer,
                correct_answer=question.correct_answer,
                category=question.category
            ))

    return wrong_questions


def generate_clinic(
    db: Session,
    submission_id: int,
    clinic_type: ClinicType,
    teacher_id: int,
    title: Optional[str] = None,
    due_date=None
) -> Assignment:
    """
    틀린 문제 기반 클리닉 과제 생성
    """
    # 1. 원본 제출 조회
    submission = db.query(Submission).filter(
        Submission.submission_id == submission_id
    ).first()

    if not submission:
        raise ValueError("제출 기록을 찾을 수 없습니다")

    if submission.status.value != "GRADED":
        raise ValueError("채점 완료된 제출만 클리닉 생성 가능합니다")

    original_assignment = db.query(Assignment).filter(
        Assignment.assignment_id == submission.assignment_id
    ).first()

    # 2. 틀린 문제 추출
    wrong_answers = db.query(Answer).filter(
        Answer.submission_id == submission_id,
        Answer.is_correct == False
    ).all()

    if not wrong_answers:
        raise ValueError("틀린 문제가 없습니다")

    wrong_question_ids = [a.question_id for a in wrong_answers]
    wrong_questions = db.query(Question).filter(
        Question.question_id.in_(wrong_question_ids)
    ).all()

    # 3. 클리닉 과제 생성
    clinic_title = title or f"[클리닉] {original_assignment.title}"

    clinic_assignment = Assignment(
        academy_id=original_assignment.academy_id,
        teacher_id=teacher_id,
        title=clinic_title,
        description=f"원본 과제: {original_assignment.title}의 오답 클리닉",
        due_date=due_date,
        assignment_type="CLINIC",
        parent_assignment_id=original_assignment.assignment_id
    )
    db.add(clinic_assignment)
    db.flush()

    # 4. 문제 복사/생성
    for idx, q in enumerate(wrong_questions, 1):
        if clinic_type == ClinicType.SAME:
            # 동일 문제 복사
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
            # 문제은행에서 유사 문제 추출
            similar = db.query(QuestionBank).filter(
                QuestionBank.academy_id == original_assignment.academy_id,
                QuestionBank.category == q.category,
                QuestionBank.difficulty == q.difficulty
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
                # 유사문제 없으면 동일문제로 대체
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

    db.commit()
    db.refresh(clinic_assignment)

    return clinic_assignment


def get_student_clinics(
    db: Session,
    student_id: int,
    academy_id: int
) -> List[dict]:
    """
    학생별 클리닉 과제 목록 조회
    """
    # 클리닉 과제 조회
    clinics = db.query(Assignment).filter(
        Assignment.academy_id == academy_id,
        Assignment.assignment_type == "CLINIC",
        Assignment.is_active == True
    ).all()

    result = []
    for clinic in clinics:
        # 해당 학생의 제출 여부 확인
        submission = db.query(Submission).filter(
            Submission.assignment_id == clinic.assignment_id,
            Submission.student_id == student_id
        ).first()

        # 원본 과제 제목
        original_title = ""
        if clinic.parent_assignment_id:
            original = db.query(Assignment).filter(
                Assignment.assignment_id == clinic.parent_assignment_id
            ).first()
            if original:
                original_title = original.title

        question_count = db.query(Question).filter(
            Question.assignment_id == clinic.assignment_id
        ).count()

        result.append({
            "assignment_id": clinic.assignment_id,
            "title": clinic.title,
            "original_assignment_title": original_title,
            "due_date": clinic.due_date,
            "question_count": question_count,
            "is_completed": submission.status.value == "GRADED" if submission else False,
            "score": submission.total_score if submission and submission.status.value == "GRADED" else None,
            "max_score": submission.max_score if submission and submission.status.value == "GRADED" else None,
            "created_at": clinic.created_at
        })

    return result
