"""
인증 관련 비즈니스 로직
회원가입, 로그인, 사용자 조회 등의 기능 제공
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.models.teacher import Teacher
from app.models.student import Student, StudentStatus
from app.schemas.user import UserCreate, UserLogin
from app.core.security import hash_password, verify_password, create_access_token, create_access_token_with_csrf
from typing import Optional, Tuple


class AuthService:
    """인증 관련 서비스 클래스"""
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """
        username으로 사용자 조회
        
        Args:
            db: 데이터베이스 세션
            username: 조회할 사용자명
            
        Returns:
            User 객체 또는 None
        """
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """
        새로운 사용자 생성 (회원가입)
        
        Args:
            db: 데이터베이스 세션
            user_data: 회원가입 정보
            
        Returns:
            생성된 User 객체
            
        Raises:
            HTTPException: username이 이미 존재하는 경우
        """
        # 1. username 중복 확인
        existing_user = AuthService.get_user_by_username(db, user_data.username)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 username입니다"
            )
        
        # 2. 비밀번호 해싱
        hashed_password = hash_password(user_data.password)
        
        # 3. User 객체 생성
        db_user = User(
            username=user_data.username,
            password_hash=hashed_password,
            academy_id=user_data.academy_id,
            user_role=user_data.user_role,
            name=user_data.name,
            phone=user_data.phone
        )
        
        # 4. 데이터베이스에 저장
        db.add(db_user)
        db.commit()
        db.refresh(db_user)  # DB에서 생성된 값들(user_id, created_at 등) 가져오기

        # 5. TEACHER 역할인 경우 Teachers 테이블에도 자동 등록
        if db_user.user_role == UserRole.TEACHER:
            db_teacher = Teacher(
                user_id=db_user.user_id,
                academy_id=db_user.academy_id,
                name=db_user.name or db_user.username,
                phone=db_user.phone,
                employment_type="FULL_TIME"
            )
            db.add(db_teacher)
            db.commit()

        # 6. STUDENT 역할인 경우 Students 테이블에도 자동 등록
        if db_user.user_role == UserRole.STUDENT:
            db_student = Student(
                academy_id=db_user.academy_id,
                name=db_user.name or db_user.username,
                parent_phone=db_user.phone or "",
                status=StudentStatus.ENROLLED,
                user_id=db_user.user_id
            )
            db.add(db_student)
            db.commit()

        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, login_data: UserLogin) -> User:
        """
        사용자 인증 (로그인)
        
        Args:
            db: 데이터베이스 세션
            login_data: 로그인 정보 (username, password)
            
        Returns:
            인증된 User 객체
            
        Raises:
            HTTPException: 인증 실패 시
        """
        # 1. 사용자 조회
        user = AuthService.get_user_by_username(db, login_data.username)
        
        # 2. 사용자가 없거나 비밀번호가 틀린 경우
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="username 또는 password가 올바르지 않습니다",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    
    @staticmethod
    def create_user_token(user: User) -> str:
        """
        사용자에 대한 JWT 토큰 생성
        
        Args:
            user: User 객체
            
        Returns:
            JWT 토큰 문자열
        """
        # 토큰에 포함할 데이터 (subject에 username 저장)
        token_data = {
            "sub": user.username,
            "user_id": user.user_id,
            "academy_id": user.academy_id,
            "role": user.user_role.value
        }
        
        # JWT 토큰 생성
        access_token = create_access_token(data=token_data)
        return access_token
    
    @staticmethod
    def create_user_token_with_csrf(user: User) -> Tuple[str, str]:
        """
        CSRF 토큰이 포함된 JWT 토큰 생성 (httpOnly 쿠키 방식용)
        
        Args:
            user: User 객체
            
        Returns:
            (JWT 토큰, CSRF 토큰) 튜플
        """
        token_data = {
            "sub": user.username,
            "user_id": user.user_id,
            "academy_id": user.academy_id,
            "role": user.user_role.value
        }
        
        # CSRF 토큰이 포함된 JWT 토큰 생성
        access_token, csrf_token = create_access_token_with_csrf(data=token_data)
        return access_token, csrf_token
