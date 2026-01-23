"""
클래스(반/수업) 관리 관련 API 엔드포인트
클래스 CRUD 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.class_schema import ClassCreate, ClassUpdate, ClassResponse, ClassDetailResponse
from app.services.class_service import ClassService
from app.models.user import User
from app.api.auth import get_current_user
from typing import List, Optional


# API 라우터 생성
router = APIRouter(
    prefix="/api/admin/classes",
    tags=["클래스 관리"]
)


@router.get("", response_model=List[ClassResponse])
async def get_classes(
    teacher_id: Optional[int] = Query(None, description="선생님 ID 필터"),
    skip: int = Query(0, ge=0, description="페이지네이션 오프셋"),
    limit: int = Query(100, ge=1, le=1000, description="페이지네이션 제한"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    클래스 목록 조회
    
    학원의 모든 클래스(반) 목록을 조회합니다.
    선생님별로 필터링할 수 있습니다.
    
    Query Parameters:
        - teacher_id: 선생님 ID 필터 (선택)
        - skip: 페이지네이션 오프셋 (기본: 0)
        - limit: 페이지네이션 제한 (기본: 100)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        List[ClassResponse]: 클래스 목록
        
    Response Fields:
        - id: 반 고유 ID
        - name: 반 이름
        - teacher_id: 담당 선생님 ID
        - teacher_name: 담당 선생님 이름
        - schedule: 수업 일정
        - capacity: 정원
        - current_students: 현재 학생 수
    
    Raises:
        401: 인증되지 않은 사용자
    
    사용 예시:
        GET /api/admin/classes
        GET /api/admin/classes?teacher_id=10
    """
    academy_id = current_user.academy_id
    
    classes = ClassService.get_classes(
        db=db,
        academy_id=academy_id,
        teacher_id=teacher_id,
        skip=skip,
        limit=limit
    )
    
    return [ClassService.to_response(db, class_obj) for class_obj in classes]


@router.get("/{class_id}", response_model=ClassDetailResponse)
async def get_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    클래스 상세 정보 조회
    
    특정 클래스의 상세 정보를 조회합니다.
    소속 학생 목록도 함께 반환됩니다.
    
    Path Parameters:
        - class_id: 반 ID
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        ClassDetailResponse: 클래스 상세 정보 (학생 목록 포함)
    
    Raises:
        401: 인증되지 않은 사용자
        404: 클래스를 찾을 수 없음
    """
    academy_id = current_user.academy_id
    
    class_obj = ClassService.get_class_by_id(db, class_id, academy_id)
    
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="클래스를 찾을 수 없습니다"
        )
    
    return ClassService.to_detail_response(db, class_obj)


@router.post("", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
async def create_class(
    class_data: ClassCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    클래스 생성
    
    새로운 클래스(반)를 생성합니다.
    
    Request Body:
        - name: 반 이름 (필수)
        - teacher_id: 담당 선생님 ID (선택)
        - schedule: 수업 일정 (선택)
        - capacity: 정원 (선택)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        ClassResponse: 생성된 클래스 정보
    
    Raises:
        401: 인증되지 않은 사용자
        404: 선생님을 찾을 수 없음
        422: 입력 데이터 검증 실패
    
    사용 예시:
        POST /api/admin/classes
        {
            "name": "영어 특강반",
            "teacher_id": 10,
            "schedule": "토 10:00",
            "capacity": 20
        }
    """
    academy_id = current_user.academy_id
    
    new_class = ClassService.create_class(
        db=db,
        academy_id=academy_id,
        class_data=class_data
    )
    
    return ClassService.to_response(db, new_class)


@router.put("/{class_id}", response_model=ClassResponse)
async def update_class(
    class_id: int,
    class_data: ClassUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    클래스 정보 수정
    
    클래스의 정보를 수정합니다.
    변경하지 않을 필드는 생략할 수 있습니다.
    
    Path Parameters:
        - class_id: 반 ID
    
    Request Body:
        - name: 반 이름 (선택)
        - teacher_id: 담당 선생님 ID (선택)
        - schedule: 수업 일정 (선택)
        - capacity: 정원 (선택)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        ClassResponse: 수정된 클래스 정보
    
    Raises:
        401: 인증되지 않은 사용자
        404: 클래스 또는 선생님을 찾을 수 없음
        422: 입력 데이터 검증 실패
    
    사용 예시:
        PUT /api/admin/classes/1
        {
            "schedule": "화/목 17:00",
            "capacity": 25
        }
    """
    academy_id = current_user.academy_id
    
    updated_class = ClassService.update_class(
        db=db,
        class_id=class_id,
        academy_id=academy_id,
        class_data=class_data
    )
    
    return ClassService.to_response(db, updated_class)


@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    클래스 삭제
    
    클래스 정보를 삭제합니다.
    
    Path Parameters:
        - class_id: 반 ID
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        204 No Content (응답 바디 없음)
    
    Raises:
        401: 인증되지 않은 사용자
        404: 클래스를 찾을 수 없음
    
    사용 예시:
        DELETE /api/admin/classes/1
    """
    academy_id = current_user.academy_id
    
    ClassService.delete_class(
        db=db,
        class_id=class_id,
        academy_id=academy_id
    )
    
    return None
