"""
선생님 메시지 센터 API
템플릿 관리, 메시지 발송, 발송 내역, 연락처 조회 기능 제공
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.api.auth import get_current_user
from app.services.teacher_app_service import TeacherAppService
from app.services.teacher_message_service import TeacherMessageService
from app.schemas.teacher_message import (
    TemplateCreateRequest, TemplateUpdateRequest, TemplateResponse, TemplateListResponse,
    MessageSendRequest, MessageSendResponse, MessageHistoryResponse,
    ContactListResponse
)


router = APIRouter(
    prefix="/api/teacher/messages",
    tags=["선생님 앱 - 메시지"]
)


# ========== 템플릿 API ==========

@router.get("/templates", response_model=TemplateListResponse)
async def get_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    템플릿 목록 조회

    내 템플릿 + 학원 공용 템플릿을 조회합니다.
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    items = TeacherMessageService.get_templates(
        db=db,
        teacher_id=teacher_id,
        academy_id=current_user.academy_id
    )

    return TemplateListResponse(items=items, total=len(items))


@router.post("/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    data: TemplateCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    템플릿 생성

    새 메시지 템플릿을 생성합니다.
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    return TeacherMessageService.create_template(
        db=db,
        teacher_id=teacher_id,
        academy_id=current_user.academy_id,
        data=data
    )


@router.put("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    data: TemplateUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    템플릿 수정

    본인이 생성한 템플릿만 수정할 수 있습니다.
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    return TeacherMessageService.update_template(
        db=db,
        template_id=template_id,
        teacher_id=teacher_id,
        academy_id=current_user.academy_id,
        data=data
    )


@router.delete("/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    템플릿 삭제

    본인이 생성한 템플릿만 삭제할 수 있습니다.
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    TeacherMessageService.delete_template(
        db=db,
        template_id=template_id,
        teacher_id=teacher_id,
        academy_id=current_user.academy_id
    )


# ========== 메시지 발송 API ==========

@router.post("/send", response_model=MessageSendResponse)
async def send_message(
    data: MessageSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    메시지 발송

    학생 또는 학부모에게 메시지를 발송합니다.

    Request Body:
    - target_type: 대상 유형 (parents, students, class)
    - target_ids: 대상 ID 목록 (학생 ID 또는 반 ID)
    - title: 메시지 제목
    - content: 메시지 내용
    - template_id: 사용한 템플릿 ID (선택)
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    return TeacherMessageService.send_message(
        db=db,
        teacher_id=teacher_id,
        academy_id=current_user.academy_id,
        data=data
    )


@router.get("/history", response_model=MessageHistoryResponse)
async def get_message_history(
    page: int = Query(1, ge=1, description="페이지 번호"),
    page_size: int = Query(20, ge=1, le=100, description="페이지 크기"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    발송 내역 조회

    학원의 메시지 발송 내역을 조회합니다.
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    items, total = TeacherMessageService.get_message_history(
        db=db,
        teacher_id=teacher_id,
        academy_id=current_user.academy_id,
        page=page,
        page_size=page_size
    )

    return MessageHistoryResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


# ========== 연락처 API ==========

@router.get("/contacts", response_model=ContactListResponse)
async def get_contacts(
    class_id: Optional[int] = Query(None, description="반 ID (필터)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    연락처 목록 조회

    담당 반 학생들의 연락처를 조회합니다.
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    items = TeacherMessageService.get_contacts(
        db=db,
        teacher_id=teacher_id,
        academy_id=current_user.academy_id,
        class_id=class_id
    )

    return ContactListResponse(items=items, total=len(items))
