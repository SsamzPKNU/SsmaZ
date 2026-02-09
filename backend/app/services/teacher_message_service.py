"""
선생님 메시지 센터 서비스
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func as sa_func
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.models.message_template import MessageTemplate, TemplateCategory
from app.models.message import Message, MessageTargetGroup, MessageStatus, MessageType
from app.models.message_recipient import MessageRecipient, RecipientStatus
from app.models.student import Student
from app.models.student_contact import StudentContact
from app.models.class_model import Class
from app.schemas.teacher_message import (
    TemplateCreateRequest, TemplateUpdateRequest, TemplateResponse,
    MessageSendRequest, MessageSendResponse, SendResultItem,
    MessageHistoryItem, RecipientItem, ContactItem,
    TemplateCategoryEnum
)


class TeacherMessageService:
    """선생님 메시지 센터 서비스"""

    # ========== 템플릿 관리 ==========

    @staticmethod
    def get_templates(
        db: Session,
        teacher_id: int,
        academy_id: int,
        category: Optional[str] = None
    ) -> List[TemplateResponse]:
        """
        템플릿 목록 조회
        - 내 템플릿 + 학원 공용 템플릿
        - category 파라미터로 필터링 가능
        """
        query = db.query(MessageTemplate).filter(
            and_(
                MessageTemplate.academy_id == academy_id,
                or_(
                    MessageTemplate.teacher_id == teacher_id,
                    MessageTemplate.teacher_id.is_(None)
                )
            )
        )

        if category:
            query = query.filter(MessageTemplate.category == category)

        templates = query.order_by(MessageTemplate.created_at.desc()).all()

        return [
            TemplateResponse(
                id=t.template_id,
                name=t.name,
                content=t.content,
                category=t.category.value if t.category else None,
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
        # 스키마 Enum → 모델 Enum 매핑
        model_category = TemplateCategory(data.category.value)

        template = MessageTemplate(
            academy_id=academy_id,
            teacher_id=teacher_id,
            name=data.name,
            content=data.content,
            category=model_category
        )
        db.add(template)
        db.commit()
        db.refresh(template)

        return TemplateResponse(
            id=template.template_id,
            name=template.name,
            content=template.content,
            category=template.category.value if template.category else None,
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
                MessageTemplate.teacher_id == teacher_id
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
        if data.category is not None:
            template.category = TemplateCategory(data.category.value)

        db.commit()
        db.refresh(template)

        return TemplateResponse(
            id=template.template_id,
            name=template.name,
            content=template.content,
            category=template.category.value if template.category else None,
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
                MessageTemplate.teacher_id == teacher_id
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
        - DB 기록만 (실제 SMS 연동은 추후)
        """
        # 반 존재 확인
        class_obj = db.query(Class).filter(
            Class.class_id == data.class_id
        ).first()
        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="반을 찾을 수 없습니다"
            )

        # 학생 목록 조회
        students = db.query(Student).filter(
            Student.student_id.in_(data.student_ids)
        ).all()

        if not students:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="유효한 학생이 없습니다"
            )

        # 메시지 유형 매핑
        msg_type = MessageType(data.type.value)

        # Message 레코드 생성
        message = Message(
            academy_id=academy_id,
            teacher_id=teacher_id,
            class_id=data.class_id,
            target_group=MessageTargetGroup.SPECIFIC_CLASSES,
            target_ids=str(data.student_ids),
            title=f"[{data.type.value}] 메시지",
            content=data.content,
            message_type=msg_type,
            template_id=data.template_id,
            sent_count=len(students),
            success_count=len(students),
            fail_count=0,
            status=MessageStatus.COMPLETED,
            sent_at=datetime.now()
        )
        db.add(message)
        db.flush()

        # MessageRecipient 레코드 생성
        results = []
        sent_count = 0
        failed_count = 0

        found_student_ids = {s.student_id for s in students}

        for student_id in data.student_ids:
            if student_id in found_student_ids:
                recipient = MessageRecipient(
                    message_id=message.message_id,
                    student_id=student_id,
                    status=RecipientStatus.SENT
                )
                db.add(recipient)
                results.append(SendResultItem(
                    student_id=student_id,
                    status="sent"
                ))
                sent_count += 1
            else:
                results.append(SendResultItem(
                    student_id=student_id,
                    status="failed",
                    error="학생을 찾을 수 없습니다"
                ))
                failed_count += 1

        # 집계 업데이트
        message.sent_count = sent_count
        message.success_count = sent_count
        message.fail_count = failed_count

        db.commit()

        return MessageSendResponse(
            message=f"메시지 발송 완료 (성공: {sent_count}, 실패: {failed_count})",
            sent_count=sent_count,
            failed_count=failed_count,
            results=results
        )

    # ========== 히스토리 조회 ==========

    @staticmethod
    def get_message_history(
        db: Session,
        teacher_id: int,
        academy_id: int,
        page: int = 1,
        limit: int = 20,
        class_id: Optional[int] = None,
        message_type: Optional[str] = None
    ) -> tuple[List[MessageHistoryItem], int]:
        """메시지 발송 내역 조회"""
        query = db.query(Message).filter(
            Message.academy_id == academy_id
        )

        # teacher_id 필터 (해당 선생님이 발송한 메시지만)
        query = query.filter(
            or_(
                Message.teacher_id == teacher_id,
                Message.teacher_id.is_(None)
            )
        )

        # class_id 필터
        if class_id:
            query = query.filter(Message.class_id == class_id)

        # message_type 필터
        if message_type:
            query = query.filter(Message.message_type == message_type)

        query = query.order_by(Message.created_at.desc())
        total = query.count()
        messages = query.offset((page - 1) * limit).limit(limit).all()

        items = []
        for m in messages:
            # 반 이름 조회
            class_name = None
            if m.class_id:
                cls = db.query(Class).filter(Class.class_id == m.class_id).first()
                if cls:
                    class_name = cls.class_name

            # 수신자 목록 조회
            recipients_data = []
            msg_recipients = db.query(MessageRecipient).filter(
                MessageRecipient.message_id == m.message_id
            ).all()

            for mr in msg_recipients:
                student = db.query(Student).filter(
                    Student.student_id == mr.student_id
                ).first()

                parent_phone = None
                if student:
                    # StudentContact에서 priority=1인 활성 연락처
                    contact = db.query(StudentContact).filter(
                        and_(
                            StudentContact.student_id == mr.student_id,
                            StudentContact.is_active == True
                        )
                    ).order_by(StudentContact.priority.asc()).first()

                    if contact:
                        parent_phone = contact.phone
                    else:
                        parent_phone = student.parent_phone

                recipients_data.append(RecipientItem(
                    student_id=mr.student_id,
                    student_name=student.name if student else "알 수 없음",
                    parent_phone=parent_phone,
                    status=mr.status.value if mr.status else "sent"
                ))

            # message_type 값 추출
            msg_type = "normal"
            if m.message_type:
                msg_type = m.message_type.value if hasattr(m.message_type, 'value') else str(m.message_type)

            items.append(MessageHistoryItem(
                id=m.message_id,
                type=msg_type,
                content=m.content,
                class_id=m.class_id,
                class_name=class_name,
                recipients=recipients_data,
                sent_at=m.sent_at,
                sent_count=m.success_count or 0,
                failed_count=m.fail_count or 0
            ))

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
        - 특정 반의 학생들 연락처 (class_id 필수)
        - StudentContacts에서 priority 가장 높은 활성 연락처 사용, 없으면 Student.parent_phone 폴백
        """
        if class_id:
            # 특정 반 학생만
            students = db.query(Student).filter(
                and_(
                    Student.academy_id == academy_id,
                    Student.class_id == class_id
                )
            ).order_by(Student.name).all()
        else:
            # 담당 반 전체
            classes = db.query(Class).filter(
                Class.teacher_id == teacher_id
            ).all()
            class_ids = [c.class_id for c in classes]

            if not class_ids:
                return []

            students = db.query(Student).filter(
                and_(
                    Student.academy_id == academy_id,
                    Student.class_id.in_(class_ids)
                )
            ).order_by(Student.name).all()

        result = []
        for s in students:
            # StudentContact에서 가장 우선순위 높은 활성 연락처
            contact = db.query(StudentContact).filter(
                and_(
                    StudentContact.student_id == s.student_id,
                    StudentContact.is_active == True
                )
            ).order_by(StudentContact.priority.asc()).first()

            parent_phone = contact.phone if contact else s.parent_phone

            result.append(ContactItem(
                student_id=s.student_id,
                student_name=s.name,
                parent_phone=parent_phone
            ))

        return result
