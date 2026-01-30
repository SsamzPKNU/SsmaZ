"""
선생님 메시지 센터 서비스
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime
import json

from app.models.message_template import MessageTemplate
from app.models.message import Message, MessageTargetGroup, MessageStatus
from app.models.student import Student
from app.models.class_model import Class
from app.schemas.teacher_message import (
    TemplateCreateRequest, TemplateUpdateRequest, TemplateResponse,
    MessageSendRequest, MessageSendResponse, MessageHistoryItem,
    ContactItem, MessageTargetType
)


class TeacherMessageService:
    """선생님 메시지 센터 서비스"""

    # ========== 템플릿 관리 ==========

    @staticmethod
    def get_templates(
        db: Session,
        teacher_id: int,
        academy_id: int
    ) -> List[TemplateResponse]:
        """
        템플릿 목록 조회
        - 내 템플릿 + 학원 공용 템플릿
        """
        templates = db.query(MessageTemplate).filter(
            and_(
                MessageTemplate.academy_id == academy_id,
                or_(
                    MessageTemplate.teacher_id == teacher_id,
                    MessageTemplate.teacher_id.is_(None)
                )
            )
        ).order_by(MessageTemplate.created_at.desc()).all()

        return [
            TemplateResponse(
                template_id=t.template_id,
                name=t.name,
                content=t.content,
                is_shared=t.teacher_id is None,
                created_at=t.created_at,
                updated_at=t.updated_at
            )
            for t in templates
        ]

    @staticmethod
    def create_template(
        db: Session,
        teacher_id: int,
        academy_id: int,
        data: TemplateCreateRequest
    ) -> TemplateResponse:
        """템플릿 생성"""
        template = MessageTemplate(
            academy_id=academy_id,
            teacher_id=teacher_id,
            name=data.name,
            content=data.content
        )
        db.add(template)
        db.commit()
        db.refresh(template)

        return TemplateResponse(
            template_id=template.template_id,
            name=template.name,
            content=template.content,
            is_shared=False,
            created_at=template.created_at,
            updated_at=template.updated_at
        )

    @staticmethod
    def update_template(
        db: Session,
        template_id: int,
        teacher_id: int,
        academy_id: int,
        data: TemplateUpdateRequest
    ) -> TemplateResponse:
        """템플릿 수정 (본인 템플릿만 가능)"""
        template = db.query(MessageTemplate).filter(
            and_(
                MessageTemplate.template_id == template_id,
                MessageTemplate.academy_id == academy_id,
                MessageTemplate.teacher_id == teacher_id  # 본인 템플릿만
            )
        ).first()

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="템플릿을 찾을 수 없거나 수정 권한이 없습니다"
            )

        if data.name is not None:
            template.name = data.name
        if data.content is not None:
            template.content = data.content

        db.commit()
        db.refresh(template)

        return TemplateResponse(
            template_id=template.template_id,
            name=template.name,
            content=template.content,
            is_shared=False,
            created_at=template.created_at,
            updated_at=template.updated_at
        )

    @staticmethod
    def delete_template(
        db: Session,
        template_id: int,
        teacher_id: int,
        academy_id: int
    ) -> bool:
        """템플릿 삭제 (본인 템플릿만 가능)"""
        template = db.query(MessageTemplate).filter(
            and_(
                MessageTemplate.template_id == template_id,
                MessageTemplate.academy_id == academy_id,
                MessageTemplate.teacher_id == teacher_id  # 본인 템플릿만
            )
        ).first()

        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="템플릿을 찾을 수 없거나 삭제 권한이 없습니다"
            )

        db.delete(template)
        db.commit()
        return True

    # ========== 메시지 발송 ==========

    @staticmethod
    def send_message(
        db: Session,
        teacher_id: int,
        academy_id: int,
        data: MessageSendRequest
    ) -> MessageSendResponse:
        """
        메시지 발송
        - 실제 SMS 발송은 외부 연동 필요 (현재는 DB 저장만)
        """
        # 대상 그룹 변환
        if data.target_type == MessageTargetType.PARENTS:
            target_group = MessageTargetGroup.PARENTS
        elif data.target_type == MessageTargetType.STUDENTS:
            target_group = MessageTargetGroup.STUDENTS
        else:
            target_group = MessageTargetGroup.SPECIFIC_CLASSES

        # 발송 대상 수 계산
        if data.target_type in [MessageTargetType.PARENTS, MessageTargetType.STUDENTS]:
            sent_count = len(data.target_ids)
        else:
            # 반별 발송시 해당 반의 학생 수 합산
            sent_count = db.query(Student).filter(
                Student.class_id.in_(data.target_ids)
            ).count()

        # 메시지 저장 (실제 발송은 외부 API 연동 필요)
        message = Message(
            academy_id=academy_id,
            target_group=target_group,
            target_ids=json.dumps(data.target_ids),
            title=data.title,
            content=data.content,
            sent_count=sent_count,
            success_count=sent_count,  # 현재는 모두 성공으로 처리
            fail_count=0,
            status=MessageStatus.COMPLETED,
            sent_at=datetime.now()
        )
        db.add(message)
        db.commit()
        db.refresh(message)

        return MessageSendResponse(
            message_id=message.message_id,
            sent_count=message.sent_count,
            success_count=message.success_count,
            fail_count=message.fail_count,
            status=message.status.value
        )

    @staticmethod
    def get_message_history(
        db: Session,
        teacher_id: int,
        academy_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[MessageHistoryItem], int]:
        """메시지 발송 내역 조회"""
        query = db.query(Message).filter(
            Message.academy_id == academy_id
        ).order_by(Message.created_at.desc())

        total = query.count()
        messages = query.offset((page - 1) * page_size).limit(page_size).all()

        items = [
            MessageHistoryItem(
                message_id=m.message_id,
                title=m.title,
                content=m.content,
                target_type=m.target_group.value,
                sent_count=m.sent_count,
                success_count=m.success_count,
                fail_count=m.fail_count,
                status=m.status.value,
                sent_at=m.sent_at,
                created_at=m.created_at
            )
            for m in messages
        ]

        return items, total

    # ========== 연락처 조회 ==========

    @staticmethod
    def get_contacts(
        db: Session,
        teacher_id: int,
        academy_id: int,
        class_id: Optional[int] = None
    ) -> List[ContactItem]:
        """
        연락처 목록 조회
        - 담당 반 학생들의 연락처
        """
        # 담당 반 목록 조회
        classes = db.query(Class).filter(
            Class.teacher_id == teacher_id
        ).all()

        class_ids = [c.class_id for c in classes]
        class_map = {c.class_id: c.name for c in classes}

        if not class_ids:
            return []

        # 특정 반 필터
        if class_id:
            if class_id not in class_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="담당 반이 아닙니다"
                )
            class_ids = [class_id]

        # 학생 목록 조회
        students = db.query(Student).filter(
            and_(
                Student.academy_id == academy_id,
                Student.class_id.in_(class_ids)
            )
        ).order_by(Student.name).all()

        return [
            ContactItem(
                student_id=s.student_id,
                student_name=s.name,
                grade=s.grade,
                school=s.school,
                class_id=s.class_id,
                class_name=class_map.get(s.class_id),
                phone=s.phone,
                parent_phone=s.parent_phone
            )
            for s in students
        ]
