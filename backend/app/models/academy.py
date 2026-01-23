"""
Academy 모델 정의
학원 정보를 저장하는 테이블
"""

from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base


class Academy(Base):
    """
    학원 정보 테이블

    컬럼 설명:
    - academy_id: 학원 고유 ID (PK)
    - academy_name: 학원 이름
    - business_number: 사업자 등록번호
    - owner_name: 대표자명
    - plan_type: 요금제 타입 (FREE, BASIC 등)
    - created_at: 생성 시간
    """
    __tablename__ = "Academies"

    academy_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="학원 고유 ID"
    )

    academy_name = Column(
        String(100),
        nullable=False,
        comment="학원 이름"
    )

    business_number = Column(
        String(20),
        nullable=True,
        comment="사업자 등록번호"
    )

    owner_name = Column(
        String(50),
        nullable=True,
        comment="대표자명"
    )

    plan_type = Column(
        String(20),
        nullable=True,
        default="FREE",
        comment="요금제 타입"
    )

    created_at = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="생성 시간"
    )

    def __repr__(self):
        return f"<Academy(academy_id={self.academy_id}, academy_name='{self.academy_name}')>"
