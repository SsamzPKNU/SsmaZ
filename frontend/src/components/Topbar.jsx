import { getCurrentUser } from '../services/api';

function Topbar({ userRole }) {
    const user = getCurrentUser();

    return (
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
                    <span className="text-xs font-bold text-slate-400">{userRole}</span>
                    <div className="w-9 h-9 rounded-full overflow-hidden border-2 border-ssamz-border shadow-sm">
                        <img src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${user?.username || 'user'}`} alt="avatar" />
                    </div>
                </div>
            </div>
        </header>
    );
}

export default Topbar;
