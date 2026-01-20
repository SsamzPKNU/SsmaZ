import { useNavigate, Link, useLocation } from 'react-router-dom';
import { getCurrentUser, logout } from '../services/api';

/**
 * 프리미엄 레이아웃 컴포넌트
 * 좌측 사이드바와 상단 헤더가 포함된 구조
 */
function Layout({ children }) {
    const navigate = useNavigate();
    const location = useLocation();
    const user = getCurrentUser();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    // 현재 경로에 따라 메뉴 구성 결정
    const isAdmin = location.pathname.startsWith('/a');
    const isStudent = location.pathname.startsWith('/s');

    const adminMenus = [
        { path: '/a', label: 'Dashboard', icon: '🏠' },
        { path: '/a/students', label: 'Student List', icon: '👥' },
        { path: '/a/classes', label: 'Classes', icon: '🏫' },
        { path: '/a/attendance', label: 'Attendance', icon: '✅' },
        { path: '/a/payments', label: 'Payments', icon: '💳' },
        { path: '/a/settings', label: 'Settings', icon: '⚙️' },
    ];

    const studentMenus = [
        { path: '/s', label: 'Dashboard', icon: '🏠' },
        { path: '/s/attendance', label: 'Attendance', icon: '📅' },
        { path: '/s/payments', label: 'Payments', icon: '💳' },
        { path: '/s/notes', label: 'Larning Logs', icon: '📢' },
    ];

    const currentMenus = isAdmin ? adminMenus : isStudent ? studentMenus : [];

    return (
        <div className="flex h-screen bg-ssamz-bg font-sans text-ssamz-text">
            {/* Brand Navy Sidebar */}
            <aside className="w-[260px] bg-ssamz-navy flex flex-col z-30 shadow-xl overflow-hidden">
                {/* Brand Logo - Sz SAMZ */}
                <div
                    onClick={() => navigate(isAdmin ? '/a' : isStudent ? '/s' : '/')}
                    className="py-10 flex flex-col items-center justify-center cursor-pointer"
                >
                    <div className="text-5xl font-serif text-white mb-0">Sz</div>
                    <div className="text-[10px] font-black text-white/50 tracking-[0.4em] uppercase -mt-1">SAMZ</div>
                </div>

                {/* Navigation Menus */}
                <nav className="flex-1 space-y-0.5 mt-2">
                    {currentMenus.map((item) => {
                        const isActive = location.pathname === item.path;
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`flex items-center px-8 py-4.5 transition-all duration-200 border-l-4 ${isActive
                                    ? 'bg-ssamz-blue text-white border-white/20'
                                    : 'text-slate-400 hover:text-white hover:bg-white/5 border-transparent'
                                    }`}
                            >
                                <span className="text-lg mr-4 opacity-80">{item.icon}</span>
                                <span className="text-[13px] font-medium tracking-wide">{item.label}</span>
                            </Link>
                        );
                    })}
                </nav>

                {/* Bottom Logout */}
                <div className="p-6 border-t border-white/5">
                    <button
                        onClick={handleLogout}
                        className="w-full flex items-center justify-center p-2 text-slate-500 hover:text-white transition-all text-[11px] font-bold uppercase tracking-widest"
                    >
                        Logout
                    </button>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 flex flex-col overflow-hidden">
                {/* Simplified Header */}
                <header className="h-[70px] bg-white border-b border-ssamz-border flex items-center justify-between px-8 z-20">
                    <div className="flex-1 max-w-sm">
                        <div className="relative">
                            <input
                                type="text"
                                placeholder="Search"
                                className="w-full bg-ssamz-bg/50 border border-ssamz-border rounded-md py-2 px-10 text-xs text-slate-400 outline-none focus:bg-white transition-all"
                            />
                            <span className="absolute left-3 top-1/2 -translate-y-1/2 opacity-30">🔍</span>
                        </div>
                    </div>

                    <div className="flex items-center space-x-6">
                        <button className="text-slate-300 hover:text-ssamz-blue transition-colors relative">
                            <span className="text-lg">🔔</span>
                            <div className="absolute -top-1 -right-1 w-2 h-2 bg-red-400 rounded-full border border-white"></div>
                        </button>
                        <div className="flex items-center space-x-3">
                            <span className="text-xs font-bold text-slate-400">{isAdmin ? 'Admin' : 'Student'}</span>
                            <div className="w-9 h-9 rounded-full overflow-hidden border-2 border-ssamz-border shadow-sm">
                                <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.username || 'admin'}`} alt="avatar" />
                            </div>
                        </div>
                    </div>
                </header>

                {/* Page Content */}
                <div className="flex-1 overflow-y-auto bg-ssamz-bg/50">
                    <div className="p-10">
                        <div className="max-w-[1400px] mx-auto animate-fade-in">
                            {children}
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default Layout;
