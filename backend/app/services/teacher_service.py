"""
선생님 관리 관련 비즈니스 로직
검색/필터/정렬/페이지네이션, User+Teacher 동시 생성, 소프트 삭제, 반 배정
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, asc, desc
from fastapi import HTTPException, status
from datetime import date, datetime
from app.models.teacher import Teacher, TeacherStatus
from app.models.class_model import Class
from app.models.user import User, UserRole
from app.schemas.teacher import TeacherCreate, TeacherUpdate
from app.core.security import hash_password
from typing import Optional, Tuple, List
import math


class TeacherService:
    """선생님 관리 서비스 클래스"""

    # 정렬 매핑
    SORT_MAP = {
        "name": Teacher.name,
        "join_date": Teacher.join_date,
        "created_at": Teacher.created_at,
    }

    @staticmethod
    def get_teachers(
        db: Session,
        academy_id: int,
        q: Optional[str] = None,
        status_filter: Optional[str] = None,
        subject: Optional[str] = None,
        sort: str = "name",
        order: str = "asc",
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Teacher], int]:
        query = db.query(Teacher).filter(Teacher.academy_id == academy_id)

        # 검색 (이름 또는 username)
        if q:
            query = query.outerjoin(User, Teacher.user_id == User.user_id).filter(
                or_(
                    Teacher.name.like(f"%{q}%"),
                    User.username.like(f"%{q}%"),
                )
            )

        # 상태 필터
        if status_filter:
            query = query.filter(Teacher.status == status_filter)

        # 과목 필터
        if subject:
            query = query.filter(Teacher.subject == subject)

        # 전체 수
        total_count = query.count()

        # 정렬
        sort_column = TeacherService.SORT_MAP.get(sort, Teacher.name)
        if order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))

        # 페이지네이션
        skip = (page - 1) * limit
        teachers = query.offset(skip).limit(limit).all()

        return teachers, total_count

    @staticmethod
    def get_teacher_by_id(db: Session, teacher_id: int, academy_id: int) -> Optional[Teacher]:
        return db.query(Teacher).filter(
            and_(
                Teacher.teacher_id == teacher_id,
                Teacher.academy_id == academy_id,
            )
        ).first()

    @staticmethod
    def create_teacher_with_user(db: Session, academy_id: int, data: TeacherCreate) -> Teacher:
        # username 중복 체크
        existing = db.query(User).filter(User.username == data.username).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 아이디입니다",
            )

        try:
            # User 생성
            new_user = User(
                academy_id=academy_id,
                username=data.username,
                password_hash=hash_password(data.password),
                user_role=UserRole.TEACHER,
                name=data.name,
                phone=data.phone,
            )
            db.add(new_user)
            db.flush()

            # join_date 파싱
            join_date_val = None
            if data.joinDate:
                join_date_val = date.fromisoformat(data.joinDate)

            # Teacher 생성
            new_teacher = Teacher(
                user_id=new_user.user_id,
                academy_id=academy_id,
                name=data.name,
                subject=data.subject,
                phone=data.phone,
                email=data.email,
                join_date=join_date_val,
                memo=data.memo,
                status=TeacherStatus.ACTIVE,
            )
            db.add(new_teacher)
            db.commit()
            db.refresh(new_teacher)
            return new_teacher
        except HTTPException:
            raise
        except Exception:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="강사 등록 중 오류가 발생했습니다",
            )

    @staticmethod
    def update_teacher(
        db: Session,
        teacher_id: int,
        academy_id: int,
        data: TeacherUpdate,
    ) -> Teacher:
        teacher = TeacherService.get_teacher_by_id(db, teacher_id, academy_id)
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="선생님을 찾을 수 없습니다",
            )

        update_data = data.model_dump(exclude_unset=True)

        # camelCase → snake_case 매핑
        if "joinDate" in update_data:
            val = update_data.pop("joinDate")
            if val:
                teacher.join_date = date.fromisoformat(val)
            else:
                teacher.join_date = None

        if "status" in update_data:
            teacher.status = update_data.pop("status")

        # 나머지 필드 직접 설정
        for field in ("name", "subject", "phone", "email", "memo"):
            if field in update_data:
                setattr(teacher, field, update_data[field])

        # User 동기화
        if teacher.user_id:
            user = db.query(User).filter(User.user_id == teacher.user_id).first()
            if user:
                if "name" in data.model_dump(exclude_unset=True):
                    user.name = data.name
                if "phone" in data.model_dump(exclude_unset=True):
                    user.phone = data.phone

        db.commit()
        db.refresh(teacher)
        return teacher

    @staticmethod
    def resign_teacher(db: Session, teacher_id: int, academy_id: int) -> bool:
        teacher = TeacherService.get_teacher_by_id(db, teacher_id, academy_id)
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="선생님을 찾을 수 없습니다",
            )

        teacher.status = TeacherStatus.RESIGNED

        # 담당 반 해제
        db.query(Class).filter(Class.teacher_id == teacher_id).update(
            {Class.teacher_id: None}
        )

        db.commit()
        return True

    @staticmethod
    def get_teacher_classes(db: Session, teacher_id: int) -> List[Class]:
        return db.query(Class).filter(Class.teacher_id == teacher_id).all()

    @staticmethod
    def assign_classes(
        db: Session, teacher_id: int, academy_id: int, class_ids: List[int]
    ) -> int:
        teacher = TeacherService.get_teacher_by_id(db, teacher_id, academy_id)
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="선생님을 찾을 수 없습니다",
            )

        added = 0
        for class_id in class_ids:
            cls = db.query(Class).filter(
                and_(Class.class_id == class_id, Class.academy_id == academy_id)
            ).first()
            if not cls:
                continue
            if cls.teacher_id == teacher_id:
                continue
            cls.teacher_id = teacher_id
            added += 1

        db.commit()
        return added

    @staticmethod
    def unassign_class(
        db: Session, teacher_id: int, class_id: int, academy_id: int
    ) -> bool:
        cls = db.query(Class).filter(
            and_(
                Class.class_id == class_id,
                Class.teacher_id == teacher_id,
                Class.academy_id == academy_id,
            )
        ).first()

        if not cls:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 반 배정을 찾을 수 없습니다",
            )

        cls.teacher_id = None
        db.commit()
        return True

    @staticmethod
    def get_assigned_classes_count(db: Session, teacher_id: int) -> int:
        return db.query(Class).filter(Class.teacher_id == teacher_id).count()

    @staticmethod
    def to_response(db: Session, teacher: Teacher) -> dict:
        """Teacher → camelCase dict 변환"""
        return {
            "id": teacher.teacher_id,
            "userId": teacher.user_id,
            "username": teacher.user.username if teacher.user else None,
            "name": teacher.name,
            "subject": teacher.subject,
            "specialization": None,
            "phone": teacher.phone,
            "email": teacher.email,
            "status": teacher.status.value if hasattr(teacher.status, "value") else teacher.status,
            "hireDate": teacher.join_date.isoformat() if teacher.join_date else None,
            "classCount": TeacherService.get_assigned_classes_count(db, teacher.teacher_id),
            "memo": getattr(teacher, "memo", None),
            "createdAt": teacher.created_at.isoformat() if teacher.created_at else None,
            "updatedAt": teacher.updated_at.isoformat() if getattr(teacher, "updated_at", None) else None,
        }

    @staticmethod
    def to_detail_response(db: Session, teacher: Teacher) -> dict:
        """Teacher → camelCase dict (classes 포함) 변환"""
        base = TeacherService.to_response(db, teacher)
        classes = db.query(Class).filter(Class.teacher_id == teacher.teacher_id).all()
        base["classes"] = [
            {
                "id": cls.class_id,
                "name": cls.class_name,
                "subject": cls.subject,
                "grade": cls.grade_level,
                "assignedAt": None,
            }
            for cls in classes
        ]
        return base
