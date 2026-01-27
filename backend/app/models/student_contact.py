"""
StudentContact 모델 정의
학생별 알림 수신 연락처를 저장하는 테이블 (복수 등록 가능)
"""

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class StudentContact(Base):
    """
    학생 연락처 테이블

    학생 한 명당 여러 연락처를 등록할 수 있으며,
    출결 알림 발송 시 priority 순서대로 발송됩니다.

    컬럼 설명:
    - contact_id: 연락처 고유 ID (PK)
    - student_id: 학생 ID (FK → Students)
    - phone: 전화번호
    - label: 관계 라벨 (엄마, 아빠, 할머니 등)
    - priority: 알림 발송 우선순위 (1이 가장 먼저)
    - is_active: 알림 수신 여부
    - created_at: 생성 시간
    - updated_at: 수정 시간
    """
    __tablename__ = "StudentContacts"

    contact_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="연락처 고유 ID"
    )

    student_id = Column(
        Integer,
        ForeignKey("Students.student_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="학생 ID"
    )

    phone = Column(
        String(20),
        nullable=False,
        comment="전화번호"
    )

    label = Column(
        String(50),
        nullable=False,
        comment="관계 라벨 (엄마, 아빠, 할머니 등)"
    )

    priority = Column(
        Integer,
        nullable=False,
        default=1,
        comment="알림 발송 우선순위 (1이 가장 먼저)"
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="알림 수신 여부"
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )

    updated_at = Column(
        TIMESTAMP,
        nullable=True,
        onupdate=func.now(),
        comment="수정 시간"
    )

    # Relationships (lazy loading으로 순환 참조 방지)
    student = relationship("app.models.student.Student", backref="student_contacts", lazy="select")

    def __repr__(self):
        return f"<StudentContact(contact_id={self.contact_id}, student_id={self.student_id}, label='{self.label}')>"
