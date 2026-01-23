"""
인증 관련 API 엔드포인트
회원가입, 로그인 API 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Cookie
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, SimpleLoginResponse, SimpleUserResponse, CurrentUserResponse
from app.services.auth_service import AuthService
from app.services.login_log_service import LoginLogService
from app.core.security import verify_token, get_token_payload, verify_csrf_token
from app.models.user import User
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional
import os

# Rate Limiter 설정 (IP 기반)
limiter = Limiter(key_func=get_remote_address)

# 환경 설정
IS_PRODUCTION = os.getenv("ENVIRONMENT", "development") == "production"

# OAuth2 스키마 설정 (Bearer 토큰 방식) - 폴백용
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

# API 라우터 생성
router = APIRouter(
    prefix="/auth",  # 모든 엔드포인트 앞에 /auth 추가
    tags=["인증"]     # Swagger 문서에서 그룹화
)


async def get_current_user(
    request: Request,
    access_token: Optional[str] = Cookie(None),  # httpOnly 쿠키에서 토큰 읽기
    bearer_token: str = Depends(oauth2_scheme),  # Bearer 헤더 폴백
    db: Session = Depends(get_db)
) -> User:
    """
    JWT 토큰을 검증하고 현재 사용자를 반환하는 의존성 함수
    
    인증 방식:
    1. httpOnly 쿠키 (access_token) + X-CSRF-Token 헤더 (권장)
    2. Bearer 토큰 헤더 (폴백)
    
    보호된 엔드포인트에서 사용:
        @router.get("/protected")
        async def protected_route(current_user: User = Depends(get_current_user)):
            return {"user": current_user.username}
    """
    token = None
    
    # 1. httpOnly 쿠키에서 토큰 확인
    if access_token:
        token = access_token
        
        # CSRF 토큰 검증 (쿠키 방식일 때만)
        csrf_token = request.headers.get("X-CSRF-Token")
        
        if not csrf_token:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF 토큰이 필요합니다",
            )
        
        if not verify_csrf_token(token, csrf_token):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF 토큰이 유효하지 않습니다",
            )
    
    # 2. Bearer 토큰 헤더에서 토큰 확인 (폴백)
    elif bearer_token:
        token = bearer_token
    
    # 3. 토큰이 없는 경우
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 토큰에서 payload 추출
    payload = get_token_payload(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않거나 만료된 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰에서 사용자 정보를 찾을 수 없습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 데이터베이스에서 사용자 조회
    user = AuthService.get_user_by_username(db, username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


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
@limiter.limit("5/minute")  # 분당 5회 제한 (Brute Force 공격 방지)
async def login(
    request: Request,  # Rate Limiter에 필요
    response: Response,  # 쿠키 설정에 필요
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    로그인 API
    
    사용자 인증 후 JWT 토큰을 httpOnly 쿠키로 설정합니다.
    CSRF 토큰은 응답 body로 반환되어 클라이언트에 저장됩니다.
    
    Args:
        login_data: 로그인 정보
            - username: 로그인 ID
            - password: 비밀번호
        db: 데이터베이스 세션 (자동 주입)
    
    Returns:
        CSRF 토큰 및 사용자 정보
        - csrf_token: CSRF 방지 토큰 (매 요청 시 헤더로 전송 필요)
        - token_type: "bearer"
        - user: 사용자 정보
    
    Cookies (httpOnly):
        access_token: JWT 토큰 (자동으로 쿠키에 저장됨)
    
    Raises:
        401: username 또는 password가 올바르지 않은 경우
        429: 분당 5회 초과 시
    
    사용 예시:
        POST /auth/login
        {
            "username": "teacher_kim",
            "password": "secure123"
        }
        
        응답:
        {
            "csrf_token": "abc123xyz...",
            "token_type": "bearer",
            "user": {
                "user_id": 1,
                "username": "teacher_kim",
                ...
            }
        }
        
        + Set-Cookie: access_token={JWT}; HttpOnly; Secure; SameSite=Strict
    """
    # 클라이언트 정보 추출
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")
    
    try:
        # 1. 사용자 인증
        user = AuthService.authenticate_user(db, login_data)
        
        # 2. 로그인 성공 로그 기록
        LoginLogService.log_success(
            db=db,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # 3. CSRF 토큰이 포함된 JWT 토큰 생성
        access_token, csrf_token = AuthService.create_user_token_with_csrf(user)
        
        # 4. httpOnly 쿠키로 JWT 토큰 설정
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,  # JavaScript에서 접근 불가 (XSS 방지)
            secure=IS_PRODUCTION,  # HTTPS에서만 전송 (프로덕션)
            samesite="strict" if IS_PRODUCTION else "lax",  # CSRF 추가 방지
            max_age=30 * 60,  # 30분
            path="/"
        )
        
        # 5. CSRF 토큰과 사용자 정보 반환
        return Token(
            csrf_token=csrf_token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )
        
    except HTTPException as e:
        # 로그인 실패 로그 기록
        failure_reason = "USER_NOT_FOUND_OR_WRONG_PASSWORD"
        user_id = None
        
        # 사용자 존재 여부 확인 (실패 원인 구분)
        existing_user = AuthService.get_user_by_username(db, login_data.username)
        if not existing_user:
            failure_reason = "USER_NOT_FOUND"
        else:
            failure_reason = "WRONG_PASSWORD"
            user_id = existing_user.user_id
        
        LoginLogService.log_failure(
            db=db,
            user_id=user_id,
            failure_reason=failure_reason,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # 원래 HTTPException 다시 발생
        raise e


@router.get("/me", response_model=CurrentUserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """
    현재 로그인한 사용자 정보 조회 API
    
    JWT 토큰을 통해 현재 로그인한 사용자의 정보를 반환합니다.
    명세서 형식: id, username, name, avatar_seed, user_role
    
    Headers (쿠키 방식):
        Cookie: access_token={JWT}
        X-CSRF-Token: {csrf_token}
    
    Headers (Bearer 방식 - 폴백):
        Authorization: Bearer {access_token}
    
    Returns:
        현재 사용자 정보
        - id: 사용자 고유 ID
        - username: 로그인 ID
        - name: 실명
        - avatar_seed: 아바타 시드 (username과 동일)
        - user_role: 사용자 역할
    
    Raises:
        401: 토큰이 없거나 유효하지 않은 경우
        403: CSRF 토큰이 없거나 유효하지 않은 경우 (쿠키 방식)
    
    사용 예시:
        GET /auth/me
        Headers: 
          - Cookie: access_token={JWT}
          - X-CSRF-Token: {csrf_token}
        
        응답:
        {
            "id": 1,
            "username": "admin",
            "name": "원장님",
            "avatar_seed": "admin",
            "user_role": "ADMIN"
        }
    """
    return CurrentUserResponse(
        id=current_user.user_id,
        username=current_user.username,
        name=current_user.name,
        avatar_seed=current_user.username,  # avatar_seed는 username과 동일
        user_role=current_user.user_role.value  # Enum을 문자열로 변환
    )


@router.post("/login-mobile", response_model=SimpleLoginResponse)
@limiter.limit("5/minute")  # 분당 5회 제한 (Brute Force 공격 방지)
async def login_mobile(
    request: Request,  # Rate Limiter에 필요
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    간단한 로그인 API (모바일/앱용)
    
    명세서 형식으로 응답합니다:
    - access_token을 응답 body에 포함
    - httpOnly 쿠키 사용 안 함
    - CSRF 토큰 사용 안 함
    
    ⚠️ 주의: 웹 브라우저에서는 /auth/login 사용을 권장합니다.
    이 엔드포인트는 모바일 앱이나 토큰을 직접 관리하는 클라이언트용입니다.
    
    Args:
        login_data: 로그인 정보
            - username: 로그인 ID
            - password: 비밀번호
        db: 데이터베이스 세션 (자동 주입)
    
    Returns:
        사용자 정보 및 JWT 토큰
        - user: 사용자 정보 (id, username, name, user_role, academy_id)
        - access_token: JWT 액세스 토큰
    
    Raises:
        401: username 또는 password가 올바르지 않은 경우
        429: 분당 5회 초과 시
    
    사용 예시:
        POST /auth/login-mobile
        {
            "username": "admin",
            "password": "password123"
        }
        
        응답:
        {
            "user": {
                "id": 1,
                "username": "admin",
                "name": "원장님",
                "user_role": "ADMIN",
                "academy_id": 1
            },
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
    """
    # 클라이언트 정보 추출
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("User-Agent")
    
    try:
        # 1. 사용자 인증
        user = AuthService.authenticate_user(db, login_data)
        
        # 2. 로그인 성공 로그 기록
        LoginLogService.log_success(
            db=db,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # 3. JWT 토큰 생성 (CSRF 없이 일반 토큰만)
        access_token = AuthService.create_user_token(user)
        
        # 4. 명세서 형식으로 응답
        return SimpleLoginResponse(
            user=SimpleUserResponse(
                id=user.user_id,
                username=user.username,
                name=user.name,
                user_role=user.user_role.value,  # Enum을 문자열로 변환
                academy_id=user.academy_id
            ),
            access_token=access_token
        )
        
    except HTTPException as e:
        # 로그인 실패 로그 기록
        failure_reason = "USER_NOT_FOUND_OR_WRONG_PASSWORD"
        user_id = None
        
        # 사용자 존재 여부 확인 (실패 원인 구분)
        existing_user = AuthService.get_user_by_username(db, login_data.username)
        if not existing_user:
            failure_reason = "USER_NOT_FOUND"
        else:
            failure_reason = "WRONG_PASSWORD"
            user_id = existing_user.user_id
        
        LoginLogService.log_failure(
            db=db,
            user_id=user_id,
            failure_reason=failure_reason,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # 원래 HTTPException 다시 발생
        raise e


@router.post("/logout")
async def logout(
    response: Response,
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db)
):
    """
    로그아웃 API
    
    httpOnly 쿠키를 삭제하고 로그아웃 로그를 기록합니다.
    
    기록되는 정보:
    - logout_time: 로그아웃 시간
    - session_duration: 세션 지속 시간 (초)
    
    Returns:
        로그아웃 성공 메시지
    """
    # 토큰에서 user_id 추출하여 로그아웃 로그 기록
    if access_token:
        payload = get_token_payload(access_token)
        if payload and payload.get("user_id"):
            LoginLogService.log_logout(
                db=db,
                user_id=payload["user_id"]
            )
    
    # httpOnly 쿠키 삭제
    response.delete_cookie(
        key="access_token",
        path="/"
    )
    
    return {"message": "로그아웃 되었습니다"}
