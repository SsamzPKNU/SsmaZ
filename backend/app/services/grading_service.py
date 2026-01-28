"""
자동 채점 서비스
"""

import re
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.submission import Submission, Answer
from app.models.assignment import Question
from app.schemas.submission import GradeResult


def normalize_answer(answer: str) -> str:
    """
    답안 정규화 (공백 제거, 소문자 변환)
    - 앞뒤 공백 제거
    - 중간 공백 모두 제거
    - 소문자로 변환
    """
    if not answer:
        return ""
    return re.sub(r'\s+', '', answer.lower().strip())


def grade_submission(db: Session, submission_id: int) -> GradeResult:
    """
    자동 채점 실행
    - 객관식/단답형: 정규화 후 비교
    - 서술형: 수동 채점 필요 (is_correct = None 유지)
    """
    submission = db.query(Submission).filter(
        Submission.submission_id == submission_id
    ).first()

    if not submission:
        raise ValueError("제출 기록을 찾을 수 없습니다")

    if submission.status.value == "GRADED":
        raise ValueError("이미 채점이 완료된 제출입니다")

    total_score = 0
    max_score = 0
    correct_count = 0
    wrong_count = 0
    wrong_question_ids = []

    for answer in submission.answers:
        question = db.query(Question).filter(
            Question.question_id == answer.question_id
        ).first()

        if not question:
            continue

        max_score += question.points

        # 서술형은 자동 채점 불가
        if question.question_type.value == "ESSAY":
            answer.is_correct = None
            answer.points_earned = 0
            continue

        # 정규화 후 비교
        student = normalize_answer(answer.student_answer or "")
        correct = normalize_answer(question.correct_answer)

        if student == correct:
            answer.is_correct = True
            answer.points_earned = question.points
            total_score += question.points
            correct_count += 1
        else:
            answer.is_correct = False
            answer.points_earned = 0
            wrong_count += 1
            wrong_question_ids.append(question.question_id)

    # Submission 업데이트
    submission.total_score = total_score
    submission.max_score = max_score
    submission.status = "GRADED"
    submission.graded_at = datetime.now()

    db.commit()

    percentage = round((total_score / max_score) * 100, 1) if max_score > 0 else 0.0

    return GradeResult(
        submission_id=submission_id,
        total_score=total_score,
        max_score=max_score,
        percentage=percentage,
        correct_count=correct_count,
        wrong_count=wrong_count,
        wrong_question_ids=wrong_question_ids
    )


def grade_single_answer(
    db: Session,
    answer_id: int,
    is_correct: bool,
    points_earned: int
) -> Answer:
    """
    개별 답안 수동 채점 (서술형용)
    """
    answer = db.query(Answer).filter(
        Answer.answer_id == answer_id
    ).first()

    if not answer:
        raise ValueError("답안을 찾을 수 없습니다")

    answer.is_correct = is_correct
    answer.points_earned = points_earned

    # Submission 점수 재계산
    submission = answer.submission
    total_score = sum(a.points_earned for a in submission.answers)
    submission.total_score = total_score

    db.commit()
    db.refresh(answer)

    return answer
