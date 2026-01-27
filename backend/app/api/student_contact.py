"""
학생 연락처 관리 API 엔드포인트
학생별 알림 수신 연락처 CRUD 기능 제공
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.schemas.student_contact import (
    StudentContactCreate,
    StudentContactUpdate,
    StudentContactResponse,
    StudentContactListResponse
)
from app.services.student_contact_service import StudentContactService

router = APIRouter(
    prefix="/students",
    tags=["StudentContacts"]
)


@router.post(
    "/{student_id}/contacts",
    response_model=StudentContactResponse,
    status_code=status.HTTP_201_CREATED,
    summary="학생 연락처 추가"
)
async def create_contact(
    student_id: int,
    contact_data: StudentContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    학생 연락처 추가

    - **student_id**: 학생 ID
    - **phone**: 전화번호
    - **label**: 관계 라벨 (엄마, 아빠, 할머니 등)
    - **priority**: 알림 발송 우선순위 (1이 가장 먼저)
    - **is_active**: 알림 수신 여부
    """
    contact = StudentContactService.create_contact(
        db=db,
        student_id=student_id,
        academy_id=current_user.academy_id,
        contact_data=contact_data
    )
    return contact


@router.get(
    "/{student_id}/contacts",
    response_model=StudentContactListResponse,
    summary="학생 연락처 목록 조회"
)
async def get_contacts(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    학생의 연락처 목록 조회 (priority 순 정렬)

    - **student_id**: 학생 ID
    """
    contacts = StudentContactService.get_contacts_by_student(
        db=db,
        student_id=student_id,
        academy_id=current_user.academy_id
    )
    return StudentContactListResponse(
        contacts=contacts,
        total=len(contacts)
    )


@router.put(
    "/contacts/{contact_id}",
    response_model=StudentContactResponse,
    summary="연락처 수정"
)
async def update_contact(
    contact_id: int,
    contact_data: StudentContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    연락처 정보 수정

    - **contact_id**: 연락처 ID
    - 수정 가능 필드: phone, label, priority, is_active
    """
    contact = StudentContactService.update_contact(
        db=db,
        contact_id=contact_id,
        academy_id=current_user.academy_id,
        contact_data=contact_data
    )
    return contact


@router.delete(
    "/contacts/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="연락처 삭제"
)
async def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    연락처 삭제

    - **contact_id**: 연락처 ID
    """
    StudentContactService.delete_contact(
        db=db,
        contact_id=contact_id,
        academy_id=current_user.academy_id
    )
    return None
