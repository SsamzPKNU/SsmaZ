"""
학생 연락처 관련 비즈니스 로직
연락처 CRUD 및 알림 발송용 조회 기능 제공
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from app.models.student_contact import StudentContact
from app.models.student import Student
from app.schemas.student_contact import StudentContactCreate, StudentContactUpdate
from typing import List, Optional, Tuple


class StudentContactService:
    """학생 연락처 관리 서비스 클래스"""

    @staticmethod
    def get_contacts_by_student(
        db: Session,
        student_id: int,
        academy_id: int
    ) -> List[StudentContact]:
        """
        학생의 연락처 목록 조회 (priority 순 정렬)

        Args:
            db: 데이터베이스 세션
            student_id: 학생 ID
            academy_id: 학원 ID (권한 검증용)

        Returns:
            연락처 목록 (priority 오름차순)
        """
        # 학생 존재 및 학원 소속 확인
        student = db.query(Student).filter(
            and_(
                Student.student_id == student_id,
                Student.academy_id == academy_id
            )
        ).first()

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="학생을 찾을 수 없습니다"
            )

        contacts = db.query(StudentContact).filter(
            StudentContact.student_id == student_id
        ).order_by(StudentContact.priority.asc()).all()

        return contacts

    @staticmethod
    def get_active_contacts(
        db: Session,
        student_id: int
    ) -> List[StudentContact]:
        """
        알림 발송용 활성화된 연락처 목록 조회

        Args:
            db: 데이터베이스 세션
            student_id: 학생 ID

        Returns:
            활성화된 연락처 목록 (priority 오름차순)
        """
        contacts = db.query(StudentContact).filter(
            and_(
                StudentContact.student_id == student_id,
                StudentContact.is_active == True
            )
        ).order_by(StudentContact.priority.asc()).all()

        return contacts

    @staticmethod
    def get_contact_by_id(
        db: Session,
        contact_id: int
    ) -> Optional[StudentContact]:
        """
        연락처 ID로 조회

        Args:
            db: 데이터베이스 세션
            contact_id: 연락처 ID

        Returns:
            연락처 객체 또는 None
        """
        return db.query(StudentContact).filter(
            StudentContact.contact_id == contact_id
        ).first()

    @staticmethod
    def create_contact(
        db: Session,
        student_id: int,
        academy_id: int,
        contact_data: StudentContactCreate
    ) -> StudentContact:
        """
        학생 연락처 등록

        Args:
            db: 데이터베이스 세션
            student_id: 학생 ID
            academy_id: 학원 ID (권한 검증용)
            contact_data: 연락처 등록 데이터

        Returns:
            생성된 연락처 객체
        """
        # 학생 존재 및 학원 소속 확인
        student = db.query(Student).filter(
            and_(
                Student.student_id == student_id,
                Student.academy_id == academy_id
            )
        ).first()

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="학생을 찾을 수 없습니다"
            )

        # 연락처 생성
        new_contact = StudentContact(
            student_id=student_id,
            phone=contact_data.phone,
            label=contact_data.label,
            priority=contact_data.priority,
            is_active=contact_data.is_active
        )

        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)

        return new_contact

    @staticmethod
    def update_contact(
        db: Session,
        contact_id: int,
        academy_id: int,
        contact_data: StudentContactUpdate
    ) -> StudentContact:
        """
        연락처 정보 수정

        Args:
            db: 데이터베이스 세션
            contact_id: 연락처 ID
            academy_id: 학원 ID (권한 검증용)
            contact_data: 수정 데이터

        Returns:
            수정된 연락처 객체
        """
        contact = StudentContactService.get_contact_by_id(db, contact_id)

        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="연락처를 찾을 수 없습니다"
            )

        # 학원 소속 확인 (연락처의 학생이 해당 학원 소속인지)
        student = db.query(Student).filter(
            and_(
                Student.student_id == contact.student_id,
                Student.academy_id == academy_id
            )
        ).first()

        if not student:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="해당 연락처에 대한 권한이 없습니다"
            )

        # 변경된 필드만 업데이트
        update_data = contact_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(contact, field, value)

        db.commit()
        db.refresh(contact)

        return contact

    @staticmethod
    def delete_contact(
        db: Session,
        contact_id: int,
        academy_id: int
    ) -> bool:
        """
        연락처 삭제

        Args:
            db: 데이터베이스 세션
            contact_id: 연락처 ID
            academy_id: 학원 ID (권한 검증용)

        Returns:
            삭제 성공 여부
        """
        contact = StudentContactService.get_contact_by_id(db, contact_id)

        if not contact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="연락처를 찾을 수 없습니다"
            )

        # 학원 소속 확인
        student = db.query(Student).filter(
            and_(
                Student.student_id == contact.student_id,
                Student.academy_id == academy_id
            )
        ).first()

        if not student:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="해당 연락처에 대한 권한이 없습니다"
            )

        db.delete(contact)
        db.commit()

        return True
