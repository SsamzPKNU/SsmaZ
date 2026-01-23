"""
키오스크 서비스
학원 태블릿 키오스크용 비즈니스 로직
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, date
from typing import List, Optional, Tuple

from app.models.student import Student
from app.models.academy import Academy
from app.models.attendance import Attendance, AttendanceStatus, AttendanceMethod


class KioskService:
    """
    키오스크 전용 서비스 클래스
    """

    @staticmethod
    def lookup_students_by_phone(
        db: Session,
        academy_id: int,
        phone_last_four: str
    ) -> List[Student]:
        """
        전화번호 뒷자리 4자리로 학생 조회

        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            phone_last_four: 전화번호 뒷자리 4자리

        Returns:
            조회된 학생 목록
        """
        students = db.query(Student).filter(
            and_(
                Student.academy_id == academy_id,
                Student.parent_phone.endswith(phone_last_four),
                Student.status == "재원"
            )
        ).all()

        return students

    @staticmethod
    def process_attendance(
        db: Session,
        student_id: int,
        academy_id: int
    ) -> Tuple[bool, str, Optional[str], Optional[datetime]]:
        """
        출결 처리 (등원/하원 자동 판단)

        Args:
            db: 데이터베이스 세션
            student_id: 학생 ID
            academy_id: 학원 ID

        Returns:
            (성공 여부, 학생 이름, 처리 유형, 처리 시간)
        """
        # 학생 존재 확인
        student = db.query(Student).filter(
            and_(
                Student.student_id == student_id,
                Student.academy_id == academy_id
            )
        ).first()

        if not student:
            return False, "", None, None

        today = date.today()
        now = datetime.now()

        # 오늘 출결 기록 조회
        existing_attendance = db.query(Attendance).filter(
            and_(
                Attendance.student_id == student_id,
                Attendance.academy_id == academy_id,
                Attendance.attendance_date == today
            )
        ).first()

        if existing_attendance:
            # 이미 등원 기록이 있으면 하원 처리
            if existing_attendance.check_out_at is None:
                existing_attendance.check_out_at = now
                db.commit()
                return True, student.name, "check_out", now
            else:
                # 이미 하원까지 완료된 경우 (재등원으로 처리하지 않음)
                return True, student.name, "already_done", existing_attendance.check_out_at
        else:
            # 새로운 등원 기록 생성
            new_attendance = Attendance(
                student_id=student_id,
                academy_id=academy_id,
                status=AttendanceStatus.PRESENT,
                check_in_at=now,
                attendance_date=today,
                method=AttendanceMethod.SELF
            )
            db.add(new_attendance)
            db.commit()
            return True, student.name, "check_in", now

    @staticmethod
    def get_academy_info(db: Session, academy_id: int) -> Optional[Academy]:
        """
        학원 정보 조회

        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID

        Returns:
            학원 정보 또는 None
        """
        academy = db.query(Academy).filter(
            Academy.academy_id == academy_id
        ).first()

        return academy
