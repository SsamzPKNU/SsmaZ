/**
 * 📄 파일명: HomePage.jsx
 * 📝 설명: 메인 페이지 (홈) - 로그인 후 표시되는 대시보드
 * 🔗 API: GET /auth/me (사용자 정보)
 * ✏️ 수정 시 주의: getCurrentUser()는 localStorage에서 사용자 정보를 가져옵니다
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
        <div className="page-wrapper-dashboard">
            {/* 헤더 */}
            <header className="header">
                <div className="header-content">
                    <div className="header-left">
                        <h1 className="logo-sm">SsmaZ</h1>
                        <button
                            onClick={() => navigate('/attendance')}
                            className="btn btn-primary"
                        >
                            <span className="mr-1">📋</span>
                            출결 관리
                        </button>
                    </div>
                    <button
                        onClick={handleLogout}
                        className="btn btn-secondary"
                    >
                        로그아웃
                    </button>
                </div>
            </header>

            {/* 메인 컨텐츠 */}
            <main className="container p-3">
                {/* 환영 메시지 */}
                <div className="card-lg mb-3">
                    <h2 className="text-3xl font-bold text-gray-dark mb-2">
                        환영합니다, {user?.name || user?.username}님! 👋
                    </h2>
                    <p className="text-gray text-lg">
                        학원 관리 서비스 SsmaZ에 오신 것을 환영합니다.
                    </p>
                </div>

                {/* 사용자 정보 카드 */}
                <div className="grid-3">
                    {/* 기본 정보 */}
                    <div className="card-md">
                        <h3 className="text-lg font-semibold text-gray-dark mb-2 flex items-center">
                            <span className="text-2xl mr-1">👤</span>
                            기본 정보
                        </h3>
                        <div>
                            <div className="mb-2">
                                <p className="text-sm text-gray">아이디</p>
                                <p className="text-gray-dark font-medium">{user?.username}</p>
                            </div>
                            <div className="mb-2">
                                <p className="text-sm text-gray">이름</p>
                                <p className="text-gray-dark font-medium">{user?.name || '-'}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray">전화번호</p>
                                <p className="text-gray-dark font-medium">{user?.phone || '-'}</p>
                            </div>
                        </div>
                    </div>

                    {/* 학원 정보 */}
                    <div className="card-md">
                        <h3 className="text-lg font-semibold text-gray-dark mb-2 flex items-center">
                            <span className="text-2xl mr-1">🏫</span>
                            학원 정보
                        </h3>
                        <div>
                            <div className="mb-2">
                                <p className="text-sm text-gray">학원 ID</p>
                                <p className="text-gray-dark font-medium">{user?.academy_id}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray">역할</p>
                                <p className="text-gray-dark font-medium">
                                    <span className="badge badge-primary">
                                        {getRoleText(user?.user_role)}
                                    </span>
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* 계정 정보 */}
                    <div className="card-md">
                        <h3 className="text-lg font-semibold text-gray-dark mb-2 flex items-center">
                            <span className="text-2xl mr-1">📅</span>
                            계정 정보
                        </h3>
                        <div>
                            <div className="mb-2">
                                <p className="text-sm text-gray">사용자 ID</p>
                                <p className="text-gray-dark font-medium">{user?.user_id}</p>
                            </div>
                            <div>
                                <p className="text-sm text-gray">가입일</p>
                                <p className="text-gray-dark font-medium">
                                    {user?.created_at ? new Date(user.created_at).toLocaleDateString('ko-KR') : '-'}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* 빠른 작업 */}
                <div className="grid-2 mt-3">
                    <div
                        onClick={() => navigate('/attendance')}
                        className="card-lg clickable-card"
                    >
                        <div className="flex items-center justify-between mb-2">
                            <h3 className="text-xl font-bold text-primary">📋 출결 대시보드 바로가기</h3>
                            <span className="text-2xl">➡️</span>
                        </div>
                        <p className="text-gray">오늘 학생들의 등하원 상태를 확인하고 관리합니다.</p>
                    </div>

                    <div className="feature-card">
                        <h3 className="text-xl font-bold mb-2">🚀 준비 중인 기능</h3>
                        <div className="grid-2 text-sm" style={{ opacity: 0.9 }}>
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
