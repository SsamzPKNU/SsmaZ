"""
QuestionBank 모델 정의
문제 은행 (클리닉용) 테이블
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    Enum, JSON, ForeignKey, Index
)
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.assignment import QuestionType, Difficulty


class QuestionBank(Base):
    """
    문제 은행 테이블 (클리닉용)

    컬럼 설명:
    - question_bank_id: 문제 고유 ID (PK)
    - academy_id: 학원 ID
    - category: 문제 유형
    - question_text: 문제 내용
    - question_type: 문제 유형 (객관식, 단답형, 서술형)
    - options: 객관식 보기 (JSON)
    - correct_answer: 정답
    - difficulty: 난이도
    - usage_count: 사용 횟수
    """
    __tablename__ = "QuestionBank"

    question_bank_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="문제 고유 ID"
    )

    academy_id = Column(
        Integer,
        ForeignKey("Academies.academy_id", ondelete="CASCADE"),
        nullable=False,
        comment="학원 ID"
    )

    category = Column(
        String(100),
        nullable=False,
        comment="문제 유형"
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

    difficulty = Column(
        Enum(Difficulty),
        default=Difficulty.MEDIUM,
        nullable=False,
        comment="난이도"
    )

    usage_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="사용 횟수"
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )

    __table_args__ = (
        Index("idx_category_difficulty", "academy_id", "category", "difficulty"),
    )

    def __repr__(self):
        return f"<QuestionBank(question_bank_id={self.question_bank_id}, category='{self.category}')>"
