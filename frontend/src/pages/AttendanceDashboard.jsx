import React, { useState, useEffect } from 'react';
import api from '../services/api';

const AttendanceDashboard = () => {
    const [students, setStudents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const ATTENDANCE_STATUS = {
        PRESENT: "출석",
        LATE: "지각",
        EARLY_LEAVE: "조퇴",
        ABSENT: "결석"
    };

    useEffect(() => {
        fetchAttendance();
    }, []);

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

    const handleCheck = async (studentId, status, action = "CHECK_IN") => {
        // Optimistic Update를 위한 백업
        const previousStudents = JSON.parse(JSON.stringify(students));

        // 화면 즉시 갱신
        setStudents(prev => prev.map(item => {
            if (item.student.student_id === studentId) {
                // 기존 attendance 정보가 없으면 새로 생성하는 척
                const currentAtt = item.attendance || {};

                const newAtt = {
                    ...currentAtt,
                    student_id: studentId,
                    status: action === "CHECK_IN" ? status : currentAtt.status,
                    is_notified: false, // 실제 응답 전 임시 상태
                    check_out_at: action === "CHECK_OUT" ? new Date().toISOString() : currentAtt.check_out_at,
                    // 체크인/상태변경 시 등원 시간 업데이트 (없는 경우)
                    check_in_at: (action === "CHECK_IN" && !currentAtt.check_in_at) ? new Date().toISOString() : currentAtt.check_in_at
                };
                return { ...item, attendance: newAtt };
            }
            return item;
        }));

        try {
            const response = await api.post('/attendance/check', {
                student_id: studentId,
                status: status, // 하원(CHECK_OUT)일 때도 status 필드는 필수이므로 현재 상태 또는 기본값 전송
                action: action
            });

            // 성공 시 서버 데이터로 교체 (is_notified 등 최신화)
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

    const getStatusBadge = (attendance) => {
        if (!attendance) return <span className="text-gray-400">미등원</span>;

        if (attendance.check_out_at) {
            return <span className="text-purple-600 font-bold">하원완료</span>;
        }

        const map = {
            "출석": { text: "출석", color: "text-green-600" },
            "지각": { text: "지각", color: "text-yellow-600" },
            "조퇴": { text: "조퇴", color: "text-orange-600" },
            "결석": { text: "결석", color: "text-red-600" }
        };

        const info = map[attendance.status];
        return info ? <span className={`${info.color} font-bold`}>{info.text}</span> : <span>{attendance.status}</span>;
    };

    if (loading) return <div className="p-8 text-center">불러오는 중...</div>;
    if (error) return <div className="p-8 text-center text-red-500">{error}</div>;

    return (
        <div className="max-w-6xl mx-auto p-6">
            <h1 className="text-3xl font-bold mb-8 text-gray-800">출결 관리 대시보드</h1>

            <div className="bg-white shadow-xl rounded-xl overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">학생 이름</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">현재 상태</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">등원 시간</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">하원 시간</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">알림</th>
                            <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">관리</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {students.map((item) => {
                            const { student, attendance } = item;
                            return (
                                <tr key={student.student_id} className="hover:bg-gray-50 transition-colors">
                                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                        {student.name}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                                        {getStatusBadge(attendance)}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {attendance?.check_in_at ? new Date(attendance.check_in_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '-'}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                        {attendance?.check_out_at ? new Date(attendance.check_out_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '-'}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                                        {attendance?.is_notified
                                            ? <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">발송됨</span>
                                            : <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">미발송</span>
                                        }
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-center space-x-2">
                                        <button
                                            onClick={() => handleCheck(student.student_id, ATTENDANCE_STATUS.PRESENT)}
                                            className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded-md text-xs font-medium transition-colors"
                                        >
                                            출석
                                        </button>
                                        <button
                                            onClick={() => handleCheck(student.student_id, ATTENDANCE_STATUS.LATE)}
                                            className="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1 rounded-md text-xs font-medium transition-colors"
                                        >
                                            지각
                                        </button>
                                        <button
                                            onClick={() => handleCheck(student.student_id, ATTENDANCE_STATUS.EARLY_LEAVE)}
                                            className="bg-orange-500 hover:bg-orange-600 text-white px-3 py-1 rounded-md text-xs font-medium transition-colors"
                                        >
                                            조퇴
                                        </button>
                                        <button
                                            onClick={() => handleCheck(student.student_id, attendance?.status || "출석", "CHECK_OUT")}
                                            className="bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded-md text-xs font-medium transition-colors"
                                            disabled={!attendance || !!attendance.check_out_at}
                                        >
                                            하원
                                        </button>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default AttendanceDashboard;
