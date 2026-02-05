"""
선생님 출결 API 테스트
- 비인증 사용자 접근 거부 (401)
- 담당하지 않는 반 접근 시 403
- 반 출결 현황 조회
- 출결 일괄 처리
- 학생 출결 수정
- 기간별 통계 조회
"""

import pytest
from datetime import date, datetime, timedelta
from fastapi.testclient import TestClient


class TestTeacherClassAttendance:
    """선생님용 반 출결 API 테스트"""

    def test_unauthorized_access(self, client: TestClient, test_class):
        """비인증 사용자 접근 거부 (401)"""
        response = client.get(f"/api/teacher/classes/{test_class.class_id}/attendance")
        assert response.status_code == 401

    def test_get_class_attendance_success(
        self, client: TestClient, teacher_headers: dict,
        test_class, students, attendance_records
    ):
        """반 출결 현황 조회 성공"""
        response = client.get(
            f"/api/teacher/classes/{test_class.class_id}/attendance",
            headers=teacher_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["class_id"] == test_class.class_id
        assert data["class_name"] == test_class.class_name
        assert "date" in data
        assert "stats" in data
        assert "students" in data

        # 통계 확인
        stats = data["stats"]
        assert stats["total"] == len(students)
        assert "present" in stats
        assert "late" in stats
        assert "absent" in stats
        assert "early" in stats
        assert "not_checked" in stats

        # 학생 목록 확인
        assert len(data["students"]) == len(students)

    def test_get_class_attendance_with_date(
        self, client: TestClient, teacher_headers: dict,
        test_class, students, attendance_records
    ):
        """특정 날짜 반 출결 현황 조회"""
        yesterday = date.today() - timedelta(days=1)

        response = client.get(
            f"/api/teacher/classes/{test_class.class_id}/attendance",
            params={"target_date": yesterday.isoformat()},
            headers=teacher_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["date"] == yesterday.isoformat()

    def test_get_class_attendance_forbidden(
        self, client: TestClient, teacher_headers: dict, another_class
    ):
        """담당하지 않는 반 접근 시 403"""
        response = client.get(
            f"/api/teacher/classes/{another_class.class_id}/attendance",
            headers=teacher_headers
        )
        assert response.status_code == 403
        assert "담당 선생님이 아닙니다" in response.json()["detail"]

    def test_get_class_attendance_not_found(
        self, client: TestClient, teacher_headers: dict
    ):
        """존재하지 않는 반 조회 시 403 (권한 검증 먼저)"""
        response = client.get(
            "/api/teacher/classes/99999/attendance",
            headers=teacher_headers
        )
        assert response.status_code == 403


class TestTeacherBatchAttendance:
    """선생님용 출결 일괄 처리 테스트"""

    def test_batch_attendance_success(
        self, client: TestClient, teacher_headers: dict,
        test_class, students
    ):
        """출결 일괄 처리 성공"""
        # 내일 날짜 사용 (기존 출결 기록이 없도록)
        tomorrow = date.today() + timedelta(days=1)

        response = client.post(
            f"/api/teacher/classes/{test_class.class_id}/attendance/batch",
            json={
                "date": tomorrow.isoformat(),
                "items": [
                    {"student_id": students[0].student_id, "status": "present"},
                    {"student_id": students[1].student_id, "status": "late"},
                    {"student_id": students[2].student_id, "status": "absent"}
                ]
            },
            headers=teacher_headers
        )
        assert response.status_code == 201

        data = response.json()
        assert data["success_count"] == 3
        assert data["fail_count"] == 0
        assert len(data["failed_items"]) == 0

    def test_batch_attendance_partial_success(
        self, client: TestClient, teacher_headers: dict,
        test_class, students, student_without_class
    ):
        """일부 학생만 성공하는 일괄 처리"""
        tomorrow = date.today() + timedelta(days=2)

        response = client.post(
            f"/api/teacher/classes/{test_class.class_id}/attendance/batch",
            json={
                "date": tomorrow.isoformat(),
                "items": [
                    {"student_id": students[0].student_id, "status": "present"},
                    {"student_id": student_without_class.student_id, "status": "present"}  # 다른 반 학생
                ]
            },
            headers=teacher_headers
        )
        assert response.status_code == 201

        data = response.json()
        assert data["success_count"] == 1
        assert data["fail_count"] == 1
        assert len(data["failed_items"]) == 1
        assert data["failed_items"][0]["student_id"] == student_without_class.student_id

    def test_batch_attendance_forbidden(
        self, client: TestClient, teacher_headers: dict, another_class, students
    ):
        """담당하지 않는 반 일괄 처리 시 403"""
        response = client.post(
            f"/api/teacher/classes/{another_class.class_id}/attendance/batch",
            json={
                "items": [
                    {"student_id": students[0].student_id, "status": "present"}
                ]
            },
            headers=teacher_headers
        )
        assert response.status_code == 403

    def test_batch_attendance_default_date(
        self, client: TestClient, teacher_headers: dict,
        test_class, students, attendance_records
    ):
        """날짜 미지정 시 오늘 날짜로 처리 (기존 기록 업데이트)"""
        response = client.post(
            f"/api/teacher/classes/{test_class.class_id}/attendance/batch",
            json={
                "items": [
                    {"student_id": students[0].student_id, "status": "late"}
                ]
            },
            headers=teacher_headers
        )
        assert response.status_code == 201

        data = response.json()
        # 기존 기록이 있으면 업데이트, 없으면 생성
        assert data["success_count"] == 1


class TestTeacherUpdateAttendance:
    """선생님용 학생 출결 수정 테스트"""

    def test_update_attendance_success(
        self, client: TestClient, teacher_headers: dict,
        students, attendance_records
    ):
        """학생 출결 수정 성공"""
        student_id = students[0].student_id
        att_id = attendance_records[0].att_id

        response = client.patch(
            f"/api/teacher/students/{student_id}/attendance/{att_id}",
            json={
                "status": "late",
                "check_in_time": "16:30",
                "memo": "버스 지연으로 인한 지각"
            },
            headers=teacher_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "지각"
        assert data["check_in_time"] == "16:30"
        assert data["memo"] == "버스 지연으로 인한 지각"

    def test_update_attendance_forbidden(
        self, client: TestClient, teacher_headers: dict,
        student_without_class, attendance_records
    ):
        """담당하지 않는 학생 수정 시 403"""
        response = client.patch(
            f"/api/teacher/students/{student_without_class.student_id}/attendance/1",
            json={"status": "present"},
            headers=teacher_headers
        )
        assert response.status_code == 403
        assert "담당 선생님이 아닙니다" in response.json()["detail"]

    def test_update_attendance_not_found(
        self, client: TestClient, teacher_headers: dict, students
    ):
        """존재하지 않는 출결 기록 수정 시 404"""
        response = client.patch(
            f"/api/teacher/students/{students[0].student_id}/attendance/99999",
            json={"status": "present"},
            headers=teacher_headers
        )
        assert response.status_code == 404


class TestTeacherAttendanceSummary:
    """선생님용 반 출결 통계 테스트"""

    def test_get_summary_success(
        self, client: TestClient, teacher_headers: dict,
        test_class, students, attendance_records
    ):
        """기간별 반 출결 통계 조회 성공"""
        response = client.get(
            f"/api/teacher/classes/{test_class.class_id}/attendance/summary",
            headers=teacher_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["class_id"] == test_class.class_id
        assert data["class_name"] == test_class.class_name
        assert "period_start" in data
        assert "period_end" in data
        assert "total_days" in data
        assert "stats" in data
        assert "students" in data

        # 통계 확인
        stats = data["stats"]
        assert "total_records" in stats
        assert "avg_attendance_rate" in stats
        assert "present" in stats
        assert "late" in stats
        assert "absent" in stats
        assert "early" in stats

        # 학생별 통계 확인
        assert len(data["students"]) == len(students)
        for student in data["students"]:
            assert "student_id" in student
            assert "student_name" in student
            assert "attendance_rate" in student
            assert "present" in student
            assert "late" in student
            assert "absent" in student
            assert "early" in student

    def test_get_summary_with_date_range(
        self, client: TestClient, teacher_headers: dict,
        test_class, students, attendance_records
    ):
        """기간 지정 통계 조회"""
        today = date.today()
        start = today - timedelta(days=7)
        end = today

        response = client.get(
            f"/api/teacher/classes/{test_class.class_id}/attendance/summary",
            params={
                "start_date": start.isoformat(),
                "end_date": end.isoformat()
            },
            headers=teacher_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert data["period_start"] == start.isoformat()
        assert data["period_end"] == end.isoformat()
        assert data["total_days"] == 8  # 7일 + 오늘

    def test_get_summary_forbidden(
        self, client: TestClient, teacher_headers: dict, another_class
    ):
        """담당하지 않는 반 통계 조회 시 403"""
        response = client.get(
            f"/api/teacher/classes/{another_class.class_id}/attendance/summary",
            headers=teacher_headers
        )
        assert response.status_code == 403


class TestTeacherStudentAttendance:
    """선생님용 개별 학생 출결 API 테스트"""

    def test_get_student_attendance_success(
        self, client: TestClient, teacher_headers: dict,
        students, attendance_records
    ):
        """학생 출결 기록 조회 성공"""
        student_id = students[0].student_id

        response = client.get(
            f"/api/teacher/students/{student_id}/attendance",
            headers=teacher_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

        # 첫 번째 기록 검증
        record = data[0]
        assert record["student_id"] == student_id
        assert "attendance_date" in record
        assert "status" in record

    def test_get_student_attendance_with_date_range(
        self, client: TestClient, teacher_headers: dict,
        students, attendance_records
    ):
        """기간 지정 학생 출결 조회"""
        student_id = students[0].student_id
        today = date.today()
        start = today - timedelta(days=3)

        response = client.get(
            f"/api/teacher/students/{student_id}/attendance",
            params={
                "start_date": start.isoformat(),
                "end_date": today.isoformat()
            },
            headers=teacher_headers
        )
        assert response.status_code == 200

        data = response.json()
        # 모든 기록이 지정 기간 내에 있는지 확인
        for record in data:
            record_date = date.fromisoformat(record["attendance_date"])
            assert start <= record_date <= today

    def test_get_student_attendance_forbidden(
        self, client: TestClient, teacher_headers: dict, student_without_class
    ):
        """담당하지 않는 학생 조회 시 403"""
        response = client.get(
            f"/api/teacher/students/{student_without_class.student_id}/attendance",
            headers=teacher_headers
        )
        assert response.status_code == 403

    def test_create_student_attendance_success(
        self, client: TestClient, teacher_headers: dict, students
    ):
        """학생 출결 등록 성공"""
        student_id = students[0].student_id
        tomorrow = date.today() + timedelta(days=10)

        response = client.post(
            f"/api/teacher/students/{student_id}/attendance",
            json={
                "attendance_date": tomorrow.isoformat(),
                "status": "present",
                "check_in_time": "16:00",
                "memo": "정상 출석"
            },
            headers=teacher_headers
        )
        assert response.status_code == 201

        data = response.json()
        assert data["student_id"] == student_id
        assert data["status"] == "출석"
        assert data["check_in_time"] == "16:00"

    def test_create_student_attendance_duplicate(
        self, client: TestClient, teacher_headers: dict,
        students, attendance_records
    ):
        """중복 출결 등록 시 400"""
        student_id = students[0].student_id
        today = date.today()

        response = client.post(
            f"/api/teacher/students/{student_id}/attendance",
            json={
                "attendance_date": today.isoformat(),
                "status": "present"
            },
            headers=teacher_headers
        )
        assert response.status_code == 400
        assert "이미 출결 기록이 존재" in response.json()["detail"]


class TestTeacherClasses:
    """선생님 담당 반 관련 API 테스트"""

    def test_get_my_classes(
        self, client: TestClient, teacher_headers: dict, test_class
    ):
        """내 담당 반 목록 조회"""
        response = client.get(
            "/api/teacher/classes",
            headers=teacher_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

        # 담당 반 확인
        class_ids = [c["id"] for c in data]
        assert test_class.class_id in class_ids

    def test_get_class_students(
        self, client: TestClient, teacher_headers: dict,
        test_class, students
    ):
        """반 학생 목록 조회"""
        response = client.get(
            f"/api/teacher/classes/{test_class.class_id}/students",
            headers=teacher_headers
        )
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert len(data) == len(students)

    def test_get_class_students_forbidden(
        self, client: TestClient, teacher_headers: dict, another_class
    ):
        """다른 반 학생 목록 조회 시 403"""
        response = client.get(
            f"/api/teacher/classes/{another_class.class_id}/students",
            headers=teacher_headers
        )
        assert response.status_code == 403
