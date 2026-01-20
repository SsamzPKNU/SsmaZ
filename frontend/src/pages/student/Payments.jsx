import { useState } from 'react';

function StudentPayments() {
    const [payments] = useState([
        { date: '2026-01-15', amount: '$350', method: 'Credit Card', status: 'Paid' },
        { date: '2025-12-15', amount: '$350', method: 'Bank Transfer', status: 'Paid' },
    ]);

    return (
        <div className="space-y-10">
            <h1 className="text-3xl font-black text-ssamz-navy tracking-tight">Payment History</h1>

            <div className="grid grid-cols-2 gap-8 mb-10">
                <div className="bg-ssamz-navy rounded-[2rem] p-8 text-white relative overflow-hidden shadow-2xl border-none">
                    <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/5 rounded-full blur-2xl"></div>
                    <p className="text-xs font-black uppercase tracking-widest opacity-60 mb-2 relative z-10">Next Payment Due</p>
                    <p className="text-3xl font-black mb-4 relative z-10">$350.00</p>
                    <p className="text-xs font-bold text-white/40 relative z-10">Due Date: February 15, 2026</p>
                    <button className="mt-8 w-full py-4 bg-ssamz-blue text-white font-black text-sm rounded-xl hover:bg-ssamz-blue/90 transition-all shadow-lg shadow-ssamz-navy/40 relative z-10">Pay Now</button>
                </div>
                <div className="bg-white rounded-[2rem] p-8 flex flex-col justify-center shadow-card border border-ssamz-border">
                    <p className="text-xs font-black text-slate-400 uppercase tracking-widest mb-2">Total Paid (2026)</p>
                    <p className="text-3xl font-black text-ssamz-navy">$700.00</p>
                    <div className="mt-4 w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                        <div className="bg-emerald-500 h-full w-[16%]"></div>
                    </div>
                </div>
            </div>

            <div className="bg-white rounded-[2rem] shadow-card border border-ssamz-border overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-[#f8fafc] text-slate-400 text-[10px] font-black uppercase tracking-widest border-b border-ssamz-border">
                        <tr>
                            <th className="px-8 py-4">Date</th>
                            <th className="px-8 py-4">Amount</th>
                            <th className="px-8 py-4">Method</th>
                            <th className="px-8 py-4">Status</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                        {payments.map((p, i) => (
                            <tr key={i} className="hover:bg-slate-50/50 transition-all">
                                <td className="px-8 py-5 text-sm font-bold text-ssamz-text">{p.date}</td>
                                <td className="px-8 py-4.5 text-sm font-black text-ssamz-text">{p.amount}</td>
                                <td className="px-8 py-5 text-sm font-bold text-slate-500">{p.method}</td>
                                <td className="px-8 py-5">
                                    <span className="px-3 py-1 bg-emerald-50 text-emerald-600 rounded-full text-[10px] font-black uppercase tracking-tighter">
                                        {p.status}
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

export default StudentPayments;
