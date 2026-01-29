"""
Support 모델 정의
문의, FAQ, 공지사항 정보를 저장하는 테이블
"""

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class InquiryStatus(str, enum.Enum):
    """문의 상태"""
    PENDING = "PENDING"      # 대기
    ANSWERED = "ANSWERED"    # 답변 완료
    CLOSED = "CLOSED"        # 종료


class NoticeTarget(str, enum.Enum):
    """공지사항 대상"""
    ALL = "ALL"              # 전체
    STUDENT = "STUDENT"      # 학생
    PARENT = "PARENT"        # 학부모
    TEACHER = "TEACHER"      # 선생님


class Inquiry(Base):
    """
    문의 테이블

    컬럼 설명:
    - inquiry_id: 문의 고유 ID (PK)
    - academy_id: 학원 ID
    - user_id: 작성자 ID (FK)
    - title: 문의 제목
    - content: 문의 내용
    - status: 상태 (PENDING, ANSWERED, CLOSED)
    - answer: 답변 내용
    - answered_by: 답변자 ID (FK)
    - answered_at: 답변 시간
    - created_at: 생성 시간
    """
    __tablename__ = "Inquiries"

    inquiry_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="문의 고유 ID"
    )

    academy_id = Column(
        Integer,
        nullable=False,
        comment="학원 ID"
    )

    user_id = Column(
        Integer,
        ForeignKey("Users.user_id", ondelete="CASCADE"),
        nullable=False,
        comment="작성자 ID"
    )

    title = Column(
        String(200),
        nullable=False,
        comment="문의 제목"
    )

    content = Column(
        Text,
        nullable=False,
        comment="문의 내용"
    )

    status = Column(
        Enum(InquiryStatus, values_callable=lambda x: [e.value for e in x]),
        default=InquiryStatus.PENDING,
        nullable=False,
        comment="상태 (PENDING, ANSWERED, CLOSED)"
    )

    answer = Column(
        Text,
        nullable=True,
        comment="답변 내용"
    )

    answered_by = Column(
        Integer,
        ForeignKey("Users.user_id", ondelete="SET NULL"),
        nullable=True,
        comment="답변자 ID"
    )

    answered_at = Column(
        TIMESTAMP,
        nullable=True,
        comment="답변 시간"
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )

    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="inquiries")
    answerer = relationship("User", foreign_keys=[answered_by])

    def __repr__(self):
        return f"<Inquiry(inquiry_id={self.inquiry_id}, title='{self.title}')>"


class FAQ(Base):
    """
    FAQ 테이블

    컬럼 설명:
    - faq_id: FAQ 고유 ID (PK)
    - academy_id: 학원 ID
    - question: 질문
    - answer: 답변
    - category: 카테고리
    - display_order: 표시 순서
    - is_active: 활성화 여부
    - created_at: 생성 시간
    - updated_at: 수정 시간
    """
    __tablename__ = "FAQs"

    faq_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="FAQ 고유 ID"
    )

    academy_id = Column(
        Integer,
        nullable=False,
        comment="학원 ID"
    )

    question = Column(
        String(500),
        nullable=False,
        comment="질문"
    )

    answer = Column(
        Text,
        nullable=False,
        comment="답변"
    )

    category = Column(
        String(50),
        default="일반",
        nullable=False,
        comment="카테고리"
    )

    display_order = Column(
        Integer,
        default=0,
        nullable=False,
        comment="표시 순서"
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="활성화 여부"
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )

    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="수정 시간"
    )

    def __repr__(self):
        return f"<FAQ(faq_id={self.faq_id}, question='{self.question[:30]}...')>"


class Notice(Base):
    """
    공지사항 테이블

    컬럼 설명:
    - notice_id: 공지사항 고유 ID (PK)
    - academy_id: 학원 ID
    - title: 제목
    - content: 내용
    - is_pinned: 상단 고정 여부
    - target: 대상 (ALL, STUDENT, PARENT, TEACHER)
    - view_count: 조회수
    - created_by: 작성자 ID (FK)
    - created_at: 생성 시간
    - updated_at: 수정 시간
    """
    __tablename__ = "Notices"

    notice_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="공지사항 고유 ID"
    )

    academy_id = Column(
        Integer,
        nullable=False,
        comment="학원 ID"
    )

    title = Column(
        String(200),
        nullable=False,
        comment="제목"
    )

    content = Column(
        Text,
        nullable=False,
        comment="내용"
    )

    is_pinned = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="상단 고정 여부"
    )

    target = Column(
        Enum(NoticeTarget, values_callable=lambda x: [e.value for e in x]),
        default=NoticeTarget.ALL,
        nullable=False,
        comment="대상 (ALL, STUDENT, PARENT, TEACHER)"
    )

    view_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="조회수"
    )

    created_by = Column(
        Integer,
        ForeignKey("Users.user_id", ondelete="SET NULL"),
        nullable=True,
        comment="작성자 ID"
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )

    updated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="수정 시간"
    )

    # Relationships
    author = relationship("User", backref="notices")

    def __repr__(self):
        return f"<Notice(notice_id={self.notice_id}, title='{self.title}')>"
