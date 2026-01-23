"""
클래스(반/수업) 관리 관련 비즈니스 로직
클래스 CRUD 기능 제공
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from app.models.class_model import Class
from app.models.teacher import Teacher
from app.models.student import Student
from app.schemas.class_schema import ClassCreate, ClassUpdate, ClassResponse, ClassDetailResponse
from typing import List, Optional


class ClassService:
    """클래스 관리 서비스 클래스"""
    
    @staticmethod
    def get_classes(
        db: Session,
        academy_id: int,
        teacher_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Class]:
        """
        클래스 목록 조회
        
        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            teacher_id: 선생님 ID 필터 (optional)
            skip: 페이지네이션 오프셋
            limit: 페이지네이션 제한
            
        Returns:
            List[Class]: 클래스 목록
        """
        query = db.query(Class).filter(Class.academy_id == academy_id)
        
        # 선생님 필터
        if teacher_id:
            query = query.filter(Class.teacher_id == teacher_id)
        
        # 정렬 및 페이지네이션
        classes = query.order_by(Class.created_at.desc()).offset(skip).limit(limit).all()
        
        return classes
    
    @staticmethod
    def get_class_by_id(db: Session, class_id: int, academy_id: int) -> Optional[Class]:
        """
        클래스 정보 조회 (ID로)
        
        Args:
            db: 데이터베이스 세션
            class_id: 반 ID
            academy_id: 학원 ID
            
        Returns:
            Optional[Class]: 클래스 정보 또는 None
        """
        return db.query(Class).filter(
            and_(
                Class.class_id == class_id,
                Class.academy_id == academy_id
            )
        ).first()
    
    @staticmethod
    def create_class(
        db: Session,
        academy_id: int,
        class_data: ClassCreate
    ) -> Class:
        """
        클래스 생성
        
        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            class_data: 클래스 정보
            
        Returns:
            Class: 생성된 클래스 정보
            
        Raises:
            HTTPException: 선생님을 찾을 수 없는 경우
        """
        # 선생님 존재 여부 확인 (지정된 경우)
        if class_data.teacher_id:
            teacher = db.query(Teacher).filter(
                and_(
                    Teacher.teacher_id == class_data.teacher_id,
                    Teacher.academy_id == academy_id
                )
            ).first()
            
            if not teacher:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="선생님을 찾을 수 없습니다"
                )
        
        # Class 객체 생성
        new_class = Class(
            academy_id=academy_id,
            teacher_id=class_data.teacher_id,
            name=class_data.name,
            schedule=class_data.schedule,
            capacity=class_data.capacity
        )
        
        db.add(new_class)
        db.commit()
        db.refresh(new_class)
        
        return new_class
    
    @staticmethod
    def update_class(
        db: Session,
        class_id: int,
        academy_id: int,
        class_data: ClassUpdate
    ) -> Class:
        """
        클래스 정보 수정
        
        Args:
            db: 데이터베이스 세션
            class_id: 반 ID
            academy_id: 학원 ID
            class_data: 수정할 정보
            
        Returns:
            Class: 수정된 클래스 정보
            
        Raises:
            HTTPException: 클래스를 찾을 수 없는 경우
        """
        class_obj = ClassService.get_class_by_id(db, class_id, academy_id)
        
        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="클래스를 찾을 수 없습니다"
            )
        
        # 선생님 변경 시 존재 여부 확인
        if class_data.teacher_id is not None:
            teacher = db.query(Teacher).filter(
                and_(
                    Teacher.teacher_id == class_data.teacher_id,
                    Teacher.academy_id == academy_id
                )
            ).first()
            
            if not teacher:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="선생님을 찾을 수 없습니다"
                )
        
        # 변경된 필드만 업데이트
        update_data = class_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(class_obj, field, value)
        
        db.commit()
        db.refresh(class_obj)
        
        return class_obj
    
    @staticmethod
    def delete_class(db: Session, class_id: int, academy_id: int) -> bool:
        """
        클래스 삭제
        
        Args:
            db: 데이터베이스 세션
            class_id: 반 ID
            academy_id: 학원 ID
            
        Returns:
            bool: 삭제 성공 여부
            
        Raises:
            HTTPException: 클래스를 찾을 수 없는 경우
        """
        class_obj = ClassService.get_class_by_id(db, class_id, academy_id)
        
        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="클래스를 찾을 수 없습니다"
            )
        
        db.delete(class_obj)
        db.commit()
        
        return True
    
    @staticmethod
    def get_current_students_count(db: Session, class_id: int) -> int:
        """
        클래스의 현재 학생 수 조회
        
        Args:
            db: 데이터베이스 세션
            class_id: 반 ID
            
        Returns:
            int: 현재 학생 수
        """
        return db.query(Student).filter(Student.class_id == class_id).count()
    
    @staticmethod
    def to_response(db: Session, class_obj: Class) -> ClassResponse:
        """
        Class 모델을 ClassResponse로 변환
        
        Args:
            db: 데이터베이스 세션
            class_obj: Class 모델 객체
            
        Returns:
            ClassResponse: 응답 스키마
        """
        # 담당 선생님 이름 조회
        teacher_name = None
        if class_obj.teacher_id:
            teacher = class_obj.teacher
            teacher_name = teacher.name if teacher else None
        
        # 현재 학생 수 조회
        current_students = ClassService.get_current_students_count(db, class_obj.class_id)
        
        return ClassResponse(
            id=class_obj.class_id,
            name=class_obj.name,
            teacher_id=class_obj.teacher_id,
            teacher_name=teacher_name,
            schedule=class_obj.schedule,
            capacity=class_obj.capacity,
            current_students=current_students
        )
    
    @staticmethod
    def to_detail_response(db: Session, class_obj: Class) -> ClassDetailResponse:
        """
        Class 모델을 ClassDetailResponse로 변환 (학생 목록 포함)
        
        Args:
            db: 데이터베이스 세션
            class_obj: Class 모델 객체
            
        Returns:
            ClassDetailResponse: 상세 응답 스키마
        """
        # 기본 정보
        response = ClassService.to_response(db, class_obj)
        
        # 소속 학생 목록
        students = db.query(Student).filter(Student.class_id == class_obj.class_id).all()
        student_list = [{"id": s.student_id, "name": s.name} for s in students]
        
        return ClassDetailResponse(
            **response.model_dump(),
            students=student_list
        )
