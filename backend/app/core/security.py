"""
보안 관련 유틸리티 함수
- 비밀번호 해싱 및 검증
- JWT 토큰 생성 및 검증
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import hashlib
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# JWT 설정값 가져오기
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def hash_password(password: str) -> str:
    """
    평문 비밀번호를 bcrypt로 해싱합니다.
    
    bcrypt는 최대 72바이트 제한이 있으므로,
    먼저 SHA-256으로 해싱하여 고정 길이로 만든 후 bcrypt를 적용합니다.
    
    Args:
        password: 사용자가 입력한 평문 비밀번호
        
    Returns:
        해싱된 비밀번호 문자열
        
    사용 예시:
        hashed = hash_password("mypassword123")
        # 결과: $2b$12$KIXxJ... (매번 다른 값 생성)
    """
    # 1단계: SHA-256으로 먼저 해싱 (어떤 길이든 32바이트로 고정)
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    # 2단계: bcrypt로 최종 해싱 (hexdigest는 64자 문자열이므로 72바이트 이내)
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_hash.encode('utf-8'), salt)
    
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    평문 비밀번호와 해싱된 비밀번호를 비교합니다.
    
    hash_password와 동일한 방식으로 SHA-256을 먼저 적용한 후
    bcrypt로 검증합니다.
    
    Args:
        plain_password: 사용자가 입력한 평문 비밀번호
        hashed_password: 데이터베이스에 저장된 해싱된 비밀번호
        
    Returns:
        비밀번호가 일치하면 True, 아니면 False
        
    사용 예시:
        is_valid = verify_password("mypassword123", stored_hash)
    """
    # 1단계: SHA-256으로 먼저 해싱
    password_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    
    # 2단계: bcrypt로 검증
    return bcrypt.checkpw(password_hash.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT 액세스 토큰을 생성합니다.
    
    Args:
        data: 토큰에 포함할 데이터 (예: {"sub": "username"})
        expires_delta: 토큰 만료 시간 (기본값: 30분)
        
    Returns:
        생성된 JWT 토큰 문자열
        
    사용 예시:
        token = create_access_token({"sub": "john_doe"})
    """
    to_encode = data.copy()
    
    # 만료 시간 설정
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 토큰에 만료 시간 추가
    to_encode.update({"exp": expire})
    
    # JWT 토큰 생성
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """
    JWT 토큰을 검증하고 사용자 정보를 추출합니다.
    
    Args:
        token: 검증할 JWT 토큰
        
    Returns:
        토큰이 유효하면 사용자명(username), 아니면 None
        
    사용 예시:
        username = verify_token(token)
        if username:
            print(f"유효한 토큰: {username}")
    """
    try:
        # 토큰 디코딩
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            return None
            
        return username
    except JWTError:
        # 토큰이 유효하지 않거나 만료됨
        return None
