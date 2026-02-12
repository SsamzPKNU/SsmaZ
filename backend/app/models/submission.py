"""
Submission 모델 정의
제출 기록 및 답안 정보를 저장하는 테이블
"""

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean,
    Enum, ForeignKey, Index, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class SubmissionStatus(str, enum.Enum):
    """제출 상태"""
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    GRADED = "GRADED"


class Submission(Base):
    """
    제출 기록 테이블

    컬럼 설명:
    - submission_id: 제출 고유 ID (PK)
    - assignment_id: 과제 ID
    - student_id: 학생 ID
    - status: 상태 (진행중, 제출됨, 채점완료)
    - total_score: 총점
    - max_score: 만점
    - submitted_at: 제출 시간
    - graded_at: 채점 완료 시간
    """
    __tablename__ = "Submissions"

    submission_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="제출 고유 ID"
    )

    assignment_id = Column(
        Integer,
        ForeignKey("Assignments.assignment_id", ondelete="CASCADE"),
        nullable=False,
        comment="과제 ID"
    )

    student_id = Column(
        Integer,
        ForeignKey("Students.student_id", ondelete="CASCADE"),
        nullable=False,
        comment="학생 ID"
    )

    status = Column(
        Enum(SubmissionStatus),
        default=SubmissionStatus.IN_PROGRESS,
        nullable=False,
        comment="제출 상태"
    )

    total_score = Column(
        Integer,
        default=0,
        nullable=False,
        comment="총점"
    )

    max_score = Column(
        Integer,
        default=0,
        nullable=False,
        comment="만점"
    )

    submitted_at = Column(
        DateTime,
        nullable=True,
        comment="제출 시간"
    )

    graded_at = Column(
        DateTime,
        nullable=True,
        comment="채점 완료 시간"
    )

    wrong_questions = Column(
        String(500),
        nullable=True,
        comment="틀린 문항 번호 (CSV)"
    )

    memo = Column(
        Text,
        nullable=True,
        comment="메모"
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="수정 시간"
    )

    # Relationships
    assignment = relationship("Assignment", back_populates="submissions")
    answers = relationship("Answer", back_populates="submission", cascade="all, delete-orphan")

    __table_args__ = (
        Index("uk_assignment_student", "assignment_id", "student_id", unique=True),
        Index("idx_student_status", "student_id", "status"),
    )

    def __repr__(self):
        return f"<Submission(submission_id={self.submission_id}, student_id={self.student_id})>"


class Answer(Base):
    """
    답안 테이블

    컬럼 설명:
    - answer_id: 답안 고유 ID (PK)
    - submission_id: 제출 ID
    - question_id: 문제 ID
    - student_answer: 학생이 입력한 답
    - is_correct: 정답 여부
    - points_earned: 획득 점수
    """
    __tablename__ = "Answers"

    answer_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="답안 고유 ID"
    )

    submission_id = Column(
        Integer,
        ForeignKey("Submissions.submission_id", ondelete="CASCADE"),
        nullable=False,
        comment="제출 ID"
    )

    question_id = Column(
        Integer,
        ForeignKey("Questions.question_id", ondelete="CASCADE"),
        nullable=False,
        comment="문제 ID"
    )

    student_answer = Column(
        String(500),
        nullable=True,
        comment="학생이 입력한 답"
    )

    is_correct = Column(
        Boolean,
        nullable=True,
        comment="정답 여부"
    )

    points_earned = Column(
        Integer,
        default=0,
        nullable=False,
        comment="획득 점수"
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="수정 시간"
    )

    # Relationships
    submission = relationship("Submission", back_populates="answers")
    question = relationship("Question", back_populates="answers")

    __table_args__ = (
        Index("uk_submission_question", "submission_id", "question_id", unique=True),
    )

    def __repr__(self):
        return f"<Answer(answer_id={self.answer_id}, question_id={self.question_id})>"
