"""
테스트용 공통 픽스처
pytest에서 사용하는 테스트 데이터 및 설정
"""

import os
import pytest

# 테스트용 환경 변수 설정 (모듈 임포트 전에 설정 필요)
os.environ["SECRET_KEY"] = "test_secret_key_for_jwt_signing_minimum_32_chars"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import date, datetime, timedelta
from typing import Generator

from app.core.database import Base, get_db
from app.models.user import User, UserRole
from app.models.teacher import Teacher, TeacherStatus
from app.models.student import Student, StudentStatus
from app.models.class_model import Class
from app.models.attendance import Attendance, AttendanceStatus, AttendanceMethod
from app.models.teacher_attendance import TeacherAttendance
from app.models.student_contact import StudentContact
from app.core.security import hash_password

# main.py에서 app 가져오기
import sys
sys.path.insert(0, str(__file__).replace("\\tests\\conftest.py", "").replace("/tests/conftest.py", ""))
from main import app

# 테스트 환경에서 rate limiter 비활성화
from app.api.auth import limiter as auth_limiter
auth_limiter.enabled = False


# 테스트용 인메모리 SQLite 데이터베이스
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """
    테스트용 데이터베이스 세션 픽스처
    각 테스트마다 새로운 데이터베이스 생성
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """
    테스트용 FastAPI 클라이언트 픽스처
    db 픽스처와 동일한 세션을 사용하도록 오버라이드
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass  # db 픽스처에서 관리하므로 여기서 close하지 않음

    app.dependency_overrides[get_db] = override_get_db

    # 테스트 환경에서 rate limiter 비활성화
    if hasattr(app.state, 'limiter'):
        app.state.limiter.enabled = False

    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db) -> User:
    """관리자 사용자 픽스처"""
    user = User(
        academy_id=1,
        username="admin_test",
        password_hash=hash_password("testpass123"),
        user_role=UserRole.ADMIN,
        name="테스트 관리자",
        phone="010-0000-0001"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def teacher_user(db) -> User:
    """선생님 사용자 픽스처"""
    user = User(
        academy_id=1,
        username="teacher_test",
        password_hash=hash_password("testpass123"),
        user_role=UserRole.TEACHER,
        name="테스트 선생님",
        phone="010-0000-0002"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def teacher(db, teacher_user) -> Teacher:
    """선생님 정보 픽스처"""
    teacher = Teacher(
        user_id=teacher_user.user_id,
        academy_id=1,
        name="테스트 선생님",
        subject="수학",
        phone="010-0000-0002",
        status=TeacherStatus.ACTIVE,
        employment_type="FULL_TIME"
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


@pytest.fixture
def another_teacher_user(db) -> User:
    """다른 선생님 사용자 픽스처"""
    user = User(
        academy_id=1,
        username="teacher_test2",
        password_hash=hash_password("testpass123"),
        user_role=UserRole.TEACHER,
        name="다른 선생님",
        phone="010-0000-0003"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def another_teacher(db, another_teacher_user) -> Teacher:
    """다른 선생님 정보 픽스처"""
    teacher = Teacher(
        user_id=another_teacher_user.user_id,
        academy_id=1,
        name="다른 선생님",
        subject="영어",
        phone="010-0000-0003",
        status=TeacherStatus.ACTIVE,
        employment_type="PART_TIME",
        hourly_rate=15000
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


@pytest.fixture
def test_class(db, teacher) -> Class:
    """테스트용 반 픽스처"""
    class_obj = Class(
        academy_id=1,
        class_name="수학 정규반 A",
        teacher_id=teacher.teacher_id,
        capacity=15
    )
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    return class_obj


@pytest.fixture
def another_class(db, another_teacher) -> Class:
    """다른 선생님 담당 반 픽스처"""
    class_obj = Class(
        academy_id=1,
        class_name="영어 정규반 A",
        teacher_id=another_teacher.teacher_id,
        capacity=12
    )
    db.add(class_obj)
    db.commit()
    db.refresh(class_obj)
    return class_obj


@pytest.fixture
def students(db, test_class) -> list:
    """테스트용 학생 목록 픽스처"""
    student_list = []
    for i in range(3):
        student = Student(
            academy_id=1,
            class_id=test_class.class_id,
            name=f"학생{i+1}",
            parent_phone=f"010-111{i}-0000",
            status=StudentStatus.ENROLLED
        )
        db.add(student)
        student_list.append(student)

    db.commit()
    for s in student_list:
        db.refresh(s)

    return student_list


@pytest.fixture
def student_without_class(db) -> Student:
    """반에 속하지 않은 학생 픽스처 (다른 학원 소속)"""
    student = Student(
        academy_id=2,  # 다른 학원
        class_id=None,
        name="반 미배정 학생",
        parent_phone="010-9999-0000",
        status=StudentStatus.ENROLLED
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@pytest.fixture
def attendance_records(db, students) -> list:
    """테스트용 출결 기록 픽스처"""
    records = []
    today = date.today()

    for i, student in enumerate(students):
        # 오늘 출결 기록
        status = [AttendanceStatus.PRESENT, AttendanceStatus.LATE, AttendanceStatus.ABSENT][i]
        record = Attendance(
            student_id=student.student_id,
            academy_id=1,
            attendance_date=today,
            status=status,
            check_in_at=datetime.now() if status != AttendanceStatus.ABSENT else None,
            method=AttendanceMethod.MANUAL,
            is_notified=False
        )
        db.add(record)
        records.append(record)

        # 과거 출결 기록 (7일간)
        for day_offset in range(1, 8):
            past_record = Attendance(
                student_id=student.student_id,
                academy_id=1,
                attendance_date=today - timedelta(days=day_offset),
                status=AttendanceStatus.PRESENT,
                check_in_at=datetime.now() - timedelta(days=day_offset),
                method=AttendanceMethod.MANUAL,
                is_notified=False
            )
            db.add(past_record)
            records.append(past_record)

    db.commit()
    for r in records:
        db.refresh(r)

    return records


@pytest.fixture
def teacher_attendance_records(db, teacher, another_teacher) -> list:
    """테스트용 선생님 출퇴근 기록 픽스처"""
    records = []
    today = date.today()

    # 오늘 출퇴근 기록
    for t in [teacher, another_teacher]:
        record = TeacherAttendance(
            teacher_id=t.teacher_id,
            date=today,
            check_in_time=datetime.now().replace(hour=9, minute=0),
            check_out_time=datetime.now().replace(hour=18, minute=0) if t == teacher else None,
            worked_minutes=540 if t == teacher else 0,
            is_approved=False
        )
        db.add(record)
        records.append(record)

    # 과거 출퇴근 기록 (7일간)
    for day_offset in range(1, 8):
        for t in [teacher, another_teacher]:
            past_record = TeacherAttendance(
                teacher_id=t.teacher_id,
                date=today - timedelta(days=day_offset),
                check_in_time=(datetime.now() - timedelta(days=day_offset)).replace(hour=9, minute=0),
                check_out_time=(datetime.now() - timedelta(days=day_offset)).replace(hour=18, minute=0),
                worked_minutes=540,
                is_approved=day_offset < 4  # 최근 3일은 승인됨
            )
            db.add(past_record)
            records.append(past_record)

    db.commit()
    for r in records:
        db.refresh(r)

    return records


def do_login(client: TestClient, username: str, password: str) -> bool:
    """
    로그인 수행 (쿠키 기반 인증)

    Args:
        client: 테스트 클라이언트
        username: 사용자명
        password: 비밀번호

    Returns:
        bool: 로그인 성공 여부
    """
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password}
    )
    return response.status_code == 200


def get_auth_headers(client: TestClient, username: str, password: str) -> dict:
    """
    로그인 후 인증 헤더 반환 (Bearer 토큰 방식)

    Args:
        client: 테스트 클라이언트
        username: 사용자명
        password: 비밀번호

    Returns:
        dict: Authorization 헤더가 포함된 딕셔너리
    """
    response = client.post(
        "/auth/login-mobile",
        json={"username": username, "password": password}
    )

    if response.status_code == 200:
        token = response.json().get("access_token")
        return {"Authorization": f"Bearer {token}"}

    return {}


@pytest.fixture
def admin_headers(client, admin_user) -> dict:
    """관리자 인증 헤더 픽스처"""
    return get_auth_headers(client, "admin_test", "testpass123")


@pytest.fixture
def teacher_headers(client, teacher_user, teacher) -> dict:
    """선생님 인증 헤더 픽스처"""
    return get_auth_headers(client, "teacher_test", "testpass123")


@pytest.fixture
def another_teacher_headers(client, another_teacher_user, another_teacher) -> dict:
    """다른 선생님 인증 헤더 픽스처"""
    return get_auth_headers(client, "teacher_test2", "testpass123")


@pytest.fixture
def student_user(db) -> User:
    """학생 사용자 픽스처"""
    user = User(
        academy_id=1,
        username="student_test",
        password_hash=hash_password("testpass123"),
        user_role=UserRole.STUDENT,
        name="테스트 학생",
        phone="010-0000-0010"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def student_with_class(db, student_user, test_class) -> Student:
    """반에 배정된 학생 픽스처 (학생 사용자와 연결)"""
    student = Student(
        academy_id=1,
        class_id=test_class.class_id,
        user_id=student_user.user_id,
        name="테스트 학생",
        parent_phone="010-1234-5678",
        status=StudentStatus.ENROLLED
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@pytest.fixture
def student_contacts(db, students) -> list:
    """테스트용 학생 연락처 픽스처"""
    contacts = []
    for i, student in enumerate(students):
        contact = StudentContact(
            student_id=student.student_id,
            phone=f"010-{1000 + i}-0001",
            label="엄마",
            priority=1,
            is_active=True
        )
        db.add(contact)
        contacts.append(contact)
    db.commit()
    for c in contacts:
        db.refresh(c)
    return contacts


@pytest.fixture
def student_headers(client, student_with_class) -> dict:
    """학생 인증 헤더 픽스처 (student_with_class에 의존하여 올바른 순서 보장)"""
    return get_auth_headers(client, "student_test", "testpass123")
