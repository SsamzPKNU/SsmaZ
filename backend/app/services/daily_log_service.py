"""
일일 기록(알림장) 비즈니스 로직
학생별 태도 점수 및 학습 기록 관리
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from datetime import date
from typing import List

from app.models.daily_log import DailyLog
from app.models.student import Student
from app.schemas.daily_log import DailyLogItem


class DailyLogService:
    """일일 기록 서비스"""

    @staticmethod
    def get_daily_logs(
        db: Session,
        class_id: int,
        log_date: date,
        academy_id: int,
    ) -> List[DailyLogItem]:
        """
        반 학생 전체의 일일 기록 조회 (기록 없는 학생도 빈 상태로 포함)
        """
        # 해당 반의 학생 목록
        students = (
            db.query(Student)
            .filter(
                and_(
                    Student.class_id == class_id,
                    Student.academy_id == academy_id,
                )
            )
            .order_by(Student.name)
            .all()
        )

        # 해당 날짜의 기록을 student_id 기준으로 매핑
        logs = (
            db.query(DailyLog)
            .filter(
                and_(
                    DailyLog.regdate == log_date,
                    DailyLog.academy_id == academy_id,
                    DailyLog.student_id.in_([s.student_id for s in students]),
                )
            )
            .all()
        )
        log_map = {log.student_id: log for log in logs}

        items = []
        for student in students:
            log = log_map.get(student.student_id)
            items.append(
                DailyLogItem(
                    id=log.log_id if log else 0,
                    studentId=student.student_id,
                    studentName=student.name,
                    attitudeScore=log.attitude_score if log else None,
                    studyNote=log.study_note if log else None,
                    isSent=log.is_sent if log else False,
                    date=log_date,
                )
            )

        return items

    @staticmethod
    def create_daily_log(
        db: Session,
        student_id: int,
        class_id: int,
        log_date: date,
        academy_id: int,
        teacher_id: int,
        attitude_score: int | None = None,
        study_note: str | None = None,
    ) -> DailyLog:
        """
        일일 기록 생성 (학생 소속 확인 + 동일 학생·날짜 중복 방지)
        """
        # 학생 존재 + 반 소속 확인
        student = db.query(Student).filter(
            and_(
                Student.student_id == student_id,
                Student.academy_id == academy_id,
            )
        ).first()

        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="학생을 찾을 수 없습니다",
            )
        if student.class_id != class_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="학생이 해당 반에 소속되어 있지 않습니다",
            )

        # 동일 학생 + 날짜 중복 체크
        existing = db.query(DailyLog).filter(
            and_(
                DailyLog.student_id == student_id,
                DailyLog.regdate == log_date,
                DailyLog.academy_id == academy_id,
            )
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="해당 학생의 해당 날짜 기록이 이미 존재합니다",
            )

        log = DailyLog(
            student_id=student_id,
            academy_id=academy_id,
            teacher_id=teacher_id,
            attitude_score=attitude_score,
            study_note=study_note,
            is_sent=False,
            regdate=log_date,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def update_daily_log(
        db: Session,
        log_id: int,
        academy_id: int,
        attitude_score: int | None = ...,
        study_note: str | None = ...,
        is_sent: bool | None = ...,
    ) -> DailyLog:
        """
        일일 기록 수정 (academy_id 검증)
        Ellipsis(...) 기본값은 '전달되지 않음'을 의미 (None과 구분)
        """
        log = db.query(DailyLog).filter(DailyLog.log_id == log_id).first()

        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="일일 기록을 찾을 수 없습니다",
            )
        if log.academy_id != academy_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="해당 기록에 대한 권한이 없습니다",
            )

        if attitude_score is not ...:
            log.attitude_score = attitude_score
        if study_note is not ...:
            log.study_note = study_note
        if is_sent is not ...:
            log.is_sent = is_sent

        db.commit()
        db.refresh(log)
        return log
