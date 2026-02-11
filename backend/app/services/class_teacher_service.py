"""
반-선생님 수준별 배정 헬퍼 서비스
기존 Class.teacher_id 참조를 점진적으로 대체하는 중간 계층
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from app.models.class_teacher import ClassTeacherAssignment, TeacherLevel
from app.models.class_model import Class
from app.models.teacher import Teacher
from typing import List, Optional


class ClassTeacherService:
    """반-선생님 수준별 배정 헬퍼"""

    @staticmethod
    def is_teacher_assigned(db: Session, class_id: int, teacher_id: int) -> bool:
        """
        선생님이 해당 반에 배정되어 있는지 (레벨 무관)
        새 테이블 우선 확인 → fallback: Classes.teacher_id
        """
        exists = db.query(ClassTeacherAssignment).filter(
            and_(
                ClassTeacherAssignment.class_id == class_id,
                ClassTeacherAssignment.teacher_id == teacher_id
            )
        ).first()
        if exists:
            return True

        # fallback: 기존 teacher_id
        cls = db.query(Class).filter(
            and_(
                Class.class_id == class_id,
                Class.teacher_id == teacher_id
            )
        ).first()
        return cls is not None

    @staticmethod
    def get_teacher_class_ids(db: Session, teacher_id: int) -> List[int]:
        """
        선생님이 담당하는 모든 반 ID (새 테이블 + fallback 합집합)
        """
        new_ids = {r.class_id for r in db.query(ClassTeacherAssignment).filter(
            ClassTeacherAssignment.teacher_id == teacher_id
        ).all()}

        legacy_ids = {c.class_id for c in db.query(Class).filter(
            Class.teacher_id == teacher_id
        ).all()}

        return list(new_ids | legacy_ids)

    @staticmethod
    def get_teacher_classes(db: Session, teacher_id: int) -> List[Class]:
        """
        선생님이 담당하는 모든 반 객체 (새 테이블 + fallback)
        """
        class_ids = ClassTeacherService.get_teacher_class_ids(db, teacher_id)
        if not class_ids:
            return []
        return db.query(Class).filter(Class.class_id.in_(class_ids)).all()

    @staticmethod
    def assign_teacher(
        db: Session,
        academy_id: int,
        class_id: int,
        teacher_id: int,
        level: str = "mid"
    ) -> ClassTeacherAssignment:
        """
        선생님을 반에 수준별 배정
        MID 레벨이면 Classes.teacher_id도 동기화
        """
        teacher_level = TeacherLevel(level)

        # 이미 같은 class+level에 배정된 레코드 확인
        existing = db.query(ClassTeacherAssignment).filter(
            and_(
                ClassTeacherAssignment.class_id == class_id,
                ClassTeacherAssignment.level == teacher_level
            )
        ).first()

        if existing:
            if existing.teacher_id == teacher_id:
                return existing
            # 다른 선생님이 배정되어 있으면 교체
            existing.teacher_id = teacher_id
            existing.academy_id = academy_id
        else:
            existing = ClassTeacherAssignment(
                academy_id=academy_id,
                class_id=class_id,
                teacher_id=teacher_id,
                level=teacher_level,
                is_primary=(teacher_level == TeacherLevel.MID)
            )
            db.add(existing)

        # MID 레벨이면 Classes.teacher_id 동기화
        if teacher_level == TeacherLevel.MID:
            cls = db.query(Class).filter(Class.class_id == class_id).first()
            if cls:
                cls.teacher_id = teacher_id

        db.flush()
        return existing

    @staticmethod
    def unassign_teacher(
        db: Session,
        class_id: int,
        teacher_id: int,
        level: Optional[str] = None
    ) -> bool:
        """
        배정 해제. level 지정 시 해당 레벨만, 미지정 시 해당 선생님의 모든 배정 해제
        MID 레벨 해제 시 Classes.teacher_id도 NULL로 동기화
        """
        query = db.query(ClassTeacherAssignment).filter(
            and_(
                ClassTeacherAssignment.class_id == class_id,
                ClassTeacherAssignment.teacher_id == teacher_id
            )
        )
        if level:
            teacher_level = TeacherLevel(level)
            query = query.filter(ClassTeacherAssignment.level == teacher_level)

        assignments = query.all()
        if not assignments:
            return False

        # MID 레벨 해제 시 Classes.teacher_id 동기화
        for a in assignments:
            if a.level == TeacherLevel.MID:
                cls = db.query(Class).filter(Class.class_id == class_id).first()
                if cls and cls.teacher_id == teacher_id:
                    cls.teacher_id = None

        for a in assignments:
            db.delete(a)

        db.flush()
        return True

    @staticmethod
    def unassign_all_for_teacher(db: Session, teacher_id: int):
        """
        선생님 퇴사 시 모든 배정 해제 + Classes.teacher_id 동기화
        """
        assignments = db.query(ClassTeacherAssignment).filter(
            ClassTeacherAssignment.teacher_id == teacher_id
        ).all()

        mid_class_ids = [a.class_id for a in assignments if a.level == TeacherLevel.MID]

        for a in assignments:
            db.delete(a)

        # MID 배정된 반들의 Classes.teacher_id NULL
        if mid_class_ids:
            db.query(Class).filter(Class.class_id.in_(mid_class_ids)).update(
                {Class.teacher_id: None}, synchronize_session='fetch'
            )

        # 레거시 teacher_id도 해제
        db.query(Class).filter(Class.teacher_id == teacher_id).update(
            {Class.teacher_id: None}, synchronize_session='fetch'
        )

        db.flush()

    @staticmethod
    def get_class_teachers(db: Session, class_id: int) -> List[dict]:
        """
        반의 수준별 선생님 목록 반환
        [{"level": "high", "teacherId": 11, "teacherName": "김선생"}, ...]
        """
        assignments = db.query(ClassTeacherAssignment).filter(
            ClassTeacherAssignment.class_id == class_id
        ).all()

        result = []
        for a in assignments:
            teacher = db.query(Teacher).filter(
                Teacher.teacher_id == a.teacher_id
            ).first()
            result.append({
                "level": a.level.value if hasattr(a.level, 'value') else a.level,
                "teacherId": a.teacher_id,
                "teacherName": teacher.name if teacher else None,
            })

        return result

    @staticmethod
    def get_assigned_classes_count(db: Session, teacher_id: int) -> int:
        """선생님이 배정된 반 수 (새 테이블 + fallback 합집합)"""
        return len(ClassTeacherService.get_teacher_class_ids(db, teacher_id))
