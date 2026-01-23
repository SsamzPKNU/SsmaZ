"""
학생 관리 관련 비즈니스 로직
학생 CRUD 기능 제공
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from app.models.student import Student, StudentStatus
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from typing import List, Optional, Tuple


class StudentService:
    """학생 관리 서비스 클래스"""

    @staticmethod
    def get_students(
        db: Session,
        academy_id: int,
        search: Optional[str] = None,
        status_filter: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Student], int]:
        """
        학생 목록 조회 (페이지네이션, 검색)

        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            search: 검색어 (이름, 학부모 전화번호)
            status_filter: 상태 필터
            page: 페이지 번호 (1부터 시작)
            limit: 페이지당 항목 수

        Returns:
            Tuple[List[Student], int]: (학생 목록, 전체 개수)
        """
        query = db.query(Student).filter(Student.academy_id == academy_id)

        # 검색 필터
        if search:
            search_filter = or_(
                Student.name.contains(search),
                Student.parent_phone.contains(search)
            )
            query = query.filter(search_filter)

        # 상태 필터
        if status_filter:
            query = query.filter(Student.status == status_filter)

        # 전체 개수
        total = query.count()

        # 페이지네이션
        offset = (page - 1) * limit
        students = query.order_by(Student.regdate.desc()).offset(offset).limit(limit).all()

        return students, total

    @staticmethod
    def get_student_by_id(db: Session, student_id: int, academy_id: int) -> Optional[Student]:
        """
        학생 정보 조회 (ID로)
        """
        return db.query(Student).filter(
            and_(
                Student.student_id == student_id,
                Student.academy_id == academy_id
            )
        ).first()

    @staticmethod
    def create_student(
        db: Session,
        academy_id: int,
        student_data: StudentCreate
    ) -> Student:
        """
        학생 등록
        """
        # Student 객체 생성
        new_student = Student(
            academy_id=academy_id,
            class_id=student_data.class_id,
            name=student_data.name,
            parent_phone=student_data.parent_phone,
            status=student_data.status or StudentStatus.ENROLLED
        )

        db.add(new_student)
        db.commit()
        db.refresh(new_student)

        return new_student

    @staticmethod
    def update_student(
        db: Session,
        student_id: int,
        academy_id: int,
        student_data: StudentUpdate
    ) -> Student:
        """
        학생 정보 수정
        """
        student = StudentService.get_student_by_id(db, student_id, academy_id)

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="학생을 찾을 수 없습니다"
            )

        # 변경된 필드만 업데이트
        update_data = student_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(student, field, value)

        db.commit()
        db.refresh(student)

        return student

    @staticmethod
    def delete_student(db: Session, student_id: int, academy_id: int) -> bool:
        """
        학생 삭제
        """
        student = StudentService.get_student_by_id(db, student_id, academy_id)

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="학생을 찾을 수 없습니다"
            )

        db.delete(student)
        db.commit()

        return True

    @staticmethod
    def to_response(student: Student) -> StudentResponse:
        """
        Student 모델을 StudentResponse로 변환
        """
        return StudentResponse(
            student_id=student.student_id,
            academy_id=student.academy_id,
            class_id=student.class_id,
            name=student.name,
            parent_phone=student.parent_phone,
            status=student.status.value if student.status else None,
            regdate=student.regdate
        )
