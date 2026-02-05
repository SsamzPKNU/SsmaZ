"""
관리자용 학생 성적/과제 조회 서비스
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_, or_
from typing import Optional, Tuple, List, Dict, Any
from datetime import date

from app.models.submission import Submission, SubmissionStatus
from app.models.assignment import Assignment
from app.models.student import Student
from app.models.class_model import Class
from app.models.user import User


class AdminGradeService:
    """관리자용 성적/과제 조회 서비스"""

    @staticmethod
    def get_student_grades(
        db: Session,
        academy_id: int,
        student_id: Optional[int] = None,
        class_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int, Dict[str, Any]]:
        """
        학생 성적 조회

        Args:
            db: DB 세션
            academy_id: 학원 ID
            student_id: 학생 ID 필터 (선택)
            class_id: 반 ID 필터 (선택)
            start_date: 시작일 필터 (선택)
            end_date: 종료일 필터 (선택)
            page: 페이지 번호
            limit: 페이지당 항목 수

        Returns:
            (성적 목록, 전체 개수, 통계)
        """
        # 기본 쿼리: Submission JOIN Assignment JOIN Student
        query = (
            db.query(
                Submission,
                Assignment.title.label("assignment_title"),
                Assignment.assignment_id,
                Student.student_id,
                Student.name.label("student_name"),
                Student.class_id,
                Class.class_name
            )
            .join(Assignment, Submission.assignment_id == Assignment.assignment_id)
            .join(Student, Submission.student_id == Student.student_id)
            .outerjoin(Class, Student.class_id == Class.class_id)
            .filter(Assignment.academy_id == academy_id)
        )

        # 필터 적용
        if student_id:
            query = query.filter(Student.student_id == student_id)
        if class_id:
            query = query.filter(Student.class_id == class_id)
        if start_date:
            query = query.filter(Submission.submitted_at >= start_date)
        if end_date:
            query = query.filter(Submission.submitted_at <= end_date)

        # 전체 개수
        total = query.count()

        # 통계 계산 (채점 완료된 것만)
        stats_query = (
            db.query(
                func.count(Submission.submission_id).label("total_count"),
                func.avg(
                    case(
                        (Submission.max_score > 0,
                         Submission.total_score * 100.0 / Submission.max_score),
                        else_=0
                    )
                ).label("avg_percentage"),
                func.max(
                    case(
                        (Submission.max_score > 0,
                         Submission.total_score * 100.0 / Submission.max_score),
                        else_=0
                    )
                ).label("max_percentage"),
                func.min(
                    case(
                        (Submission.max_score > 0,
                         Submission.total_score * 100.0 / Submission.max_score),
                        else_=0
                    )
                ).label("min_percentage")
            )
            .join(Assignment, Submission.assignment_id == Assignment.assignment_id)
            .join(Student, Submission.student_id == Student.student_id)
            .filter(Assignment.academy_id == academy_id)
            .filter(Submission.status == SubmissionStatus.GRADED)
        )

        if student_id:
            stats_query = stats_query.filter(Student.student_id == student_id)
        if class_id:
            stats_query = stats_query.filter(Student.class_id == class_id)

        stats_result = stats_query.first()

        stats = {
            "total_count": stats_result.total_count or 0,
            "average_percentage": round(stats_result.avg_percentage or 0, 1),
            "highest_percentage": round(stats_result.max_percentage or 0, 1),
            "lowest_percentage": round(stats_result.min_percentage or 0, 1)
        }

        # 페이지네이션 및 정렬
        offset = (page - 1) * limit
        results = (
            query
            .order_by(Submission.submitted_at.desc().nullslast())
            .offset(offset)
            .limit(limit)
            .all()
        )

        # 결과 변환
        records = []
        for row in results:
            submission = row[0]
            percentage = (
                round(submission.total_score * 100 / submission.max_score, 1)
                if submission.max_score > 0 else 0
            )
            records.append({
                "submission_id": submission.submission_id,
                "student_id": row.student_id,
                "student_name": row.student_name,
                "class_id": row.class_id,
                "class_name": row.class_name,
                "assignment_id": row.assignment_id,
                "assignment_title": row.assignment_title,
                "total_score": submission.total_score,
                "max_score": submission.max_score,
                "percentage": percentage,
                "status": submission.status.value,
                "submitted_at": submission.submitted_at,
                "graded_at": submission.graded_at
            })

        return records, total, stats

    @staticmethod
    def get_assignments_overview(
        db: Session,
        academy_id: int,
        class_id: Optional[int] = None,
        teacher_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int, Dict[str, Any]]:
        """
        과제 현황 조회

        Args:
            db: DB 세션
            academy_id: 학원 ID
            class_id: 반 ID 필터 (선택)
            teacher_id: 선생님 ID 필터 (선택)
            is_active: 활성 여부 필터 (선택)
            page: 페이지 번호
            limit: 페이지당 항목 수

        Returns:
            (과제 목록, 전체 개수, 통계)
        """
        # 기본 쿼리
        query = (
            db.query(Assignment)
            .filter(Assignment.academy_id == academy_id)
        )

        if class_id:
            query = query.filter(Assignment.class_id == class_id)
        if teacher_id:
            query = query.filter(Assignment.teacher_id == teacher_id)
        if is_active is not None:
            query = query.filter(Assignment.is_active == is_active)

        # 전체 개수
        total = query.count()

        # 통계
        active_count = (
            db.query(func.count(Assignment.assignment_id))
            .filter(Assignment.academy_id == academy_id)
            .filter(Assignment.is_active == True)
            .scalar() or 0
        )

        total_assignments = (
            db.query(func.count(Assignment.assignment_id))
            .filter(Assignment.academy_id == academy_id)
            .scalar() or 0
        )

        # 페이지네이션
        offset = (page - 1) * limit
        assignments = (
            query
            .order_by(Assignment.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        # 각 과제별 통계 계산
        records = []
        completion_rates = []

        for assignment in assignments:
            # 반에 속한 학생 수 계산
            if assignment.class_id:
                total_students = (
                    db.query(func.count(Student.student_id))
                    .filter(Student.class_id == assignment.class_id)
                    .filter(Student.academy_id == academy_id)
                    .scalar() or 0
                )
            else:
                # 개인 과제인 경우 제출된 학생 수 기준
                total_students = (
                    db.query(func.count(Submission.submission_id))
                    .filter(Submission.assignment_id == assignment.assignment_id)
                    .scalar() or 0
                )

            # 제출 현황
            submitted_count = (
                db.query(func.count(Submission.submission_id))
                .filter(Submission.assignment_id == assignment.assignment_id)
                .filter(Submission.status.in_([SubmissionStatus.SUBMITTED, SubmissionStatus.GRADED]))
                .scalar() or 0
            )

            graded_count = (
                db.query(func.count(Submission.submission_id))
                .filter(Submission.assignment_id == assignment.assignment_id)
                .filter(Submission.status == SubmissionStatus.GRADED)
                .scalar() or 0
            )

            # 완료율 계산
            completion_rate = (
                round(submitted_count * 100 / total_students, 1)
                if total_students > 0 else 0
            )
            completion_rates.append(completion_rate)

            # 반 정보 조회
            class_obj = None
            class_name = None
            if assignment.class_id:
                class_obj = db.query(Class).filter(Class.class_id == assignment.class_id).first()
                class_name = class_obj.class_name if class_obj else None

            # 선생님 정보 조회
            teacher = db.query(User).filter(User.user_id == assignment.teacher_id).first()
            teacher_name = teacher.name if teacher else "알 수 없음"

            records.append({
                "assignment_id": assignment.assignment_id,
                "title": assignment.title,
                "class_id": assignment.class_id,
                "class_name": class_name,
                "teacher_id": assignment.teacher_id,
                "teacher_name": teacher_name,
                "due_date": assignment.due_date,
                "is_active": assignment.is_active,
                "total_students": total_students,
                "submitted_count": submitted_count,
                "graded_count": graded_count,
                "completion_rate": completion_rate,
                "created_at": assignment.created_at
            })

        # 평균 완료율
        avg_completion_rate = (
            round(sum(completion_rates) / len(completion_rates), 1)
            if completion_rates else 0
        )

        stats = {
            "total_assignments": total_assignments,
            "active_count": active_count,
            "average_completion_rate": avg_completion_rate
        }

        return records, total, stats

    @staticmethod
    def get_student_assignments(
        db: Session,
        academy_id: int,
        student_id: Optional[int] = None,
        class_id: Optional[int] = None,
        status_filter: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int, Dict[str, Any]]:
        """
        학생별 과제 상태 조회

        Args:
            db: DB 세션
            academy_id: 학원 ID
            student_id: 학생 ID 필터 (선택)
            class_id: 반 ID 필터 (선택)
            status_filter: 상태 필터 ('completed' or 'incomplete')
            page: 페이지 번호
            limit: 페이지당 항목 수

        Returns:
            (학생별 과제 목록, 전체 개수, 통계)
        """
        # 학생 필터 조건
        student_query = db.query(Student).filter(Student.academy_id == academy_id)
        if student_id:
            student_query = student_query.filter(Student.student_id == student_id)
        if class_id:
            student_query = student_query.filter(Student.class_id == class_id)

        students = student_query.all()
        student_ids = [s.student_id for s in students]
        student_map = {s.student_id: s for s in students}

        if not student_ids:
            return [], 0, {
                "total_count": 0,
                "completed_count": 0,
                "incomplete_count": 0,
                "completion_rate": 0
            }

        # 해당 학생들이 받은 과제 조회 (반 기준 또는 개인 과제)
        # 학생의 class_id와 일치하는 과제 + 해당 학생에게 배정된 개인 과제
        assignments_query = (
            db.query(Assignment)
            .filter(Assignment.academy_id == academy_id)
            .filter(Assignment.is_active == True)
        )

        if class_id:
            assignments_query = assignments_query.filter(
                or_(
                    Assignment.class_id == class_id,
                    Assignment.class_id.is_(None)
                )
            )

        assignments = assignments_query.all()

        # 각 학생-과제 조합에 대한 상태 계산
        records = []
        completed_count = 0
        incomplete_count = 0

        for student in students:
            # 학생의 반 정보
            class_obj = None
            if student.class_id:
                class_obj = db.query(Class).filter(Class.class_id == student.class_id).first()

            for assignment in assignments:
                # 반 과제인 경우 학생의 반과 일치해야 함
                if assignment.class_id and assignment.class_id != student.class_id:
                    continue

                # 제출 상태 확인
                submission = (
                    db.query(Submission)
                    .filter(Submission.assignment_id == assignment.assignment_id)
                    .filter(Submission.student_id == student.student_id)
                    .first()
                )

                # 상태 결정
                if submission is None:
                    status = "NOT_STARTED"
                    is_completed = False
                elif submission.status == SubmissionStatus.IN_PROGRESS:
                    status = "IN_PROGRESS"
                    is_completed = False
                elif submission.status == SubmissionStatus.SUBMITTED:
                    status = "SUBMITTED"
                    is_completed = True
                else:  # GRADED
                    status = "GRADED"
                    is_completed = True

                # 필터 적용
                if status_filter == "completed" and not is_completed:
                    continue
                if status_filter == "incomplete" and is_completed:
                    continue

                if is_completed:
                    completed_count += 1
                else:
                    incomplete_count += 1

                # 점수율 계산
                percentage = None
                if submission and submission.status == SubmissionStatus.GRADED and submission.max_score > 0:
                    percentage = round(submission.total_score * 100 / submission.max_score, 1)

                records.append({
                    "student_id": student.student_id,
                    "student_name": student.name,
                    "class_id": student.class_id,
                    "class_name": class_obj.class_name if class_obj else None,
                    "assignment_id": assignment.assignment_id,
                    "assignment_title": assignment.title,
                    "due_date": assignment.due_date,
                    "status": status,
                    "total_score": submission.total_score if submission else None,
                    "max_score": submission.max_score if submission else None,
                    "percentage": percentage,
                    "submitted_at": submission.submitted_at if submission else None
                })

        # 전체 개수
        total = len(records)

        # 통계
        total_count = completed_count + incomplete_count
        stats = {
            "total_count": total_count,
            "completed_count": completed_count,
            "incomplete_count": incomplete_count,
            "completion_rate": round(completed_count * 100 / total_count, 1) if total_count > 0 else 0
        }

        # 페이지네이션 (메모리에서)
        offset = (page - 1) * limit
        paginated_records = records[offset:offset + limit]

        return paginated_records, total, stats
