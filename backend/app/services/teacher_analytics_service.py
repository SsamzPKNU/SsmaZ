"""
선생님 오답 분석 서비스
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import date, timedelta
from collections import Counter

from app.models.assignment import Assignment, Question, AssignmentType
from app.models.submission import Submission, Answer, SubmissionStatus
from app.models.student import Student
from app.models.class_model import Class
from app.services.class_teacher_service import ClassTeacherService
from app.schemas.teacher_analytics import (
    QuestionAnalysisItem, StudentWeaknessItem, StudentWeaknessCategory,
    UnitStatsItem
)


class TeacherAnalyticsService:
    """선생님 오답 분석 서비스"""

    @staticmethod
    def get_question_analysis(
        db: Session,
        teacher_id: int,
        academy_id: int,
        analysis_type: Optional[str] = None,
        item_id: Optional[int] = None,
        class_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[QuestionAnalysisItem]:
        """문항별 오답률 분석"""
        # 기본 날짜 범위: 최근 30일
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # 과제 쿼리
        query = db.query(Assignment).filter(
            and_(
                Assignment.academy_id == academy_id,
                Assignment.teacher_id == teacher_id
            )
        )

        if analysis_type == "clinic":
            query = query.filter(Assignment.assignment_type == AssignmentType.CLINIC)
        elif analysis_type == "normal":
            query = query.filter(Assignment.assignment_type == AssignmentType.NORMAL)

        if item_id:
            query = query.filter(Assignment.assignment_id == item_id)

        if class_id:
            query = query.filter(Assignment.class_id == class_id)

        assignments = query.all()
        assignment_ids = [a.assignment_id for a in assignments]

        if not assignment_ids:
            return []

        # 문제별 분석
        questions = db.query(Question).filter(
            Question.assignment_id.in_(assignment_ids)
        ).all()

        items = []
        for q in questions:
            # 해당 문제에 대한 모든 답안 조회
            answers = db.query(Answer).join(Submission).filter(
                and_(
                    Answer.question_id == q.question_id,
                    Submission.status == SubmissionStatus.GRADED
                )
            ).all()

            total_attempts = len(answers)
            if total_attempts == 0:
                continue

            wrong_answers = [a for a in answers if a.is_correct == False]
            wrong_count = len(wrong_answers)
            wrong_rate = round((wrong_count / total_attempts * 100), 1)

            # 자주 틀리는 오답 (상위 3개)
            wrong_answer_texts = [a.student_answer for a in wrong_answers if a.student_answer]
            common_wrong = [ans for ans, cnt in Counter(wrong_answer_texts).most_common(3)]

            items.append(QuestionAnalysisItem(
                question_id=q.question_id,
                question_number=q.question_number,
                question_text=q.question_text,
                category=q.category,
                difficulty=q.difficulty.value,
                total_attempts=total_attempts,
                wrong_count=wrong_count,
                wrong_rate=wrong_rate,
                common_wrong_answers=common_wrong
            ))

        # 오답률 높은 순으로 정렬
        items.sort(key=lambda x: x.wrong_rate, reverse=True)

        return items

    @staticmethod
    def get_student_weakness(
        db: Session,
        teacher_id: int,
        academy_id: int,
        class_id: Optional[int] = None
    ) -> List[StudentWeaknessItem]:
        """학생별 취약점 분석"""
        # 담당 반 목록 (수준별 배정 + 레거시)
        classes = ClassTeacherService.get_teacher_classes(db, teacher_id)
        class_ids = [c.class_id for c in classes]
        class_map = {c.class_id: c.name for c in classes}

        if class_id:
            if class_id not in class_ids:
                return []
            class_ids = [class_id]

        if not class_ids:
            return []

        # 학생 목록
        students = db.query(Student).filter(
            and_(
                Student.academy_id == academy_id,
                Student.class_id.in_(class_ids)
            )
        ).all()

        items = []
        for student in students:
            # 학생의 모든 채점된 답안 조회
            answers = db.query(Answer).join(Submission).filter(
                and_(
                    Submission.student_id == student.student_id,
                    Submission.status == SubmissionStatus.GRADED
                )
            ).all()

            if not answers:
                continue

            total_questions = len(answers)
            wrong_answers = [a for a in answers if a.is_correct == False]
            total_wrong = len(wrong_answers)
            overall_wrong_rate = round((total_wrong / total_questions * 100), 1)

            # 카테고리별 취약점 분석
            category_stats = {}
            for ans in answers:
                question = db.query(Question).filter(
                    Question.question_id == ans.question_id
                ).first()

                if question and question.category:
                    cat = question.category
                    if cat not in category_stats:
                        category_stats[cat] = {"total": 0, "wrong": 0}
                    category_stats[cat]["total"] += 1
                    if ans.is_correct == False:
                        category_stats[cat]["wrong"] += 1

            weak_categories = []
            for cat, stats in category_stats.items():
                if stats["total"] > 0:
                    wrong_rate = round((stats["wrong"] / stats["total"] * 100), 1)
                    weak_categories.append(StudentWeaknessCategory(
                        category=cat,
                        total_questions=stats["total"],
                        wrong_count=stats["wrong"],
                        wrong_rate=wrong_rate
                    ))

            # 오답률 높은 순으로 정렬
            weak_categories.sort(key=lambda x: x.wrong_rate, reverse=True)

            items.append(StudentWeaknessItem(
                student_id=student.student_id,
                student_name=student.name,
                class_id=student.class_id,
                class_name=class_map.get(student.class_id),
                total_questions=total_questions,
                total_wrong=total_wrong,
                overall_wrong_rate=overall_wrong_rate,
                weak_categories=weak_categories[:5]  # 상위 5개 취약 유형
            ))

        # 전체 오답률 높은 순으로 정렬
        items.sort(key=lambda x: x.overall_wrong_rate, reverse=True)

        return items

    @staticmethod
    def get_unit_stats(
        db: Session,
        teacher_id: int,
        academy_id: int,
        analysis_type: Optional[str] = None,
        class_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[UnitStatsItem]:
        """단원별 통계"""
        # 기본 날짜 범위: 최근 30일
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # 과제 쿼리
        query = db.query(Assignment).filter(
            and_(
                Assignment.academy_id == academy_id,
                Assignment.teacher_id == teacher_id
            )
        )

        if analysis_type == "clinic":
            query = query.filter(Assignment.assignment_type == AssignmentType.CLINIC)
        elif analysis_type == "normal":
            query = query.filter(Assignment.assignment_type == AssignmentType.NORMAL)

        if class_id:
            query = query.filter(Assignment.class_id == class_id)

        assignments = query.all()
        assignment_ids = [a.assignment_id for a in assignments]

        if not assignment_ids:
            return []

        # 문제별 카테고리 통계
        questions = db.query(Question).filter(
            Question.assignment_id.in_(assignment_ids)
        ).all()

        category_data = {}

        for q in questions:
            category = q.category or "미분류"

            if category not in category_data:
                category_data[category] = {
                    "total_questions": 0,
                    "total_attempts": 0,
                    "correct_count": 0,
                    "wrong_count": 0,
                    "difficulties": []
                }

            category_data[category]["total_questions"] += 1
            category_data[category]["difficulties"].append(q.difficulty.value)

            # 해당 문제에 대한 답안 조회
            answers = db.query(Answer).join(Submission).filter(
                and_(
                    Answer.question_id == q.question_id,
                    Submission.status == SubmissionStatus.GRADED
                )
            ).all()

            for ans in answers:
                category_data[category]["total_attempts"] += 1
                if ans.is_correct:
                    category_data[category]["correct_count"] += 1
                else:
                    category_data[category]["wrong_count"] += 1

        items = []
        for category, data in category_data.items():
            total_attempts = data["total_attempts"]
            if total_attempts == 0:
                correct_rate = 0
                wrong_rate = 0
            else:
                correct_rate = round((data["correct_count"] / total_attempts * 100), 1)
                wrong_rate = round((data["wrong_count"] / total_attempts * 100), 1)

            # 평균 난이도 계산
            difficulties = data["difficulties"]
            if difficulties:
                diff_map = {"EASY": 1, "MEDIUM": 2, "HARD": 3}
                avg_diff_value = sum(diff_map.get(d, 2) for d in difficulties) / len(difficulties)
                if avg_diff_value < 1.5:
                    avg_difficulty = "EASY"
                elif avg_diff_value < 2.5:
                    avg_difficulty = "MEDIUM"
                else:
                    avg_difficulty = "HARD"
            else:
                avg_difficulty = "MEDIUM"

            items.append(UnitStatsItem(
                category=category,
                total_questions=data["total_questions"],
                total_attempts=data["total_attempts"],
                correct_count=data["correct_count"],
                wrong_count=data["wrong_count"],
                correct_rate=correct_rate,
                wrong_rate=wrong_rate,
                avg_difficulty=avg_difficulty
            ))

        # 오답률 높은 순으로 정렬
        items.sort(key=lambda x: x.wrong_rate, reverse=True)

        return items
