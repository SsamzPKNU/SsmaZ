"""
메시지 센터 관련 API 엔드포인트
단체 메시지 발송 및 이력 조회 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.core.database import get_db
from app.schemas.message import (
    MessageSendRequest,
    MessageSendResponse,
    MessageHistoryResponse,
    MessageDetailResponse
)
from app.services.message_service import MessageService
from app.models.user import User
from app.models.message import Message
from app.api.auth import get_current_user
from typing import List


# API 라우터 생성
router = APIRouter(
    prefix="/api/admin/messages",
    tags=["메시지 센터"]
)


@router.get("", response_model=List[MessageHistoryResponse])
async def get_message_history(
    skip: int = Query(0, ge=0, description="페이지네이션 오프셋"),
    limit: int = Query(100, ge=1, le=1000, description="페이지네이션 제한"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    메시지 발송 내역 조회 (이력)
    
    과거에 발송한 단체 메시지의 이력을 조회합니다.
    발송 건수, 성공/실패 건수, 발송 시간 등을 확인할 수 있습니다.
    
    Query Parameters:
        - skip: 페이지네이션 오프셋 (기본: 0)
        - limit: 페이지네이션 제한 (기본: 100, 최대: 1000)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        List[MessageHistoryResponse]: 메시지 발송 이력 목록
        
    Response Fields:
        - id: 메시지 ID
        - summary: 제목 요약
        - sent_count: 발송 건수
        - success_count: 성공 건수
        - fail_count: 실패 건수
        - sent_at: 발송 시간
    
    Raises:
        401: 인증되지 않은 사용자
    
    사용 예시:
        GET /api/admin/messages
        GET /api/admin/messages?skip=0&limit=50
    """
    academy_id = current_user.academy_id
    
    messages = MessageService.get_message_history(
        db=db,
        academy_id=academy_id,
        skip=skip,
        limit=limit
    )
    
    return [MessageService.to_history_response(msg) for msg in messages]


@router.post("/send", response_model=MessageSendResponse, status_code=status.HTTP_201_CREATED)
async def send_bulk_message(
    message_data: MessageSendRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    단체 메시지 발송
    
    대상 그룹에게 단체 메시지를 발송합니다.
    - 학부모 전체
    - 학생 전체
    - 선생님 전체
    - 특정 대상만
    
    Request Body:
        - target_group: 대상 그룹 (parents, students, teachers, specific_classes)
        - target_ids: 특정 대상 ID 목록 (비어있으면 전체 발송)
        - title: 제목 (필수)
        - content: 내용 (필수)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        MessageSendResponse:
            - status: 발송 상태 (success, failed)
            - sent_count: 발송 건수
            - estimated_cost: 예상 비용 (원)
            - message_id: 메시지 ID
    
    Raises:
        401: 인증되지 않은 사용자
        422: 입력 데이터 검증 실패
    
    사용 예시:
        POST /api/admin/messages/send
        {
            "target_group": "parents",
            "target_ids": [],
            "title": "설 연휴 휴강 안내",
            "content": "SSamZ 학원입니다. 설 연휴 기간(1/28~1/30)은 휴강입니다."
        }
        
        응답:
        {
            "status": "success",
            "sent_count": 150,
            "estimated_cost": 3000,
            "message_id": 501
        }
    
    참고:
        - SMS 단가: 1건당 20원 (예시)
        - 실제 SMS 발송은 외부 API 연동 필요 (현재는 시뮬레이션)
        - 발송 이력은 자동으로 저장됩니다
    """
    academy_id = current_user.academy_id
    
    result = MessageService.send_bulk_message(
        db=db,
        academy_id=academy_id,
        message_data=message_data
    )
    
    return result


@router.get("/{message_id}", response_model=MessageDetailResponse)
async def get_message_detail(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    메시지 상세 정보 조회
    
    특정 메시지의 상세 정보를 조회합니다.
    
    Path Parameters:
        - message_id: 메시지 ID
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        MessageDetailResponse: 메시지 상세 정보
    
    Raises:
        401: 인증되지 않은 사용자
        404: 메시지를 찾을 수 없음
    
    사용 예시:
        GET /api/admin/messages/501
    """
    academy_id = current_user.academy_id
    
    message = db.query(Message).filter(
        and_(
            Message.message_id == message_id,
            Message.academy_id == academy_id
        )
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="메시지를 찾을 수 없습니다"
        )
    
    return MessageService.to_detail_response(message)
