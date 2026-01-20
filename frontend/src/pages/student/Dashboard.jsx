import { useNavigate } from 'react-router-dom';
import { getCurrentUser } from '../../services/api';
import StatCard from '../../components/StatCard';

/**
 * Student Dashboard - Matching the Navy theme
 */
function StudentDashboard() {
    const navigate = useNavigate();
    const user = getCurrentUser();

    // Student specific cards: Attendance, Learning Logs, Next Payment
    const cards = [
        { label: "Today's Attendance", value: 'Checked In', time: '09:00 AM', icon: '📍', color: 'text-sky-500', bg: 'bg-sky-50' },
        { label: 'Next Payment', value: 'Feb 15, 2026', amount: '$350', icon: '💳', color: 'text-emerald-500', bg: 'bg-emerald-50' },
        { label: 'Recent Grade', value: 'A+', subject: 'Mathematics', icon: '📝', color: 'text-blue-500', bg: 'bg-blue-50' },
    ];

    return (
        <div className="space-y-12">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold text-ssamz-navy tracking-tight">Student Dashboard</h1>
                <p className="text-sm font-bold text-slate-400">Welcome back, <span className="text-ssamz-blue">{user?.name || 'Student'}</span></p>
            </div>

            {/* Quick Stats Grid - Brand Styled */}
            <div className="grid grid-cols-3 gap-8">
                {cards.map((card, idx) => (
                    <StatCard
                        key={idx}
                        label={card.label}
                        value={card.value}
                        icon={card.icon}
                        active={false}
                    />
                ))}
            </div>

            <div className="grid grid-cols-2 gap-8">
                {/* Learning Logs Mini View - Brand Styled */}
                <div className="bg-white rounded-[2rem] p-8 shadow-card border border-ssamz-border">
                    <div className="flex justify-between items-center mb-8">
                        <h3 className="text-lg font-bold text-ssamz-navy">Recent Learning Logs</h3>
                        <button onClick={() => navigate('/s/notes')} className="text-xs font-black text-ssamz-blue uppercase tracking-tighter hover:underline">View All</button>
                    </div>
                    <div className="space-y-6">
                        {[
                            { date: '2026.01.20', subject: 'Math', note: 'Linear equations practice completed.' },
                            { date: '2026.01.19', subject: 'English', note: 'Vocabulary test: 95/100' },
                        ].map((log, i) => (
                            <div key={i} className="p-4 bg-ssamz-bg/50 rounded-xl border border-ssamz-border group hover:border-ssamz-blue transition-all">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="text-[10px] font-black text-slate-400 uppercase">{log.date}</span>
                                    <span className="text-[10px] font-black text-ssamz-blue bg-white px-2 py-0.5 rounded shadow-sm">{log.subject}</span>
                                </div>
                                <p className="text-sm font-bold text-slate-600 truncate">{log.note}</p>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Notices / Announcements - Brand Styled */}
                <div className="bg-ssamz-navy rounded-[2rem] p-8 text-white relative overflow-hidden shadow-2xl border-none">
                    <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/5 rounded-full blur-2xl"></div>
                    <h3 className="text-lg font-bold mb-6 relative z-10">Academy Notices</h3>
                    <div className="space-y-4 relative z-10">
                        <div className="p-5 bg-white/5 rounded-2xl border border-white/10">
                            <h4 className="text-sm font-black mb-2">Winter Break Schedule</h4>
                            <p className="text-xs opacity-60 leading-relaxed">The academy will be closed from Jan 25th to Jan 28th for Lunar New Year.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default StudentDashboard;
