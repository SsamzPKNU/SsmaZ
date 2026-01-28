"""
PDF 출력 API 라우터
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User, UserRole
from app.models.assignment import Assignment
from app.models.submission import Submission
from app.models.student import Student
from app.services.pdf_service import generate_assignment_pdf, generate_result_pdf

router = APIRouter()


@router.get("/assignment/{assignment_id}")
async def download_assignment_pdf(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    과제 문제지 PDF 다운로드
    """
    assignment = db.query(Assignment).filter(
        Assignment.assignment_id == assignment_id,
        Assignment.academy_id == current_user.academy_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="과제를 찾을 수 없습니다"
        )

    try:
        pdf_bytes = generate_assignment_pdf(db, assignment_id)

        filename = f"assignment_{assignment_id}_{assignment.title}.pdf"
        # 파일명에서 특수문자 제거
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


@router.get("/result/{submission_id}")
async def download_result_pdf(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    채점 결과지 PDF 다운로드
    """
    submission = db.query(Submission).filter(
        Submission.submission_id == submission_id
    ).first()

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="제출 기록을 찾을 수 없습니다"
        )

    # 권한 확인
    if current_user.user_role == UserRole.STUDENT:
        student = db.query(Student).filter(
            Student.academy_id == current_user.academy_id,
            Student.name == current_user.name
        ).first()

        if not student or submission.student_id != student.student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="권한이 없습니다"
            )
    else:
        assignment = db.query(Assignment).filter(
            Assignment.assignment_id == submission.assignment_id,
            Assignment.academy_id == current_user.academy_id
        ).first()

        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="권한이 없습니다"
            )

    if submission.status.value != "GRADED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="채점이 완료되지 않은 제출입니다"
        )

    try:
        pdf_bytes = generate_result_pdf(db, submission_id)

        assignment = db.query(Assignment).filter(
            Assignment.assignment_id == submission.assignment_id
        ).first()

        student = db.query(Student).filter(
            Student.student_id == submission.student_id
        ).first()

        filename = f"result_{submission_id}_{student.name if student else 'unknown'}.pdf"
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
