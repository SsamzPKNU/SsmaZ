"""
학생 포털 API 테스트
Student Portal API의 주요 엔드포인트를 테스트합니다.
"""

import pytest
from datetime import date


class TestStudentSchedule:
    """학생 스케줄 API 테스트"""

    def test_unauthorized_access(self, client):
        """비인증 접근 거부"""
        response = client.get("/api/student/schedules")
        assert response.status_code == 401

    def test_non_student_access_forbidden(self, client, admin_headers, admin_user):
        """학생이 아닌 역할로 접근 시 401 또는 403 에러"""
        response = client.get(
            "/api/student/schedules",
            headers=admin_headers
        )
        # 인증 실패(401) 또는 권한 부족(403) 모두 허용
        assert response.status_code in [401, 403]

    def test_get_schedules_all_success(self, client, student_headers):
        """type=all 스케줄 조회 성공 (500 에러 수정 검증)"""
        response = client.get(
            "/api/student/schedules",
            params={"type": "all"},
            headers=student_headers
        )
        assert response.status_code == 200
        data = response.json()

        # 응답 스키마 검증
        assert "student_id" in data
        assert "student_name" in data
        assert "start_date" in data
        assert "end_date" in data
        assert "weekly_schedule" in data
        assert "events" in data

        # weekly_schedule 구조 검증
        assert isinstance(data["weekly_schedule"], list)

        # events 구조 검증
        assert isinstance(data["events"], list)

    def test_get_schedules_default_type(self, client, student_headers):
        """기본 타입 (all) 스케줄 조회"""
        response = client.get(
            "/api/student/schedules",
            headers=student_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "weekly_schedule" in data
        assert "events" in data

    def test_get_schedules_assignment_type(self, client, student_headers):
        """type=assignment 스케줄 조회"""
        response = client.get(
            "/api/student/schedules",
            params={"type": "assignment"},
            headers=student_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "events" in data

    def test_get_schedules_with_date_range(self, client, student_headers):
        """날짜 범위 지정 스케줄 조회"""
        today = date.today()
        response = client.get(
            "/api/student/schedules",
            params={
                "start_date": today.isoformat(),
                "end_date": today.isoformat()
            },
            headers=student_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["start_date"] == today.isoformat()
        assert data["end_date"] == today.isoformat()


class TestStudentScheduleSingular:
    """학생 스케줄 단수형 API 테스트 (/api/student/schedule)"""

    def test_schedule_singular_endpoint(self, client, student_headers):
        """단수형 엔드포인트도 동일하게 동작"""
        response = client.get(
            "/api/student/schedule",
            params={"type": "all"},
            headers=student_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "weekly_schedule" in data
        assert "events" in data


class TestStudentDashboard:
    """학생 대시보드 API 테스트"""

    def test_unauthorized_access(self, client):
        """비인증 접근 거부"""
        response = client.get("/api/student/dashboard")
        assert response.status_code == 401

    def test_get_dashboard_success(self, client, student_headers):
        """대시보드 조회 성공"""
        response = client.get(
            "/api/student/dashboard",
            headers=student_headers
        )
        assert response.status_code == 200
        data = response.json()

        # 응답 스키마 검증
        assert "student_id" in data
        assert "student_name" in data
        assert "attendance" in data
        assert "assignments" in data
        assert "today_classes" in data


class TestStudentAttendance:
    """학생 출결 API 테스트"""

    def test_unauthorized_access(self, client):
        """비인증 접근 거부"""
        response = client.get("/api/student/attendance")
        assert response.status_code == 401

    def test_get_attendance_success(self, client, student_headers):
        """출결 조회 성공"""
        response = client.get(
            "/api/student/attendance",
            headers=student_headers
        )
        assert response.status_code == 200
        data = response.json()

        # 응답 스키마 검증
        assert "student_id" in data
        assert "student_name" in data
        assert "year" in data
        assert "month" in data
        assert "summary" in data
        assert "records" in data

    def test_get_attendance_with_year_month(self, client, student_headers):
        """연도/월 지정 출결 조회"""
        response = client.get(
            "/api/student/attendance",
            params={"year": 2024, "month": 1},
            headers=student_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["year"] == 2024
        assert data["month"] == 1


class TestStudentPayments:
    """학생 수납 API 테스트"""

    def test_unauthorized_access(self, client):
        """비인증 접근 거부"""
        response = client.get("/api/student/payments")
        assert response.status_code == 401

    def test_get_payments_success(self, client, student_headers):
        """수납 조회 성공"""
        response = client.get(
            "/api/student/payments",
            headers=student_headers
        )
        assert response.status_code == 200
        data = response.json()

        # 응답 스키마 검증
        assert "student_id" in data
        assert "student_name" in data
        assert "year" in data
        assert "summary" in data
        assert "monthly" in data
        assert "records" in data


class TestStudentGrades:
    """학생 성적 API 테스트"""

    def test_unauthorized_access(self, client):
        """비인증 접근 거부"""
        response = client.get("/api/student/grades")
        assert response.status_code == 401

    def test_get_grades_success(self, client, student_headers):
        """성적 조회 성공"""
        response = client.get(
            "/api/student/grades",
            headers=student_headers
        )
        assert response.status_code == 200
        data = response.json()

        # 응답 스키마 검증
        assert "student_id" in data
        assert "student_name" in data
        assert "total_count" in data
        assert "average_percentage" in data
        assert "grades" in data


class TestStudentAssignments:
    """학생 과제 API 테스트"""

    def test_unauthorized_access(self, client):
        """비인증 접근 거부"""
        response = client.get("/api/student/assignments")
        assert response.status_code == 401

    def test_get_assignments_success(self, client, student_headers):
        """과제 목록 조회 성공"""
        response = client.get(
            "/api/student/assignments",
            headers=student_headers
        )
        assert response.status_code == 200
        data = response.json()

        # 응답 스키마 검증
        assert "student_id" in data
        assert "student_name" in data
        assert "total_count" in data
        assert "assignments" in data

    def test_get_assignments_remaining(self, client, student_headers):
        """미완료 과제만 조회"""
        response = client.get(
            "/api/student/assignments",
            params={"status": "remaining"},
            headers=student_headers
        )
        assert response.status_code == 200

    def test_get_assignments_completed(self, client, student_headers):
        """완료 과제만 조회"""
        response = client.get(
            "/api/student/assignments",
            params={"status": "completed"},
            headers=student_headers
        )
        assert response.status_code == 200
