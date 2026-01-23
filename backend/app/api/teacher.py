"""
선생님 관리 관련 API 엔드포인트
선생님 CRUD 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherResponse
from app.services.teacher_service import TeacherService
from app.models.user import User
from app.api.auth import get_current_user
from typing import List, Optional


# API 라우터 생성
router = APIRouter(
    prefix="/api/admin/teachers",
    tags=["선생님 관리"]
)


@router.get("", response_model=List[TeacherResponse])
async def get_teachers(
    status: Optional[str] = Query(None, description="재직 상태 필터 (active, leave, resigned)"),
    skip: int = Query(0, ge=0, description="페이지네이션 오프셋"),
    limit: int = Query(100, ge=1, le=1000, description="페이지네이션 제한"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    선생님 목록 조회
    
    학원의 모든 선생님 목록을 조회합니다.
    재직 상태별로 필터링할 수 있습니다.
    
    Query Parameters:
        - status: 재직 상태 필터 (active, leave, resigned)
        - skip: 페이지네이션 오프셋 (기본: 0)
        - limit: 페이지네이션 제한 (기본: 100, 최대: 1000)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        List[TeacherResponse]: 선생님 목록
        
    Response Fields:
        - id: 선생님 고유 ID
        - name: 선생님 이름
        - subject: 담당 과목
        - phone: 전화번호
        - email: 이메일
        - join_date: 입사일
        - status: 재직 상태 (active, leave, resigned)
        - assigned_classes: 담당 반 수
    
    Raises:
        401: 인증되지 않은 사용자
    
    사용 예시:
        GET /api/admin/teachers
        GET /api/admin/teachers?status=active
        GET /api/admin/teachers?skip=0&limit=10
    """
    academy_id = current_user.academy_id
    
    # 선생님 목록 조회
    teachers = TeacherService.get_teachers(
        db=db,
        academy_id=academy_id,
        status=status,
        skip=skip,
        limit=limit
    )
    
    # 응답 변환
    return [TeacherService.to_response(db, teacher) for teacher in teachers]


@router.get("/{teacher_id}", response_model=TeacherResponse)
async def get_teacher(
    teacher_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    선생님 정보 조회 (단일)
    
    특정 선생님의 상세 정보를 조회합니다.
    
    Path Parameters:
        - teacher_id: 선생님 ID
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        TeacherResponse: 선생님 정보
    
    Raises:
        401: 인증되지 않은 사용자
        404: 선생님을 찾을 수 없음
    """
    academy_id = current_user.academy_id
    
    teacher = TeacherService.get_teacher_by_id(db, teacher_id, academy_id)
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="선생님을 찾을 수 없습니다"
        )
    
    return TeacherService.to_response(db, teacher)


@router.post("", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
async def create_teacher(
    teacher_data: TeacherCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    선생님 등록
    
    새로운 선생님을 등록합니다.
    
    Request Body:
        - name: 선생님 이름 (필수)
        - subject: 담당 과목 (선택)
        - phone: 전화번호 (선택)
        - email: 이메일 (선택)
        - join_date: 입사일 (선택)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        TeacherResponse: 생성된 선생님 정보
    
    Raises:
        401: 인증되지 않은 사용자
        422: 입력 데이터 검증 실패
    
    사용 예시:
        POST /api/admin/teachers
        {
            "name": "새선생",
            "subject": "영어",
            "phone": "010-9999-8888",
            "email": "new@ssamz.com",
            "join_date": "2026-02-01"
        }
    """
    academy_id = current_user.academy_id
    
    # 선생님 생성
    new_teacher = TeacherService.create_teacher(
        db=db,
        academy_id=academy_id,
        teacher_data=teacher_data
    )
    
    return TeacherService.to_response(db, new_teacher)


@router.put("/{teacher_id}", response_model=TeacherResponse)
async def update_teacher(
    teacher_id: int,
    teacher_data: TeacherUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    선생님 정보 수정
    
    선생님의 정보를 수정합니다.
    변경하지 않을 필드는 생략할 수 있습니다.
    
    Path Parameters:
        - teacher_id: 선생님 ID
    
    Request Body:
        - name: 선생님 이름 (선택)
        - subject: 담당 과목 (선택)
        - phone: 전화번호 (선택)
        - email: 이메일 (선택)
        - join_date: 입사일 (선택)
        - status: 재직 상태 (선택: active, leave, resigned)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        TeacherResponse: 수정된 선생님 정보
    
    Raises:
        401: 인증되지 않은 사용자
        404: 선생님을 찾을 수 없음
        422: 입력 데이터 검증 실패
    
    사용 예시:
        PUT /api/admin/teachers/10
        {
            "subject": "수학",
            "status": "active"
        }
    """
    academy_id = current_user.academy_id
    
    # 선생님 정보 수정
    updated_teacher = TeacherService.update_teacher(
        db=db,
        teacher_id=teacher_id,
        academy_id=academy_id,
        teacher_data=teacher_data
    )
    
    return TeacherService.to_response(db, updated_teacher)


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(
    teacher_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    선생님 삭제
    
    선생님 정보를 삭제합니다.
    
    Path Parameters:
        - teacher_id: 선생님 ID
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        204 No Content (응답 바디 없음)
    
    Raises:
        401: 인증되지 않은 사용자
        404: 선생님을 찾을 수 없음
    
    사용 예시:
        DELETE /api/admin/teachers/10
    """
    academy_id = current_user.academy_id
    
    # 선생님 삭제
    TeacherService.delete_teacher(
        db=db,
        teacher_id=teacher_id,
        academy_id=academy_id
    )
    
    return None
