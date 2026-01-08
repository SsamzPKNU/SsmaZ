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
                        <h1 className="text-2xl font-bold text-primary-700">SsmaZ</h1>
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

                {/* 기능 안내 */}
                <div className="mt-8 bg-gradient-to-r from-primary-500 to-primary-600 rounded-2xl shadow-xl p-8 text-white">
                    <h3 className="text-2xl font-bold mb-4">🚀 다음 기능을 준비 중입니다</h3>
                    <ul className="space-y-2">
                        <li className="flex items-center">
                            <span className="mr-2">✅</span>
                            학생 관리
                        </li>
                        <li className="flex items-center">
                            <span className="mr-2">✅</span>
                            수업 일정 관리
                        </li>
                        <li className="flex items-center">
                            <span className="mr-2">✅</span>
                            출결 관리
                        </li>
                        <li className="flex items-center">
                            <span className="mr-2">✅</span>
                            성적 관리
                        </li>
                    </ul>
                </div>
            </main>
        </div>
    );
}

export default HomePage;
