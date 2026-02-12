"""
클래스(반/수업) 관리 관련 API 엔드포인트
클래스 CRUD 기능 제공
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.class_schema import ClassCreate, ClassUpdate, ClassResponse, ClassDetailResponse, ClassStatus
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse, ScheduleListResponse
from app.services.class_service import ClassService
from app.services.schedule_service import ScheduleService
from app.models.user import User
from app.models.student import Student
from app.api.auth import get_current_user
from typing import List, Optional
from app.services.push_notification_service import PushNotificationService

import logging
logger = logging.getLogger(__name__)


# API 라우터 생성
router = APIRouter(
    prefix="/admin/classes",
    tags=["클래스 관리"]
)


@router.get("", response_model=List[ClassResponse])
async def get_classes(
    teacher_id: Optional[int] = Query(None, description="선생님 ID 필터"),
    status: Optional[ClassStatus] = Query(None, description="반 상태 필터 (active, inactive, pending, closed)"),
    skip: int = Query(0, ge=0, description="페이지네이션 오프셋"),
    limit: int = Query(100, ge=1, le=1000, description="페이지네이션 제한"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    클래스 목록 조회

    학원의 모든 클래스(반) 목록을 조회합니다.
    선생님별 또는 상태별로 필터링할 수 있습니다.

    Query Parameters:
        - teacher_id: 선생님 ID 필터 (선택)
        - status: 반 상태 필터 (active, inactive, pending, closed) (선택)
        - skip: 페이지네이션 오프셋 (기본: 0)
        - limit: 페이지네이션 제한 (기본: 100)

    Headers:
        Authorization: Bearer {access_token}

    Returns:
        List[ClassResponse]: 클래스 목록

    Response Fields:
        - id: 반 고유 ID
        - name: 반 이름
        - teacher_id: 담당 선생님 ID
        - teacher_name: 담당 선생님 이름
        - capacity: 정원
        - current_students: 현재 학생 수
        - subject: 과목
        - grade_level: 학년/레벨
        - fee: 수강료
        - status: 반 상태

    Raises:
        401: 인증되지 않은 사용자

    사용 예시:
        GET /api/admin/classes
        GET /api/admin/classes?teacher_id=10
        GET /api/admin/classes?status=active
    """
    academy_id = current_user.academy_id

    classes = ClassService.get_classes(
        db=db,
        academy_id=academy_id,
        teacher_id=teacher_id,
        status_filter=status,
        skip=skip,
        limit=limit
    )
    
    return [ClassService.to_response(db, class_obj) for class_obj in classes]


@router.get("/{class_id}", response_model=ClassDetailResponse)
async def get_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    클래스 상세 정보 조회
    
    특정 클래스의 상세 정보를 조회합니다.
    소속 학생 목록도 함께 반환됩니다.
    
    Path Parameters:
        - class_id: 반 ID
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        ClassDetailResponse: 클래스 상세 정보 (학생 목록 포함)
    
    Raises:
        401: 인증되지 않은 사용자
        404: 클래스를 찾을 수 없음
    """
    academy_id = current_user.academy_id
    
    class_obj = ClassService.get_class_by_id(db, class_id, academy_id)
    
    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="클래스를 찾을 수 없습니다"
        )
    
    return ClassService.to_detail_response(db, class_obj)


@router.post("", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
async def create_class(
    class_data: ClassCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    클래스 생성
    
    새로운 클래스(반)를 생성합니다.
    
    Request Body:
        - name: 반 이름 (필수)
        - teacher_id: 담당 선생님 ID (선택)
        - schedule: 수업 일정 (선택)
        - capacity: 정원 (선택)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        ClassResponse: 생성된 클래스 정보
    
    Raises:
        401: 인증되지 않은 사용자
        404: 선생님을 찾을 수 없음
        422: 입력 데이터 검증 실패
    
    사용 예시:
        POST /api/admin/classes
        {
            "name": "영어 특강반",
            "teacher_id": 10,
            "schedule": "토 10:00",
            "capacity": 20
        }
    """
    academy_id = current_user.academy_id
    
    new_class = ClassService.create_class(
        db=db,
        academy_id=academy_id,
        class_data=class_data
    )
    
    return ClassService.to_response(db, new_class)


@router.put("/{class_id}", response_model=ClassResponse)
async def update_class(
    class_id: int,
    class_data: ClassUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    클래스 정보 수정
    
    클래스의 정보를 수정합니다.
    변경하지 않을 필드는 생략할 수 있습니다.
    
    Path Parameters:
        - class_id: 반 ID
    
    Request Body:
        - name: 반 이름 (선택)
        - teacher_id: 담당 선생님 ID (선택)
        - schedule: 수업 일정 (선택)
        - capacity: 정원 (선택)
    
    Headers:
        Authorization: Bearer {access_token}
    
    Returns:
        ClassResponse: 수정된 클래스 정보
    
    Raises:
        401: 인증되지 않은 사용자
        404: 클래스 또는 선생님을 찾을 수 없음
        422: 입력 데이터 검증 실패
    
    사용 예시:
        PUT /api/admin/classes/1
        {
            "schedule": "화/목 17:00",
            "capacity": 25
        }
    """
    academy_id = current_user.academy_id
    
    updated_class = ClassService.update_class(
        db=db,
        class_id=class_id,
        academy_id=academy_id,
        class_data=class_data
    )
    
    return ClassService.to_response(db, updated_class)


@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_class(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    클래스 삭제

    클래스 정보를 삭제합니다.

    Path Parameters:
        - class_id: 반 ID

    Headers:
        Authorization: Bearer {access_token}

    Returns:
        204 No Content (응답 바디 없음)

    Raises:
        401: 인증되지 않은 사용자
        404: 클래스를 찾을 수 없음

    사용 예시:
        DELETE /api/admin/classes/1
    """
    academy_id = current_user.academy_id

    ClassService.delete_class(
        db=db,
        class_id=class_id,
        academy_id=academy_id
    )

    return None


# ========================================
# 반별 학생 목록 API
# ========================================

@router.get("/{class_id}/students")
async def get_class_students(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    반별 학생 목록 조회

    특정 반에 소속된 학생 목록을 조회합니다.

    Path Parameters:
        - class_id: 반 ID

    Headers:
        Authorization: Bearer {access_token}

    Returns:
        학생 목록 (student_id, name, status)

    Raises:
        401: 인증되지 않은 사용자
        404: 클래스를 찾을 수 없음

    사용 예시:
        GET /api/admin/classes/1/students
    """
    academy_id = current_user.academy_id

    # 클래스 존재 확인
    class_obj = ClassService.get_class_by_id(db, class_id, academy_id)

    if not class_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="클래스를 찾을 수 없습니다"
        )

    # 학생 목록 조회
    students = db.query(Student).filter(Student.class_id == class_id).all()

    return {
        "class_id": class_id,
        "class_name": class_obj.name,
        "students": [
            {
                "student_id": s.student_id,
                "name": s.name,
                "status": s.status.value if s.status else None
            }
            for s in students
        ],
        "total": len(students)
    }


# ========================================
# 시간표 API
# ========================================

@router.get("/{class_id}/schedules", response_model=ScheduleListResponse)
async def get_class_schedules(
    class_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    클래스 시간표 목록 조회

    특정 클래스의 시간표 목록을 조회합니다.

    Path Parameters:
        - class_id: 반 ID

    Headers:
        Authorization: Bearer {access_token}

    Returns:
        ScheduleListResponse: 시간표 목록

    Raises:
        401: 인증되지 않은 사용자
        404: 클래스를 찾을 수 없음

    사용 예시:
        GET /api/admin/classes/1/schedules
    """
    academy_id = current_user.academy_id

    schedules = ScheduleService.get_schedules_by_class(
        db=db,
        class_id=class_id,
        academy_id=academy_id
    )

    return ScheduleListResponse(
        items=[ScheduleService.to_response(s) for s in schedules],
        total=len(schedules)
    )


@router.post("/{class_id}/schedules", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    class_id: int,
    schedule_data: ScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    시간표 생성

    클래스에 새로운 시간표를 추가합니다.

    Path Parameters:
        - class_id: 반 ID

    Request Body:
        - day_of_week: 요일 (월, 화, 수, 목, 금, 토, 일)
        - start_time: 시작 시간
        - end_time: 종료 시간

    Headers:
        Authorization: Bearer {access_token}

    Returns:
        ScheduleResponse: 생성된 시간표 정보

    Raises:
        401: 인증되지 않은 사용자
        404: 클래스를 찾을 수 없음

    사용 예시:
        POST /api/admin/classes/1/schedules
        {
            "day_of_week": "월",
            "start_time": "16:00:00",
            "end_time": "18:00:00"
        }
    """
    academy_id = current_user.academy_id

    new_schedule = ScheduleService.create_schedule(
        db=db,
        class_id=class_id,
        academy_id=academy_id,
        schedule_data=schedule_data
    )

    return ScheduleService.to_response(new_schedule)


@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    시간표 수정

    Path Parameters:
        - schedule_id: 시간표 ID

    Request Body:
        - day_of_week: 요일 (선택)
        - start_time: 시작 시간 (선택)
        - end_time: 종료 시간 (선택)
    """
    academy_id = current_user.academy_id

    # 수정 전 정보 저장 (알림 body 조합용)
    old_schedule = ScheduleService.get_schedule_by_id(db, schedule_id)
    if not old_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="시간표를 찾을 수 없습니다"
        )

    old_day = old_schedule.day_of_week
    old_start = old_schedule.start_time
    old_end = old_schedule.end_time

    updated = ScheduleService.update_schedule(
        db=db,
        schedule_id=schedule_id,
        academy_id=academy_id,
        update_data=schedule_data
    )

    # 푸시 알림 발송
    try:
        from app.models.class_model import Class as ClassModel
        class_obj = db.query(ClassModel).filter(ClassModel.class_id == updated.class_id).first()
        if class_obj:
            changes = []
            if schedule_data.day_of_week is not None and schedule_data.day_of_week != old_day:
                changes.append(f"{old_day} → {schedule_data.day_of_week}")
            if schedule_data.start_time is not None and schedule_data.start_time != old_start:
                changes.append(f"{old_start.strftime('%H:%M')} → {schedule_data.start_time.strftime('%H:%M')}")
            if schedule_data.end_time is not None and schedule_data.end_time != old_end:
                changes.append(f"~{old_end.strftime('%H:%M')} → ~{schedule_data.end_time.strftime('%H:%M')}")

            if changes:
                body_text = f"{class_obj.class_name} - {', '.join(changes)}"
                PushNotificationService.send_schedule_notification(
                    db, updated.class_id, class_obj.class_name, body_text, updated.schedule_id
                )
    except Exception as e:
        logger.error(f"[FCM] 일정 변경 알림 발송 실패: {e}")

    return ScheduleService.to_response(updated)


@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    시간표 삭제

    시간표를 삭제합니다.

    Path Parameters:
        - schedule_id: 시간표 ID

    Headers:
        Authorization: Bearer {access_token}

    Returns:
        204 No Content (응답 바디 없음)

    Raises:
        401: 인증되지 않은 사용자
        403: 권한 없음
        404: 시간표를 찾을 수 없음

    사용 예시:
        DELETE /api/admin/classes/schedules/1
    """
    academy_id = current_user.academy_id

    ScheduleService.delete_schedule(
        db=db,
        schedule_id=schedule_id,
        academy_id=academy_id
    )

    return None
