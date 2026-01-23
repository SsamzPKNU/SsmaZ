"""
학생 관리 관련 비즈니스 로직
학생 CRUD 기능 및 User 계정 연동 제공
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from app.models.student import Student, StudentStatus
from app.models.user import User, UserRole
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from app.core.security import hash_password
from typing import List, Optional, Tuple


class StudentService:
    """학생 관리 서비스 클래스"""
    
    @staticmethod
    def get_students(
        db: Session,
        academy_id: int,
        search: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Student], int]:
        """
        학생 목록 조회 (페이지네이션, 검색)
        
        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            search: 검색어 (이름, 전화번호, 학부모 전화번호)
            status: 상태 필터
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
                Student.phone.contains(search),
                Student.parent_phone.contains(search)
            )
            query = query.filter(search_filter)
        
        # 상태 필터
        if status:
            query = query.filter(Student.status == status)
        
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
        
        Args:
            db: 데이터베이스 세션
            student_id: 학생 ID
            academy_id: 학원 ID
            
        Returns:
            Optional[Student]: 학생 정보 또는 None
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
        학생 등록 (User 계정도 함께 생성 가능)
        
        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            student_data: 학생 정보 (username, password 포함 가능)
            
        Returns:
            Student: 생성된 학생 정보
            
        Raises:
            HTTPException: username 중복 시
        """
        user_id = None
        
        # username과 password가 모두 제공된 경우 User 계정 생성
        if student_data.username and student_data.password:
            # username 중복 체크
            existing_user = db.query(User).filter(User.username == student_data.username).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 사용 중인 username입니다"
                )
            
            # User 계정 생성
            hashed_password = hash_password(student_data.password)
            new_user = User(
                username=student_data.username,
                password_hash=hashed_password,
                academy_id=academy_id,
                user_role=UserRole.STUDENT,
                name=student_data.name,
                phone=student_data.phone
            )
            db.add(new_user)
            db.flush()  # user_id 생성
            user_id = new_user.user_id
        
        # Student 객체 생성
        new_student = Student(
            user_id=user_id,
            academy_id=academy_id,
            name=student_data.name,
            school=student_data.school,
            grade=student_data.grade,
            phone=student_data.phone,
            parent_phone=student_data.parent_phone,
            enrollment_date=student_data.enrollment_date,
            status=StudentStatus.ENROLLED
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
        
        Args:
            db: 데이터베이스 세션
            student_id: 학생 ID
            academy_id: 학원 ID
            student_data: 수정할 정보
            
        Returns:
            Student: 수정된 학생 정보
            
        Raises:
            HTTPException: 학생을 찾을 수 없는 경우
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
        
        Args:
            db: 데이터베이스 세션
            student_id: 학생 ID
            academy_id: 학원 ID
            
        Returns:
            bool: 삭제 성공 여부
            
        Raises:
            HTTPException: 학생을 찾을 수 없는 경우
        """
        student = StudentService.get_student_by_id(db, student_id, academy_id)
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="학생을 찾을 수 없습니다"
            )
        
        # 연결된 User 계정도 함께 삭제 (옵션)
        # if student.user_id:
        #     user = db.query(User).filter(User.user_id == student.user_id).first()
        #     if user:
        #         db.delete(user)
        
        db.delete(student)
        db.commit()
        
        return True
    
    @staticmethod
    def to_response(student: Student) -> StudentResponse:
        """
        Student 모델을 StudentResponse로 변환
        
        Args:
            student: Student 모델 객체
            
        Returns:
            StudentResponse: 응답 스키마
        """
        return StudentResponse(
            id=student.student_id,
            name=student.name,
            school=student.school,
            grade=student.grade,
            phone=student.phone,
            parent_phone=student.parent_phone,
            enrollment_date=student.enrollment_date,
            status=student.status.value
        )
