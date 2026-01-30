"""
학생 포털 API 스키마 정의
학생용 대시보드, 출결, 수납, 스케줄, 성적 조회 응답 스키마
"""

from datetime import date, time, datetime
from typing import List, Optional
from pydantic import BaseModel


# ========== 출결 조회 ==========

class AttendanceRecord(BaseModel):
    """개별 출결 기록"""
    att_id: int
    attendance_date: date
    status: str  # 출석, 지각, 결석, 조퇴
    check_in_at: Optional[datetime] = None
    check_out_at: Optional[datetime] = None
    memo: Optional[str] = None


class AttendanceSummary(BaseModel):
    """출결 통계 요약"""
    present: int
    late: int
    early_leave: int
    absent: int
    total_class_days: int
    attendance_rate: float


class StudentAttendanceResponse(BaseModel):
    """학생 출결 조회 응답"""
    student_id: int
    student_name: str
    year: int
    month: int
    summary: AttendanceSummary
    records: List[AttendanceRecord]


# ========== 대시보드 ==========

class DashboardAttendance(BaseModel):
    """대시보드 출결 정보"""
    this_month_rate: float
    total_days: int
    present_days: int


class DashboardAssignments(BaseModel):
    """대시보드 과제 정보"""
    completion_rate: float
    total_count: int
    completed_count: int


class TodayClass(BaseModel):
    """오늘 수업 정보"""
    class_id: int
    class_name: str
    start_time: time
    end_time: time


class StudentDashboardResponse(BaseModel):
    """학생 대시보드 응답"""
    student_id: int
    student_name: str
    attendance: DashboardAttendance
    assignments: DashboardAssignments
    today_classes: List[TodayClass]


# ========== 수납 조회 ==========

class PaymentRecord(BaseModel):
    """결제/청구 기록"""
    invoice_id: Optional[int] = None
    payment_id: Optional[int] = None
    month: int
    amount: int
    description: Optional[str] = None
    status: str  # PENDING, SENT, PAID, OVERDUE, CANCELLED
    due_date: Optional[date] = None
    paid_at: Optional[datetime] = None


class MonthlyPaymentSummary(BaseModel):
    """월별 납부 요약"""
    month: int
    total_amount: int
    paid_amount: int
    unpaid_amount: int
    status: str  # 완납, 미납, 부분납


class StudentPaymentsResponse(BaseModel):
    """학생 수납 조회 응답"""
    student_id: int
    student_name: str
    year: int
    summary: dict  # total_paid, total_unpaid, payment_rate
    monthly: List[MonthlyPaymentSummary]
    records: List[PaymentRecord]


# ========== 스케줄 조회 ==========

class ScheduleEvent(BaseModel):
    """스케줄 이벤트"""
    event_id: str  # schedule_123 또는 assignment_456
    event_type: str  # class, assignment
    title: str
    date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    description: Optional[str] = None
    class_id: Optional[int] = None
    class_name: Optional[str] = None


class WeeklySchedule(BaseModel):
    """주간 정규 시간표"""
    day_of_week: str
    schedules: List[ScheduleEvent]


class StudentScheduleResponse(BaseModel):
    """학생 스케줄 조회 응답"""
    student_id: int
    student_name: str
    start_date: date
    end_date: date
    weekly_schedule: List[WeeklySchedule]
    events: List[ScheduleEvent]


# ========== 성적 조회 ==========

class GradeRecord(BaseModel):
    """성적 기록"""
    submission_id: int
    assignment_id: int
    assignment_title: str
    class_name: Optional[str] = None
    total_score: int
    max_score: int
    percentage: float
    submitted_at: Optional[datetime] = None
    graded_at: Optional[datetime] = None


class StudentGradesResponse(BaseModel):
    """학생 성적 조회 응답"""
    student_id: int
    student_name: str
    total_count: int
    average_percentage: float
    grades: List[GradeRecord]


# ========== 성적 분석 ==========

class MonthlyGradeAnalysis(BaseModel):
    """월별 성적 분석"""
    month: int
    year: int
    average_score: float
    total_assignments: int


class SubjectAnalysis(BaseModel):
    """과목별 성적 분석"""
    subject: str  # Class.name 활용
    average_score: float
    total_assignments: int
    recent_trend: str  # 상승, 하락, 유지


class GradeAnalysisResponse(BaseModel):
    """학생 성적 분석 응답"""
    student_id: int
    student_name: str
    period: str  # 3m, 6m, 1y
    overall_average: float
    monthly_trend: List[MonthlyGradeAnalysis]
    by_subject: List[SubjectAnalysis]


# ========== 과제 조회/제출 ==========

class StudentAssignmentItem(BaseModel):
    """과제 목록 항목"""
    assignment_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    class_name: Optional[str] = None
    status: str  # NOT_STARTED, IN_PROGRESS, SUBMITTED, GRADED
    submission_id: Optional[int] = None


class StudentAssignmentsResponse(BaseModel):
    """과제 목록 응답"""
    student_id: int
    student_name: str
    total_count: int
    assignments: List[StudentAssignmentItem]


class QuestionItem(BaseModel):
    """문제 항목 (과제 상세용)"""
    question_id: int
    question_number: int
    question_text: str
    question_type: str  # CHOICE, SHORT_ANSWER, ESSAY
    options: Optional[List[str]] = None
    points: int
    current_answer: Optional[str] = None


class StudentAssignmentDetailResponse(BaseModel):
    """과제 상세 응답"""
    assignment_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    class_name: Optional[str] = None
    status: str  # NOT_STARTED, IN_PROGRESS, SUBMITTED, GRADED
    submission_id: Optional[int] = None
    total_questions: int
    max_score: int
    questions: List[QuestionItem]


class AnswerSubmitItem(BaseModel):
    """답안 제출 항목"""
    question_id: int
    answer: str


class AssignmentSubmitRequest(BaseModel):
    """과제 제출 요청"""
    answers: List[AnswerSubmitItem]


class AssignmentSubmitResponse(BaseModel):
    """과제 제출 응답"""
    submission_id: int
    status: str
    submitted_at: datetime
    message: str
