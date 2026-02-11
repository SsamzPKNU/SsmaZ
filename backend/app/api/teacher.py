"""
선생님 관리 관련 API 엔드포인트
ADMIN 전용, camelCase 응답, 반 배정 포함
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.teacher import TeacherCreate, TeacherUpdate, ClassAssign
from app.services.teacher_service import TeacherService
from app.services.class_teacher_service import ClassTeacherService
from app.models.user import User
from app.api.deps import get_admin_user
from typing import Optional
import math


router = APIRouter(
    prefix="/api/admin/teachers",
    tags=["선생님 관리"],
)


@router.get("")
async def get_teachers(
    q: Optional[str] = Query(None, description="검색어 (이름/아이디)"),
    status: Optional[str] = Query(None, description="상태 필터 (active, leave, resigned)"),
    subject: Optional[str] = Query(None, description="과목 필터"),
    sort: str = Query("name", description="정렬 기준 (name, join_date, created_at)"),
    order: str = Query("asc", description="정렬 방향 (asc, desc)"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지 크기"),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """선생님 목록 조회 (검색/필터/정렬/페이지네이션)"""
    academy_id = admin_user.academy_id

    teachers, total_count = TeacherService.get_teachers(
        db=db,
        academy_id=academy_id,
        q=q,
        status_filter=status,
        subject=subject,
        sort=sort,
        order=order,
        page=page,
        limit=limit,
    )

    total_pages = math.ceil(total_count / limit) if total_count > 0 else 1

    return {
        "teachers": [TeacherService.to_response(db, t) for t in teachers],
        "totalCount": total_count,
        "totalPages": total_pages,
        "currentPage": page,
    }


@router.get("/{teacher_id}")
async def get_teacher(
    teacher_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """선생님 상세 조회 (담당반 포함)"""
    teacher = TeacherService.get_teacher_by_id(db, teacher_id, admin_user.academy_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="선생님을 찾을 수 없습니다",
        )
    return TeacherService.to_detail_response(db, teacher)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_teacher(
    data: TeacherCreate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """선생님 등록 (User + Teacher 동시 생성)"""
    new_teacher = TeacherService.create_teacher_with_user(
        db=db,
        academy_id=admin_user.academy_id,
        data=data,
    )
    return {"success": True, "teacherId": new_teacher.teacher_id}


@router.put("/{teacher_id}")
async def update_teacher(
    teacher_id: int,
    data: TeacherUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """선생님 정보 수정"""
    TeacherService.update_teacher(
        db=db,
        teacher_id=teacher_id,
        academy_id=admin_user.academy_id,
        data=data,
    )
    return {"success": True}


@router.delete("/{teacher_id}")
async def delete_teacher(
    teacher_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """선생님 퇴사 처리 (소프트 삭제: status=resigned + 반 해제)"""
    TeacherService.resign_teacher(
        db=db,
        teacher_id=teacher_id,
        academy_id=admin_user.academy_id,
    )
    return {"success": True}


@router.get("/{teacher_id}/classes")
async def get_teacher_classes(
    teacher_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """선생님 담당반 목록 조회"""
    teacher = TeacherService.get_teacher_by_id(db, teacher_id, admin_user.academy_id)
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="선생님을 찾을 수 없습니다",
        )

    classes = TeacherService.get_teacher_classes(db, teacher_id)

    # 배정 레벨 정보 매핑
    from app.models.class_teacher import ClassTeacherAssignment
    assignments = db.query(ClassTeacherAssignment).filter(
        ClassTeacherAssignment.teacher_id == teacher_id
    ).all()
    level_map = {a.class_id: (a.level.value if hasattr(a.level, 'value') else a.level) for a in assignments}

    return {
        "classes": [
            {
                "id": cls.class_id,
                "name": cls.class_name,
                "subject": cls.subject,
                "grade": cls.grade_level,
                "level": level_map.get(cls.class_id),
                "assignedAt": None,
            }
            for cls in classes
        ]
    }


@router.post("/{teacher_id}/classes")
async def assign_classes(
    teacher_id: int,
    data: ClassAssign,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """선생님에게 반 배정 (level: high/mid/low, 기본값 mid)"""
    added = TeacherService.assign_classes(
        db=db,
        teacher_id=teacher_id,
        academy_id=admin_user.academy_id,
        class_ids=data.class_ids,
        level=data.level or "mid",
    )
    return {"success": True, "added": added}


@router.delete("/{teacher_id}/classes/{class_id}")
async def unassign_class(
    teacher_id: int,
    class_id: int,
    level: Optional[str] = Query(None, description="해제할 수준 (high/mid/low, 미지정 시 전체)"),
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """선생님 반 배정 해제 (level 지정 시 해당 수준만 해제)"""
    TeacherService.unassign_class(
        db=db,
        teacher_id=teacher_id,
        class_id=class_id,
        academy_id=admin_user.academy_id,
        level=level,
    )
    return {"success": True}
