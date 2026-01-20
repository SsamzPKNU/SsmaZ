import { useNavigate } from 'react-router-dom';
import { getCurrentUser } from '../../services/api';
import StatCard from '../../components/StatCard';

/**
 * Admin Dashboard - Matching the new Navy mockup
 */
function AdminDashboard() {
    const navigate = useNavigate();
    const user = getCurrentUser();

    // Stats matching the mockup style
    const stats = [
        { label: "Today's Attendance", value: '45/50', icon: '🌀', active: true },
        { label: 'Monthly Revenue', value: '$12,500', icon: '💲', active: false },
        { label: 'New Students', value: '8', icon: '🎓', active: false },
    ];

    return (
        <div className="space-y-12">
            {/* Page Title & Actions */}
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-black text-ssamz-navy tracking-tight">Dashboard Overview</h1>
                <div className="flex space-x-3">
                    <button className="px-6 py-2.5 bg-ssamz-navy text-white font-bold rounded-lg shadow-lg hover:shadow-xl transition-all">+ Add Task</button>
                    <button className="px-6 py-2.5 bg-white text-slate-600 border border-slate-200 font-bold rounded-lg hover:bg-slate-50 transition-all">Export Report</button>
                </div>
            </div>

            {/* Quick Stats Grid - Matching Brand Colors */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                {stats.map((stat, idx) => (
                    <StatCard
                        key={idx}
                        label={stat.label}
                        value={stat.value}
                        icon={stat.icon}
                        active={stat.active}
                    />
                ))}
            </div>

            {/* Performance Chart Section */}
            <div className="bg-white rounded-[2rem] p-10 shadow-card border border-ssamz-border">
                <div className="flex justify-between items-center mb-10">
                    <div>
                        <h3 className="text-lg font-black text-ssamz-navy">Student Growth</h3>
                        <p className="text-xs text-slate-400 font-bold mt-1">Monthly performance and attendance trends</p>
                    </div>
                    <select className="bg-ssamz-bg border-none rounded-lg px-4 py-2 text-[10px] font-black text-slate-400 uppercase tracking-widest outline-none">
                        <option>Last 6 Months</option>
                        <option>Last Year</option>
                    </select>
                </div>

                {/* Refined Chart visualization */}
                <div className="h-64 flex items-end justify-between px-4 space-x-6">
                    {[60, 45, 80, 55, 95, 70].map((h, i) => (
                        <div key={i} className="flex-1 flex flex-col items-center gap-4">
                            <div
                                style={{ height: `${h}%` }}
                                className={`w-full bg-ssamz-blue rounded-xl transition-all cursor-pointer relative group ${i === 4 ? 'opacity-100' : 'opacity-20 hover:opacity-100'}`}
                            >
                                <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-ssamz-navy text-white text-[10px] px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-all font-bold">
                                    {h}%
                                </div>
                            </div>
                            <span className="text-[10px] font-black text-slate-300 uppercase tracking-widest">Month {i + 1}</span>
                        </div>
                    ))}
                </div>
            </div>

            {/* Bottom Grid: Activity & Notices */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="bg-white rounded-[2rem] p-8 shadow-card border border-ssamz-border">
                    <h3 className="text-lg font-black text-ssamz-navy mb-8">Recent Activity</h3>
                    <div className="space-y-6">
                        {[
                            { name: 'Admin', action: 'added a new student', time: '2 mins ago' },
                            { name: 'Teacher Lee', action: 'updated attendance', time: '1 hour ago' },
                            { name: 'System', action: 'sent payment alerts', time: '3 hours ago' },
                        ].map((act, i) => (
                            <div key={i} className="flex items-start space-x-4 border-l-2 border-slate-50 pl-6 py-2">
                                <div className="flex-1">
                                    <p className="text-[13px] leading-relaxed"><span className="font-bold text-ssamz-text">{act.name}</span> <span className="text-slate-400">{act.action}</span></p>
                                    <p className="text-[10px] text-slate-300 font-black mt-1 uppercase tracking-widest">{act.time}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
                <div className="bg-ssamz-navy rounded-[2rem] p-8 text-white relative overflow-hidden shadow-2xl">
                    <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/5 rounded-full blur-2xl"></div>
                    <h3 className="text-lg font-black mb-4 relative z-10">Urgent Notifications</h3>
                    <p className="text-xs text-white/40 mb-10 leading-relaxed font-medium relative z-10">System maintenance scheduled for tonight. <br /> All data will be safely backed up automatically.</p>
                    <button className="w-full py-4 bg-white/10 hover:bg-white/20 text-white font-bold text-xs rounded-xl transition-all border border-white/10 relative z-10 uppercase tracking-widest">View Maintenance Log</button>
                </div>
            </div>
        </div>
    );
}

export default AdminDashboard;
