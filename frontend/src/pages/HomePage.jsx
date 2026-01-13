/**
 * 메인 페이지 (홈)
 * 로그인 후 표시되는 대시보드
 */

import { useNavigate } from 'react-router-dom';
import { getCurrentUser, logout } from '../services/api';

function HomePage() {
    const navigate = useNavigate();
    const user = getCurrentUser();

    /**
     * 로그아웃 핸들러
     */
    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    // 사용자 역할에 따른 한글 표시
    const getRoleText = (role) => {
        const roleMap = {
            'ADMIN': '관리자',
            'TEACHER': '선생님',
            'STUDENT': '학생'
        };
        return roleMap[role] || role;
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100">
            {/* 헤더 */}
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-4">
                            <h1 className="text-2xl font-bold text-primary-700">SsmaZ</h1>
                            <button
                                onClick={() => navigate('/attendance')}
                                className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition font-medium text-sm flex items-center"
                            >
                                <span className="mr-1.5">📋</span>
                                출결 관리
                            </button>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition"
                        >
                            로그아웃
                        </button>
                    </div>
                </div>
            </header>

            {/* 메인 컨텐츠 */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                {/* 환영 메시지 */}
                <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
                    <h2 className="text-3xl font-bold text-gray-800 mb-4">
                        환영합니다, {user?.name || user?.username}님! 👋
                    </h2>
                    <p className="text-gray-600 text-lg">
                        학원 관리 서비스 SsmaZ에 오신 것을 환영합니다.
                    </p>
                </div>

                {/* 사용자 정보 카드 */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* 기본 정보 */}
                    <div className="bg-white rounded-xl shadow-lg p-6">
                        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                            <span className="text-2xl mr-2">👤</span>
                            기본 정보
                        </h3>
                        <div className="space-y-3">
                            <div>
                                <p className="text-sm text-gray-500">아이디</p>
                                <p className="text-gray-800 font-medium">{user?.username}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">이름</p>
                                <p className="text-gray-800 font-medium">{user?.name || '-'}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">전화번호</p>
                                <p className="text-gray-800 font-medium">{user?.phone || '-'}</p>
                            </div>
                        </div>
                    </div>

                    {/* 학원 정보 */}
                    <div className="bg-white rounded-xl shadow-lg p-6">
                        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                            <span className="text-2xl mr-2">🏫</span>
                            학원 정보
                        </h3>
                        <div className="space-y-3">
                            <div>
                                <p className="text-sm text-gray-500">학원 ID</p>
                                <p className="text-gray-800 font-medium">{user?.academy_id}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">역할</p>
                                <p className="text-gray-800 font-medium">
                                    <span className="inline-block px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm">
                                        {getRoleText(user?.user_role)}
                                    </span>
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* 계정 정보 */}
                    <div className="bg-white rounded-xl shadow-lg p-6">
                        <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                            <span className="text-2xl mr-2">📅</span>
                            계정 정보
                        </h3>
                        <div className="space-y-3">
                            <div>
                                <p className="text-sm text-gray-500">사용자 ID</p>
                                <p className="text-gray-800 font-medium">{user?.user_id}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray-500">가입일</p>
                                <p className="text-gray-800 font-medium">
                                    {user?.created_at ? new Date(user.created_at).toLocaleDateString('ko-KR') : '-'}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 빠른 작업 */}
                <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div
                        onClick={() => navigate('/attendance')}
                        className="cursor-pointer bg-white border-2 border-primary-500 rounded-2xl p-6 shadow-md hover:shadow-lg transition-all transform hover:-translate-y-1"
                    >
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-xl font-bold text-primary-700">📋 출결 대시보드 바로가기</h3>
                            <span className="text-2xl">➡️</span>
                        </div>
                        <p className="text-gray-600">오늘 학생들의 등하원 상태를 확인하고 관리합니다.</p>
                    </div>

                    <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-2xl shadow-xl p-6 text-white">
                        <h3 className="text-xl font-bold mb-3">🚀 준비 중인 기능</h3>
                        <div className="grid grid-cols-2 gap-2 text-sm opacity-90">
                            <div className="flex items-center">✅ 학생 관리</div>
                            <div className="flex items-center">✅ 수업 일정</div>
                            <div className="flex items-center">✅ 성적 관리</div>
                            <div className="flex items-center">✅ 알림 설정</div>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default HomePage;
