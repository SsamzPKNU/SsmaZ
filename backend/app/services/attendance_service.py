from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, date
from app.models.attendance import Attendance, AttendanceStatus, AttendanceMethod
from app.models.student import Student
from app.schemas.attendance import AttendanceResponse, AttendanceStats, AttendanceBatchItem
from typing import Optional, List, Tuple

def send_sms_notification(parent_phone: str, message: str) -> bool:
    """
    (가상) SMS 발송 함수 (인터페이스만 구현)
    실제 서비스(Solapi 등) 연동 시 여기에 구현
    """
    print(f"[SMS 발송] To: {parent_phone} / Msg: {message}")
    # 가상으로 성공 처리
    return True

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
