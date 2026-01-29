"""
Support 관련 비즈니스 로직
문의, FAQ, 공지사항 CRUD 처리
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import List, Optional, Tuple

from app.models.support import Inquiry, FAQ, Notice, InquiryStatus, NoticeTarget
from app.models.user import User
from app.schemas.support import (
    InquiryCreate, InquiryAnswer, InquiryResponse,
    FAQCreate, FAQUpdate, FAQResponse,
    NoticeCreate, NoticeUpdate, NoticeResponse
)


class InquiryService:
    """문의 관련 서비스"""

    @staticmethod
    def get_inquiries(
        db: Session,
        academy_id: int,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Inquiry], int]:
        """문의 목록 조회"""
        query = db.query(Inquiry).filter(Inquiry.academy_id == academy_id)

        if status:
            query = query.filter(Inquiry.status == status)

        total = query.count()
        inquiries = query.order_by(Inquiry.created_at.desc()).offset(skip).limit(limit).all()

        return inquiries, total

    @staticmethod
    def get_inquiry(db: Session, inquiry_id: int, academy_id: int) -> Optional[Inquiry]:
        """문의 상세 조회"""
        return db.query(Inquiry).filter(
            and_(
                Inquiry.inquiry_id == inquiry_id,
                Inquiry.academy_id == academy_id
            )
        ).first()

    @staticmethod
    def create_inquiry(
        db: Session,
        academy_id: int,
        user_id: int,
        data: InquiryCreate
    ) -> Inquiry:
        """문의 생성"""
        inquiry = Inquiry(
            academy_id=academy_id,
            user_id=user_id,
            title=data.title,
            content=data.content,
            status=InquiryStatus.PENDING
        )
        db.add(inquiry)
        db.commit()
        db.refresh(inquiry)
        return inquiry

    @staticmethod
    def answer_inquiry(
        db: Session,
        inquiry_id: int,
        academy_id: int,
        answerer_id: int,
        data: InquiryAnswer
    ) -> Optional[Inquiry]:
        """문의 답변"""
        inquiry = InquiryService.get_inquiry(db, inquiry_id, academy_id)
        if not inquiry:
            return None

        inquiry.answer = data.answer
        inquiry.answered_by = answerer_id
        inquiry.answered_at = datetime.now()
        inquiry.status = InquiryStatus.ANSWERED

        db.commit()
        db.refresh(inquiry)
        return inquiry

    @staticmethod
    def close_inquiry(db: Session, inquiry_id: int, academy_id: int) -> Optional[Inquiry]:
        """문의 종료"""
        inquiry = InquiryService.get_inquiry(db, inquiry_id, academy_id)
        if not inquiry:
            return None

        inquiry.status = InquiryStatus.CLOSED
        db.commit()
        db.refresh(inquiry)
        return inquiry

    @staticmethod
    def to_response(inquiry: Inquiry) -> InquiryResponse:
        """Inquiry 모델을 InquiryResponse로 변환"""
        return InquiryResponse(
            inquiry_id=inquiry.inquiry_id,
            academy_id=inquiry.academy_id,
            user_id=inquiry.user_id,
            user_name=inquiry.user.name if inquiry.user else None,
            title=inquiry.title,
            content=inquiry.content,
            status=inquiry.status.value if inquiry.status else "PENDING",
            answer=inquiry.answer,
            answered_by=inquiry.answered_by,
            answerer_name=inquiry.answerer.name if inquiry.answerer else None,
            answered_at=inquiry.answered_at,
            created_at=inquiry.created_at
        )


class FAQService:
    """FAQ 관련 서비스"""

    @staticmethod
    def get_faqs(
        db: Session,
        academy_id: int,
        category: Optional[str] = None,
        is_active: Optional[bool] = True,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[FAQ], int]:
        """FAQ 목록 조회"""
        query = db.query(FAQ).filter(FAQ.academy_id == academy_id)

        if category:
            query = query.filter(FAQ.category == category)
        if is_active is not None:
            query = query.filter(FAQ.is_active == is_active)

        total = query.count()
        faqs = query.order_by(FAQ.display_order, FAQ.created_at.desc()).offset(skip).limit(limit).all()

        return faqs, total

    @staticmethod
    def get_faq(db: Session, faq_id: int, academy_id: int) -> Optional[FAQ]:
        """FAQ 상세 조회"""
        return db.query(FAQ).filter(
            and_(
                FAQ.faq_id == faq_id,
                FAQ.academy_id == academy_id
            )
        ).first()

    @staticmethod
    def create_faq(db: Session, academy_id: int, data: FAQCreate) -> FAQ:
        """FAQ 생성"""
        faq = FAQ(
            academy_id=academy_id,
            question=data.question,
            answer=data.answer,
            category=data.category,
            display_order=data.display_order,
            is_active=True
        )
        db.add(faq)
        db.commit()
        db.refresh(faq)
        return faq

    @staticmethod
    def update_faq(
        db: Session,
        faq_id: int,
        academy_id: int,
        data: FAQUpdate
    ) -> Optional[FAQ]:
        """FAQ 수정"""
        faq = FAQService.get_faq(db, faq_id, academy_id)
        if not faq:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(faq, field, value)

        db.commit()
        db.refresh(faq)
        return faq

    @staticmethod
    def delete_faq(db: Session, faq_id: int, academy_id: int) -> bool:
        """FAQ 삭제"""
        faq = FAQService.get_faq(db, faq_id, academy_id)
        if not faq:
            return False

        db.delete(faq)
        db.commit()
        return True

    @staticmethod
    def to_response(faq: FAQ) -> FAQResponse:
        """FAQ 모델을 FAQResponse로 변환"""
        return FAQResponse(
            faq_id=faq.faq_id,
            academy_id=faq.academy_id,
            question=faq.question,
            answer=faq.answer,
            category=faq.category,
            display_order=faq.display_order,
            is_active=faq.is_active,
            created_at=faq.created_at,
            updated_at=faq.updated_at
        )


class NoticeService:
    """공지사항 관련 서비스"""

    @staticmethod
    def get_notices(
        db: Session,
        academy_id: int,
        target: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Notice], int]:
        """공지사항 목록 조회"""
        query = db.query(Notice).filter(Notice.academy_id == academy_id)

        if target:
            query = query.filter(Notice.target == target)

        total = query.count()
        # 고정 공지 우선, 그 다음 최신순
        notices = query.order_by(
            Notice.is_pinned.desc(),
            Notice.created_at.desc()
        ).offset(skip).limit(limit).all()

        return notices, total

    @staticmethod
    def get_notice(
        db: Session,
        notice_id: int,
        academy_id: int,
        increment_view: bool = False
    ) -> Optional[Notice]:
        """공지사항 상세 조회"""
        notice = db.query(Notice).filter(
            and_(
                Notice.notice_id == notice_id,
                Notice.academy_id == academy_id
            )
        ).first()

        if notice and increment_view:
            notice.view_count += 1
            db.commit()
            db.refresh(notice)

        return notice

    @staticmethod
    def create_notice(
        db: Session,
        academy_id: int,
        created_by: int,
        data: NoticeCreate
    ) -> Notice:
        """공지사항 생성"""
        notice = Notice(
            academy_id=academy_id,
            title=data.title,
            content=data.content,
            is_pinned=data.is_pinned,
            target=data.target,
            created_by=created_by
        )
        db.add(notice)
        db.commit()
        db.refresh(notice)
        return notice

    @staticmethod
    def update_notice(
        db: Session,
        notice_id: int,
        academy_id: int,
        data: NoticeUpdate
    ) -> Optional[Notice]:
        """공지사항 수정"""
        notice = NoticeService.get_notice(db, notice_id, academy_id)
        if not notice:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(notice, field, value)

        db.commit()
        db.refresh(notice)
        return notice

    @staticmethod
    def delete_notice(db: Session, notice_id: int, academy_id: int) -> bool:
        """공지사항 삭제"""
        notice = NoticeService.get_notice(db, notice_id, academy_id)
        if not notice:
            return False

        db.delete(notice)
        db.commit()
        return True

    @staticmethod
    def to_response(notice: Notice) -> NoticeResponse:
        """Notice 모델을 NoticeResponse로 변환"""
        return NoticeResponse(
            notice_id=notice.notice_id,
            academy_id=notice.academy_id,
            title=notice.title,
            content=notice.content,
            is_pinned=notice.is_pinned,
            target=notice.target.value if notice.target else "ALL",
            view_count=notice.view_count,
            created_by=notice.created_by,
            author_name=notice.author.name if notice.author else None,
            created_at=notice.created_at,
            updated_at=notice.updated_at
        )
