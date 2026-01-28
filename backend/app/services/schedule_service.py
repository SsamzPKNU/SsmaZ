"""
시간표 관리 관련 비즈니스 로직
시간표 CRUD 기능 제공
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from app.models.schedule import Schedule
from app.models.class_model import Class
from app.schemas.schedule import ScheduleCreate, ScheduleResponse
from typing import List, Optional


class ScheduleService:
    """시간표 관리 서비스 클래스"""

    @staticmethod
    def get_schedules_by_class(
        db: Session,
        class_id: int,
        academy_id: int
    ) -> List[Schedule]:
        """
        클래스별 시간표 목록 조회

        Args:
            db: 데이터베이스 세션
            class_id: 반 ID
            academy_id: 학원 ID

        Returns:
            List[Schedule]: 시간표 목록

        Raises:
            HTTPException: 클래스를 찾을 수 없는 경우
        """
        # 클래스 존재 확인
        class_obj = db.query(Class).filter(
            and_(
                Class.class_id == class_id,
                Class.academy_id == academy_id
            )
        ).first()

        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="클래스를 찾을 수 없습니다"
            )

        schedules = db.query(Schedule).filter(
            Schedule.class_id == class_id
        ).order_by(
            Schedule.day_of_week,
            Schedule.start_time
        ).all()

        return schedules

    @staticmethod
    def create_schedule(
        db: Session,
        class_id: int,
        academy_id: int,
        schedule_data: ScheduleCreate
    ) -> Schedule:
        """
        시간표 생성

        Args:
            db: 데이터베이스 세션
            class_id: 반 ID
            academy_id: 학원 ID
            schedule_data: 시간표 정보

        Returns:
            Schedule: 생성된 시간표

        Raises:
            HTTPException: 클래스를 찾을 수 없는 경우
        """
        # 클래스 존재 확인
        class_obj = db.query(Class).filter(
            and_(
                Class.class_id == class_id,
                Class.academy_id == academy_id
            )
        ).first()

        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="클래스를 찾을 수 없습니다"
            )

        # 시간표 생성
        new_schedule = Schedule(
            class_id=class_id,
            day_of_week=schedule_data.day_of_week,
            start_time=schedule_data.start_time,
            end_time=schedule_data.end_time
        )

        db.add(new_schedule)
        db.commit()
        db.refresh(new_schedule)

        return new_schedule

    @staticmethod
    def get_schedule_by_id(db: Session, schedule_id: int) -> Optional[Schedule]:
        """
        시간표 ID로 조회

        Args:
            db: 데이터베이스 세션
            schedule_id: 시간표 ID

        Returns:
            Optional[Schedule]: 시간표 또는 None
        """
        return db.query(Schedule).filter(
            Schedule.schedule_id == schedule_id
        ).first()

    @staticmethod
    def delete_schedule(
        db: Session,
        schedule_id: int,
        academy_id: int
    ) -> bool:
        """
        시간표 삭제

        Args:
            db: 데이터베이스 세션
            schedule_id: 시간표 ID
            academy_id: 학원 ID

        Returns:
            bool: 삭제 성공 여부

        Raises:
            HTTPException: 시간표를 찾을 수 없거나 권한이 없는 경우
        """
        schedule = db.query(Schedule).filter(
            Schedule.schedule_id == schedule_id
        ).first()

        if not schedule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="시간표를 찾을 수 없습니다"
            )

        # 해당 학원의 클래스인지 확인
        class_obj = db.query(Class).filter(
            and_(
                Class.class_id == schedule.class_id,
                Class.academy_id == academy_id
            )
        ).first()

        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="권한이 없습니다"
            )

        db.delete(schedule)
        db.commit()

        return True

    @staticmethod
    def to_response(schedule: Schedule) -> ScheduleResponse:
        """
        Schedule 모델을 ScheduleResponse로 변환

        Args:
            schedule: Schedule 모델 객체

        Returns:
            ScheduleResponse: 응답 스키마
        """
        return ScheduleResponse(
            schedule_id=schedule.schedule_id,
            class_id=schedule.class_id,
            day_of_week=schedule.day_of_week,
            start_time=schedule.start_time,
            end_time=schedule.end_time,
            created_at=schedule.created_at
        )
