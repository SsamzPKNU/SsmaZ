import { useState } from 'react';

/**
 * Refined Admin System Logs Page
 */
function AdminLogs() {
    const [logs] = useState([
        { id: 1, type: 'LOGIN', target: '김원장 (admin)', time: '2026-01-20 12:30:15', status: 'SUCCESS', ip: '127.0.0.1' },
        { id: 2, type: 'SMS', target: '이민호 학부모', time: '2026-01-20 12:35:42', status: 'DELIVERED', ip: 'System' },
        { id: 3, type: 'PAYMENT', target: '박서준 수납', time: '2026-01-20 13:10:05', status: 'COMPLETED', ip: '127.0.0.1' },
        { id: 4, type: 'LOGIN', target: '이강사 (teacher)', time: '2026-01-20 13:42:10', status: 'FAILED', ip: '192.168.0.5' },
        { id: 5, type: 'SYSTEM', target: 'DB Backup', time: '2026-01-20 04:00:00', status: 'SUCCESS', ip: 'AuthServer' },
    ]);

    return (
        <div className="space-y-10">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-black text-ssamz-navy mb-8">System Logs</h1>
                <div className="flex space-x-3 mb-8">
                    <button className="px-6 py-2.5 bg-white text-red-400 border border-red-100 font-bold rounded-lg hover:bg-red-50 transition-all">Clear Logs</button>
                </div>
            </div>

            {/* Log Categories - Brand Responsive */}
            <div className="flex space-x-2 mb-8">
                {['All Logs', 'Login Logs', 'Delivery Logs', 'Payment Logs', 'Security'].map((cat, i) => (
                    <button key={i} className={`px-5 py-2.5 rounded-full text-[10px] font-black transition-all ${i === 0 ? 'bg-ssamz-navy text-white shadow-lg' : 'bg-white text-slate-400 border border-slate-100 hover:bg-slate-50'}`}>
                        {cat}
                    </button>
                ))}
            </div>

            {/* Activity Table - Brand Styled */}
            <div className="bg-white rounded-[2rem] shadow-card border border-ssamz-border overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-[#f8fafc] text-slate-400 text-[11px] font-bold border-b border-ssamz-border">
                        <tr>
                            <th className="px-8 py-4">Event Type</th>
                            <th className="px-8 py-4">Target / User</th>
                            <th className="px-8 py-4">Timestamp</th>
                            <th className="px-8 py-4">Status</th>
                            <th className="px-8 py-4">IP / Actor</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                        {logs.map((log) => (
                            <tr key={log.id} className="hover:bg-slate-50/50 transition-all">
                                <td className="px-8 py-4.5">
                                    <span className="px-2 py-1 bg-ssamz-bg text-slate-400 text-[9px] font-black rounded tracking-widest uppercase">
                                        {log.type}
                                    </span>
                                </td>
                                <td className="px-8 py-4.5 text-[13px] font-bold text-ssamz-text">{log.target}</td>
                                <td className="px-8 py-4.5 text-[12px] font-black text-slate-300 font-mono tracking-tight">{log.time}</td>
                                <td className="px-8 py-4.5">
                                    <div className="flex items-center space-x-2">
                                        <div className={`w-1.5 h-1.5 rounded-full ${log.status === 'SUCCESS' || log.status === 'DELIVERED' || log.status === 'COMPLETED' ? 'bg-emerald-500' : 'bg-red-400'}`}></div>
                                        <span className={`text-[10px] font-black tracking-widest ${log.status === 'SUCCESS' || log.status === 'DELIVERED' || log.status === 'COMPLETED' ? 'text-emerald-500' : 'text-red-400'}`}>{log.status}</span>
                                    </div>
                                </td>
                                <td className="px-8 py-4.5 text-[11px] text-slate-400 font-medium">{log.ip}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="flex justify-center mt-6">
                <button className="text-[10px] font-black text-slate-300 hover:text-ssamz-navy transition-all uppercase tracking-widest py-4">View Older Logs ...</button>
            </div>
        </div>
    );
}

export default AdminLogs;
