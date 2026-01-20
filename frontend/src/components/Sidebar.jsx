import { useNavigate, Link, useLocation } from 'react-router-dom';
import { logout } from '../services/api';

function Sidebar({ menus }) {
    const navigate = useNavigate();
    const location = useLocation();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    // Determine home path based on first menu item or default
    const homePath = menus.length > 0 ? menus[0].path : '/';

    return (
        <aside className="w-[260px] bg-ssamz-navy flex flex-col z-30 shadow-xl overflow-hidden min-h-screen">
            {/* Brand Logo - Sz SAMZ */}
            <div
                onClick={() => navigate(homePath)}
                className="py-10 flex flex-col items-center justify-center cursor-pointer"
            >
                <div className="text-5xl font-serif text-white mb-0">Sz</div>
                <div className="text-[10px] font-black text-white/50 tracking-[0.4em] uppercase -mt-1">SAMZ</div>
            </div>

            {/* Navigation Menus */}
            <nav className="flex-1 space-y-0.5 mt-2">
                {menus.map((item) => {
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
    );
}

export default Sidebar;
