"""
Support API 라우터
문의, FAQ, 공지사항 관련 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.api.auth import get_current_user
from app.api.deps import get_admin_user
from app.models.user import User
from app.schemas.support import (
    InquiryCreate, InquiryAnswer, InquiryResponse, InquiryListResponse,
    FAQCreate, FAQUpdate, FAQResponse, FAQListResponse,
    NoticeCreate, NoticeUpdate, NoticeResponse, NoticeListResponse
)
from app.services.support_service import InquiryService, FAQService, NoticeService

router = APIRouter(
    prefix="/api/admin/support",
    tags=["상담/문의 관리"]
)


# ============================================
# 문의 (Inquiry) API
# ============================================

@router.get("/inquiries", response_model=InquiryListResponse)
async def get_inquiries(
    status: Optional[str] = Query(None, description="상태 필터 (PENDING, ANSWERED, CLOSED)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """문의 목록 조회"""
    inquiries, total = InquiryService.get_inquiries(
        db=db,
        academy_id=current_user.academy_id,
        status=status,
        skip=skip,
        limit=limit
    )
    return InquiryListResponse(
        total=total,
        inquiries=[InquiryService.to_response(i) for i in inquiries]
    )


@router.get("/inquiries/{inquiry_id}", response_model=InquiryResponse)
async def get_inquiry(
    inquiry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """문의 상세 조회"""
    inquiry = InquiryService.get_inquiry(db, inquiry_id, current_user.academy_id)
    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문의를 찾을 수 없습니다"
        )
    return InquiryService.to_response(inquiry)


@router.post("/inquiries", response_model=InquiryResponse, status_code=status.HTTP_201_CREATED)
async def create_inquiry(
    data: InquiryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """문의 등록"""
    inquiry = InquiryService.create_inquiry(
        db=db,
        academy_id=current_user.academy_id,
        user_id=current_user.user_id,
        data=data
    )
    return InquiryService.to_response(inquiry)


@router.post("/inquiries/{inquiry_id}/answer", response_model=InquiryResponse)
async def answer_inquiry(
    inquiry_id: int,
    data: InquiryAnswer,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """문의 답변 (관리자 전용)"""
    inquiry = InquiryService.answer_inquiry(
        db=db,
        inquiry_id=inquiry_id,
        academy_id=admin_user.academy_id,
        answerer_id=admin_user.user_id,
        data=data
    )
    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문의를 찾을 수 없습니다"
        )
    return InquiryService.to_response(inquiry)


@router.post("/inquiries/{inquiry_id}/close", response_model=InquiryResponse)
async def close_inquiry(
    inquiry_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """문의 종료 (관리자 전용)"""
    inquiry = InquiryService.close_inquiry(db, inquiry_id, admin_user.academy_id)
    if not inquiry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="문의를 찾을 수 없습니다"
        )
    return InquiryService.to_response(inquiry)


# ============================================
# FAQ API
# ============================================

@router.get("/faqs", response_model=FAQListResponse)
async def get_faqs(
    category: Optional[str] = Query(None, description="카테고리 필터"),
    is_active: Optional[bool] = Query(True, description="활성화 여부"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """FAQ 목록 조회"""
    faqs, total = FAQService.get_faqs(
        db=db,
        academy_id=current_user.academy_id,
        category=category,
        is_active=is_active,
        skip=skip,
        limit=limit
    )
    return FAQListResponse(
        total=total,
        faqs=[FAQService.to_response(f) for f in faqs]
    )


@router.get("/faqs/{faq_id}", response_model=FAQResponse)
async def get_faq(
    faq_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """FAQ 상세 조회"""
    faq = FAQService.get_faq(db, faq_id, current_user.academy_id)
    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ를 찾을 수 없습니다"
        )
    return FAQService.to_response(faq)


@router.post("/faqs", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
async def create_faq(
    data: FAQCreate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """FAQ 생성 (관리자 전용)"""
    faq = FAQService.create_faq(
        db=db,
        academy_id=admin_user.academy_id,
        data=data
    )
    return FAQService.to_response(faq)


@router.put("/faqs/{faq_id}", response_model=FAQResponse)
async def update_faq(
    faq_id: int,
    data: FAQUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """FAQ 수정 (관리자 전용)"""
    faq = FAQService.update_faq(
        db=db,
        faq_id=faq_id,
        academy_id=admin_user.academy_id,
        data=data
    )
    if not faq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ를 찾을 수 없습니다"
        )
    return FAQService.to_response(faq)


@router.delete("/faqs/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_faq(
    faq_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """FAQ 삭제 (관리자 전용)"""
    if not FAQService.delete_faq(db, faq_id, admin_user.academy_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FAQ를 찾을 수 없습니다"
        )
    return None


# ============================================
# 공지사항 (Notice) API
# ============================================

@router.get("/notices", response_model=NoticeListResponse)
async def get_notices(
    target: Optional[str] = Query(None, description="대상 필터 (ALL, STUDENT, PARENT, TEACHER)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """공지사항 목록 조회"""
    notices, total = NoticeService.get_notices(
        db=db,
        academy_id=current_user.academy_id,
        target=target,
        skip=skip,
        limit=limit
    )
    return NoticeListResponse(
        total=total,
        notices=[NoticeService.to_response(n) for n in notices]
    )


@router.get("/notices/{notice_id}", response_model=NoticeResponse)
async def get_notice(
    notice_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """공지사항 상세 조회 (조회수 증가)"""
    notice = NoticeService.get_notice(
        db=db,
        notice_id=notice_id,
        academy_id=current_user.academy_id,
        increment_view=True
    )
    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="공지사항을 찾을 수 없습니다"
        )
    return NoticeService.to_response(notice)


@router.post("/notices", response_model=NoticeResponse, status_code=status.HTTP_201_CREATED)
async def create_notice(
    data: NoticeCreate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """공지사항 생성 (관리자 전용)"""
    notice = NoticeService.create_notice(
        db=db,
        academy_id=admin_user.academy_id,
        created_by=admin_user.user_id,
        data=data
    )
    return NoticeService.to_response(notice)


@router.put("/notices/{notice_id}", response_model=NoticeResponse)
async def update_notice(
    notice_id: int,
    data: NoticeUpdate,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """공지사항 수정 (관리자 전용)"""
    notice = NoticeService.update_notice(
        db=db,
        notice_id=notice_id,
        academy_id=admin_user.academy_id,
        data=data
    )
    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="공지사항을 찾을 수 없습니다"
        )
    return NoticeService.to_response(notice)


@router.delete("/notices/{notice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notice(
    notice_id: int,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """공지사항 삭제 (관리자 전용)"""
    if not NoticeService.delete_notice(db, notice_id, admin_user.academy_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="공지사항을 찾을 수 없습니다"
        )
    return None
