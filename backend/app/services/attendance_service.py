from sqlalchemy.orm import Session
from sqlalchemy import and_, func, case
from datetime import datetime, date
from app.models.attendance import Attendance, AttendanceStatus, AttendanceMethod
from app.models.student import Student
from app.models.class_model import Class
from app.schemas.attendance import AttendanceResponse, AttendanceStats, AttendanceBatchItem
from typing import Optional, List, Tuple, Dict, Any

def send_sms_notification(parent_phone: str, message: str) -> bool:
    """
    (가상) SMS 발송 함수 (인터페이스만 구현)
    실제 서비스(Solapi 등) 연동 시 여기에 구현
    """
    print(f"[SMS 발송] To: {parent_phone} / Msg: {message}")
    # 가상으로 성공 처리
    return True

def get_display_status(status_value: str, check_out_at) -> str:
    """check_out_at이 존재하면 '하원' 반환, 아니면 원래 상태값 반환"""
    if check_out_at is not None:
        return "하원"
    return status_value

class AttendanceService:
    @staticmethod
    def check_attendance(
        db: Session, 
        student_id: int, 
        status: AttendanceStatus, 
        method: AttendanceMethod = AttendanceMethod.MANUAL,
        is_checkout: bool = False
    ) -> Attendance:
        """
        출결 체크 비즈니스 로직
        """
        today = date.today()
        now = datetime.now()

        # 1. 학생 정보 조회 (전화번호 필요)
        student = db.query(Student).filter(Student.student_id == student_id).first()
        if not student:
            raise ValueError(f"Student ID {student_id} not found")

        # 2. 오늘 날짜의 출결 기록 조회
        attendance_record = db.query(Attendance).filter(
            Attendance.student_id == student_id,
            Attendance.attendance_date == today
        ).first()

        # 로직 분기: 하원 vs 등원(출석/지각/조퇴/결석)
        if is_checkout:
             # 하원 처리
             if not attendance_record:
                 raise ValueError("해당 학생의 오늘 등원 기록이 없습니다.")
             
             if attendance_record.check_out_at:
                 raise ValueError("이미 하원 처리가 완료된 학생입니다.")
             
             attendance_record.check_out_at = now
             # 하원은 상태 변경을 원칙으로 하지 않지만 필요시 status를 업데이트할 수 있음
             
        else:
             # 등원(출석/지각/조퇴/결석) 처리
             if not attendance_record:
                 # 새로운 행 생성
                 attendance_record = Attendance(
                     student_id=student_id,
                     academy_id=student.academy_id,
                     status=status,
                     check_in_at=now,
                     attendance_date=today,
                     method=method,
                     is_notified=False,
                     memo=None
                 )
                 db.add(attendance_record)
             else:
                 # 기존 기록이 있으면 상태만 업데이트
                 attendance_record.status = status
                 # 만약 이전에 등원 시간이 기록되지 않았다면 현재 시간으로 기록
                 if not attendance_record.check_in_at:
                     attendance_record.check_in_at = now
        
        db.commit()
        db.refresh(attendance_record)

        # 알림 발송용 메시지 구성
        status_label = "하원" if is_checkout else attendance_record.status.value
        
        message = f"[SsmaZ 알림] {student.name} 학생이 {status_label}하였습니다. (시간: {now.strftime('%H:%M')})"
        
        # 알림 발송 (전송 성공 시 is_notified 업데이트)
        if send_sms_notification(student.parent_phone, message):
            attendance_record.is_notified = True
            db.commit()

        return attendance_record

    @staticmethod
    def get_today_attendance(db: Session, academy_id: Optional[int] = None) -> Tuple[list, AttendanceStats]:
        """
        오늘 출결 현황 조회 (통계 포함)

        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID (None이면 전체 조회 - 하위 호환성)

        Returns:
            Tuple[list, AttendanceStats]: (학생별 출결 목록, 통계)
        """
        today = date.today()

        # 학생 조회 (academy_id 필터링)
        student_query = db.query(Student).filter(Student.status == "재원")
        if academy_id:
            student_query = student_query.filter(Student.academy_id == academy_id)
        students = student_query.all()

        result = []
        stats = AttendanceStats(total=len(students))

        for student in students:
            # 해당 학생의 오늘 출결 기록 조회
            att = db.query(Attendance).filter(
                and_(
                    Attendance.student_id == student.student_id,
                    Attendance.attendance_date == today
                )
            ).first()

            # 통계 집계
            if att:
                if att.status == AttendanceStatus.PRESENT:
                    stats.present += 1
                elif att.status == AttendanceStatus.LATE:
                    stats.late += 1
                elif att.status == AttendanceStatus.ABSENT:
                    stats.absent += 1
                elif att.status == AttendanceStatus.EARLY_LEAVE:
                    stats.early += 1

            result.append({
                "student": student,
                "attendance": att
            })

        return result, stats

    @staticmethod
    def check_attendance_batch(
        db: Session,
        academy_id: int,
        items: List[AttendanceBatchItem],
        target_date: Optional[date] = None
    ) -> dict:
        """
        출결 일괄 저장

        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            items: 출결 항목 리스트
            target_date: 대상 날짜 (기본값: 오늘)

        Returns:
            dict: {success_count, fail_count, failed_items}
        """
        target = target_date or date.today()
        now = datetime.now()

        success_count = 0
        failed_items = []

        for item in items:
            try:
                # 학생 확인 (해당 학원 소속인지)
                student = db.query(Student).filter(
                    and_(
                        Student.student_id == item.student_id,
                        Student.academy_id == academy_id
                    )
                ).first()

                if not student:
                    failed_items.append({
                        "student_id": item.student_id,
                        "error": "학생을 찾을 수 없습니다"
                    })
                    continue

                # 기존 출결 기록 확인
                existing = db.query(Attendance).filter(
                    and_(
                        Attendance.student_id == item.student_id,
                        Attendance.attendance_date == target
                    )
                ).first()

                if existing:
                    # 기존 기록 업데이트
                    existing.status = item.status
                else:
                    # 새 기록 생성
                    new_record = Attendance(
                        student_id=item.student_id,
                        academy_id=academy_id,
                        status=item.status,
                        check_in_at=now if item.status != AttendanceStatus.ABSENT else None,
                        attendance_date=target,
                        method=AttendanceMethod.MANUAL,
                        is_notified=False
                    )
                    db.add(new_record)

                success_count += 1

            except Exception as e:
                failed_items.append({
                    "student_id": item.student_id,
                    "error": str(e)
                })

        db.commit()

        return {
            "success_count": success_count,
            "fail_count": len(failed_items),
            "failed_items": failed_items
        }

    # ==================== 통계 메서드 ====================

    @staticmethod
    def get_attendance_stats(
        db: Session,
        academy_id: int,
        start_date: date,
        end_date: date
    ) -> dict:
        """
        기간별 출석 통계 조회 (대시보드용)

        Returns:
            dict: {summary, daily_stats, class_stats}
        """
        base_filter = [
            Attendance.academy_id == academy_id,
            Attendance.attendance_date >= start_date,
            Attendance.attendance_date <= end_date,
        ]

        # 1) summary: 전체 기간 출석 상태별 집계
        summary_row = db.query(
            func.count().label("total"),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label("present"),
            func.sum(case((Attendance.status == AttendanceStatus.LATE, 1), else_=0)).label("late"),
            func.sum(case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)).label("absent"),
            func.sum(case((Attendance.status == AttendanceStatus.EARLY_LEAVE, 1), else_=0)).label("early"),
        ).filter(*base_filter).first()

        summary = {
            "total": summary_row.total or 0,
            "present": int(summary_row.present or 0),
            "late": int(summary_row.late or 0),
            "absent": int(summary_row.absent or 0),
            "early": int(summary_row.early or 0),
        }

        # 2) daily_stats: 날짜별 집계
        daily_rows = db.query(
            Attendance.attendance_date.label("date"),
            func.count().label("total"),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label("present"),
            func.sum(case((Attendance.status == AttendanceStatus.LATE, 1), else_=0)).label("late"),
            func.sum(case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)).label("absent"),
            func.sum(case((Attendance.status == AttendanceStatus.EARLY_LEAVE, 1), else_=0)).label("early"),
        ).filter(
            *base_filter
        ).group_by(
            Attendance.attendance_date
        ).order_by(
            Attendance.attendance_date
        ).all()

        daily_stats = [
            {
                "date": row.date,
                "total": row.total or 0,
                "present": int(row.present or 0),
                "late": int(row.late or 0),
                "absent": int(row.absent or 0),
                "early": int(row.early or 0),
            }
            for row in daily_rows
        ]

        # 3) class_stats: 반별 집계
        class_rows = db.query(
            Student.class_id,
            Class.class_name,
            func.count(func.distinct(Attendance.student_id)).label("total_students"),
            func.count().label("total_records"),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label("present"),
            func.sum(case((Attendance.status == AttendanceStatus.LATE, 1), else_=0)).label("late"),
            func.sum(case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)).label("absent"),
            func.sum(case((Attendance.status == AttendanceStatus.EARLY_LEAVE, 1), else_=0)).label("early"),
        ).select_from(Attendance).join(
            Student, Attendance.student_id == Student.student_id
        ).outerjoin(
            Class, Student.class_id == Class.class_id
        ).filter(
            *base_filter
        ).group_by(
            Student.class_id, Class.class_name
        ).all()

        class_stats = []
        for row in class_rows:
            total_records = row.total_records or 0
            present = int(row.present or 0)
            attendance_rate = round((present / total_records) * 100, 1) if total_records > 0 else 0.0
            class_stats.append({
                "class_id": row.class_id,
                "class_name": row.class_name,
                "total_students": row.total_students or 0,
                "total_records": total_records,
                "present": present,
                "late": int(row.late or 0),
                "absent": int(row.absent or 0),
                "early": int(row.early or 0),
                "attendance_rate": attendance_rate,
            })

        return {
            "summary": summary,
            "daily_stats": daily_stats,
            "class_stats": class_stats,
        }

    # ==================== 관리자용 메서드 ====================

    @staticmethod
    def get_student_attendance_list(
        db: Session,
        academy_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        class_id: Optional[int] = None,
        student_id: Optional[int] = None,
        status: Optional[AttendanceStatus] = None,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int, AttendanceStats]:
        """
        기간별 학생 출결 조회 (관리자용)

        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            start_date: 조회 시작일
            end_date: 조회 종료일
            class_id: 반 ID 필터 (선택)
            student_id: 학생 ID 필터 (선택)
            status: 출결 상태 필터 (선택)
            page: 페이지 번호
            limit: 페이지당 항목 수

        Returns:
            Tuple[List[Dict], int, AttendanceStats]: (출결 기록 목록, 전체 개수, 통계)
        """
        # 기본 쿼리 (학생/반 정보 JOIN)
        query = db.query(
            Attendance,
            Student.name.label("student_name"),
            Student.class_id,
            Class.class_name
        ).join(
            Student, Attendance.student_id == Student.student_id
        ).outerjoin(
            Class, Student.class_id == Class.class_id
        ).filter(
            Attendance.academy_id == academy_id
        )

        # 기간 필터
        if start_date:
            query = query.filter(Attendance.attendance_date >= start_date)
        if end_date:
            query = query.filter(Attendance.attendance_date <= end_date)

        # 반 필터
        if class_id:
            query = query.filter(Student.class_id == class_id)

        # 학생 필터
        if student_id:
            query = query.filter(Attendance.student_id == student_id)

        # 상태 필터
        if status:
            query = query.filter(Attendance.status == status)

        # 전체 개수
        total = query.count()

        # 통계 계산 (SQLAlchemy case 문 사용 - DB 호환성)
        stats_query = db.query(
            func.count().label("total"),
            func.sum(case((Attendance.status == AttendanceStatus.PRESENT, 1), else_=0)).label("present"),
            func.sum(case((Attendance.status == AttendanceStatus.LATE, 1), else_=0)).label("late"),
            func.sum(case((Attendance.status == AttendanceStatus.ABSENT, 1), else_=0)).label("absent"),
            func.sum(case((Attendance.status == AttendanceStatus.EARLY_LEAVE, 1), else_=0)).label("early")
        ).select_from(Attendance).join(
            Student, Attendance.student_id == Student.student_id
        ).filter(Attendance.academy_id == academy_id)

        if start_date:
            stats_query = stats_query.filter(Attendance.attendance_date >= start_date)
        if end_date:
            stats_query = stats_query.filter(Attendance.attendance_date <= end_date)
        if class_id:
            stats_query = stats_query.filter(Student.class_id == class_id)
        if student_id:
            stats_query = stats_query.filter(Attendance.student_id == student_id)
        if status:
            stats_query = stats_query.filter(Attendance.status == status)

        stats_result = stats_query.first()
        stats = AttendanceStats(
            total=stats_result.total or 0,
            present=int(stats_result.present or 0),
            late=int(stats_result.late or 0),
            absent=int(stats_result.absent or 0),
            early=int(stats_result.early or 0)
        )

        # 페이지네이션 (최신순)
        offset = (page - 1) * limit
        records = query.order_by(
            Attendance.attendance_date.desc(),
            Student.name
        ).offset(offset).limit(limit).all()

        # 결과 변환
        result = []
        for att, student_name, s_class_id, class_name in records:
            result.append({
                "att_id": att.att_id,
                "student_id": att.student_id,
                "student_name": student_name,
                "class_id": s_class_id,
                "class_name": class_name,
                "attendance_date": att.attendance_date,
                "status": get_display_status(att.status.value, att.check_out_at),
                "check_in_at": att.check_in_at,
                "check_out_at": att.check_out_at,
                "memo": att.memo
            })

        return result, total, stats

    @staticmethod
    def admin_create_attendance(
        db: Session,
        academy_id: int,
        student_id: int,
        attendance_date: date,
        status: AttendanceStatus,
        check_in_at: Optional[datetime] = None,
        memo: Optional[str] = None
    ) -> Attendance:
        """
        관리자 권한 학생 출결 생성

        Args:
            db: 데이터베이스 세션
            academy_id: 학원 ID
            student_id: 학생 ID
            attendance_date: 출결 날짜
            status: 출결 상태
            check_in_at: 등원 시간 (선택)
            memo: 메모 (선택)

        Returns:
            Attendance: 생성된 출결 기록

        Raises:
            ValueError: 학생을 찾을 수 없거나 중복 기록인 경우
        """
        # 학생 확인 (해당 학원 소속인지)
        student = db.query(Student).filter(
            and_(
                Student.student_id == student_id,
                Student.academy_id == academy_id
            )
        ).first()

        if not student:
            raise ValueError("해당 학원에 소속된 학생을 찾을 수 없습니다")

        # 중복 체크
        existing = db.query(Attendance).filter(
            and_(
                Attendance.student_id == student_id,
                Attendance.attendance_date == attendance_date
            )
        ).first()

        if existing:
            raise ValueError("해당 날짜에 이미 출결 기록이 존재합니다")

        # 출결 기록 생성
        new_record = Attendance(
            student_id=student_id,
            academy_id=academy_id,
            attendance_date=attendance_date,
            status=status,
            check_in_at=check_in_at or (datetime.now() if status != AttendanceStatus.ABSENT else None),
            method=AttendanceMethod.MANUAL,
            is_notified=False,
            memo=memo
        )

        db.add(new_record)
        db.commit()
        db.refresh(new_record)

        return new_record

    @staticmethod
    def admin_update_attendance(
        db: Session,
        att_id: int,
        academy_id: int,
        status: Optional[AttendanceStatus] = None,
        check_in_at: Optional[datetime] = None,
        check_out_at: Optional[datetime] = None,
        memo: Optional[str] = None
    ) -> Attendance:
        """
        관리자 권한 학생 출결 수정

        Args:
            db: 데이터베이스 세션
            att_id: 출결 기록 ID
            academy_id: 학원 ID (권한 검증용)
            status: 출결 상태 (선택)
            check_in_at: 등원 시간 (선택)
            check_out_at: 하원 시간 (선택)
            memo: 메모 (선택)

        Returns:
            Attendance: 수정된 출결 기록

        Raises:
            ValueError: 출결 기록을 찾을 수 없거나 권한이 없는 경우
        """
        # 출결 기록 조회
        attendance = db.query(Attendance).filter(
            Attendance.att_id == att_id
        ).first()

        if not attendance:
            raise ValueError("출결 기록을 찾을 수 없습니다")

        # 학원 소속 확인
        if attendance.academy_id != academy_id:
            raise ValueError("해당 출결 기록에 대한 권한이 없습니다")

        # 필드 업데이트
        if status is not None:
            attendance.status = status
        if check_in_at is not None:
            attendance.check_in_at = check_in_at
        if check_out_at is not None:
            attendance.check_out_at = check_out_at
        if memo is not None:
            attendance.memo = memo

        db.commit()
        db.refresh(attendance)

        return attendance
