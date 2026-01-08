"""
인증 관련 API 엔드포인트
회원가입, 로그인 API 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import AuthService

# API 라우터 생성
router = APIRouter(
    prefix="/auth",  # 모든 엔드포인트 앞에 /auth 추가
    tags=["인증"]     # Swagger 문서에서 그룹화
)


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    회원가입 API
    
    새로운 사용자를 등록합니다.
    
    Args:
        user_data: 회원가입 정보
            - username: 로그인 ID (3-50자, 영문/숫자/언더스코어)
            - password: 비밀번호 (최소 6자)
            - academy_id: 소속 학원 ID
            - user_role: 사용자 역할 (ADMIN/TEACHER/STUDENT, 기본값: TEACHER)
            - name: 실명 (선택)
            - phone: 전화번호 (선택)
        db: 데이터베이스 세션 (자동 주입)
    
    Returns:
        생성된 사용자 정보 (비밀번호 제외)
    
    Raises:
        400: username이 이미 존재하는 경우
        422: 입력 데이터 검증 실패
    
    사용 예시:
        POST /auth/signup
        {
            "username": "teacher_kim",
            "password": "secure123",
            "academy_id": 1,
            "user_role": "TEACHER",
            "name": "김선생",
            "phone": "010-1234-5678"
        }
    """
    # AuthService를 통해 사용자 생성
    new_user = AuthService.create_user(db, user_data)
    return new_user


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    로그인 API
    
    사용자 인증 후 JWT 토큰을 발급합니다.
    
    Args:
        login_data: 로그인 정보
            - username: 로그인 ID
            - password: 비밀번호
        db: 데이터베이스 세션 (자동 주입)
    
    Returns:
        JWT 토큰 및 사용자 정보
        - access_token: JWT 토큰 (헤더에 "Bearer {token}" 형식으로 사용)
        - token_type: "bearer"
        - user: 사용자 정보
    
    Raises:
        401: username 또는 password가 올바르지 않은 경우
    
    사용 예시:
        POST /auth/login
        {
            "username": "teacher_kim",
            "password": "secure123"
        }
        
        응답:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer",
            "user": {
                "user_id": 1,
                "username": "teacher_kim",
                ...
            }
        }
    """
    # 1. 사용자 인증
    user = AuthService.authenticate_user(db, login_data)
    
    # 2. JWT 토큰 생성
    access_token = AuthService.create_user_token(user)
    
    # 3. 토큰과 사용자 정보 반환
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    db: Session = Depends(get_db)
    # TODO: JWT 토큰 검증 의존성 추가 필요
):
    """
    현재 로그인한 사용자 정보 조회 API
    
    JWT 토큰을 통해 현재 로그인한 사용자의 정보를 반환합니다.
    (향후 JWT 토큰 검증 로직 추가 필요)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        현재 사용자 정보
    """
    # TODO: 토큰에서 사용자 정보 추출 후 반환
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="JWT 토큰 검증 기능은 추후 구현 예정입니다"
    )
