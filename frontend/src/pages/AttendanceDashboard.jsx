/**
 * 📄 파일명: AttendanceDashboard.jsx
 * 📝 설명: 출결 관리 대시보드 - 학생 출석 상태를 관리합니다
 * 🔗 API: GET /attendance/today, POST /attendance/check
 * ✏️ 수정 시 주의: handleCheck 함수에서 optimistic update를 사용합니다
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

// 출석 상태 상수
const ATTENDANCE_STATUS = {
    PRESENT: "출석",
    LATE: "지각",
    EARLY_LEAVE: "조퇴",
    ABSENT: "결석"
};

function AttendanceDashboard() {
    const navigate = useNavigate();
    const [students, setStudents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // 페이지 로드 시 출석 데이터 불러오기
    useEffect(() => {
        fetchAttendance();
    }, []);

    /**
     * 출석 데이터 불러오기
     */
    const fetchAttendance = async () => {
        try {
            setLoading(true);
            const response = await api.get('/attendance/today');
            setStudents(response.data.students);
            setError(null);
        } catch (err) {
            console.error("Fetch error:", err);
            setError("출결 정보를 불러오는 중 오류가 발생했습니다.");
        } finally {
            setLoading(false);
        }
    };

    /**
     * 출석 체크 핸들러
     * optimistic update 패턴 사용 (화면 먼저 갱신 후 API 호출)
     */
    const handleCheck = async (studentId, status, action = "CHECK_IN") => {
        // Optimistic Update를 위한 백업
        const previousStudents = JSON.parse(JSON.stringify(students));

        // 화면 즉시 갱신
        setStudents(prev => prev.map(item => {
            if (item.student.student_id === studentId) {
                const currentAtt = item.attendance || {};
                const newAtt = {
                    ...currentAtt,
                    student_id: studentId,
                    status: action === "CHECK_IN" ? status : currentAtt.status,
                    is_notified: false,
                    check_out_at: action === "CHECK_OUT" ? new Date().toISOString() : currentAtt.check_out_at,
                    check_in_at: (action === "CHECK_IN" && !currentAtt.check_in_at) ? new Date().toISOString() : currentAtt.check_in_at
                };
                return { ...item, attendance: newAtt };
            }
            return item;
        }));

        try {
            const response = await api.post('/attendance/check', {
                student_id: studentId,
                status: status,
                action: action
            });

            // 성공 시 서버 데이터로 교체
            setStudents(prev => prev.map(item => {
                if (item.student.student_id === studentId) {
                    return { ...item, attendance: response.data };
                }
                return item;
            }));

        } catch (err) {
            console.error("Check error:", err);
            alert(`처리 실패: ${err.response?.data?.detail || err.message}`);
            // 에러 시 롤백
            setStudents(previousStudents);
        }
    };

    /**
     * 출석 상태 배지 렌더링
     */
    const getStatusBadge = (attendance) => {
        if (!attendance) return <span className="text-gray">미등원</span>;

        if (attendance.check_out_at) {
            return <span className="text-purple font-bold">하원완료</span>;
        }

        const statusMap = {
            "출석": { text: "출석", className: "text-green font-bold" },
            "지각": { text: "지각", className: "text-yellow font-bold" },
            "조퇴": { text: "조퇴", className: "text-orange font-bold" },
            "결석": { text: "결석", className: "text-red font-bold" }
        };

        const info = statusMap[attendance.status];
        return info ? <span className={info.className}>{info.text}</span> : <span>{attendance.status}</span>;
    };

    // 로딩 상태
    if (loading) {
        return (
            <div className="page-wrapper">
                <p className="text-gray">불러오는 중...</p>
            </div>
        );
    }

    // 에러 상태
    if (error) {
        return (
            <div className="page-wrapper">
                <p className="text-red">{error}</p>
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto p-3">
            {/* 헤더 */}
            <div className="flex items-center gap-2 mb-3">
                <button
                    onClick={() => navigate('/')}
                    className="btn btn-secondary rounded-full"
                    title="홈으로 돌아가기"
                >
                    🏠
                </button>
                <h1 className="text-3xl font-bold text-gray-dark">출결 관리 대시보드</h1>
            </div>

            {/* 테이블 */}
            <div className="table-wrapper">
                <table className="table">
                    <thead>
                        <tr>
                            <th>학생 이름</th>
                            <th>현재 상태</th>
                            <th>등원 시간</th>
                            <th>하원 시간</th>
                            <th>알림</th>
                            <th style={{ textAlign: 'center' }}>관리</th>
                        </tr>
                    </thead>
                    <tbody>
                        {students.map((item) => {
                            const { student, attendance } = item;
                            return (
                                <tr key={student.student_id}>
                                    <td className="font-medium">{student.name}</td>
                                    <td>{getStatusBadge(attendance)}</td>
                                    <td className="text-gray">
                                        {attendance?.check_in_at
                                            ? new Date(attendance.check_in_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                            : '-'}
                                    </td>
                                    <td className="text-gray">
                                        {attendance?.check_out_at
                                            ? new Date(attendance.check_out_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
                                            : '-'}
                                    </td>
                                    <td>
                                        {attendance?.is_notified
                                            ? <span className="badge badge-green">발송됨</span>
                                            : <span className="badge badge-gray">미발송</span>
                                        }
                                    </td>
                                    <td>
                                        <div className="table-actions">
                                            <button
                                                onClick={() => handleCheck(student.student_id, ATTENDANCE_STATUS.PRESENT)}
                                                className="btn btn-sm btn-green"
                                            >
                                                출석
                                            </button>
                                            <button
                                                onClick={() => handleCheck(student.student_id, ATTENDANCE_STATUS.LATE)}
                                                className="btn btn-sm btn-yellow"
                                            >
                                                지각
                                            </button>
                                            <button
                                                onClick={() => handleCheck(student.student_id, ATTENDANCE_STATUS.EARLY_LEAVE)}
                                                className="btn btn-sm btn-orange"
                                            >
                                                조퇴
                                            </button>
                                            <button
                                                onClick={() => handleCheck(student.student_id, attendance?.status || "출석", "CHECK_OUT")}
                                                className="btn btn-sm btn-purple"
                                                disabled={!attendance || !!attendance.check_out_at}
                                            >
                                                하원
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default AttendanceDashboard;
