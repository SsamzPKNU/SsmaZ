"""
선생님 과제/채점 관리 API
과제 CRUD, 채점 관리 기능 제공
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.api.auth import get_current_user
from app.services.teacher_app_service import TeacherAppService
from app.services.teacher_assignment_service import TeacherAssignmentService
from app.schemas.teacher_assignment import (
    AssignmentCreateRequest, AssignmentUpdateRequest,
    AssignmentListResponse, AssignmentDetailResponse,
    GradingListResponse, SubmissionListResponse, StudentSubmissionDetail,
    GradeSubmissionRequest, GradeSubmissionResponse,
    QuickGradeRequest, QuickGradeResponse
)


router = APIRouter(
    prefix="/teacher",
    tags=["선생님 앱 - 과제/채점"]
)


# ========== 과제 관리 API ==========

@router.get("/assignments", response_model=AssignmentListResponse)
async def get_assignments(
    class_id: Optional[int] = Query(None, description="반 ID (필터)"),
    status_filter: Optional[str] = Query(None, description="상태 필터 (active, inactive)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    과제 목록 조회

    담당 반의 과제 목록을 조회합니다.

    Query Parameters:
    - class_id: 반 ID (필터)
    - status: 상태 필터 (active, inactive)
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    items, stats = TeacherAssignmentService.get_assignments(
        db=db,
        teacher_id=teacher_id,
        academy_id=current_user.academy_id,
        class_id=class_id,
        status_filter=status_filter
    )

    return AssignmentListResponse(
        items=items,
        total=len(items),
        stats=stats
    )


@router.get("/assignments/{assignment_id}", response_model=AssignmentDetailResponse)
async def get_assignment_detail(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    과제 상세 조회

    과제의 상세 정보와 문제 목록을 조회합니다.
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    return TeacherAssignmentService.get_assignment_detail(
        db=db,
        assignment_id=assignment_id,
        teacher_id=teacher_id,
        academy_id=current_user.academy_id
    )


@router.post("/assignments", response_model=AssignmentDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    data: AssignmentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    과제 생성

    새 과제와 문제를 생성합니다.

    Request Body:
    - title: 과제 제목
    - description: 과제 설명 (선택)
    - class_id: 반 ID (NULL이면 개인 과제)
    - due_date: 마감일 (선택)
    - assignment_type: 과제 유형 (NORMAL, CLINIC)
    - questions: 문제 목록
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    return TeacherAssignmentService.create_assignment(
        db=db,
        teacher_id=teacher_id,
        academy_id=current_user.academy_id,
        data=data
    )


@router.put("/assignments/{assignment_id}", response_model=AssignmentDetailResponse)
async def update_assignment(
    assignment_id: int,
    data: AssignmentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    과제 수정

    과제의 기본 정보를 수정합니다.
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    return TeacherAssignmentService.update_assignment(
        db=db,
        assignment_id=assignment_id,
        teacher_id=teacher_id,
        academy_id=current_user.academy_id,
        data=data
    )


@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    과제 삭제

    과제와 관련 문제를 삭제합니다.
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    TeacherAssignmentService.delete_assignment(
        db=db,
        assignment_id=assignment_id,
        teacher_id=teacher_id,
        academy_id=current_user.academy_id
    )


# ========== 채점 관리 API ==========

@router.get("/grading", response_model=GradingListResponse)
async def get_grading_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    채점 대기 목록 조회

    채점이 필요한 제출 목록을 조회합니다.
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    items, total_pending = TeacherAssignmentService.get_grading_list(
        db=db,
        teacher_id=teacher_id,
        academy_id=current_user.academy_id
    )

    return GradingListResponse(
        items=items,
        total=len(items),
        total_pending=total_pending
    )


@router.get("/grading/{assignment_id}/submissions", response_model=SubmissionListResponse)
async def get_assignment_submissions(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    과제별 제출 현황 조회

    특정 과제의 학생별 제출 현황을 조회합니다.
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    return TeacherAssignmentService.get_assignment_submissions(
        db=db,
        assignment_id=assignment_id,
        teacher_id=teacher_id,
        academy_id=current_user.academy_id
    )


@router.get("/grading/{assignment_id}/submissions/{student_id}", response_model=StudentSubmissionDetail)
async def get_student_submission(
    assignment_id: int,
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    학생별 제출 상세 조회

    학생의 제출 내용과 답안을 조회합니다.
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    return TeacherAssignmentService.get_student_submission_detail(
        db=db,
        assignment_id=assignment_id,
        student_id=student_id,
        teacher_id=teacher_id,
        academy_id=current_user.academy_id
    )


@router.post("/grading/{assignment_id}/submissions/{student_id}", response_model=GradeSubmissionResponse)
async def grade_submission(
    assignment_id: int,
    student_id: int,
    data: GradeSubmissionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    채점 저장

    학생의 제출에 대해 채점 결과를 저장합니다.

    Request Body:
    - answers: 채점 결과 목록
      - answer_id: 답안 ID
      - points_earned: 부여 점수
      - is_correct: 정답 여부
    - feedback: 전체 피드백 (선택)
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    return TeacherAssignmentService.grade_submission(
        db=db,
        assignment_id=assignment_id,
        student_id=student_id,
        teacher_id=teacher_id,
        academy_id=current_user.academy_id,
        data=data
    )


@router.post("/grading/{assignment_id}/quick-grade", response_model=QuickGradeResponse)
async def quick_grade(
    assignment_id: int,
    data: QuickGradeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    간편 채점 (총점 직접 입력)

    문항별 채점 없이 총점을 직접 입력하여 채점합니다.
    Submission이 없는 학생은 자동으로 생성됩니다.

    Request Body:
    - grades: 성적 배열
      - student_id: 학생 ID
      - score: 획득 점수
      - max_score: 최대 점수 (기본값 100)
    """
    teacher_id = TeacherAppService.get_teacher_id(db, current_user.user_id, current_user.academy_id)

    return TeacherAssignmentService.quick_grade(
        db=db,
        assignment_id=assignment_id,
        teacher_id=teacher_id,
        academy_id=current_user.academy_id,
        data=data
    )
