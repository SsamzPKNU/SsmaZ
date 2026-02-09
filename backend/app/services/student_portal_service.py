"""
학생 포털 서비스
학생용 대시보드, 출결, 수납, 스케줄, 성적 조회 비즈니스 로직
"""

from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_
from calendar import monthrange

from app.models.user import User
from app.models.student import Student
from app.models.attendance import Attendance, AttendanceStatus
from app.services.attendance_service import get_display_status
from app.models.submission import Submission, SubmissionStatus, Answer
from app.models.assignment import Assignment, Question
from app.models.schedule import Schedule
from app.models.class_model import Class
from app.models.invoice import Invoice, InvoiceStatus
from app.models.payment import Payment, PaymentStatus


class StudentPortalService:
    """
    학생 포털 서비스

    주요 기능:
    - 학생 출결 조회
    - 학생 대시보드
    - 학생 수납 조회
    - 학생 스케줄 조회
    - 학생 성적 조회/분석
    """

    def __init__(self, db: Session):
        self.db = db

    def get_students_for_user(self, user: User) -> List[Student]:
        """사용자에게 연결된 학생 목록 조회"""
        students = self.db.query(Student).filter(
            Student.user_id == user.user_id
        ).all()
        return students

    def get_primary_student(self, user: User) -> Optional[Student]:
        """사용자에게 연결된 첫 번째 학생 반환"""
        students = self.get_students_for_user(user)
        return students[0] if students else None

    # ========== 출결 조회 ==========

    def get_attendance(
        self,
        user: User,
        year: Optional[int] = None,
        month: Optional[int] = None
    ) -> dict:
        """
        학생 출결 조회

        Args:
            user: 현재 로그인한 사용자
            year: 조회할 연도 (기본: 현재 연도)
            month: 조회할 월 (기본: 현재 월)

        Returns:
            출결 기록 및 통계
        """
        student = self.get_primary_student(user)
        if not student:
            return self._empty_attendance_response(year, month)

        today = date.today()
        year = year or today.year
        month = month or today.month

        # 해당 월의 출결 기록 조회
        records = self.db.query(Attendance).filter(
            Attendance.student_id == student.student_id,
            extract('year', Attendance.attendance_date) == year,
            extract('month', Attendance.attendance_date) == month
        ).order_by(Attendance.attendance_date.asc()).all()

        # 통계 계산
        present = sum(1 for r in records if r.status == AttendanceStatus.PRESENT)
        late = sum(1 for r in records if r.status == AttendanceStatus.LATE)
        early_leave = sum(1 for r in records if r.status == AttendanceStatus.EARLY_LEAVE)
        absent = sum(1 for r in records if r.status == AttendanceStatus.ABSENT)
        total_class_days = len(records)

        # 출석률 계산 (지각, 조퇴는 0.5로 계산)
        if total_class_days > 0:
            effective_present = present + (late * 0.5) + (early_leave * 0.5)
            attendance_rate = round((effective_present / total_class_days) * 100, 1)
        else:
            attendance_rate = 0.0

        return {
            "student_id": student.student_id,
            "student_name": student.name,
            "year": year,
            "month": month,
            "summary": {
                "present": present,
                "late": late,
                "early_leave": early_leave,
                "absent": absent,
                "total_class_days": total_class_days,
                "attendance_rate": attendance_rate
            },
            "records": [
                {
                    "att_id": r.att_id,
                    "attendance_date": r.attendance_date,
                    "status": get_display_status(r.status.value, r.check_out_at) if r.status else None,
                    "check_in_at": r.check_in_at,
                    "check_out_at": r.check_out_at,
                    "memo": r.memo
                }
                for r in records
            ]
        }

    def _empty_attendance_response(self, year: int, month: int) -> dict:
        """빈 출결 응답 생성"""
        today = date.today()
        return {
            "student_id": 0,
            "student_name": "",
            "year": year or today.year,
            "month": month or today.month,
            "summary": {
                "present": 0,
                "late": 0,
                "early_leave": 0,
                "absent": 0,
                "total_class_days": 0,
                "attendance_rate": 0.0
            },
            "records": []
        }

    # ========== 대시보드 ==========

    def get_dashboard(self, user: User) -> dict:
        """
        학생 대시보드 조회

        Returns:
            출결 통계, 과제 완료율, 오늘 수업 정보
        """
        student = self.get_primary_student(user)
        if not student:
            return self._empty_dashboard_response()

        today = date.today()

        # 이번 달 출결 통계
        attendance_stats = self._get_month_attendance_stats(student.student_id, today)

        # 과제 완료율 (최근 30일)
        assignment_stats = self._get_assignment_stats(student.student_id)

        # 오늘 수업
        today_classes = self._get_today_classes(student)

        return {
            "student_id": student.student_id,
            "student_name": student.name,
            "attendance": attendance_stats,
            "assignments": assignment_stats,
            "today_classes": today_classes
        }

    def _get_month_attendance_stats(self, student_id: int, today: date) -> dict:
        """이번 달 출결 통계"""
        records = self.db.query(Attendance).filter(
            Attendance.student_id == student_id,
            extract('year', Attendance.attendance_date) == today.year,
            extract('month', Attendance.attendance_date) == today.month
        ).all()

        total_days = len(records)
        present_days = sum(1 for r in records if r.status == AttendanceStatus.PRESENT)
        late_days = sum(1 for r in records if r.status == AttendanceStatus.LATE)
        early_leave_days = sum(1 for r in records if r.status == AttendanceStatus.EARLY_LEAVE)

        if total_days > 0:
            effective_present = present_days + (late_days * 0.5) + (early_leave_days * 0.5)
            rate = round((effective_present / total_days) * 100, 1)
        else:
            rate = 0.0

        return {
            "this_month_rate": rate,
            "total_days": total_days,
            "present_days": present_days
        }

    def _get_assignment_stats(self, student_id: int) -> dict:
        """과제 완료율 통계"""
        # 학생에게 할당된 과제 (최근 30일 또는 마감일 기준)
        thirty_days_ago = date.today() - timedelta(days=30)

        submissions = self.db.query(Submission).filter(
            Submission.student_id == student_id,
            Submission.created_at >= thirty_days_ago
        ).all()

        total_count = len(submissions)
        completed_count = sum(
            1 for s in submissions
            if s.status in [SubmissionStatus.SUBMITTED, SubmissionStatus.GRADED]
        )

        if total_count > 0:
            completion_rate = round((completed_count / total_count) * 100, 1)
        else:
            completion_rate = 0.0

        return {
            "completion_rate": completion_rate,
            "total_count": total_count,
            "completed_count": completed_count
        }

    def _get_today_classes(self, student: Student) -> List[dict]:
        """오늘 수업 목록"""
        if not student.class_id:
            return []

        # 오늘 요일
        today = date.today()
        weekday_map = {0: "월", 1: "화", 2: "수", 3: "목", 4: "금", 5: "토", 6: "일"}
        today_weekday = weekday_map[today.weekday()]

        # 해당 반의 오늘 스케줄 조회
        schedules = self.db.query(Schedule).join(Class).filter(
            Schedule.class_id == student.class_id,
            Schedule.day_of_week == today_weekday
        ).all()

        result = []
        for s in schedules:
            class_obj = self.db.query(Class).filter(
                Class.class_id == s.class_id
            ).first()

            if class_obj:
                result.append({
                    "class_id": class_obj.class_id,
                    "class_name": class_obj.name,
                    "start_time": s.start_time,
                    "end_time": s.end_time
                })

        return result

    def _empty_dashboard_response(self) -> dict:
        """빈 대시보드 응답"""
        return {
            "student_id": 0,
            "student_name": "",
            "attendance": {
                "this_month_rate": 0.0,
                "total_days": 0,
                "present_days": 0
            },
            "assignments": {
                "completion_rate": 0.0,
                "total_count": 0,
                "completed_count": 0
            },
            "today_classes": []
        }

    # ========== 수납 조회 ==========

    def get_payments(self, user: User, year: Optional[int] = None) -> dict:
        """
        학생 수납 조회

        Args:
            user: 현재 로그인한 사용자
            year: 조회할 연도 (기본: 현재 연도)

        Returns:
            월별 납부 현황 및 상세 기록
        """
        student = self.get_primary_student(user)
        if not student:
            return self._empty_payments_response(year)

        year = year or date.today().year

        # 청구서 조회
        invoices = self.db.query(Invoice).filter(
            Invoice.student_id == student.student_id,
            extract('year', Invoice.due_date) == year
        ).order_by(Invoice.due_date.asc()).all()

        # 월별 집계
        monthly_data = {}
        records = []
        total_paid = 0
        total_unpaid = 0

        for inv in invoices:
            month = inv.due_date.month

            if month not in monthly_data:
                monthly_data[month] = {
                    "month": month,
                    "total_amount": 0,
                    "paid_amount": 0,
                    "unpaid_amount": 0
                }

            monthly_data[month]["total_amount"] += inv.amount

            if inv.status == InvoiceStatus.PAID:
                monthly_data[month]["paid_amount"] += inv.amount
                total_paid += inv.amount
            else:
                monthly_data[month]["unpaid_amount"] += inv.amount
                total_unpaid += inv.amount

            records.append({
                "invoice_id": inv.invoice_id,
                "payment_id": inv.payment_id,
                "month": month,
                "amount": inv.amount,
                "description": inv.description,
                "status": inv.status.value if inv.status else None,
                "due_date": inv.due_date,
                "paid_at": inv.paid_at
            })

        # 월별 상태 결정
        monthly = []
        for month_num in sorted(monthly_data.keys()):
            data = monthly_data[month_num]
            if data["unpaid_amount"] == 0:
                status = "완납"
            elif data["paid_amount"] == 0:
                status = "미납"
            else:
                status = "부분납"

            monthly.append({
                "month": data["month"],
                "total_amount": data["total_amount"],
                "paid_amount": data["paid_amount"],
                "unpaid_amount": data["unpaid_amount"],
                "status": status
            })

        total_amount = total_paid + total_unpaid
        payment_rate = round((total_paid / total_amount) * 100, 1) if total_amount > 0 else 0.0

        return {
            "student_id": student.student_id,
            "student_name": student.name,
            "year": year,
            "summary": {
                "total_paid": total_paid,
                "total_unpaid": total_unpaid,
                "payment_rate": payment_rate
            },
            "monthly": monthly,
            "records": records
        }

    def _empty_payments_response(self, year: int) -> dict:
        """빈 수납 응답"""
        return {
            "student_id": 0,
            "student_name": "",
            "year": year or date.today().year,
            "summary": {
                "total_paid": 0,
                "total_unpaid": 0,
                "payment_rate": 0.0
            },
            "monthly": [],
            "records": []
        }

    # ========== 스케줄 조회 ==========

    def get_schedule(
        self,
        user: User,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        event_type: str = "all"
    ) -> dict:
        """
        학생 스케줄 조회

        Args:
            user: 현재 로그인한 사용자
            start_date: 시작일 (기본: 오늘)
            end_date: 종료일 (기본: 30일 후)
            event_type: 이벤트 유형 (all, assignment)

        Returns:
            주간 시간표 및 이벤트 목록
        """
        student = self.get_primary_student(user)
        if not student:
            return self._empty_schedule_response(start_date, end_date)

        today = date.today()
        start_date = start_date or today
        end_date = end_date or (today + timedelta(days=30))

        # 주간 정규 시간표
        weekly_schedule = self._get_weekly_schedule(student)

        # 기간 내 이벤트 (과제 마감일 등)
        events = self._get_schedule_events(student, start_date, end_date, event_type)

        return {
            "student_id": student.student_id,
            "student_name": student.name,
            "start_date": start_date,
            "end_date": end_date,
            "weekly_schedule": weekly_schedule,
            "events": events
        }

    def _get_weekly_schedule(self, student: Student) -> List[dict]:
        """주간 정규 시간표"""
        if not student.class_id:
            return []

        schedules = self.db.query(Schedule).filter(
            Schedule.class_id == student.class_id
        ).order_by(Schedule.start_time.asc()).all()

        # 요일별 그룹화
        weekday_order = ["월", "화", "수", "목", "금", "토", "일"]
        by_day = {day: [] for day in weekday_order}

        for s in schedules:
            class_obj = self.db.query(Class).filter(
                Class.class_id == s.class_id
            ).first()

            if s.day_of_week in by_day:
                by_day[s.day_of_week].append({
                    "event_id": f"schedule_{s.schedule_id}",
                    "event_type": "class",
                    "title": class_obj.name if class_obj else "수업",
                    "date": None,  # 정규 시간표는 날짜 없음
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "description": None,
                    "class_id": s.class_id,
                    "class_name": class_obj.name if class_obj else None
                })

        return [
            {"day_of_week": day, "schedules": by_day[day]}
            for day in weekday_order
            if by_day[day]
        ]

    def _get_schedule_events(
        self,
        student: Student,
        start_date: date,
        end_date: date,
        event_type: str
    ) -> List[dict]:
        """기간 내 이벤트 조회"""
        events = []

        # 과제 마감일
        if event_type in ["all", "assignment"]:
            assignments_query = self.db.query(Assignment).filter(
                Assignment.due_date >= start_date,
                Assignment.due_date <= end_date,
                Assignment.is_active == True
            )

            # 반 과제 또는 개인 과제
            if student.class_id:
                assignments_query = assignments_query.filter(
                    (Assignment.class_id == student.class_id) |
                    (Assignment.class_id.is_(None))
                )

            assignments = assignments_query.order_by(Assignment.due_date.asc()).all()

            for a in assignments:
                class_obj = None
                if a.class_id:
                    class_obj = self.db.query(Class).filter(
                        Class.class_id == a.class_id
                    ).first()

                events.append({
                    "event_id": f"assignment_{a.assignment_id}",
                    "event_type": "assignment",
                    "title": a.title,
                    "date": a.due_date,
                    "start_time": None,
                    "end_time": None,
                    "description": a.description,
                    "class_id": a.class_id,
                    "class_name": class_obj.name if class_obj else None
                })

        return events

    def _empty_schedule_response(self, start_date: date, end_date: date) -> dict:
        """빈 스케줄 응답"""
        today = date.today()
        return {
            "student_id": 0,
            "student_name": "",
            "start_date": start_date or today,
            "end_date": end_date or (today + timedelta(days=30)),
            "weekly_schedule": [],
            "events": []
        }

    # ========== 성적 조회 ==========

    def get_grades(
        self,
        user: User,
        subject: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> dict:
        """
        학생 성적 조회

        Args:
            user: 현재 로그인한 사용자
            subject: 과목명 필터 (선택)
            start_date: 시작일 (선택)
            end_date: 종료일 (선택)

        Returns:
            채점 완료된 성적 목록
        """
        student = self.get_primary_student(user)
        if not student:
            return self._empty_grades_response()

        # 채점 완료된 제출물 조회
        query = self.db.query(Submission).join(Assignment).filter(
            Submission.student_id == student.student_id,
            Submission.status == SubmissionStatus.GRADED
        )

        if start_date:
            query = query.filter(Submission.graded_at >= start_date)
        if end_date:
            query = query.filter(Submission.graded_at <= end_date)

        submissions = query.order_by(Submission.graded_at.desc()).all()

        grades = []
        total_percentage = 0.0

        for sub in submissions:
            assignment = sub.assignment

            # 과목 필터 (Class.name 활용)
            class_name = None
            if assignment.class_id:
                class_obj = self.db.query(Class).filter(
                    Class.class_id == assignment.class_id
                ).first()
                class_name = class_obj.name if class_obj else None

            if subject and class_name and subject.lower() not in class_name.lower():
                continue

            percentage = round((sub.total_score / sub.max_score) * 100, 1) if sub.max_score > 0 else 0.0
            total_percentage += percentage

            grades.append({
                "submission_id": sub.submission_id,
                "assignment_id": assignment.assignment_id,
                "assignment_title": assignment.title,
                "class_name": class_name,
                "total_score": sub.total_score,
                "max_score": sub.max_score,
                "percentage": percentage,
                "submitted_at": sub.submitted_at,
                "graded_at": sub.graded_at
            })

        total_count = len(grades)
        average_percentage = round(total_percentage / total_count, 1) if total_count > 0 else 0.0

        return {
            "student_id": student.student_id,
            "student_name": student.name,
            "total_count": total_count,
            "average_percentage": average_percentage,
            "grades": grades
        }

    def _empty_grades_response(self) -> dict:
        """빈 성적 응답"""
        return {
            "student_id": 0,
            "student_name": "",
            "total_count": 0,
            "average_percentage": 0.0,
            "grades": []
        }

    # ========== 성적 분석 ==========

    def get_grade_analysis(self, user: User, period: str = "3m") -> dict:
        """
        학생 성적 분석

        Args:
            user: 현재 로그인한 사용자
            period: 분석 기간 (3m, 6m, 1y)

        Returns:
            월별 추이, 과목별 분석
        """
        student = self.get_primary_student(user)
        if not student:
            return self._empty_analysis_response(period)

        # 기간 계산
        today = date.today()
        if period == "3m":
            start_date = today - timedelta(days=90)
        elif period == "6m":
            start_date = today - timedelta(days=180)
        else:  # 1y
            start_date = today - timedelta(days=365)

        # 채점 완료된 제출물 조회
        submissions = self.db.query(Submission).join(Assignment).filter(
            Submission.student_id == student.student_id,
            Submission.status == SubmissionStatus.GRADED,
            Submission.graded_at >= start_date
        ).all()

        # 월별 분석
        monthly_data = {}
        subject_data = {}
        total_percentage = 0.0

        for sub in submissions:
            if not sub.graded_at:
                continue

            year = sub.graded_at.year
            month = sub.graded_at.month
            key = (year, month)

            percentage = round((sub.total_score / sub.max_score) * 100, 1) if sub.max_score > 0 else 0.0
            total_percentage += percentage

            # 월별 집계
            if key not in monthly_data:
                monthly_data[key] = {"total": 0.0, "count": 0}
            monthly_data[key]["total"] += percentage
            monthly_data[key]["count"] += 1

            # 과목별 집계 (Class.name 활용)
            assignment = sub.assignment
            subject_name = "기타"
            if assignment.class_id:
                class_obj = self.db.query(Class).filter(
                    Class.class_id == assignment.class_id
                ).first()
                if class_obj:
                    subject_name = class_obj.name

            if subject_name not in subject_data:
                subject_data[subject_name] = {"scores": [], "count": 0}
            subject_data[subject_name]["scores"].append(percentage)
            subject_data[subject_name]["count"] += 1

        # 월별 추이 생성
        monthly_trend = []
        for (year, month), data in sorted(monthly_data.items()):
            avg = round(data["total"] / data["count"], 1) if data["count"] > 0 else 0.0
            monthly_trend.append({
                "month": month,
                "year": year,
                "average_score": avg,
                "total_assignments": data["count"]
            })

        # 과목별 분석 생성
        by_subject = []
        for subject_name, data in subject_data.items():
            scores = data["scores"]
            avg = round(sum(scores) / len(scores), 1) if scores else 0.0

            # 추세 계산 (최근 3개 vs 이전 3개)
            if len(scores) >= 6:
                recent = sum(scores[-3:]) / 3
                earlier = sum(scores[-6:-3]) / 3
                if recent > earlier + 5:
                    trend = "상승"
                elif recent < earlier - 5:
                    trend = "하락"
                else:
                    trend = "유지"
            else:
                trend = "유지"

            by_subject.append({
                "subject": subject_name,
                "average_score": avg,
                "total_assignments": data["count"],
                "recent_trend": trend
            })

        total_count = len(submissions)
        overall_average = round(total_percentage / total_count, 1) if total_count > 0 else 0.0

        return {
            "student_id": student.student_id,
            "student_name": student.name,
            "period": period,
            "overall_average": overall_average,
            "monthly_trend": monthly_trend,
            "by_subject": by_subject
        }

    def _empty_analysis_response(self, period: str) -> dict:
        """빈 성적 분석 응답"""
        return {
            "student_id": 0,
            "student_name": "",
            "period": period,
            "overall_average": 0.0,
            "monthly_trend": [],
            "by_subject": []
        }

    # ========== 과제 조회/제출 ==========

    def get_assignments(self, user: User, status: Optional[str] = None) -> dict:
        """
        학생 과제 목록 조회

        Args:
            user: 현재 로그인한 사용자
            status: 필터 (remaining: 미완료, completed: 완료)

        Returns:
            과제 목록
        """
        student = self.get_primary_student(user)
        if not student:
            return self._empty_assignments_response()

        # 학생에게 할당된 과제 조회
        assignments_query = self.db.query(Assignment).filter(
            Assignment.is_active == True
        )

        # 반 과제 또는 개인 과제
        if student.class_id:
            assignments_query = assignments_query.filter(
                (Assignment.class_id == student.class_id) |
                (Assignment.class_id.is_(None))
            )

        assignments = assignments_query.order_by(Assignment.due_date.desc()).all()

        result_assignments = []
        for assignment in assignments:
            # 해당 과제에 대한 제출 기록 확인
            submission = self.db.query(Submission).filter(
                Submission.assignment_id == assignment.assignment_id,
                Submission.student_id == student.student_id
            ).first()

            # 상태 결정
            if submission:
                if submission.status == SubmissionStatus.GRADED:
                    assignment_status = "GRADED"
                elif submission.status == SubmissionStatus.SUBMITTED:
                    assignment_status = "SUBMITTED"
                else:
                    assignment_status = "IN_PROGRESS"
            else:
                assignment_status = "NOT_STARTED"

            # 필터 적용
            if status == "remaining" and assignment_status in ["SUBMITTED", "GRADED"]:
                continue
            if status == "completed" and assignment_status not in ["SUBMITTED", "GRADED"]:
                continue

            # 클래스명 조회
            class_name = None
            if assignment.class_id:
                class_obj = self.db.query(Class).filter(
                    Class.class_id == assignment.class_id
                ).first()
                class_name = class_obj.name if class_obj else None

            result_assignments.append({
                "assignment_id": assignment.assignment_id,
                "title": assignment.title,
                "description": assignment.description,
                "due_date": assignment.due_date,
                "class_name": class_name,
                "status": assignment_status,
                "submission_id": submission.submission_id if submission else None
            })

        return {
            "student_id": student.student_id,
            "student_name": student.name,
            "total_count": len(result_assignments),
            "assignments": result_assignments
        }

    def get_assignment_detail(self, user: User, assignment_id: int) -> Optional[dict]:
        """
        과제 상세 조회

        Args:
            user: 현재 로그인한 사용자
            assignment_id: 과제 ID

        Returns:
            과제 상세 정보 (문제 포함)
        """
        student = self.get_primary_student(user)
        if not student:
            return None

        # 과제 조회
        assignment = self.db.query(Assignment).filter(
            Assignment.assignment_id == assignment_id,
            Assignment.is_active == True
        ).first()

        if not assignment:
            return None

        # 학생이 접근 가능한 과제인지 확인
        if assignment.class_id and student.class_id != assignment.class_id:
            return None

        # 제출 기록 확인
        submission = self.db.query(Submission).filter(
            Submission.assignment_id == assignment_id,
            Submission.student_id == student.student_id
        ).first()

        # 상태 결정
        if submission:
            if submission.status == SubmissionStatus.GRADED:
                status = "GRADED"
            elif submission.status == SubmissionStatus.SUBMITTED:
                status = "SUBMITTED"
            else:
                status = "IN_PROGRESS"
        else:
            status = "NOT_STARTED"

        # 클래스명 조회
        class_name = None
        if assignment.class_id:
            class_obj = self.db.query(Class).filter(
                Class.class_id == assignment.class_id
            ).first()
            class_name = class_obj.name if class_obj else None

        # 문제 목록 조회
        questions = self.db.query(Question).filter(
            Question.assignment_id == assignment_id
        ).order_by(Question.question_number.asc()).all()

        # 기존 답안 조회 (제출 기록이 있는 경우)
        answers_map = {}
        if submission:
            answers = self.db.query(Answer).filter(
                Answer.submission_id == submission.submission_id
            ).all()
            answers_map = {a.question_id: a.student_answer for a in answers}

        question_list = []
        max_score = 0
        for q in questions:
            max_score += q.points
            question_list.append({
                "question_id": q.question_id,
                "question_number": q.question_number,
                "question_text": q.question_text,
                "question_type": q.question_type.value if q.question_type else "CHOICE",
                "options": q.options,
                "points": q.points,
                "current_answer": answers_map.get(q.question_id)
            })

        return {
            "assignment_id": assignment.assignment_id,
            "title": assignment.title,
            "description": assignment.description,
            "due_date": assignment.due_date,
            "class_name": class_name,
            "status": status,
            "submission_id": submission.submission_id if submission else None,
            "total_questions": len(questions),
            "max_score": max_score,
            "questions": question_list
        }

    def submit_assignment(
        self,
        user: User,
        assignment_id: int,
        answers: List[dict]
    ) -> Optional[dict]:
        """
        과제 제출

        Args:
            user: 현재 로그인한 사용자
            assignment_id: 과제 ID
            answers: 답안 목록 [{"question_id": 1, "answer": "답"}]

        Returns:
            제출 결과
        """
        student = self.get_primary_student(user)
        if not student:
            return None

        # 과제 조회
        assignment = self.db.query(Assignment).filter(
            Assignment.assignment_id == assignment_id,
            Assignment.is_active == True
        ).first()

        if not assignment:
            return None

        # 학생이 접근 가능한 과제인지 확인
        if assignment.class_id and student.class_id != assignment.class_id:
            return None

        # 기존 제출 기록 확인 또는 생성
        submission = self.db.query(Submission).filter(
            Submission.assignment_id == assignment_id,
            Submission.student_id == student.student_id
        ).first()

        # 이미 제출 완료된 경우
        if submission and submission.status in [SubmissionStatus.SUBMITTED, SubmissionStatus.GRADED]:
            return {
                "submission_id": submission.submission_id,
                "status": submission.status.value,
                "submitted_at": submission.submitted_at,
                "message": "이미 제출된 과제입니다."
            }

        now = datetime.now()

        if not submission:
            # 새 제출 기록 생성
            # max_score 계산
            questions = self.db.query(Question).filter(
                Question.assignment_id == assignment_id
            ).all()
            max_score = sum(q.points for q in questions)

            submission = Submission(
                assignment_id=assignment_id,
                student_id=student.student_id,
                status=SubmissionStatus.SUBMITTED,
                total_score=0,
                max_score=max_score,
                submitted_at=now
            )
            self.db.add(submission)
            self.db.flush()  # submission_id 생성
        else:
            # 기존 제출 기록 업데이트
            submission.status = SubmissionStatus.SUBMITTED
            submission.submitted_at = now

        # 답안 저장/업데이트
        for answer_data in answers:
            question_id = answer_data.get("question_id")
            student_answer = answer_data.get("answer")

            # 기존 답안 확인
            existing_answer = self.db.query(Answer).filter(
                Answer.submission_id == submission.submission_id,
                Answer.question_id == question_id
            ).first()

            if existing_answer:
                existing_answer.student_answer = student_answer
            else:
                new_answer = Answer(
                    submission_id=submission.submission_id,
                    question_id=question_id,
                    student_answer=student_answer,
                    is_correct=None,
                    points_earned=0
                )
                self.db.add(new_answer)

        self.db.commit()

        return {
            "submission_id": submission.submission_id,
            "status": submission.status.value,
            "submitted_at": submission.submitted_at,
            "message": "과제가 성공적으로 제출되었습니다."
        }

    def _empty_assignments_response(self) -> dict:
        """빈 과제 목록 응답"""
        return {
            "student_id": 0,
            "student_name": "",
            "total_count": 0,
            "assignments": []
        }
