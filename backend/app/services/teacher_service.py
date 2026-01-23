"""
선생님 관리 관련 비즈니스 로직
선생님 CRUD 기능 제공
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from app.models.teacher import Teacher, TeacherStatus
from app.models.class_model import Class
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherResponse
from typing import List, Optional


class TeacherService:
    """선생님 관리 서비스 클래스"""
    
    @staticmethod
    def get_teachers(
        db: Session, 
        academy_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Teacher]:
        """
        선생님 목록 조회
        
        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            status: 재직 상태 필터 (optional)
            skip: 페이지네이션 오프셋
            limit: 페이지네이션 제한
            
        Returns:
            List[Teacher]: 선생님 목록
        """
        query = db.query(Teacher).filter(Teacher.academy_id == academy_id)
        
        # 상태 필터링
        if status:
            query = query.filter(Teacher.status == status)
        
        # 최신순 정렬
        query = query.order_by(Teacher.created_at.desc())
        
        # 페이지네이션
        teachers = query.offset(skip).limit(limit).all()
        
        return teachers
    
    @staticmethod
    def get_teachers_count(db: Session, academy_id: int, status: Optional[str] = None) -> int:
        """
        선생님 총 개수 조회
        
        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            status: 재직 상태 필터 (optional)
            
        Returns:
            int: 선생님 총 개수
        """
        query = db.query(Teacher).filter(Teacher.academy_id == academy_id)
        
        if status:
            query = query.filter(Teacher.status == status)
        
        return query.count()
    
    @staticmethod
    def get_teacher_by_id(db: Session, teacher_id: int, academy_id: int) -> Optional[Teacher]:
        """
        선생님 정보 조회 (ID로)
        
        Args:
            db: 데이터베이스 세션
            teacher_id: 선생님 ID
            academy_id: 학원 ID
            
        Returns:
            Optional[Teacher]: 선생님 정보 또는 None
        """
        return db.query(Teacher).filter(
            and_(
                Teacher.teacher_id == teacher_id,
                Teacher.academy_id == academy_id
            )
        ).first()
    
    @staticmethod
    def create_teacher(db: Session, academy_id: int, teacher_data: TeacherCreate) -> Teacher:
        """
        선생님 등록
        
        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            teacher_data: 선생님 정보
            
        Returns:
            Teacher: 생성된 선생님 정보
        """
        # Teacher 객체 생성
        new_teacher = Teacher(
            academy_id=academy_id,
            name=teacher_data.name,
            subject=teacher_data.subject,
            phone=teacher_data.phone,
            email=teacher_data.email,
            join_date=teacher_data.join_date,
            status=TeacherStatus.ACTIVE  # 기본값: 재직
        )
        
        # 데이터베이스에 저장
        db.add(new_teacher)
        db.commit()
        db.refresh(new_teacher)
        
        return new_teacher
    
    @staticmethod
    def update_teacher(
        db: Session, 
        teacher_id: int, 
        academy_id: int, 
        teacher_data: TeacherUpdate
    ) -> Teacher:
        """
        선생님 정보 수정
        
        Args:
            db: 데이터베이스 세션
            teacher_id: 선생님 ID
            academy_id: 학원 ID
            teacher_data: 수정할 정보
            
        Returns:
            Teacher: 수정된 선생님 정보
            
        Raises:
            HTTPException: 선생님을 찾을 수 없는 경우
        """
        # 선생님 조회
        teacher = TeacherService.get_teacher_by_id(db, teacher_id, academy_id)
        
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="선생님을 찾을 수 없습니다"
            )
        
        # 변경된 필드만 업데이트
        update_data = teacher_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(teacher, field, value)
        
        db.commit()
        db.refresh(teacher)
        
        return teacher
    
    @staticmethod
    def delete_teacher(db: Session, teacher_id: int, academy_id: int) -> bool:
        """
        선생님 삭제
        
        Args:
            db: 데이터베이스 세션
            teacher_id: 선생님 ID
            academy_id: 학원 ID
            
        Returns:
            bool: 삭제 성공 여부
            
        Raises:
            HTTPException: 선생님을 찾을 수 없는 경우
        """
        # 선생님 조회
        teacher = TeacherService.get_teacher_by_id(db, teacher_id, academy_id)
        
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="선생님을 찾을 수 없습니다"
            )
        
        # 삭제
        db.delete(teacher)
        db.commit()
        
        return True
    
    @staticmethod
    def get_assigned_classes_count(db: Session, teacher_id: int) -> int:
        """
        선생님의 담당 반 수 조회
        
        Args:
            db: 데이터베이스 세션
            teacher_id: 선생님 ID
            
        Returns:
            int: 담당 반 수
        """
        # Class 테이블에서 실제 담당 반 수 조회
        return db.query(Class).filter(Class.teacher_id == teacher_id).count()
    
    @staticmethod
    def to_response(db: Session, teacher: Teacher) -> TeacherResponse:
        """
        Teacher 모델을 TeacherResponse로 변환
        
        Args:
            db: 데이터베이스 세션
            teacher: Teacher 모델 객체
            
        Returns:
            TeacherResponse: 응답 스키마
        """
        # 담당 반 수 조회
        assigned_classes = TeacherService.get_assigned_classes_count(db, teacher.teacher_id)
        
        return TeacherResponse(
            id=teacher.teacher_id,
            name=teacher.name,
            subject=teacher.subject,
            phone=teacher.phone,
            email=teacher.email,
            join_date=teacher.join_date,
            status=teacher.status.value,
            assigned_classes=assigned_classes
        )
