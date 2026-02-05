"""
관리자 출결 API 테스트
- 비인증 사용자 접근 거부 (401)
- TEACHER 권한으로 ADMIN API 접근 거부 (403)
- 기간별 학생 출결 조회
- 기간별 선생님 출퇴근 조회
- 학생 출결 생성/수정
- 선생님 출퇴근 수정
"""

import pytest
from datetime import date, datetime, timedelta
from fastapi.testclient import TestClient


class TestAdminStudentAttendance:
    """관리자용 학생 출결 API 테스트"""

    def test_unauthorized_access(self, client: TestClient):
        """비인증 사용자 접근 거부 (401)"""
        response = client.get("/admin/student-attendance/list")
        assert response.status_code == 401

    def test_teacher_forbidden(
        self, client: TestClient, teacher_headers: dict, students, attendance_records
    ):
        """TEACHER 권한으로 ADMIN API 접근 거부 (403)"""
        response = client.get(
            "/admin/student-attendance/list",
            headers=teacher_headers
        )
        assert response.status_code == 403
        assert "관리자 권한" in response.json()["detail"]

    def test_get_student_attendance_list_success(
        self, client: TestClient, admin_headers: dict, students, attendance_records
    ):
        """기간별 학생 출결 조회 성공"""
        today = date.today()
        response = client.get(
            "/admin/student-attendance/list",
            params={
                "start_date": (today - timedelta(days=7)).isoformat(),
                "end_date": today.isoformat(),
                "page": 1,
                "limit": 20
            },
            headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "records" in data
        assert "total" in data
        assert "stats" in data
        assert data["page"] == 1
        assert data["limit"] == 20

        # 통계 확인
        stats = data["stats"]
        assert "total" in stats
        assert "present" in stats
        assert "late" in stats
        assert "absent" in stats
        assert "early" in stats

    def test_get_student_attendance_list_with_class_filter(
        self, client: TestClient, admin_headers: dict,
        test_class, students, attendance_records
    ):
        """반 ID 필터 적용 조회"""
        response = client.get(
            "/admin/student-attendance/list",
            params={"class_id": test_class.class_id},
            headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        # 해당 반 학생들만 조회됨
        for record in data["records"]:
            assert record["class_id"] == test_class.class_id

    def test_get_student_attendance_list_with_status_filter(
        self, client: TestClient, admin_headers: dict, students, attendance_records
    ):
        """출결 상태 필터 적용 조회"""
        response = client.get(
            "/admin/student-attendance/list",
            params={"status": "출석"},
            headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        for record in data["records"]:
            assert record["status"] == "출석"

    def test_get_student_attendance_list_invalid_status(
        self, client: TestClient, admin_headers: dict
    ):
        """유효하지 않은 출결 상태 필터"""
        response = client.get(
            "/admin/student-attendance/list",
            params={"status": "invalid_status"},
            headers=admin_headers
        )
        assert response.status_code == 400
        assert "유효하지 않은 출결 상태" in response.json()["detail"]

    def test_create_student_attendance_success(
        self, client: TestClient, admin_headers: dict, students
    ):
        """학생 출결 생성 성공"""
        # 출결 기록이 없는 날짜 사용
        tomorrow = date.today() + timedelta(days=1)

        response = client.post(
            "/admin/student-attendance",
            json={
                "student_id": students[0].student_id,
                "attendance_date": tomorrow.isoformat(),
                "status": "출석",
                "memo": "테스트 출결"
            },
            headers=admin_headers
        )
        assert response.status_code == 201

        data = response.json()
        assert data["student_id"] == students[0].student_id
        assert data["status"] == "출석"
        assert data["memo"] == "테스트 출결"

    def test_create_student_attendance_duplicate(
        self, client: TestClient, admin_headers: dict, students, attendance_records
    ):
        """중복 출결 기록 생성 실패"""
        today = date.today()

        response = client.post(
            "/admin/student-attendance",
            json={
                "student_id": students[0].student_id,
                "attendance_date": today.isoformat(),
                "status": "출석"
            },
            headers=admin_headers
        )
        assert response.status_code == 400
        assert "이미 출결 기록이 존재" in response.json()["detail"]

    def test_create_student_attendance_invalid_student(
        self, client: TestClient, admin_headers: dict
    ):
        """존재하지 않는 학생 출결 생성 실패"""
        response = client.post(
            "/admin/student-attendance",
            json={
                "student_id": 99999,
                "attendance_date": date.today().isoformat(),
                "status": "출석"
            },
            headers=admin_headers
        )
        assert response.status_code == 400
        assert "학생을 찾을 수 없" in response.json()["detail"]

    def test_update_student_attendance_success(
        self, client: TestClient, admin_headers: dict, attendance_records
    ):
        """학생 출결 수정 성공"""
        att_id = attendance_records[0].att_id

        response = client.patch(
            f"/admin/student-attendance/{att_id}",
            json={
                "status": "지각",
                "memo": "수정된 메모"
            },
            headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "지각"
        assert data["memo"] == "수정된 메모"

    def test_update_student_attendance_not_found(
        self, client: TestClient, admin_headers: dict
    ):
        """존재하지 않는 출결 기록 수정 실패"""
        response = client.patch(
            "/admin/student-attendance/99999",
            json={"status": "출석"},
            headers=admin_headers
        )
        assert response.status_code == 400
        assert "출결 기록을 찾을 수 없" in response.json()["detail"]


class TestAdminTeacherAttendance:
    """관리자용 선생님 출퇴근 API 테스트"""

    def test_unauthorized_access(self, client: TestClient):
        """비인증 사용자 접근 거부 (401)"""
        response = client.get("/admin/teacher-attendance/list")
        assert response.status_code == 401

    def test_teacher_forbidden(
        self, client: TestClient, teacher_headers: dict
    ):
        """TEACHER 권한으로 ADMIN API 접근 거부 (403)"""
        response = client.get(
            "/admin/teacher-attendance/list",
            headers=teacher_headers
        )
        assert response.status_code == 403

    def test_get_teacher_attendance_list_success(
        self, client: TestClient, admin_headers: dict,
        teacher, another_teacher, teacher_attendance_records
    ):
        """기간별 선생님 출퇴근 조회 성공"""
        today = date.today()
        response = client.get(
            "/admin/teacher-attendance/list",
            params={
                "start_date": (today - timedelta(days=7)).isoformat(),
                "end_date": today.isoformat(),
                "page": 1,
                "limit": 20
            },
            headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert "records" in data
        assert "total" in data
        assert data["page"] == 1
        assert data["limit"] == 20

    def test_get_teacher_attendance_list_with_teacher_filter(
        self, client: TestClient, admin_headers: dict,
        teacher, teacher_attendance_records
    ):
        """선생님 ID 필터 적용 조회"""
        response = client.get(
            "/admin/teacher-attendance/list",
            params={"teacher_id": teacher.teacher_id},
            headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        for record in data["records"]:
            assert record["teacher_id"] == teacher.teacher_id

    def test_get_teacher_attendance_list_with_approval_filter(
        self, client: TestClient, admin_headers: dict, teacher_attendance_records
    ):
        """승인 여부 필터 적용 조회"""
        response = client.get(
            "/admin/teacher-attendance/list",
            params={"is_approved": True},
            headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        for record in data["records"]:
            assert record["is_approved"] is True

    def test_update_teacher_attendance_success(
        self, client: TestClient, admin_headers: dict, teacher_attendance_records
    ):
        """선생님 출퇴근 기록 수정 성공"""
        record_id = teacher_attendance_records[0].id
        new_check_in = datetime.now().replace(hour=8, minute=30).isoformat()

        response = client.patch(
            f"/admin/teacher-attendance/{record_id}",
            json={
                "check_in_time": new_check_in,
                "is_approved": True
            },
            headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["is_approved"] is True

    def test_update_teacher_attendance_not_found(
        self, client: TestClient, admin_headers: dict
    ):
        """존재하지 않는 출퇴근 기록 수정 실패"""
        response = client.patch(
            "/admin/teacher-attendance/99999",
            json={"is_approved": True},
            headers=admin_headers
        )
        assert response.status_code == 404

    def test_approve_teacher_attendance(
        self, client: TestClient, admin_headers: dict, teacher_attendance_records
    ):
        """선생님 출퇴근 승인"""
        # 미승인 기록 찾기
        unapproved = next(r for r in teacher_attendance_records if not r.is_approved)

        response = client.patch(
            f"/admin/attendance/{unapproved.id}/approve",
            headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["is_approved"] is True

    def test_approve_already_approved(
        self, client: TestClient, admin_headers: dict, teacher_attendance_records
    ):
        """이미 승인된 기록 재승인 시도"""
        # 승인된 기록 찾기
        approved = next(r for r in teacher_attendance_records if r.is_approved)

        response = client.patch(
            f"/admin/attendance/{approved.id}/approve",
            headers=admin_headers
        )
        assert response.status_code == 400
        assert "이미 승인된" in response.json()["detail"]


class TestAdminAttendancePagination:
    """페이지네이션 테스트"""

    def test_student_attendance_pagination(
        self, client: TestClient, admin_headers: dict, students, attendance_records
    ):
        """학생 출결 페이지네이션"""
        # 첫 페이지
        response1 = client.get(
            "/admin/student-attendance/list",
            params={"page": 1, "limit": 5},
            headers=admin_headers
        )
        assert response1.status_code == 200
        data1 = response1.json()

        # 두 번째 페이지
        response2 = client.get(
            "/admin/student-attendance/list",
            params={"page": 2, "limit": 5},
            headers=admin_headers
        )
        assert response2.status_code == 200
        data2 = response2.json()

        # 페이지 정보 확인
        assert data1["page"] == 1
        assert data2["page"] == 2
        assert len(data1["records"]) <= 5
        assert len(data2["records"]) <= 5

    def test_teacher_attendance_pagination(
        self, client: TestClient, admin_headers: dict, teacher_attendance_records
    ):
        """선생님 출퇴근 페이지네이션"""
        response = client.get(
            "/admin/teacher-attendance/list",
            params={"page": 1, "limit": 5},
            headers=admin_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["page"] == 1
        assert len(data["records"]) <= 5
