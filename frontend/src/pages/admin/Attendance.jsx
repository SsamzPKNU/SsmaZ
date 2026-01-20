import { useState } from 'react';

/**
 * Refined Admin Attendance Management Page
 */
function AdminAttendance() {
    const [attendance] = useState([
        { id: 1, name: '이민호', class: '초급 수학 A반', time: '09:05', status: '출석', note: '정상 등원' },
        { id: 2, name: '박서준', class: '중급 영어 B반', time: '13:00', status: '출석', note: '정상 등원' },
        { id: 3, name: '강하늘', class: '초급 수학 A반', time: '09:15', status: '지각', note: '버스 지연' },
        { id: 4, name: '정해인', class: '고급 과학 C반', time: '-', status: '결석', note: '개인 사정' },
    ]);

    return (
        <div className="space-y-10">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-black text-ssamz-navy mb-8">Attendance Control</h1>
                <div className="flex space-x-3 mb-8">
                    <button className="px-6 py-2.5 bg-white text-slate-500 border border-slate-200 font-bold rounded-lg hover:bg-slate-50 transition-all">Download Report</button>
                    <button className="px-6 py-2.5 bg-ssamz-navy text-white font-bold rounded-lg shadow-lg hover:shadow-xl transition-all">Manual Check-In</button>
                </div>
            </div>

            {/* Quick Stats Grid - Brand Styled */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
                {[
                    { label: 'Present Today', value: '42', icon: '✅', active: true },
                    { label: 'Late', value: '3', icon: '⏰', active: false },
                    { label: 'Absent', value: '2', icon: '❌', active: false },
                    { label: 'Waiting', value: '5', icon: '⏳', active: false },
                ].map((stat, i) => (
                    <div key={i} className={`p-6 bg-white rounded-xl flex items-center space-x-5 border ${stat.active ? 'border-ssamz-blue shadow-card' : 'border-slate-100 shadow-sm'}`}>
                        <div className={`w-12 h-12 rounded-full flex items-center justify-center text-xl ${stat.active ? 'bg-blue-50 text-ssamz-blue' : 'bg-slate-50 text-slate-300'}`}>
                            {stat.icon}
                        </div>
                        <div>
                            <p className="text-[10px] font-bold text-slate-400 mb-0.5">{stat.label}</p>
                            <p className="text-lg font-bold text-ssamz-text">{stat.value}</p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Attendance List Table - Brand Styled */}
            <div className="bg-white rounded-[2rem] shadow-card border border-ssamz-border overflow-hidden">
                <div className="px-8 py-5 border-b border-ssamz-border flex items-center justify-between">
                    <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest">Daily Log - 2026.01.20</p>
                    <div className="relative">
                        <input
                            type="text"
                            placeholder="Search student..."
                            className="px-8 py-1.5 bg-ssamz-bg border border-ssamz-border rounded-lg text-[11px] font-bold outline-none focus:ring-1 ring-ssamz-blue/30 w-48"
                        />
                        <span className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[10px] opacity-30">🔍</span>
                    </div>
                </div>
                <table className="w-full text-left">
                    <thead className="bg-[#f8fafc] text-slate-400 text-[11px] font-bold border-b border-ssamz-border">
                        <tr>
                            <th className="px-8 py-4">Student</th>
                            <th className="px-8 py-4">Class</th>
                            <th className="px-8 py-4">Check-In</th>
                            <th className="px-8 py-4">Status</th>
                            <th className="px-8 py-4">Note</th>
                            <th className="px-8 py-4 text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                        {attendance.map((log) => (
                            <tr key={log.id} className="hover:bg-slate-50/50 transition-all">
                                <td className="px-8 py-4.5 text-[13px] font-bold text-ssamz-text">{log.name}</td>
                                <td className="px-8 py-4.5 text-[13px] font-medium text-slate-500">{log.class}</td>
                                <td className="px-8 py-4.5 text-[13px] font-black text-slate-500">{log.time}</td>
                                <td className="px-8 py-4.5">
                                    <span className={`px-3 py-1 rounded-lg text-[10px] font-bold ${log.status === '출석' ? 'bg-sky-50 text-ssamz-blue' :
                                        log.status === '지각' ? 'bg-amber-50 text-amber-500' : 'bg-red-50 text-red-500'
                                        }`}>
                                        {log.status}
                                    </span>
                                </td>
                                <td className="px-8 py-4.5 text-[11px] text-slate-400 font-medium">{log.note}</td>
                                <td className="px-8 py-4.5 text-center">
                                    <button className="px-3 py-1 text-ssamz-blue text-[10px] font-black hover:underline transition-all">Edit</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default AdminAttendance;
