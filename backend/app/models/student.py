"""
Student 모델 정의
학원생 정보를 저장하는 테이블
"""

from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Student(Base):
    """
    학생 정보 테이블
    
    컬럼 설명:
    - student_id: 학생 고유 ID (PK)
    - name: 학생 이름
    - parent_phone: 학부모 전화번호 (알림 발송용)
    - academy_id: 학원 ID
    """
    __tablename__ = "Students"
    
    student_id = Column(
        Integer, 
        primary_key=True, 
        index=True, 
        autoincrement=True,
        comment="학생 고유 ID"
    )
    
    name = Column(
        String(50), 
        nullable=False,
        comment="학생 이름"
    )
    
    parent_phone = Column(
        String(20), 
        nullable=False,
        comment="학부모 전화번호"
    )
    
    academy_id = Column(
        Integer, 
        nullable=False,
        comment="학원 ID"
    )

    def __repr__(self):
        return f"<Student(student_id={self.student_id}, name='{self.name}')>"
