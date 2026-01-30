"""
선생님 프린트 관리 API
과제/시험/리포트 목록 및 PDF 생성 기능 제공
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional
from datetime import date

from app.core.database import get_db
from app.models.user import User
from app.models.assignment import Assignment, Question, AssignmentType
from app.models.submission import Submission, SubmissionStatus
from app.models.student import Student
from app.models.class_model import Class
from app.api.auth import get_current_user
from app.services.teacher_app_service import TeacherAppService
from app.services.pdf_service import generate_assignment_pdf, generate_result_pdf
from app.schemas.teacher_print import (
    PrintAssignmentItem, PrintAssignmentListResponse,
    PrintExamItem, PrintExamListResponse,
    PrintReportItem, PrintReportListResponse,
    PDFGenerateRequest, PrintDocumentType
)


router = APIRouter(
    prefix="/api/teacher/print",
    tags=["선생님 앱 - 프린트"]
)


@router.get("/assignments", response_model=PrintAssignmentListResponse)
async def get_print_assignments(
    class_id: Optional[int] = Query(None, description="반 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    프린트용 과제 목록 조회

    인쇄 가능한 과제 목록을 조회합니다.

    Query Parameters:
    - class_id: 반 ID (필터)
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    # 담당 반 정보
    classes = db.query(Class).filter(Class.teacher_id == teacher_id).all()
    class_map = {c.class_id: c.name for c in classes}

    # 과제 조회
    query = db.query(Assignment).filter(
        and_(
            Assignment.academy_id == current_user.academy_id,
            Assignment.teacher_id == current_user.user_id,
            Assignment.is_active == True,
            Assignment.assignment_type == AssignmentType.NORMAL
        )
    )

    if class_id:
        query = query.filter(Assignment.class_id == class_id)

    assignments = query.order_by(Assignment.created_at.desc()).all()

    items = []
    for a in assignments:
        # 문제 수 및 총점
        questions = db.query(Question).filter(
            Question.assignment_id == a.assignment_id
        ).all()

        question_count = len(questions)
        total_points = sum(q.points for q in questions)

        items.append(PrintAssignmentItem(
            assignment_id=a.assignment_id,
            title=a.title,
            class_id=a.class_id,
            class_name=class_map.get(a.class_id),
            due_date=a.due_date,
            question_count=question_count,
            total_points=total_points,
            assignment_type=a.assignment_type.value,
            created_at=a.created_at
        ))

    return PrintAssignmentListResponse(items=items, total=len(items))


@router.get("/exams", response_model=PrintExamListResponse)
async def get_print_exams(
    class_id: Optional[int] = Query(None, description="반 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    프린트용 시험 목록 조회

    인쇄 가능한 시험 목록을 조회합니다. (채점 완료된 과제)

    Query Parameters:
    - class_id: 반 ID (필터)
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    # 담당 반 정보
    classes = db.query(Class).filter(Class.teacher_id == teacher_id).all()
    class_map = {c.class_id: c.name for c in classes}

    # 과제 조회 (채점된 제출이 있는 과제)
    query = db.query(Assignment).filter(
        and_(
            Assignment.academy_id == current_user.academy_id,
            Assignment.teacher_id == current_user.user_id
        )
    )

    if class_id:
        query = query.filter(Assignment.class_id == class_id)

    assignments = query.order_by(Assignment.created_at.desc()).all()

    items = []
    for a in assignments:
        # 채점된 제출이 있는지 확인
        graded_count = db.query(Submission).filter(
            and_(
                Submission.assignment_id == a.assignment_id,
                Submission.status == SubmissionStatus.GRADED
            )
        ).count()

        if graded_count == 0:
            continue

        # 문제 수 및 총점
        questions = db.query(Question).filter(
            Question.assignment_id == a.assignment_id
        ).all()

        question_count = len(questions)
        total_points = sum(q.points for q in questions)

        # 제출 수
        submission_count = db.query(Submission).filter(
            Submission.assignment_id == a.assignment_id
        ).count()

        # 평균 점수
        avg_score_result = db.query(func.avg(Submission.total_score)).filter(
            and_(
                Submission.assignment_id == a.assignment_id,
                Submission.status == SubmissionStatus.GRADED
            )
        ).scalar()

        avg_score = round(float(avg_score_result), 1) if avg_score_result else None

        items.append(PrintExamItem(
            assignment_id=a.assignment_id,
            title=a.title,
            class_id=a.class_id,
            class_name=class_map.get(a.class_id),
            due_date=a.due_date,
            question_count=question_count,
            total_points=total_points,
            submission_count=submission_count,
            avg_score=avg_score,
            created_at=a.created_at
        ))

    return PrintExamListResponse(items=items, total=len(items))


@router.get("/reports", response_model=PrintReportListResponse)
async def get_print_reports(
    class_id: Optional[int] = Query(None, description="반 ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    프린트용 리포트 목록 조회

    학생별 성적 리포트 목록을 조회합니다.

    Query Parameters:
    - class_id: 반 ID (필터)
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    # 담당 반 정보
    classes = db.query(Class).filter(Class.teacher_id == teacher_id).all()
    class_ids = [c.class_id for c in classes]
    class_map = {c.class_id: c.name for c in classes}

    if not class_ids:
        return PrintReportListResponse(items=[], total=0)

    # 학생 조회
    student_query = db.query(Student).filter(
        and_(
            Student.academy_id == current_user.academy_id,
            Student.class_id.in_(class_ids)
        )
    )

    if class_id:
        if class_id not in class_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="담당 반이 아닙니다"
            )
        student_query = student_query.filter(Student.class_id == class_id)

    students = student_query.order_by(Student.name).all()

    items = []
    for student in students:
        # 해당 학생의 제출 현황
        submissions = db.query(Submission).filter(
            Submission.student_id == student.student_id
        ).all()

        assignment_count = len(submissions)
        completed_count = len([s for s in submissions if s.status == SubmissionStatus.GRADED])

        # 평균 점수
        graded_submissions = [s for s in submissions if s.status == SubmissionStatus.GRADED and s.max_score > 0]
        if graded_submissions:
            avg_score = round(
                sum(s.total_score / s.max_score * 100 for s in graded_submissions) / len(graded_submissions),
                1
            )
        else:
            avg_score = None

        # 마지막 활동
        last_submission = db.query(Submission).filter(
            Submission.student_id == student.student_id
        ).order_by(Submission.updated_at.desc()).first()

        last_activity = last_submission.updated_at if last_submission else None

        items.append(PrintReportItem(
            student_id=student.student_id,
            student_name=student.name,
            class_id=student.class_id,
            class_name=class_map.get(student.class_id),
            assignment_count=assignment_count,
            completed_count=completed_count,
            avg_score=avg_score,
            last_activity=last_activity
        ))

    return PrintReportListResponse(items=items, total=len(items))


@router.post("/generate")
async def generate_pdf(
    data: PDFGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    PDF 생성

    과제, 시험, 리포트의 PDF를 생성합니다.

    Request Body:
    - document_type: 문서 유형 (assignment, exam, report)
    - document_id: 문서 ID
    - show_answers: 정답 표시 여부
    - show_points: 배점 표시 여부
    - layout: 레이아웃 (portrait, landscape)
    """
    try:
        if data.document_type == PrintDocumentType.ASSIGNMENT:
            # 과제 PDF
            assignment = db.query(Assignment).filter(
                and_(
                    Assignment.assignment_id == data.document_id,
                    Assignment.academy_id == current_user.academy_id
                )
            ).first()

            if not assignment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="과제를 찾을 수 없습니다"
                )

            pdf_bytes = generate_assignment_pdf(db, data.document_id)
            filename = f"assignment_{data.document_id}_{assignment.title}.pdf"

        elif data.document_type == PrintDocumentType.EXAM:
            # 시험 결과 PDF (첫 번째 채점된 제출 기준)
            submission = db.query(Submission).filter(
                and_(
                    Submission.assignment_id == data.document_id,
                    Submission.status == SubmissionStatus.GRADED
                )
            ).first()

            if not submission:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="채점된 제출을 찾을 수 없습니다"
                )

            pdf_bytes = generate_result_pdf(db, submission.submission_id)
            filename = f"exam_result_{data.document_id}.pdf"

        elif data.document_type == PrintDocumentType.REPORT:
            # 학생 리포트 PDF - 간단한 요약 생성
            # 실제로는 별도의 리포트 PDF 생성 함수 필요
            student = db.query(Student).filter(
                and_(
                    Student.student_id == data.document_id,
                    Student.academy_id == current_user.academy_id
                )
            ).first()

            if not student:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="학생을 찾을 수 없습니다"
                )

            # 학생의 최근 채점된 제출 하나 선택
            submission = db.query(Submission).filter(
                and_(
                    Submission.student_id == data.document_id,
                    Submission.status == SubmissionStatus.GRADED
                )
            ).order_by(Submission.graded_at.desc()).first()

            if not submission:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="채점된 제출이 없습니다"
                )

            pdf_bytes = generate_result_pdf(db, submission.submission_id)
            filename = f"report_{student.name}.pdf"

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="지원하지 않는 문서 유형입니다"
            )

        # 파일명 정리
        filename = "".join(c for c in filename if c.isalnum() or c in "._- ")

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
            }
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF 생성 중 오류가 발생했습니다: {str(e)}"
        )
