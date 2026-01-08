from sqlalchemy.orm import Session
from datetime import datetime, date
from app.models.attendance import Attendance, AttendanceStatus, AttendanceMethod
from app.models.student import Student
from app.schemas.attendance import AttendanceResponse
from typing import Optional

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
    def get_today_attendance(db: Session) -> list:
        today = date.today()
        students = db.query(Student).all()
        
        result = []
        for student in students:
            # 해당 학생의 오늘 출결 기록 조회
            att = db.query(Attendance).filter(
                Attendance.student_id == student.student_id,
                Attendance.attendance_date == today
            ).first()
            
            result.append({
                "student": student,
                "attendance": att
            })
        return result
