import { useState } from 'react';

/**
 * Premium Admin Classes Management Page
 */
function AdminClasses() {
    const [classes] = useState([
        { id: 1, name: '초급 수학 A반', teacher: '김철수', students: 12, schedule: '월/수/금 15:00', status: '진행중' },
        { id: 2, name: '중급 영어 B반', teacher: '이영희', students: 8, schedule: '화/목 17:00', status: '진행중' },
        { id: 3, name: '고급 과학 C반', teacher: '박지성', students: 15, schedule: '토 10:00', status: '모집중' },
        { id: 4, name: '기초 코딩 D반', teacher: '최민수', students: 10, schedule: '월/수/금 18:00', status: '진행중' },
    ]);

    return (
        <div className="space-y-10">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-black text-ssamz-navy mb-8">Class Management</h1>
                <div className="flex space-x-3 mb-8">
                    <button className="px-6 py-2.5 bg-ssamz-navy text-white font-bold rounded-lg shadow-lg hover:shadow-xl transition-all">+ New Class</button>
                </div>
            </div>

            {/* Class Stats Summary - Brand Styled */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
                {[
                    { label: 'Total Classes', value: '18', icon: '🏫', active: true },
                    { label: 'Active Students', value: '142', icon: '👤', active: false },
                    { label: 'Average Size', value: '7.8', icon: '📊', active: false },
                    { label: 'Pending Apps', value: '5', icon: '📩', active: false },
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

            {/* Class List Table - Brand Styled */}
            <div className="bg-white rounded-[2rem] shadow-card border border-ssamz-border overflow-hidden">
                <div className="px-8 py-5 border-b border-ssamz-border flex items-center justify-between">
                    <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest">Operating Classes</p>
                    <select className="bg-ssamz-bg border-none rounded-lg px-3 py-1.5 text-[10px] font-black text-slate-400 uppercase outline-none">
                        <option>All Teachers</option>
                    </select>
                </div>
                <table className="w-full text-left">
                    <thead className="bg-[#f8fafc] text-slate-400 text-[11px] font-bold border-b border-ssamz-border">
                        <tr>
                            <th className="px-8 py-4">Class Name</th>
                            <th className="px-8 py-4">Teacher</th>
                            <th className="px-8 py-4">Students</th>
                            <th className="px-8 py-4">Schedule</th>
                            <th className="px-8 py-4">Status</th>
                            <th className="px-8 py-4 text-center">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                        {classes.map((cls) => (
                            <tr key={cls.id} className="hover:bg-slate-50/50 transition-all">
                                <td className="px-8 py-4.5">
                                    <div className="text-[13px] font-bold text-ssamz-text">{cls.name}</div>
                                    <div className="text-[10px] text-slate-300 font-medium tracking-wider">#{cls.id}</div>
                                </td>
                                <td className="px-8 py-4.5 text-[13px] font-medium text-slate-500">{cls.teacher}</td>
                                <td className="px-8 py-4.5 text-[13px] font-medium text-slate-500">{cls.students}명</td>
                                <td className="px-8 py-4.5 text-[12px] font-medium text-slate-400">{cls.schedule}</td>
                                <td className="px-8 py-4.5">
                                    <span className={`px-3 py-1 rounded-lg text-[10px] font-bold ${cls.status === '진행중' ? 'bg-sky-50 text-ssamz-blue' : 'bg-emerald-50 text-emerald-500'}`}>
                                        {cls.status}
                                    </span>
                                </td>
                                <td className="px-8 py-4.5 text-center">
                                    <button className="p-2 text-slate-200 hover:text-ssamz-blue transition-colors">
                                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                                        </svg>
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export default AdminClasses;
