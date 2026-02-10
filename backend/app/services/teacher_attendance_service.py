"""
선생님 출퇴근 관련 비즈니스 로직
출근/퇴근 처리, 근무시간 계산, 승인 처리 기능 제공
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException, status
from app.models.teacher_attendance import TeacherAttendance
from app.models.teacher import Teacher
from app.models.user import User, UserRole
from typing import List, Optional, Tuple, Dict, Any
from datetime import date, datetime


def _derive_status(attendance) -> str:
    """기존 데이터 하위호환용: status 컬럼이 없거나 'pending'인 레코드의 상태 추론"""
    if hasattr(attendance, 'status') and attendance.status and attendance.status != 'pending':
        return attendance.status
    if attendance.is_approved:
        return "approved"
    if attendance.check_out_time:
        return "checked_out"
    if attendance.check_in_time:
        return "checked_in"
    return "pending"


class TeacherAttendanceService:
    """선생님 출퇴근 관리 서비스 클래스"""

    @staticmethod
    def get_teacher_by_user_id(db: Session, user_id: int) -> Optional[Teacher]:
        """
        User ID로 Teacher 조회

        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID

        Returns:
            Teacher 객체 또는 None
        """
        return db.query(Teacher).filter(Teacher.user_id == user_id).first()

    @staticmethod
    def check_in(
        db: Session,
        teacher_id: int,
        target_date: Optional[date] = None,
        memo: Optional[str] = None
    ) -> TeacherAttendance:
        """
        출근 처리

        당일 중복 출근을 방지하고, 새로운 출근 기록을 생성합니다.

        Args:
            db: 데이터베이스 세션
            teacher_id: 선생님 ID
            target_date: 근무일 (미입력 시 오늘)

        Returns:
            생성된 출퇴근 기록
        """
        work_date = target_date or date.today()
        now = datetime.now()

        # 선생님 존재 확인
        teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="선생님을 찾을 수 없습니다"
            )

        # 당일 중복 출근 체크
        existing = db.query(TeacherAttendance).filter(
            and_(
                TeacherAttendance.teacher_id == teacher_id,
                TeacherAttendance.date == work_date
            )
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"이미 {work_date} 출근 기록이 있습니다"
            )

        # 출근 기록 생성
        attendance = TeacherAttendance(
            teacher_id=teacher_id,
            date=work_date,
            check_in_time=now,
            status="checked_in",
            worked_minutes=0,
            memo=memo,
            is_approved=False
        )

        db.add(attendance)
        db.commit()
        db.refresh(attendance)

        return attendance

    @staticmethod
    def check_out(
        db: Session,
        teacher_id: int
    ) -> TeacherAttendance:
        """
        퇴근 처리

        당일 출근 기록을 찾아 퇴근 시간을 기록하고,
        근무시간을 자동으로 계산합니다.

        Args:
            db: 데이터베이스 세션
            teacher_id: 선생님 ID

        Returns:
            수정된 출퇴근 기록
        """
        today = date.today()
        now = datetime.now()

        # 오늘 출근 기록 조회
        attendance = db.query(TeacherAttendance).filter(
            and_(
                TeacherAttendance.teacher_id == teacher_id,
                TeacherAttendance.date == today
            )
        ).first()

        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="오늘 출근 기록이 없습니다. 먼저 출근 처리를 해주세요."
            )

        if attendance.check_out_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 퇴근 처리가 완료되었습니다"
            )

        # 퇴근 시간 기록
        attendance.check_out_time = now
        attendance.status = "checked_out"

        # 근무시간 계산 (분 단위)
        if attendance.check_in_time:
            time_diff = now - attendance.check_in_time
            attendance.worked_minutes = int(time_diff.total_seconds() / 60)

        db.commit()
        db.refresh(attendance)

        return attendance

    @staticmethod
    def get_attendance_list(
        db: Session,
        teacher_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[dict], int]:
        """
        기간별 출퇴근 기록 조회

        Args:
            db: 데이터베이스 세션
            teacher_id: 선생님 ID
            start_date: 조회 시작일
            end_date: 조회 종료일
            page: 페이지 번호
            limit: 페이지당 항목 수

        Returns:
            (출퇴근 기록 dict 목록, 전체 개수)
        """
        query = db.query(TeacherAttendance, Teacher).join(
            Teacher, TeacherAttendance.teacher_id == Teacher.teacher_id
        ).filter(
            TeacherAttendance.teacher_id == teacher_id
        )

        # 기간 필터
        if start_date:
            query = query.filter(TeacherAttendance.date >= start_date)
        if end_date:
            query = query.filter(TeacherAttendance.date <= end_date)

        # 전체 개수
        total = query.count()

        # 페이지네이션 (최신순)
        offset = (page - 1) * limit
        rows = query.order_by(TeacherAttendance.date.desc()).offset(offset).limit(limit).all()

        result = []
        for attendance, teacher in rows:
            result.append({
                "id": attendance.id,
                "teacher_id": attendance.teacher_id,
                "teacher_name": teacher.name,
                "date": attendance.date,
                "check_in_at": attendance.check_in_time,
                "check_out_at": attendance.check_out_time,
                "status": _derive_status(attendance),
                "memo": attendance.memo,
                "approved": attendance.is_approved,
                "worked_minutes": attendance.worked_minutes,
            })

        return result, total

    @staticmethod
    def get_work_summary(
        db: Session,
        teacher_id: int,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        월별 근무시간 요약 및 예상 급여 계산

        Args:
            db: 데이터베이스 세션
            teacher_id: 선생님 ID
            start_date: 조회 시작일
            end_date: 조회 종료일

        Returns:
            근무시간 요약 정보 (dict)
        """
        # 선생님 정보 조회
        teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="선생님을 찾을 수 없습니다"
            )

        # 기간 내 총 근무시간 집계
        result = db.query(
            func.sum(TeacherAttendance.worked_minutes).label("total_minutes"),
            func.count(TeacherAttendance.id).label("total_days")
        ).filter(
            and_(
                TeacherAttendance.teacher_id == teacher_id,
                TeacherAttendance.date >= start_date,
                TeacherAttendance.date <= end_date
            )
        ).first()

        total_minutes = result.total_minutes or 0
        total_days = result.total_days or 0
        total_hours = round(total_minutes / 60, 2)
        avg_hours = round(total_hours / total_days, 2) if total_days > 0 else 0.0

        # 지각/결석 카운트
        late_count = db.query(func.count(TeacherAttendance.id)).filter(
            and_(
                TeacherAttendance.teacher_id == teacher_id,
                TeacherAttendance.date >= start_date,
                TeacherAttendance.date <= end_date,
                TeacherAttendance.status == "late"
            )
        ).scalar() or 0

        absent_count = db.query(func.count(TeacherAttendance.id)).filter(
            and_(
                TeacherAttendance.teacher_id == teacher_id,
                TeacherAttendance.date >= start_date,
                TeacherAttendance.date <= end_date,
                TeacherAttendance.status == "absent"
            )
        ).scalar() or 0

        # 예상 급여 계산 (시급 * 시간)
        estimated_salary = None
        if teacher.hourly_rate and teacher.employment_type == "PART_TIME":
            estimated_salary = int(total_hours * teacher.hourly_rate)

        return {
            "teacher_id": teacher_id,
            "teacher_name": teacher.name,
            "period_start": start_date,
            "period_end": end_date,
            "start_date": start_date,
            "end_date": end_date,
            "total_minutes": total_minutes,
            "total_hours": total_hours,
            "total_days": total_days,
            "avg_hours": avg_hours,
            "late_count": late_count,
            "absent_count": absent_count,
            "employment_type": teacher.employment_type,
            "hourly_rate": teacher.hourly_rate,
            "estimated_salary": estimated_salary
        }

    @staticmethod
    def get_all_attendance_by_date(
        db: Session,
        academy_id: int,
        target_date: date,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[dict]:
        """
        전체 선생님 출퇴근 현황 조회 (관리자용)
        - target_date만 있으면 해당일 현황 (미출근=absent 포함)
        - start_date+end_date 있으면 기간 내 기록 반환

        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            target_date: 조회 날짜 (단일일)
            start_date: 기간 조회 시작일
            end_date: 기간 조회 종료일

        Returns:
            출퇴근 현황 목록 (선생님 정보 포함)
        """
        from app.models.teacher import TeacherStatus

        # 기간 조회 모드
        if start_date and end_date:
            records = db.query(TeacherAttendance, Teacher).join(
                Teacher, TeacherAttendance.teacher_id == Teacher.teacher_id
            ).filter(
                and_(
                    Teacher.academy_id == academy_id,
                    TeacherAttendance.date >= start_date,
                    TeacherAttendance.date <= end_date
                )
            ).order_by(TeacherAttendance.date.desc(), Teacher.name).all()

            result = []
            for attendance, teacher in records:
                work_minutes = attendance.worked_minutes or 0
                result.append({
                    "id": attendance.id,
                    "teacher_id": teacher.teacher_id,
                    "teacher_name": teacher.name,
                    "subject": teacher.subject,
                    "date": attendance.date,
                    "check_in_at": attendance.check_in_time,
                    "check_out_at": attendance.check_out_time,
                    "status": _derive_status(attendance),
                    "memo": attendance.memo,
                    "approved": attendance.is_approved,
                    "work_minutes": work_minutes,
                    "work_hours": round(work_minutes / 60, 2),
                })
            return result

        # 단일일 조회 모드: LEFT JOIN으로 미출근 강사 포함
        active_teachers = db.query(Teacher).filter(
            and_(
                Teacher.academy_id == academy_id,
                Teacher.status == TeacherStatus.ACTIVE
            )
        ).all()

        attendance_map = {}
        records = db.query(TeacherAttendance).filter(
            and_(
                TeacherAttendance.teacher_id.in_([t.teacher_id for t in active_teachers]),
                TeacherAttendance.date == target_date
            )
        ).all()
        for att in records:
            attendance_map[att.teacher_id] = att

        result = []
        for teacher in active_teachers:
            att = attendance_map.get(teacher.teacher_id)
            if att:
                work_minutes = att.worked_minutes or 0
                result.append({
                    "id": att.id,
                    "teacher_id": teacher.teacher_id,
                    "teacher_name": teacher.name,
                    "subject": teacher.subject,
                    "date": target_date,
                    "check_in_at": att.check_in_time,
                    "check_out_at": att.check_out_time,
                    "status": _derive_status(att),
                    "memo": att.memo,
                    "approved": att.is_approved,
                    "work_minutes": work_minutes,
                    "work_hours": round(work_minutes / 60, 2),
                })
            else:
                # 미출근 강사
                result.append({
                    "id": None,
                    "teacher_id": teacher.teacher_id,
                    "teacher_name": teacher.name,
                    "subject": teacher.subject,
                    "date": target_date,
                    "check_in_at": None,
                    "check_out_at": None,
                    "status": "absent",
                    "memo": None,
                    "approved": False,
                    "work_minutes": 0,
                    "work_hours": 0.0,
                })

        return result

    @staticmethod
    def approve_attendance(
        db: Session,
        attendance_id: int,
        admin_user_id: int,
        academy_id: int
    ) -> TeacherAttendance:
        """
        출퇴근 기록 승인 처리

        Args:
            db: 데이터베이스 세션
            attendance_id: 출퇴근 기록 ID
            admin_user_id: 승인하는 관리자의 user_id
            academy_id: 학원 ID (권한 검증용)

        Returns:
            승인된 출퇴근 기록
        """
        # 출퇴근 기록 조회
        attendance = db.query(TeacherAttendance).filter(
            TeacherAttendance.id == attendance_id
        ).first()

        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="출퇴근 기록을 찾을 수 없습니다"
            )

        # 선생님의 학원 소속 확인
        teacher = db.query(Teacher).filter(
            and_(
                Teacher.teacher_id == attendance.teacher_id,
                Teacher.academy_id == academy_id
            )
        ).first()

        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="해당 출퇴근 기록에 대한 권한이 없습니다"
            )

        if attendance.is_approved:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 승인된 기록입니다"
            )

        # 승인 처리
        attendance.is_approved = True
        attendance.approved_by = admin_user_id
        attendance.status = "approved"

        db.commit()
        db.refresh(attendance)

        return attendance

    # ==================== 관리자용 메서드 ====================

    @staticmethod
    def get_attendance_list_by_period(
        db: Session,
        academy_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        teacher_id: Optional[int] = None,
        is_approved: Optional[bool] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[dict], int]:
        """
        기간별 선생님 출퇴근 조회 (관리자용)

        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            start_date: 조회 시작일
            end_date: 조회 종료일
            teacher_id: 선생님 ID 필터 (선택)
            is_approved: 승인 여부 필터 (선택)
            page: 페이지 번호
            limit: 페이지당 항목 수

        Returns:
            Tuple[List[dict], int]: (출퇴근 기록 목록, 전체 개수)
        """
        query = db.query(TeacherAttendance, Teacher).join(
            Teacher, TeacherAttendance.teacher_id == Teacher.teacher_id
        ).filter(Teacher.academy_id == academy_id)

        # 기간 필터
        if start_date:
            query = query.filter(TeacherAttendance.date >= start_date)
        if end_date:
            query = query.filter(TeacherAttendance.date <= end_date)

        # 선생님 필터
        if teacher_id:
            query = query.filter(TeacherAttendance.teacher_id == teacher_id)

        # 승인 여부 필터
        if is_approved is not None:
            query = query.filter(TeacherAttendance.is_approved == is_approved)

        # 전체 개수
        total = query.count()

        # 페이지네이션 (최신순)
        offset = (page - 1) * limit
        records = query.order_by(
            TeacherAttendance.date.desc(),
            Teacher.name
        ).offset(offset).limit(limit).all()

        # 결과 변환
        result = []
        for attendance, teacher in records:
            result.append({
                "id": attendance.id,
                "teacher_id": teacher.teacher_id,
                "teacher_name": teacher.name,
                "date": attendance.date,
                "check_in_time": attendance.check_in_time,
                "check_out_time": attendance.check_out_time,
                "worked_minutes": attendance.worked_minutes,
                "is_approved": attendance.is_approved
            })

        return result, total

    @staticmethod
    def admin_update_attendance(
        db: Session,
        attendance_id: int,
        academy_id: int,
        check_in_time: Optional[datetime] = None,
        check_out_time: Optional[datetime] = None,
        is_approved: Optional[bool] = None
    ) -> TeacherAttendance:
        """
        관리자 권한 선생님 출퇴근 수정

        Args:
            db: 데이터베이스 세션
            attendance_id: 출퇴근 기록 ID
            academy_id: 학원 ID (권한 검증용)
            check_in_time: 출근 시간 (선택)
            check_out_time: 퇴근 시간 (선택)
            is_approved: 승인 여부 (선택)

        Returns:
            TeacherAttendance: 수정된 출퇴근 기록

        Raises:
            HTTPException: 출퇴근 기록을 찾을 수 없거나 권한이 없는 경우
        """
        # 출퇴근 기록 조회
        attendance = db.query(TeacherAttendance).filter(
            TeacherAttendance.id == attendance_id
        ).first()

        if not attendance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="출퇴근 기록을 찾을 수 없습니다"
            )

        # 선생님의 학원 소속 확인
        teacher = db.query(Teacher).filter(
            and_(
                Teacher.teacher_id == attendance.teacher_id,
                Teacher.academy_id == academy_id
            )
        ).first()

        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="해당 출퇴근 기록에 대한 권한이 없습니다"
            )

        # 필드 업데이트
        if check_in_time is not None:
            attendance.check_in_time = check_in_time
        if check_out_time is not None:
            attendance.check_out_time = check_out_time
        if is_approved is not None:
            attendance.is_approved = is_approved

        # 근무시간 재계산
        if attendance.check_in_time and attendance.check_out_time:
            time_diff = attendance.check_out_time - attendance.check_in_time
            attendance.worked_minutes = int(time_diff.total_seconds() / 60)

        db.commit()
        db.refresh(attendance)

        return attendance
