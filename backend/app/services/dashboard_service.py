"""
대시보드 관련 비즈니스 로직
학원 운영 핵심 지표 조회 및 계산
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, extract
from app.models.user import User, UserRole
from app.models.student import Student
from app.models.attendance import Attendance, AttendanceStatus
from app.schemas.dashboard import (
    DashboardResponse, 
    SummaryStats, 
    AttendanceRate, 
    RecentActivity,
    RevenueTrend
)
from datetime import datetime, date, timedelta
from typing import List
import calendar


class DashboardService:
    """대시보드 관련 서비스 클래스"""
    
    @staticmethod
    def get_admin_dashboard(db: Session, academy_id: int) -> DashboardResponse:
        """
        관리자 대시보드 전체 통계 조회
        
        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            
        Returns:
            DashboardResponse: 대시보드 전체 데이터
        """
        # 1. 요약 통계
        summary = DashboardService._get_summary_stats(db, academy_id)
        
        # 2. 출석률
        attendance_rate = DashboardService._get_attendance_rate(db, academy_id)
        
        # 3. 최근 활동 내역
        recent_activities = DashboardService._get_recent_activities(db, academy_id)
        
        # 4. 매출 추이 (최근 6개월)
        revenue_trend = DashboardService._get_revenue_trend(db, academy_id)
        
        return DashboardResponse(
            summary=summary,
            attendance_rate=attendance_rate,
            recent_activities=recent_activities,
            revenue_trend=revenue_trend
        )
    
    @staticmethod
    def _get_summary_stats(db: Session, academy_id: int) -> SummaryStats:
        """전체 요약 통계 계산"""
        
        # 전체 수강생 수 (재원 중인 학생만)
        total_students = db.query(Student).filter(
            and_(
                Student.academy_id == academy_id,
                Student.status == "재원"
            )
        ).count()
        
        # 전체 강사 수 (TEACHER 역할)
        total_teachers = db.query(User).filter(
            and_(
                User.academy_id == academy_id,
                User.user_role == UserRole.TEACHER
            )
        ).count()
        
        # TODO: 이번 달 매출 (Payment 테이블 구현 후 실제 계산)
        # 현재는 더미 데이터로 계산 (학생 수 * 300,000원)
        monthly_revenue = total_students * 300000
        
        # TODO: 미납 총액 (Payment 테이블 구현 후 실제 계산)
        # 현재는 더미 데이터 (학생 수의 약 10%가 미납이라고 가정)
        unpaid_amount = int(total_students * 0.1 * 250000)
        
        return SummaryStats(
            total_students=total_students,
            total_teachers=total_teachers,
            monthly_revenue=monthly_revenue,
            unpaid_amount=unpaid_amount
        )
    
    @staticmethod
    def _get_attendance_rate(db: Session, academy_id: int) -> AttendanceRate:
        """출석률 계산"""
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # 오늘 출석률 계산
        today_rate = DashboardService._calculate_attendance_rate(db, academy_id, today)
        
        # 어제 출석률 계산
        yesterday_rate = DashboardService._calculate_attendance_rate(db, academy_id, yesterday)
        
        return AttendanceRate(
            today=today_rate,
            yesterday=yesterday_rate
        )
    
    @staticmethod
    def _calculate_attendance_rate(db: Session, academy_id: int, target_date: date) -> float:
        """특정 날짜의 출석률 계산"""
        
        # 해당 날짜의 전체 재원생 수
        total_students = db.query(Student).filter(
            and_(
                Student.academy_id == academy_id,
                Student.status == "재원"
            )
        ).count()
        
        if total_students == 0:
            return 0.0
        
        # 해당 날짜에 출석한 학생 수 (출석, 지각 포함)
        attended_count = db.query(Attendance).filter(
            and_(
                Attendance.academy_id == academy_id,
                Attendance.attendance_date == target_date,
                Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE])
            )
        ).count()
        
        # 출석률 계산 (소수점 첫째자리까지)
        rate = (attended_count / total_students) * 100
        return round(rate, 1)
    
    @staticmethod
    def _get_recent_activities(db: Session, academy_id: int, limit: int = 10) -> List[RecentActivity]:
        """최근 활동 내역 조회"""
        
        activities = []
        activity_id = 1
        
        # 1. 최근 신규 학생 등록 (최근 7일)
        recent_date = datetime.now() - timedelta(days=7)
        new_students = db.query(Student).filter(
            and_(
                Student.academy_id == academy_id,
                Student.regdate >= recent_date
            )
        ).order_by(Student.regdate.desc()).limit(5).all()
        
        for student in new_students:
            time_str = student.regdate.strftime("%I:%M %p") if student.regdate else ""
            activities.append(RecentActivity(
                id=activity_id,
                type="join",
                message=f"신규 학생({student.name}) 등록",
                time=time_str
            ))
            activity_id += 1
        
        # 2. 최근 출석 기록 (오늘)
        today = date.today()
        recent_attendance = db.query(Attendance).join(Student).filter(
            and_(
                Attendance.academy_id == academy_id,
                Attendance.attendance_date == today,
                Attendance.check_in_at.isnot(None)
            )
        ).order_by(Attendance.check_in_at.desc()).limit(5).all()
        
        for att in recent_attendance:
            student = att.student
            time_str = att.check_in_at.strftime("%I:%M %p") if att.check_in_at else ""
            activities.append(RecentActivity(
                id=activity_id,
                type="attendance",
                message=f"{student.name} 학생 등원",
                time=time_str
            ))
            activity_id += 1
        
        # TODO: Payment 테이블 구현 후 결제 내역 추가
        # 현재는 더미 데이터 추가
        if len(activities) < 5:
            activities.append(RecentActivity(
                id=activity_id,
                type="payment",
                message="김철수 학생 1월 수강료 납부",
                time="10:30 AM"
            ))
        
        # 시간순 정렬 및 제한
        return activities[:limit]
    
    @staticmethod
    def _get_revenue_trend(db: Session, academy_id: int, months: int = 6) -> List[RevenueTrend]:
        """최근 N개월 매출 추이"""
        
        trends = []
        current_date = datetime.now()
        
        # TODO: Payment 테이블 구현 후 실제 매출 데이터로 계산
        # 현재는 더미 데이터 생성
        
        total_students = db.query(Student).filter(
            and_(
                Student.academy_id == academy_id,
                Student.status == "재원"
            )
        ).count()
        
        # 최근 N개월 데이터 생성
        for i in range(months - 1, -1, -1):
            # N개월 전 날짜 계산
            target_date = current_date - timedelta(days=i * 30)
            month_str = target_date.strftime("%Y-%m")
            
            # 더미 매출 데이터 (학생 수 기반으로 약간의 변동 추가)
            base_amount = total_students * 300000
            # 월별로 약간의 변동 (-5% ~ +5%)
            variation = (i % 3 - 1) * 0.05  # -5%, 0%, +5% 순환
            amount = int(base_amount * (1 + variation))
            
            trends.append(RevenueTrend(
                month=month_str,
                amount=amount
            ))
        
        return trends
