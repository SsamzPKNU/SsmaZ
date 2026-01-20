import { useState } from 'react';

function StudentAttendance() {
    const [history] = useState([
        { date: '2026-01-20', checkIn: '09:00', checkOut: '12:00', status: 'Present' },
        { date: '2026-01-19', checkIn: '09:05', checkOut: '12:05', status: 'Late' },
        { date: '2026-01-18', checkIn: '08:55', checkOut: '11:55', status: 'Present' },
    ]);

    return (
        <div className="space-y-10">
            <h1 className="text-3xl font-black text-ssamz-navy tracking-tight">Attendance Record</h1>

            <div className="bg-white rounded-[2rem] shadow-card border border-ssamz-border overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-[#f8fafc] text-slate-400 text-[10px] font-black uppercase tracking-widest border-b border-ssamz-border">
                        <tr>
                            <th className="px-8 py-4">Date</th>
                            <th className="px-8 py-4">Check In</th>
                            <th className="px-8 py-4">Check Out</th>
                            <th className="px-8 py-4">Status</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                        {history.map((h, i) => (
                            <tr key={i} className="hover:bg-slate-50/50 transition-all">
                                <td className="px-8 py-5 text-sm font-bold text-ssamz-text">{h.date}</td>
                                <td className="px-8 py-5 text-sm font-bold text-slate-500">{h.checkIn}</td>
                                <td className="px-8 py-5 text-sm font-bold text-slate-500">{h.checkOut}</td>
                                <td className="px-8 py-5">
                                    <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-tighter ${h.status === 'Present' ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600'
                                        }`}>
                                        {h.status}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default StudentAttendance;
