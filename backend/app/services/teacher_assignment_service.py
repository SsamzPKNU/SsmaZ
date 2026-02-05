"""
선생님 과제/채점 관리 서비스
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.models.assignment import Assignment, Question, AssignmentType, QuestionType, Difficulty
from app.models.submission import Submission, Answer, SubmissionStatus
from app.models.student import Student
from app.models.class_model import Class
from app.models.teacher import Teacher
from app.schemas.teacher_assignment import (
    AssignmentCreateRequest, AssignmentUpdateRequest,
    AssignmentListItem, AssignmentDetailResponse, AssignmentStats,
    QuestionResponse,
    GradingListItem, SubmissionListItem, SubmissionListResponse,
    StudentSubmissionDetail, AnswerDetail,
    GradeSubmissionRequest, GradeSubmissionResponse
)


class TeacherAssignmentService:
    """선생님 과제/채점 관리 서비스"""

    # ========== 과제 관리 ==========

    @staticmethod
    def get_assignments(
        db: Session,
        teacher_id: int,
        user_id: int,
        academy_id: int,
        class_id: Optional[int] = None,
        status_filter: Optional[str] = None
    ) -> tuple[List[AssignmentListItem], AssignmentStats]:
        """과제 목록 조회"""
        # 담당 반 목록
        classes = db.query(Class).filter(Class.teacher_id == teacher_id).all()
        class_ids = [c.class_id for c in classes]
        class_map = {c.class_id: c.name for c in classes}

        # 기본 쿼리: 내가 출제한 과제 또는 담당 반 과제
        query = db.query(Assignment).filter(
            and_(
                Assignment.academy_id == academy_id,
                Assignment.teacher_id == teacher_id
            )
        )

        # 반 필터
        if class_id:
            query = query.filter(Assignment.class_id == class_id)

        # 상태 필터
        if status_filter == "active":
            query = query.filter(Assignment.is_active == True)
        elif status_filter == "inactive":
            query = query.filter(Assignment.is_active == False)

        assignments = query.order_by(Assignment.created_at.desc()).all()

        items = []
        total_active = 0
        total_submit_rates = []

        for a in assignments:
            # 문제 수
            question_count = db.query(Question).filter(
                Question.assignment_id == a.assignment_id
            ).count()

            # 제출 현황
            if a.class_id:
                student_count = db.query(Student).filter(
                    Student.class_id == a.class_id
                ).count()
            else:
                student_count = 1  # 개인 과제

            submission_count = db.query(Submission).filter(
                and_(
                    Submission.assignment_id == a.assignment_id,
                    Submission.status != SubmissionStatus.IN_PROGRESS
                )
            ).count()

            submit_rate = round((submission_count / student_count * 100), 1) if student_count > 0 else 0

            if a.is_active:
                total_active += 1
            total_submit_rates.append(submit_rate)

            items.append(AssignmentListItem(
                assignment_id=a.assignment_id,
                title=a.title,
                class_id=a.class_id,
                class_name=class_map.get(a.class_id),
                due_date=a.due_date,
                assignment_type=a.assignment_type.value,
                is_active=a.is_active,
                question_count=question_count,
                submission_count=submission_count,
                submit_rate=submit_rate,
                created_at=a.created_at
            ))

        avg_submit_rate = round(sum(total_submit_rates) / len(total_submit_rates), 1) if total_submit_rates else 0

        stats = AssignmentStats(
            total=len(items),
            active=total_active,
            avg_submit_rate=avg_submit_rate
        )

        return items, stats

    @staticmethod
    def get_assignment_detail(
        db: Session,
        assignment_id: int,
        user_id: int,
        academy_id: int
    ) -> AssignmentDetailResponse:
        """과제 상세 조회"""
        assignment = db.query(Assignment).filter(
            and_(
                Assignment.assignment_id == assignment_id,
                Assignment.academy_id == academy_id,
                Assignment.teacher_id == user_id
            )
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="과제를 찾을 수 없습니다"
            )

        # 반 이름
        class_name = None
        if assignment.class_id:
            class_obj = db.query(Class).filter(Class.class_id == assignment.class_id).first()
            class_name = class_obj.name if class_obj else None

        # 문제 목록
        questions = db.query(Question).filter(
            Question.assignment_id == assignment_id
        ).order_by(Question.question_number).all()

        question_responses = [
            QuestionResponse(
                question_id=q.question_id,
                question_number=q.question_number,
                question_text=q.question_text,
                question_type=q.question_type.value,
                options=q.options,
                correct_answer=q.correct_answer,
                points=q.points,
                category=q.category,
                difficulty=q.difficulty.value
            )
            for q in questions
        ]

        # 제출 현황
        if assignment.class_id:
            student_count = db.query(Student).filter(
                Student.class_id == assignment.class_id
            ).count()
        else:
            student_count = 1

        submission_count = db.query(Submission).filter(
            and_(
                Submission.assignment_id == assignment_id,
                Submission.status != SubmissionStatus.IN_PROGRESS
            )
        ).count()

        submit_rate = round((submission_count / student_count * 100), 1) if student_count > 0 else 0

        return AssignmentDetailResponse(
            assignment_id=assignment.assignment_id,
            title=assignment.title,
            description=assignment.description,
            class_id=assignment.class_id,
            class_name=class_name,
            due_date=assignment.due_date,
            assignment_type=assignment.assignment_type.value,
            is_active=assignment.is_active,
            questions=question_responses,
            submission_count=submission_count,
            submit_rate=submit_rate,
            created_at=assignment.created_at,
            updated_at=assignment.updated_at
        )

    @staticmethod
    def create_assignment(
        db: Session,
        user_id: int,
        academy_id: int,
        data: AssignmentCreateRequest
    ) -> AssignmentDetailResponse:
        """과제 생성"""
        # 과제 생성
        assignment = Assignment(
            academy_id=academy_id,
            teacher_id=user_id,
            class_id=data.class_id,
            title=data.title,
            description=data.description,
            due_date=data.due_date,
            assignment_type=AssignmentType(data.assignment_type.value),
            is_active=True
        )
        db.add(assignment)
        db.flush()

        # 문제 생성
        for q_data in data.questions:
            question = Question(
                assignment_id=assignment.assignment_id,
                question_number=q_data.question_number,
                question_text=q_data.question_text,
                question_type=QuestionType(q_data.question_type.value),
                options=q_data.options,
                correct_answer=q_data.correct_answer,
                points=q_data.points,
                category=q_data.category,
                difficulty=Difficulty(q_data.difficulty.value)
            )
            db.add(question)

        db.commit()
        db.refresh(assignment)

        return TeacherAssignmentService.get_assignment_detail(
            db, assignment.assignment_id, user_id, academy_id
        )

    @staticmethod
    def update_assignment(
        db: Session,
        assignment_id: int,
        user_id: int,
        academy_id: int,
        data: AssignmentUpdateRequest
    ) -> AssignmentDetailResponse:
        """과제 수정"""
        assignment = db.query(Assignment).filter(
            and_(
                Assignment.assignment_id == assignment_id,
                Assignment.academy_id == academy_id,
                Assignment.teacher_id == user_id
            )
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="과제를 찾을 수 없습니다"
            )

        if data.title is not None:
            assignment.title = data.title
        if data.description is not None:
            assignment.description = data.description
        if data.due_date is not None:
            assignment.due_date = data.due_date
        if data.is_active is not None:
            assignment.is_active = data.is_active

        db.commit()
        db.refresh(assignment)

        return TeacherAssignmentService.get_assignment_detail(
            db, assignment_id, user_id, academy_id
        )

    @staticmethod
    def delete_assignment(
        db: Session,
        assignment_id: int,
        user_id: int,
        academy_id: int
    ) -> bool:
        """과제 삭제"""
        assignment = db.query(Assignment).filter(
            and_(
                Assignment.assignment_id == assignment_id,
                Assignment.academy_id == academy_id,
                Assignment.teacher_id == user_id
            )
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="과제를 찾을 수 없습니다"
            )

        db.delete(assignment)
        db.commit()
        return True

    # ========== 채점 관리 ==========

    @staticmethod
    def get_grading_list(
        db: Session,
        teacher_id: int,
        user_id: int,
        academy_id: int
    ) -> tuple[List[GradingListItem], int]:
        """채점 대기 목록 조회"""
        # 담당 반 목록
        classes = db.query(Class).filter(Class.teacher_id == teacher_id).all()
        class_map = {c.class_id: c.name for c in classes}

        # 내가 출제한 과제 중 채점 대기가 있는 것
        assignments = db.query(Assignment).filter(
            and_(
                Assignment.academy_id == academy_id,
                Assignment.teacher_id == user_id,
                Assignment.is_active == True
            )
        ).all()

        items = []
        total_pending = 0

        for a in assignments:
            # 전체 제출 수
            total_submissions = db.query(Submission).filter(
                and_(
                    Submission.assignment_id == a.assignment_id,
                    Submission.status != SubmissionStatus.IN_PROGRESS
                )
            ).count()

            # 채점 대기 수
            pending_count = db.query(Submission).filter(
                and_(
                    Submission.assignment_id == a.assignment_id,
                    Submission.status == SubmissionStatus.SUBMITTED
                )
            ).count()

            if pending_count > 0:
                total_pending += pending_count
                items.append(GradingListItem(
                    assignment_id=a.assignment_id,
                    title=a.title,
                    class_id=a.class_id,
                    class_name=class_map.get(a.class_id),
                    due_date=a.due_date,
                    pending_count=pending_count,
                    total_submissions=total_submissions
                ))

        return items, total_pending

    @staticmethod
    def get_assignment_submissions(
        db: Session,
        assignment_id: int,
        user_id: int,
        academy_id: int
    ) -> SubmissionListResponse:
        """과제별 제출 현황 조회"""
        assignment = db.query(Assignment).filter(
            and_(
                Assignment.assignment_id == assignment_id,
                Assignment.academy_id == academy_id,
                Assignment.teacher_id == user_id
            )
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="과제를 찾을 수 없습니다"
            )

        # 만점 계산
        max_score = db.query(func.sum(Question.points)).filter(
            Question.assignment_id == assignment_id
        ).scalar() or 0

        # 제출 목록
        submissions = db.query(Submission).filter(
            Submission.assignment_id == assignment_id
        ).all()

        items = []
        submitted_count = 0
        graded_count = 0

        for sub in submissions:
            student = db.query(Student).filter(
                Student.student_id == sub.student_id
            ).first()

            class_name = None
            if student and student.class_id:
                class_obj = db.query(Class).filter(Class.class_id == student.class_id).first()
                class_name = class_obj.name if class_obj else None

            score_rate = None
            if sub.status == SubmissionStatus.GRADED and max_score > 0:
                score_rate = round((sub.total_score / max_score * 100), 1)

            if sub.status != SubmissionStatus.IN_PROGRESS:
                submitted_count += 1
            if sub.status == SubmissionStatus.GRADED:
                graded_count += 1

            items.append(SubmissionListItem(
                student_id=sub.student_id,
                student_name=student.name if student else "Unknown",
                class_name=class_name,
                status=sub.status.value,
                submitted_at=sub.submitted_at,
                total_score=sub.total_score if sub.status == SubmissionStatus.GRADED else None,
                max_score=max_score,
                score_rate=score_rate
            ))

        return SubmissionListResponse(
            assignment_id=assignment_id,
            assignment_title=assignment.title,
            items=items,
            total=len(items),
            submitted_count=submitted_count,
            graded_count=graded_count
        )

    @staticmethod
    def get_student_submission_detail(
        db: Session,
        assignment_id: int,
        student_id: int,
        user_id: int,
        academy_id: int
    ) -> StudentSubmissionDetail:
        """학생별 제출 상세 조회"""
        assignment = db.query(Assignment).filter(
            and_(
                Assignment.assignment_id == assignment_id,
                Assignment.academy_id == academy_id,
                Assignment.teacher_id == user_id
            )
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="과제를 찾을 수 없습니다"
            )

        submission = db.query(Submission).filter(
            and_(
                Submission.assignment_id == assignment_id,
                Submission.student_id == student_id
            )
        ).first()

        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="제출 기록을 찾을 수 없습니다"
            )

        student = db.query(Student).filter(
            Student.student_id == student_id
        ).first()

        # 만점 계산
        max_score = db.query(func.sum(Question.points)).filter(
            Question.assignment_id == assignment_id
        ).scalar() or 0

        # 답안 목록
        answers = db.query(Answer).filter(
            Answer.submission_id == submission.submission_id
        ).all()

        answer_details = []
        for ans in answers:
            question = db.query(Question).filter(
                Question.question_id == ans.question_id
            ).first()

            if question:
                answer_details.append(AnswerDetail(
                    answer_id=ans.answer_id,
                    question_id=ans.question_id,
                    question_number=question.question_number,
                    question_text=question.question_text,
                    question_type=question.question_type.value,
                    correct_answer=question.correct_answer,
                    student_answer=ans.student_answer,
                    is_correct=ans.is_correct,
                    points=question.points,
                    points_earned=ans.points_earned
                ))

        # 문제 번호순 정렬
        answer_details.sort(key=lambda x: x.question_number)

        return StudentSubmissionDetail(
            submission_id=submission.submission_id,
            student_id=student_id,
            student_name=student.name if student else "Unknown",
            status=submission.status.value,
            submitted_at=submission.submitted_at,
            graded_at=submission.graded_at,
            total_score=submission.total_score,
            max_score=max_score,
            answers=answer_details
        )

    @staticmethod
    def grade_submission(
        db: Session,
        assignment_id: int,
        student_id: int,
        user_id: int,
        academy_id: int,
        data: GradeSubmissionRequest
    ) -> GradeSubmissionResponse:
        """채점 저장"""
        assignment = db.query(Assignment).filter(
            and_(
                Assignment.assignment_id == assignment_id,
                Assignment.academy_id == academy_id,
                Assignment.teacher_id == user_id
            )
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="과제를 찾을 수 없습니다"
            )

        submission = db.query(Submission).filter(
            and_(
                Submission.assignment_id == assignment_id,
                Submission.student_id == student_id
            )
        ).first()

        if not submission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="제출 기록을 찾을 수 없습니다"
            )

        # 각 답안 채점
        total_score = 0
        for grade_data in data.answers:
            answer = db.query(Answer).filter(
                and_(
                    Answer.answer_id == grade_data.answer_id,
                    Answer.submission_id == submission.submission_id
                )
            ).first()

            if answer:
                answer.is_correct = grade_data.is_correct
                answer.points_earned = grade_data.points_earned
                total_score += grade_data.points_earned

        # 만점 계산
        max_score = db.query(func.sum(Question.points)).filter(
            Question.assignment_id == assignment_id
        ).scalar() or 0

        # 제출 상태 업데이트
        submission.status = SubmissionStatus.GRADED
        submission.total_score = total_score
        submission.max_score = max_score
        submission.graded_at = datetime.now()

        db.commit()
        db.refresh(submission)

        return GradeSubmissionResponse(
            submission_id=submission.submission_id,
            status=submission.status.value,
            total_score=submission.total_score,
            max_score=max_score,
            graded_at=submission.graded_at
        )
