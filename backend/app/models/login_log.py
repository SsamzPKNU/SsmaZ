"""
로그인 로그 모델 정의
로그인/로그아웃 시도 기록을 저장하는 테이블

** 기존 login_logs 테이블 구조에 맞춰 정의됨 **
"""

from sqlalchemy import Column, Integer, String, Enum, TIMESTAMP, ForeignKey, Text
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class LoginStatus(str, enum.Enum):
    """로그인 상태"""
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"


class LoginLog(Base):
    """
    로그인 로그 테이블
    
    기존 테이블 구조:
    - log_id: INT(11), PK, auto_increment
    - user_id: INT(11), FK
    - login_time: TIMESTAMP
    - ip_address: VARCHAR(45)
    - status: ENUM('SUCCESS','FAIL')
    - user_agent: TEXT
    - failure_reason: VARCHAR(255)
    - logout_time: TIMESTAMP (로그아웃 시간)
    - session_duration: INT(11) (세션 지속 시간, 초)
    """
    __tablename__ = "login_logs"
    
    # 기본 키
    log_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="로그 고유 ID"
    )
    
    # 사용자 ID (외래 키)
    user_id = Column(
        Integer,
        ForeignKey('Users.user_id', ondelete='SET NULL'),
        nullable=True,
        comment="로그인한 사용자 ID"
    )
    
    # 로그인 시간
    login_time = Column(
        TIMESTAMP,
        server_default=func.now(),
        nullable=False,
        comment="로그인 시간"
    )
    
    # 클라이언트 IP
    ip_address = Column(
        String(45),
        nullable=True,
        comment="클라이언트 IP 주소"
    )
    
    # 로그인 상태 (SUCCESS/FAIL)
    status = Column(
        Enum(LoginStatus),
        nullable=False,
        comment="로그인 상태"
    )
    
    # 브라우저/클라이언트 정보
    user_agent = Column(
        Text,
        nullable=True,
        comment="브라우저/클라이언트 정보"
    )
    
    # 실패 사유
    failure_reason = Column(
        String(255),
        nullable=True,
        comment="실패 사유"
    )
    
    # 로그아웃 시간
    logout_time = Column(
        TIMESTAMP,
        nullable=True,
        comment="로그아웃 시간"
    )
    
    # 세션 지속 시간 (초)
    session_duration = Column(
        Integer,
        nullable=True,
        comment="세션 지속 시간 (초)"
    )
    
    def __repr__(self):
        """객체를 문자열로 표현 (디버깅용)"""
        return f"<LoginLog(log_id={self.log_id}, user_id={self.user_id}, status={self.status}, login_time={self.login_time})>"
