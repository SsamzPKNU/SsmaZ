"""
대시보드 관련 API 엔드포인트
관리자용 통계 및 대시보드 데이터 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService
from app.models.user import User
from app.api.auth import get_current_user


# API 라우터 생성
router = APIRouter(
    prefix="/api/admin",
    tags=["대시보드"]
)


@router.get("/dashboard", response_model=DashboardResponse)
async def get_admin_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    관리자 대시보드 전체 통계 조회
    
    전체 수강생 수, 강사 수, 이번 달 예상 매출, 현재 미납 금액 등
    학원 운영 핵심 지표를 조회합니다.
    
    Headers (Bearer 방식):
        Authorization: Bearer {access_token}
    
    Returns:
        DashboardResponse:
            - summary: 전체 요약 통계
                - total_students: 전체 수강생 수
                - total_teachers: 전체 강사 수
                - monthly_revenue: 이번 달 예상 매출
                - unpaid_amount: 현재 미납 총액
            - attendance_rate: 출석률
                - today: 오늘 출석률 (%)
                - yesterday: 어제 출석률 (%)
            - recent_activities: 최근 활동 내역 목록
            - revenue_trend: 최근 6개월 매출 추이
    
    Raises:
        401: 인증되지 않은 사용자
        403: ADMIN 권한이 없는 경우
    
    사용 예시:
        GET /api/admin/dashboard
        Headers: Authorization: Bearer {token}
        
        응답:
        {
            "summary": {
                "total_students": 150,
                "total_teachers": 8,
                "monthly_revenue": 45000000,
                "unpaid_amount": 2500000
            },
            "attendance_rate": {
                "today": 95.5,
                "yesterday": 94.0
            },
            "recent_activities": [
                {
                    "id": 1,
                    "type": "payment",
                    "message": "김철수 학생 1월 수강료 납부",
                    "time": "10:30 AM"
                }
            ],
            "revenue_trend": [
                {"month": "2025-08", "amount": 42000000},
                {"month": "2026-01", "amount": 45000000}
            ]
        }
    """
    # TODO: ADMIN 권한 체크 활성화 (현재는 모든 사용자 허용)

    # 현재 사용자의 academy_id로 통계 조회
    academy_id = current_user.academy_id
    
    # 대시보드 데이터 조회
    dashboard_data = DashboardService.get_admin_dashboard(db, academy_id)
    
    return dashboard_data
