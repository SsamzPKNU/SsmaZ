import { useState } from 'react';
import StatCard from '../../components/StatCard';
import Table from '../../components/Table';

/**
 * Admin Students - Matching the new Navy mockup
 */
function AdminStudents() {
    const [students] = useState([
        { id: 1, name: 'Kim Chulsso (010-1234....)', class: '1', contact: 'Closs', status: 'Active' },
        { id: 2, name: 'Lee Younghie (010-1234....)', class: '1', contact: '$12,500', status: 'Active' },
        { id: 3, name: 'Lee Younghie (010-5678....)', class: '10', contact: '$1,000', status: 'Inactive' },
    ]);

    return (
        <div className="space-y-10">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-black text-ssamz-navy mb-8">Student Management</h1>
                <div className="flex space-x-3 mb-8">
                    <button className="px-6 py-2.5 bg-ssamz-navy text-white font-bold rounded-lg shadow-lg hover:shadow-xl transition-all">+ Add Student</button>
                    <button className="px-6 py-2.5 bg-white text-ssamz-blue border border-ssamz-blue font-bold rounded-xl hover:bg-blue-50 transition-all">Export to Excel</button>
                </div>
            </div>

            {/* Stats Cards - Precisely Matching Brand Colors */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-10">
                {[
                    { label: "Today's Attendance", value: '45/50', icon: '🌀', active: true },
                    { label: 'Monthly Revenue', value: '$12,500', icon: '💲', active: false },
                    { label: 'New Students', value: '8', icon: '🎓', active: false },
                ].map((stat, i) => (
                    <StatCard
                        key={i}
                        label={stat.label}
                        value={stat.value}
                        icon={stat.icon}
                        active={stat.active}
                    />
                ))}
            </div>

            {/* Table - Consistent Brand Style */}
            <div className="bg-white rounded-[2rem] shadow-card border border-ssamz-border overflow-hidden">
                <div className="px-8 py-5 border-b border-ssamz-border">
                    <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest">Recent Students</p>
                </div>
                <Table
                    headers={['Name', 'Class', 'Contact', 'Status']}
                    data={students}
                    renderRow={(student, idx) => (
                        <tr key={idx} className="hover:bg-slate-50/50 transition-all">
                            <td className="px-8 py-4.5 text-[13px] font-medium text-ssamz-text">{student.name}</td>
                            <td className="px-8 py-4.5 text-[13px] font-medium text-slate-500">{student.class}</td>
                            <td className="px-8 py-4.5 text-[13px] font-medium text-slate-500">{student.contact}</td>
                            <td className="px-8 py-4.5">
                                <span className={`px-4 py-1.5 rounded-lg text-[11px] font-bold ${student.status === 'Active' ? 'bg-emerald-50 text-emerald-500' : 'bg-slate-100 text-slate-400'}`}>
                                    {student.status}
                                </span>
                            </td>
                        </tr>
                    )}
                />
            </div>
        </div>
    );
}

export default AdminStudents;
