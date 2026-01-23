"""
선생님용 앱 비즈니스 로직
선생님이 담당하는 반과 학생 관리 기능 제공
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException, status
from app.models.user import User
from app.models.teacher import Teacher
from app.models.class_model import Class
from app.models.student import Student
from app.models.attendance import Attendance, AttendanceStatus
from app.schemas.teacher_app import (
    TeacherDashboardResponse,
    TeacherClassResponse,
    TeacherStudentResponse,
    StudentDetailResponse,
    AttendanceRecordResponse,
    AttendanceCreateRequest
)
from typing import List, Optional
from datetime import date, datetime, timedelta


class TeacherAppService:
    """선생님용 앱 서비스 클래스"""
    
    @staticmethod
    def get_teacher_id(db: Session, user_id: int, academy_id: int) -> int:
        """
        User ID로 Teacher ID 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            academy_id: 학원 ID
            
        Returns:
            int: Teacher ID
            
        Raises:
            HTTPException: Teacher 정보를 찾을 수 없는 경우
        """
        teacher = db.query(Teacher).filter(
            and_(
                Teacher.user_id == user_id,
                Teacher.academy_id == academy_id
            )
        ).first()
        
        if not teacher:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="선생님 정보를 찾을 수 없습니다"
            )
        
        return teacher.teacher_id
    
    @staticmethod
    def verify_class_teacher(db: Session, class_id: int, teacher_id: int) -> bool:
        """
        선생님이 해당 반의 담당인지 확인
        
        Args:
            db: 데이터베이스 세션
            class_id: 반 ID
            teacher_id: 선생님 ID
            
        Returns:
            bool: 담당 선생님 여부
        """
        class_obj = db.query(Class).filter(
            and_(
                Class.class_id == class_id,
                Class.teacher_id == teacher_id
            )
        ).first()
        
        return class_obj is not None
    
    @staticmethod
    def verify_student_teacher(db: Session, student_id: int, teacher_id: int, academy_id: int) -> bool:
        """
        선생님이 해당 학생의 담당인지 확인
        (학생이 선생님의 담당 반에 속해있는지 확인)
        
        Args:
            db: 데이터베이스 세션
            student_id: 학생 ID
            teacher_id: 선생님 ID
            academy_id: 학원 ID
            
        Returns:
            bool: 담당 학생 여부
        """
        student = db.query(Student).filter(
            and_(
                Student.student_id == student_id,
                Student.academy_id == academy_id
            )
        ).first()
        
        if not student or not student.class_id:
            return False
        
        return TeacherAppService.verify_class_teacher(db, student.class_id, teacher_id)
    
    @staticmethod
    def get_teacher_dashboard(db: Session, user_id: int, academy_id: int) -> TeacherDashboardResponse:
        """
        선생님 대시보드 데이터 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            academy_id: 학원 ID
            
        Returns:
            TeacherDashboardResponse: 대시보드 데이터
        """
        teacher_id = TeacherAppService.get_teacher_id(db, user_id, academy_id)
        
        # 담당 반 수
        total_classes = db.query(Class).filter(Class.teacher_id == teacher_id).count()
        
        # 담당 학생 수 (담당 반에 속한 학생들)
        total_students = db.query(Student).join(Class).filter(
            and_(
                Class.teacher_id == teacher_id,
                Student.class_id == Class.class_id
            )
        ).count()
        
        # 오늘 출석률
        today = date.today()
        if total_students > 0:
            attended = db.query(Attendance).join(Student).join(Class).filter(
                and_(
                    Class.teacher_id == teacher_id,
                    Attendance.attendance_date == today,
                    Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE])
                )
            ).count()
            today_attendance_rate = round((attended / total_students) * 100, 1)
        else:
            today_attendance_rate = 0.0
        
        # 이번 달 수납률 (현재는 더미 데이터)
        # TODO: Payment 테이블 연동 후 실제 계산
        monthly_collection_rate = 88.0
        
        return TeacherDashboardResponse(
            total_classes=total_classes,
            total_students=total_students,
            today_attendance_rate=today_attendance_rate,
            monthly_collection_rate=monthly_collection_rate
        )
    
    @staticmethod
    def get_teacher_classes(db: Session, user_id: int, academy_id: int) -> List[TeacherClassResponse]:
        """
        선생님의 담당 반 목록 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            academy_id: 학원 ID
            
        Returns:
            List[TeacherClassResponse]: 담당 반 목록
        """
        teacher_id = TeacherAppService.get_teacher_id(db, user_id, academy_id)
        
        classes = db.query(Class).filter(Class.teacher_id == teacher_id).all()
        
        result = []
        for class_obj in classes:
            # 반별 학생 수 계산
            student_count = db.query(Student).filter(Student.class_id == class_obj.class_id).count()
            
            result.append(TeacherClassResponse(
                id=class_obj.class_id,
                name=class_obj.name,
                schedule=class_obj.schedule,
                student_count=student_count,
                capacity=class_obj.capacity
            ))
        
        return result
    
    @staticmethod
    def get_class_students(
        db: Session,
        class_id: int,
        user_id: int,
        academy_id: int
    ) -> List[TeacherStudentResponse]:
        """
        특정 반의 학생 목록 조회
        
        Args:
            db: 데이터베이스 세션
            class_id: 반 ID
            user_id: 사용자 ID
            academy_id: 학원 ID
            
        Returns:
            List[TeacherStudentResponse]: 학생 목록
            
        Raises:
            HTTPException: 권한이 없거나 반을 찾을 수 없는 경우
        """
        teacher_id = TeacherAppService.get_teacher_id(db, user_id, academy_id)
        
        # 권한 확인
        if not TeacherAppService.verify_class_teacher(db, class_id, teacher_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="해당 반의 담당 선생님이 아닙니다"
            )
        
        # 반 정보 조회
        class_obj = db.query(Class).filter(Class.class_id == class_id).first()
        if not class_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="반을 찾을 수 없습니다"
            )
        
        # 학생 목록 조회
        students = db.query(Student).filter(Student.class_id == class_id).all()
        
        result = []
        for student in students:
            result.append(TeacherStudentResponse(
                id=student.student_id,
                name=student.name,
                grade=student.grade,
                school=student.school,
                phone=student.phone,
                parent_phone=student.parent_phone,
                class_name=class_obj.name
            ))
        
        return result
    
    @staticmethod
    def get_student_detail(
        db: Session,
        student_id: int,
        user_id: int,
        academy_id: int
    ) -> StudentDetailResponse:
        """
        학생 상세 정보 조회
        
        Args:
            db: 데이터베이스 세션
            student_id: 학생 ID
            user_id: 사용자 ID
            academy_id: 학원 ID
            
        Returns:
            StudentDetailResponse: 학생 상세 정보
            
        Raises:
            HTTPException: 권한이 없거나 학생을 찾을 수 없는 경우
        """
        teacher_id = TeacherAppService.get_teacher_id(db, user_id, academy_id)
        
        # 학생 조회
        student = db.query(Student).filter(
            and_(
                Student.student_id == student_id,
                Student.academy_id == academy_id
            )
        ).first()
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="학생을 찾을 수 없습니다"
            )
        
        # 권한 확인
        if not TeacherAppService.verify_student_teacher(db, student_id, teacher_id, academy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="해당 학생의 담당 선생님이 아닙니다"
            )
        
        # 반 이름 조회
        class_name = None
        if student.class_id:
            class_obj = db.query(Class).filter(Class.class_id == student.class_id).first()
            class_name = class_obj.name if class_obj else None
        
        # 최근 30일 출석률 계산
        thirty_days_ago = date.today() - timedelta(days=30)
        total_days = db.query(Attendance).filter(
            and_(
                Attendance.student_id == student_id,
                Attendance.attendance_date >= thirty_days_ago
            )
        ).count()
        
        attended_days = db.query(Attendance).filter(
            and_(
                Attendance.student_id == student_id,
                Attendance.attendance_date >= thirty_days_ago,
                Attendance.status.in_([AttendanceStatus.PRESENT, AttendanceStatus.LATE])
            )
        ).count()
        
        attendance_rate = round((attended_days / total_days * 100), 1) if total_days > 0 else 0.0
        
        # 최근 출결 기록 (5건)
        recent_records = db.query(Attendance).filter(
            Attendance.student_id == student_id
        ).order_by(Attendance.attendance_date.desc()).limit(5).all()
        
        recent_attendance = [
            {
                "date": record.attendance_date.isoformat(),
                "status": record.status.value
            }
            for record in recent_records
        ]
        
        return StudentDetailResponse(
            id=student.student_id,
            name=student.name,
            grade=student.grade,
            school=student.school,
            phone=student.phone,
            parent_phone=student.parent_phone,
            enrollment_date=student.enrollment_date,
            status=student.status.value,
            class_id=student.class_id,
            class_name=class_name,
            attendance_rate=attendance_rate,
            recent_attendance=recent_attendance
        )
    
    @staticmethod
    def get_student_attendance(
        db: Session,
        student_id: int,
        user_id: int,
        academy_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[AttendanceRecordResponse]:
        """
        학생 출결 기록 조회
        
        Args:
            db: 데이터베이스 세션
            student_id: 학생 ID
            user_id: 사용자 ID
            academy_id: 학원 ID
            start_date: 시작일 (선택)
            end_date: 종료일 (선택)
            
        Returns:
            List[AttendanceRecordResponse]: 출결 기록 목록
        """
        teacher_id = TeacherAppService.get_teacher_id(db, user_id, academy_id)
        
        # 권한 확인
        if not TeacherAppService.verify_student_teacher(db, student_id, teacher_id, academy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="해당 학생의 담당 선생님이 아닙니다"
            )
        
        # 기본 날짜 범위 설정 (최근 30일)
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # 출결 기록 조회
        records = db.query(Attendance).join(Student).filter(
            and_(
                Attendance.student_id == student_id,
                Attendance.attendance_date >= start_date,
                Attendance.attendance_date <= end_date
            )
        ).order_by(Attendance.attendance_date.desc()).all()
        
        result = []
        for record in records:
            result.append(AttendanceRecordResponse(
                id=record.attendance_id,
                student_id=record.student_id,
                student_name=record.student.name,
                attendance_date=record.attendance_date,
                status=record.status.value,
                check_in_time=record.check_in_at.strftime("%H:%M") if record.check_in_at else None,
                check_out_time=record.check_out_at.strftime("%H:%M") if record.check_out_at else None,
                memo=record.memo
            ))
        
        return result
    
    @staticmethod
    def create_attendance(
        db: Session,
        student_id: int,
        user_id: int,
        academy_id: int,
        attendance_data: AttendanceCreateRequest
    ) -> AttendanceRecordResponse:
        """
        출결 기록 등록
        
        Args:
            db: 데이터베이스 세션
            student_id: 학생 ID
            user_id: 사용자 ID
            academy_id: 학원 ID
            attendance_data: 출결 정보
            
        Returns:
            AttendanceRecordResponse: 등록된 출결 기록
        """
        teacher_id = TeacherAppService.get_teacher_id(db, user_id, academy_id)
        
        # 학생 조회
        student = db.query(Student).filter(
            and_(
                Student.student_id == student_id,
                Student.academy_id == academy_id
            )
        ).first()
        
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="학생을 찾을 수 없습니다"
            )
        
        # 권한 확인
        if not TeacherAppService.verify_student_teacher(db, student_id, teacher_id, academy_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="해당 학생의 담당 선생님이 아닙니다"
            )
        
        # 중복 체크 (같은 날짜에 이미 기록이 있는지)
        existing = db.query(Attendance).filter(
            and_(
                Attendance.student_id == student_id,
                Attendance.attendance_date == attendance_data.attendance_date
            )
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="해당 날짜에 이미 출결 기록이 존재합니다"
            )
        
        # 시간 파싱
        check_in_at = None
        check_out_at = None
        
        if attendance_data.check_in_time:
            hour, minute = map(int, attendance_data.check_in_time.split(':'))
            check_in_at = datetime.combine(attendance_data.attendance_date, datetime.min.time()).replace(hour=hour, minute=minute)
        
        if attendance_data.check_out_time:
            hour, minute = map(int, attendance_data.check_out_time.split(':'))
            check_out_at = datetime.combine(attendance_data.attendance_date, datetime.min.time()).replace(hour=hour, minute=minute)
        
        # 출결 기록 생성
        new_record = Attendance(
            student_id=student_id,
            academy_id=academy_id,
            attendance_date=attendance_data.attendance_date,
            status=attendance_data.status,
            check_in_at=check_in_at,
            check_out_at=check_out_at,
            memo=attendance_data.memo
        )
        
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        
        return AttendanceRecordResponse(
            id=new_record.attendance_id,
            student_id=new_record.student_id,
            student_name=student.name,
            attendance_date=new_record.attendance_date,
            status=new_record.status.value,
            check_in_time=attendance_data.check_in_time,
            check_out_time=attendance_data.check_out_time,
            memo=new_record.memo
        )
    
    @staticmethod
    def get_all_teacher_students(
        db: Session,
        user_id: int,
        academy_id: int
    ) -> List[TeacherStudentResponse]:
        """
        선생님이 담당하는 모든 학생 조회
        
        Args:
            db: 데이터베이스 세션
            user_id: 사용자 ID
            academy_id: 학원 ID
            
        Returns:
            List[TeacherStudentResponse]: 전체 학생 목록
        """
        teacher_id = TeacherAppService.get_teacher_id(db, user_id, academy_id)
        
        # 담당 반들의 학생 조회
        students = db.query(Student).join(Class).filter(
            Class.teacher_id == teacher_id
        ).all()
        
        result = []
        for student in students:
            class_obj = db.query(Class).filter(Class.class_id == student.class_id).first()
            class_name = class_obj.name if class_obj else None
            
            result.append(TeacherStudentResponse(
                id=student.student_id,
                name=student.name,
                grade=student.grade,
                school=student.school,
                phone=student.phone,
                parent_phone=student.parent_phone,
                class_name=class_name
            ))
        
        return result
