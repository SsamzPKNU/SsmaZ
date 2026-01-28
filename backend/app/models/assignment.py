"""
Assignment 모델 정의
과제 및 문제 정보를 저장하는 테이블
"""

from sqlalchemy import (
    Column, Integer, String, Text, Date, DateTime, Boolean,
    Enum, JSON, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class AssignmentType(str, enum.Enum):
    """과제 유형"""
    NORMAL = "NORMAL"
    CLINIC = "CLINIC"


class QuestionType(str, enum.Enum):
    """문제 유형"""
    CHOICE = "CHOICE"
    SHORT_ANSWER = "SHORT_ANSWER"
    ESSAY = "ESSAY"


class Difficulty(str, enum.Enum):
    """문제 난이도"""
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class Assignment(Base):
    """
    과제 테이블

    컬럼 설명:
    - assignment_id: 과제 고유 ID (PK)
    - academy_id: 학원 ID
    - class_id: 반 ID (NULL이면 개인 과제)
    - teacher_id: 출제한 선생님 ID
    - title: 과제 제목
    - description: 과제 설명
    - due_date: 마감일
    - assignment_type: 과제 유형 (NORMAL, CLINIC)
    - parent_assignment_id: 클리닉일 경우 원본 과제 ID
    - is_active: 활성화 여부
    """
    __tablename__ = "Assignments"

    assignment_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="과제 고유 ID"
    )

    academy_id = Column(
        Integer,
        ForeignKey("Academies.academy_id", ondelete="CASCADE"),
        nullable=False,
        comment="학원 ID"
    )

    class_id = Column(
        Integer,
        nullable=True,
        comment="반 ID (NULL이면 개인 과제)"
    )

    teacher_id = Column(
        Integer,
        ForeignKey("Users.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="출제한 선생님 ID"
    )

    title = Column(
        String(200),
        nullable=False,
        comment="과제 제목"
    )

    description = Column(
        Text,
        nullable=True,
        comment="과제 설명"
    )

    due_date = Column(
        Date,
        nullable=True,
        comment="마감일"
    )

    assignment_type = Column(
        Enum(AssignmentType),
        default=AssignmentType.NORMAL,
        nullable=False,
        comment="과제 유형 (NORMAL, CLINIC)"
    )

    parent_assignment_id = Column(
        Integer,
        ForeignKey("Assignments.assignment_id", ondelete="SET NULL"),
        nullable=True,
        comment="클리닉일 경우 원본 과제 ID"
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="활성화 여부"
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
    questions = relationship("Question", back_populates="assignment", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="assignment", cascade="all, delete-orphan")
    parent_assignment = relationship("Assignment", remote_side=[assignment_id], backref="clinic_assignments")

    __table_args__ = (
        Index("idx_academy_due", "academy_id", "due_date"),
        Index("idx_type", "assignment_type"),
    )

    def __repr__(self):
        return f"<Assignment(assignment_id={self.assignment_id}, title='{self.title}')>"


class Question(Base):
    """
    문제 테이블

    컬럼 설명:
    - question_id: 문제 고유 ID (PK)
    - assignment_id: 과제 ID
    - question_number: 문제 번호
    - question_text: 문제 내용
    - question_type: 문제 유형 (객관식, 단답형, 서술형)
    - options: 객관식 보기 (JSON)
    - correct_answer: 정답
    - points: 배점
    - category: 문제 유형 (클리닉 생성용)
    - difficulty: 난이도
    """
    __tablename__ = "Questions"

    question_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="문제 고유 ID"
    )

    assignment_id = Column(
        Integer,
        ForeignKey("Assignments.assignment_id", ondelete="CASCADE"),
        nullable=False,
        comment="과제 ID"
    )

    question_number = Column(
        Integer,
        nullable=False,
        comment="문제 번호"
    )

    question_text = Column(
        Text,
        nullable=False,
        comment="문제 내용"
    )

    question_type = Column(
        Enum(QuestionType),
        default=QuestionType.CHOICE,
        nullable=False,
        comment="문제 유형"
    )

    options = Column(
        JSON,
        nullable=True,
        comment="객관식 보기"
    )

    correct_answer = Column(
        String(500),
        nullable=False,
        comment="정답"
    )

    points = Column(
        Integer,
        default=1,
        nullable=False,
        comment="배점"
    )

    category = Column(
        String(100),
        nullable=True,
        comment="문제 유형 (클리닉 생성용)"
    )

    difficulty = Column(
        Enum(Difficulty),
        default=Difficulty.MEDIUM,
        nullable=False,
        comment="난이도"
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )

    # Relationships
    assignment = relationship("Assignment", back_populates="questions")
    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")

    __table_args__ = (
        Index("uk_assignment_number", "assignment_id", "question_number", unique=True),
        Index("idx_category", "category"),
    )

    def __repr__(self):
        return f"<Question(question_id={self.question_id}, number={self.question_number})>"
