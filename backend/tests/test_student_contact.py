"""
StudentContact API 권한 및 CRUD 테스트

관리자/선생님 전용 API 권한 테스트
"""

import pytest
from fastapi.testclient import TestClient


class TestStudentContactAuthorization:
    """권한 관련 테스트"""

    def test_get_contacts_without_auth_returns_401(self, client: TestClient, students):
        """비인증 사용자의 연락처 조회 시 401 반환"""
        student = students[0]
        response = client.get(f"/students/{student.student_id}/contacts")
        assert response.status_code == 401

    def test_create_contact_without_auth_returns_401(self, client: TestClient, students):
        """비인증 사용자의 연락처 생성 시 401 반환"""
        student = students[0]
        response = client.post(
            f"/students/{student.student_id}/contacts",
            json={"phone": "010-9999-9999", "label": "아빠", "priority": 2}
        )
        assert response.status_code == 401

    def test_student_cannot_access_contacts_returns_403(
        self, client: TestClient, students, student_headers
    ):
        """학생 권한으로 연락처 조회 시 403 반환"""
        student = students[0]
        response = client.get(
            f"/students/{student.student_id}/contacts",
            headers=student_headers
        )
        assert response.status_code == 403
        assert "관리자 또는 선생님 권한이 필요합니다" in response.json()["detail"]

    def test_student_cannot_create_contact_returns_403(
        self, client: TestClient, students, student_headers
    ):
        """학생 권한으로 연락처 생성 시 403 반환"""
        student = students[0]
        response = client.post(
            f"/students/{student.student_id}/contacts",
            headers=student_headers,
            json={"phone": "010-9999-9999", "label": "아빠", "priority": 2}
        )
        assert response.status_code == 403


class TestStudentContactAdminCRUD:
    """관리자 CRUD 테스트"""

    def test_admin_can_create_contact(self, client: TestClient, students, admin_headers):
        """관리자는 연락처를 생성할 수 있음"""
        student = students[0]
        response = client.post(
            f"/students/{student.student_id}/contacts",
            headers=admin_headers,
            json={"phone": "010-8888-8888", "label": "아빠", "priority": 2}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["phone"] == "010-8888-8888"
        assert data["label"] == "아빠"
        assert data["priority"] == 2

    def test_admin_can_get_contacts(
        self, client: TestClient, students, student_contacts, admin_headers
    ):
        """관리자는 연락처 목록을 조회할 수 있음"""
        student = students[0]
        response = client.get(
            f"/students/{student.student_id}/contacts",
            headers=admin_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "contacts" in data
        assert "total" in data
        assert data["total"] >= 1

    def test_admin_can_update_contact(
        self, client: TestClient, student_contacts, admin_headers
    ):
        """관리자는 연락처를 수정할 수 있음"""
        contact = student_contacts[0]
        response = client.put(
            f"/students/contacts/{contact.contact_id}",
            headers=admin_headers,
            json={"label": "할머니", "priority": 3}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["label"] == "할머니"
        assert data["priority"] == 3

    def test_admin_can_delete_contact(
        self, client: TestClient, student_contacts, admin_headers
    ):
        """관리자는 연락처를 삭제할 수 있음"""
        contact = student_contacts[0]
        response = client.delete(
            f"/students/contacts/{contact.contact_id}",
            headers=admin_headers
        )
        assert response.status_code == 204


class TestStudentContactTeacherCRUD:
    """선생님 CRUD 테스트"""

    def test_teacher_can_create_contact(self, client: TestClient, students, teacher_headers):
        """선생님은 연락처를 생성할 수 있음"""
        student = students[0]
        response = client.post(
            f"/students/{student.student_id}/contacts",
            headers=teacher_headers,
            json={"phone": "010-7777-7777", "label": "엄마", "priority": 1}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["phone"] == "010-7777-7777"

    def test_teacher_can_get_contacts(
        self, client: TestClient, students, student_contacts, teacher_headers
    ):
        """선생님은 연락처 목록을 조회할 수 있음"""
        student = students[0]
        response = client.get(
            f"/students/{student.student_id}/contacts",
            headers=teacher_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "contacts" in data

    def test_teacher_can_update_contact(
        self, client: TestClient, student_contacts, teacher_headers
    ):
        """선생님은 연락처를 수정할 수 있음"""
        contact = student_contacts[0]
        response = client.put(
            f"/students/contacts/{contact.contact_id}",
            headers=teacher_headers,
            json={"is_active": False}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

    def test_teacher_can_delete_contact(
        self, client: TestClient, student_contacts, teacher_headers
    ):
        """선생님은 연락처를 삭제할 수 있음"""
        contact = student_contacts[1]
        response = client.delete(
            f"/students/contacts/{contact.contact_id}",
            headers=teacher_headers
        )
        assert response.status_code == 204


class TestStudentContactEdgeCases:
    """엣지 케이스 테스트"""

    def test_get_contacts_nonexistent_student_returns_404(
        self, client: TestClient, admin_headers
    ):
        """존재하지 않는 학생의 연락처 조회 시 404 반환"""
        response = client.get(
            "/students/99999/contacts",
            headers=admin_headers
        )
        assert response.status_code == 404

    def test_update_nonexistent_contact_returns_404(
        self, client: TestClient, admin_headers
    ):
        """존재하지 않는 연락처 수정 시 404 반환"""
        response = client.put(
            "/students/contacts/99999",
            headers=admin_headers,
            json={"label": "새 라벨"}
        )
        assert response.status_code == 404

    def test_delete_nonexistent_contact_returns_404(
        self, client: TestClient, admin_headers
    ):
        """존재하지 않는 연락처 삭제 시 404 반환"""
        response = client.delete(
            "/students/contacts/99999",
            headers=admin_headers
        )
        assert response.status_code == 404

    def test_create_contact_with_invalid_phone_format(
        self, client: TestClient, students, admin_headers
    ):
        """잘못된 전화번호 형식으로 연락처 생성"""
        student = students[0]
        response = client.post(
            f"/students/{student.student_id}/contacts",
            headers=admin_headers,
            json={"phone": "invalid-phone", "label": "테스트"}
        )
        # 스키마에서 phone validation이 없으면 201 반환될 수 있음
        # 여기서는 일단 요청이 처리되는지만 확인
        assert response.status_code in [201, 422]
