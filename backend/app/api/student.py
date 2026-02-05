"""
학생 관리 관련 API 엔드포인트
학생 CRUD 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse, StudentListResponse
from app.services.student_service import StudentService
from app.models.user import User
from app.api.auth import get_current_user
from typing import Optional


# API 라우터 생성
router = APIRouter(
    prefix="/api/admin/students",
    tags=["학생 관리"]
)


@router.get("", response_model=StudentListResponse)
async def get_students(
    page: int = Query(1, ge=1, description="페이지 번호 (1부터 시작)"),
    limit: int = Query(20, ge=1, le=100, description="페이지당 항목 수 (최대: 100)"),
    search: Optional[str] = Query(None, description="검색어 (이름, 전화번호)"),
    status: Optional[str] = Query(None, description="상태 필터 (enrolled, paused, withdrawn)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    학생 목록 조회
    
    학원의 모든 학생 목록을 조회합니다.
    검색, 상태 필터, 페이지네이션을 지원합니다.
    
    Query Parameters:
        - page: 페이지 번호 (기본: 1)
        - limit: 페이지당 항목 수 (기본: 20, 최대: 100)
        - search: 검색어 (이름, 전화번호, 학부모 전화번호)
        - status: 상태 필터 (enrolled, paused, withdrawn)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        StudentListResponse:
            - total: 전체 학생 수
            - page: 현재 페이지
            - students: 학생 목록
    
    Raises:
        401: 인증되지 않은 사용자
    
    사용 예시:
        GET /api/admin/students
        GET /api/admin/students?page=1&limit=20
        GET /api/admin/students?search=김철수
        GET /api/admin/students?status=enrolled
    """
    academy_id = current_user.academy_id
    
    # 학생 목록 조회
    students, total = StudentService.get_students(
        db=db,
        academy_id=academy_id,
        search=search,
        status_filter=status,
        page=page,
        limit=limit
    )
    
    # 응답 변환
    return StudentListResponse(
        total=total,
        page=page,
        students=[StudentService.to_response(student) for student in students]
    )


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    학생 정보 조회 (단일)
    
    특정 학생의 상세 정보를 조회합니다.
    
    Path Parameters:
        - student_id: 학생 ID
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        StudentResponse: 학생 정보
    
    Raises:
        401: 인증되지 않은 사용자
        404: 학생을 찾을 수 없음
    """
    academy_id = current_user.academy_id
    
    student = StudentService.get_student_by_id(db, student_id, academy_id)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="학생을 찾을 수 없습니다"
        )
    
    return StudentService.to_response(student)


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    학생 등록
    
    새로운 학생을 등록합니다.
    username과 password를 함께 제공하면 로그인 계정도 자동으로 생성됩니다.
    
    Request Body:
        - name: 학생 이름 (필수)
        - school: 학교명 (선택)
        - grade: 학년 (선택)
        - phone: 학생 전화번호 (선택)
        - parent_phone: 학부모 전화번호 (필수)
        - enrollment_date: 등록일 (선택)
        - username: 로그인 ID (선택, password와 함께 제공 시 계정 생성)
        - password: 비밀번호 (선택, username과 함께 제공 시 계정 생성)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        StudentResponse: 생성된 학생 정보
    
    Raises:
        400: username 중복
        401: 인증되지 않은 사용자
        422: 입력 데이터 검증 실패
    
    사용 예시:
        POST /api/admin/students
        {
            "name": "이학생",
            "school": "행복중",
            "grade": "중2",
            "phone": "010-5555-6666",
            "parent_phone": "010-7777-8888",
            "username": "student_lee",
            "password": "initial_password"
        }
    """
    academy_id = current_user.academy_id
    
    # 학생 생성 (User 계정도 함께 생성 가능)
    new_student = StudentService.create_student(
        db=db,
        academy_id=academy_id,
        student_data=student_data
    )
    
    return StudentService.to_response(new_student)


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    student_data: StudentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    학생 정보 수정
    
    학생의 정보를 수정합니다.
    변경하지 않을 필드는 생략할 수 있습니다.
    
    Path Parameters:
        - student_id: 학생 ID
    
    Request Body:
        - name: 학생 이름 (선택)
        - school: 학교명 (선택)
        - grade: 학년 (선택)
        - phone: 학생 전화번호 (선택)
        - parent_phone: 학부모 전화번호 (선택)
        - enrollment_date: 등록일 (선택)
        - status: 학생 상태 (선택: enrolled, paused, withdrawn)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        StudentResponse: 수정된 학생 정보
    
    Raises:
        401: 인증되지 않은 사용자
        404: 학생을 찾을 수 없음
        422: 입력 데이터 검증 실패
    
    사용 예시:
        PUT /api/admin/students/1
        {
            "grade": "중3",
            "status": "enrolled"
        }
    """
    academy_id = current_user.academy_id
    
    # 학생 정보 수정
    updated_student = StudentService.update_student(
        db=db,
        student_id=student_id,
        academy_id=academy_id,
        student_data=student_data
    )
    
    return StudentService.to_response(updated_student)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    학생 삭제
    
    학생 정보를 삭제합니다.
    
    Path Parameters:
        - student_id: 학생 ID
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        204 No Content (응답 바디 없음)
    
    Raises:
        401: 인증되지 않은 사용자
        404: 학생을 찾을 수 없음
    
    사용 예시:
        DELETE /api/admin/students/1
    """
    academy_id = current_user.academy_id
    
    # 학생 삭제
    StudentService.delete_student(
        db=db,
        student_id=student_id,
        academy_id=academy_id
    )
    
    return None
