"""
ADMIN 권한 체크 의존성 함수
결제 관리 등 관리자 전용 기능에 사용
"""

from fastapi import Depends, HTTPException, status
from app.api.auth import get_current_user
from app.models.user import User, UserRole


async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    ADMIN 권한 체크 의존성 함수

    현재 로그인한 사용자가 ADMIN 권한을 가지고 있는지 확인합니다.

    Args:
        current_user: 현재 로그인한 사용자 (get_current_user 의존성)

    Returns:
        ADMIN 권한을 가진 사용자 객체

    Raises:
        403 Forbidden: ADMIN 권한이 없는 경우

    사용 예시:
        @router.get("/admin/payments")
        async def get_payments(
            admin_user: User = Depends(get_admin_user)
        ):
            # admin_user는 ADMIN 권한이 보장됨
            return {"message": "관리자 전용 페이지"}
    """
    if current_user.user_role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다. 현재 권한: " + current_user.user_role.value
        )

    return current_user


async def get_student_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    학생/학부모 권한 체크 의존성 함수

    STUDENT 역할이거나 연결된 학생이 있는 사용자만 허용합니다.

    Args:
        current_user: 현재 로그인한 사용자 (get_current_user 의존성)

    Returns:
        학생 권한을 가진 사용자 객체

    Raises:
        403 Forbidden: 학생/학부모 권한이 없는 경우

    사용 예시:
        @router.get("/student/dashboard")
        async def get_dashboard(
            student_user: User = Depends(get_student_user)
        ):
            # student_user는 학생/학부모 권한이 보장됨
            return {"message": "학생 대시보드"}
    """
    if current_user.user_role == UserRole.STUDENT:
        return current_user

    if hasattr(current_user, 'students') and current_user.students:
        return current_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="학생 또는 학부모 권한이 필요합니다"
    )
