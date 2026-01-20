import { useState } from 'react';

/**
 * Refined Admin Payment Management Page
 */
function AdminPayments() {
    const [payments] = useState([
        { id: 1, name: '이민호', amount: '₩350,000', plan: '수학 정규반', date: '2026-01-15', status: '완료' },
        { id: 2, name: '박서준', amount: '₩280,000', plan: '영어 기초반', date: '2026-01-18', status: '완료' },
        { id: 3, name: '김태리', amount: '₩420,000', plan: '코딩 고급반', date: '-', status: '미납' },
        { id: 4, name: '강하늘', amount: '₩350,000', plan: '수학 정규반', date: '2026-01-20', status: '완료' },
        { id: 5, name: '신민아', amount: '₩280,000', plan: '영어 기초반', date: '-', status: '대기' },
    ]);

    return (
        <div className="space-y-10">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-black text-ssamz-navy mb-8">Payment Control</h1>
                <div className="flex space-x-3 mb-8">
                    <button className="px-6 py-2.5 bg-white text-slate-500 border border-slate-200 font-bold rounded-lg hover:bg-slate-50 transition-all">Excel Export</button>
                    <button className="px-6 py-2.5 bg-ssamz-navy text-white font-bold rounded-lg shadow-lg hover:shadow-xl transition-all">Add Payment</button>
                </div>
            </div>

            {/* Financial Stats Grid - Brand Styled */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-10">
                {[
                    { label: 'Monthly Revenue', value: '₩12,500,000', icon: '💰', growth: '+12%', active: true },
                    { label: 'Receivables', value: '₩2,140,000', icon: '📉', growth: '-5%', active: false },
                    { label: 'Paid Ratio', value: '84%', icon: '📊', growth: '+2%', active: false },
                ].map((stat, i) => (
                    <div key={i} className={`p-8 bg-white rounded-2xl flex items-center justify-between border ${stat.active ? 'border-ssamz-blue shadow-card' : 'border-slate-100 shadow-sm'}`}>
                        <div className="flex items-center space-x-6">
                            <div className={`w-14 h-14 rounded-full flex items-center justify-center text-2xl ${stat.active ? 'bg-blue-50 text-ssamz-blue' : 'bg-slate-50 text-slate-300'}`}>
                                {stat.icon}
                            </div>
                            <div>
                                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">{stat.label}</p>
                                <p className="text-xl font-bold text-ssamz-text">{stat.value}</p>
                            </div>
                        </div>
                        <div className={`text-[10px] font-black ${stat.growth.startsWith('+') ? 'text-emerald-500' : 'text-red-400'}`}>
                            {stat.growth}
                        </div>
                    </div>
                ))}
            </div>

            {/* Payment Record Table - Brand Styled */}
            <div className="bg-white rounded-[2rem] shadow-card border border-ssamz-border overflow-hidden">
                <div className="px-8 py-5 border-b border-ssamz-border flex items-center justify-between">
                    <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest">Payment History</p>
                    <select className="bg-ssamz-bg border-none rounded-lg px-3 py-1.5 text-[10px] font-black text-slate-400 uppercase outline-none">
                        <option>Monthly (Jan 2026)</option>
                    </select>
                </div>
                <table className="w-full text-left">
                    <thead className="bg-[#f8fafc] text-slate-400 text-[11px] font-bold border-b border-ssamz-border">
                        <tr>
                            <th className="px-8 py-4">Student</th>
                            <th className="px-8 py-4">Plan</th>
                            <th className="px-8 py-4">Amount</th>
                            <th className="px-8 py-4">Date</th>
                            <th className="px-8 py-4">Status</th>
                            <th className="px-8 py-4 text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                        {payments.map((p) => (
                            <tr key={p.id} className="hover:bg-slate-50/50 transition-all">
                                <td className="px-8 py-4.5 text-[13px] font-bold text-ssamz-text">{p.name}</td>
                                <td className="px-8 py-4.5 text-[13px] font-medium text-slate-500">{p.plan}</td>
                                <td className="px-8 py-4.5 text-[13px] font-black text-slate-700">{p.amount}</td>
                                <td className="px-8 py-4.5 text-[12px] font-medium text-slate-400">{p.date}</td>
                                <td className="px-8 py-4.5">
                                    <span className={`px-3 py-1 rounded-lg text-[10px] font-bold ${p.status === '완료' ? 'bg-emerald-50 text-emerald-500' :
                                        p.status === '미납' ? 'bg-red-50 text-red-500' : 'bg-amber-50 text-amber-500'
                                        }`}>
                                        {p.status}
                                    </span>
                                </td>
                                <td className="px-8 py-4.5 text-center">
                                    <button className="px-3 py-1 text-ssamz-blue text-[10px] font-black hover:underline transition-all">Receipt</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default AdminPayments;
