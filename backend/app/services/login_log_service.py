"""
로그인 로그 관련 서비스
로그인 시도 기록 및 조회 기능 제공

** 기존 login_logs 테이블 구조에 맞춰 구현됨 **
"""

from sqlalchemy.orm import Session
from app.models.login_log import LoginLog, LoginStatus
from app.models.user import User
from typing import Optional, List
from datetime import datetime, timedelta


class LoginLogService:
    """로그인 로그 관련 서비스 클래스"""
    
    @staticmethod
    def create_log(
        db: Session,
        user_id: Optional[int],
        status: LoginStatus,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        failure_reason: Optional[str] = None
    ) -> LoginLog:
        """
        로그인 로그 생성
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            status: 로그인 상태 (SUCCESS/FAIL)
            ip_address: 클라이언트 IP
            user_agent: 클라이언트 정보
            failure_reason: 실패 사유
            
        Returns:
            생성된 LoginLog 객체
        """
        log = LoginLog(
            user_id=user_id,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason=failure_reason
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        return log
    
    @staticmethod
    def log_success(
        db: Session,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> LoginLog:
        """
        로그인 성공 로그 생성
        
        Args:
            db: 데이터베이스 세션
            user: 로그인한 사용자
            ip_address: 클라이언트 IP
            user_agent: 클라이언트 정보
            
        Returns:
            생성된 LoginLog 객체
        """
        return LoginLogService.create_log(
            db=db,
            user_id=user.user_id,
            status=LoginStatus.SUCCESS,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_failure(
        db: Session,
        user_id: Optional[int],
        failure_reason: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> LoginLog:
        """
        로그인 실패 로그 생성
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID (알 수 없으면 None)
            failure_reason: 실패 사유 (USER_NOT_FOUND, WRONG_PASSWORD 등)
            ip_address: 클라이언트 IP
            user_agent: 클라이언트 정보
            
        Returns:
            생성된 LoginLog 객체
        """
        return LoginLogService.create_log(
            db=db,
            user_id=user_id,
            status=LoginStatus.FAIL,
            failure_reason=failure_reason,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def get_recent_logs_by_user(
        db: Session,
        user_id: int,
        limit: int = 10
    ) -> List[LoginLog]:
        """
        특정 사용자의 최근 로그인 로그 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 조회할 user_id
            limit: 조회할 로그 수
            
        Returns:
            LoginLog 목록
        """
        return db.query(LoginLog).filter(
            LoginLog.user_id == user_id
        ).order_by(
            LoginLog.login_time.desc()
        ).limit(limit).all()
    
    @staticmethod
    def get_failed_attempts_count(
        db: Session,
        user_id: int,
        minutes: int = 30
    ) -> int:
        """
        최근 N분간 로그인 실패 횟수 조회
        
        계정 잠금 로직에 사용할 수 있습니다.
        
        Args:
            db: 데이터베이스 세션
            user_id: 조회할 user_id
            minutes: 조회할 시간 범위 (분)
            
        Returns:
            실패 횟수
        """
        since = datetime.utcnow() - timedelta(minutes=minutes)
        
        return db.query(LoginLog).filter(
            LoginLog.user_id == user_id,
            LoginLog.status == LoginStatus.FAIL,
            LoginLog.login_time >= since
        ).count()
    
    @staticmethod
    def get_recent_logs_by_ip(
        db: Session,
        ip_address: str,
        limit: int = 20
    ) -> List[LoginLog]:
        """
        특정 IP의 최근 로그인 로그 조회
        
        의심스러운 IP 활동 감지에 사용됩니다.
        
        Args:
            db: 데이터베이스 세션
            ip_address: 조회할 IP 주소
            limit: 조회할 로그 수
            
        Returns:
            LoginLog 목록
        """
        return db.query(LoginLog).filter(
            LoginLog.ip_address == ip_address
        ).order_by(
            LoginLog.login_time.desc()
        ).limit(limit).all()
    
    @staticmethod
    def log_logout(
        db: Session,
        user_id: int
    ) -> Optional[LoginLog]:
        """
        로그아웃 로그 기록
        
        가장 최근 성공한 로그인 로그를 찾아서
        logout_time과 session_duration을 업데이트합니다.
        
        Args:
            db: 데이터베이스 세션
            user_id: 로그아웃하는 사용자 ID
            
        Returns:
            업데이트된 LoginLog 객체 또는 None
        """
        # 가장 최근 성공한 로그인 로그 찾기 (아직 로그아웃 안 한 것)
        login_log = db.query(LoginLog).filter(
            LoginLog.user_id == user_id,
            LoginLog.status == LoginStatus.SUCCESS,
            LoginLog.logout_time == None  # 아직 로그아웃 안 함
        ).order_by(
            LoginLog.login_time.desc()
        ).first()
        
        if not login_log:
            return None
        
        # 로그아웃 시간 및 세션 지속 시간 계산
        logout_time = datetime.utcnow()
        
        # session_duration 계산 (초 단위)
        if login_log.login_time:
            session_duration = int((logout_time - login_log.login_time).total_seconds())
        else:
            session_duration = 0
        
        # 로그 업데이트
        login_log.logout_time = logout_time
        login_log.session_duration = session_duration
        
        db.commit()
        db.refresh(login_log)
        
        return login_log
    
    @staticmethod
    def get_active_sessions(
        db: Session,
        user_id: int
    ) -> List[LoginLog]:
        """
        활성 세션 조회 (로그아웃하지 않은 로그인)
        
        Args:
            db: 데이터베이스 세션
            user_id: 조회할 user_id
            
        Returns:
            활성 세션 목록
        """
        return db.query(LoginLog).filter(
            LoginLog.user_id == user_id,
            LoginLog.status == LoginStatus.SUCCESS,
            LoginLog.logout_time == None
        ).order_by(
            LoginLog.login_time.desc()
        ).all()
