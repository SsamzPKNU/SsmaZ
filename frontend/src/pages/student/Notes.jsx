import { useState } from 'react';

function StudentNotes() {
    const [logs] = useState([
        { date: '2026-01-20', subject: 'Math', teacher: 'Lee', content: 'Focused on linear equations. High participation.' },
        { date: '2026-01-19', subject: 'English', teacher: 'Park', content: 'Vocabulary test results: Improved significantly.' },
        { date: '2026-01-18', subject: 'Science', teacher: 'Kim', content: 'Chemical reactions lab. Followed safety protocols well.' },
    ]);

    return (
        <div className="space-y-10">
            <h1 className="text-3xl font-black text-ssamz-navy tracking-tight">Learning Logs & Notes</h1>

            <div className="grid grid-cols-1 gap-6">
                {logs.map((log, i) => (
                    <div key={i} className="bg-white rounded-[2rem] p-10 shadow-card border border-ssamz-border group hover:border-ssamz-blue/30 transition-all">
                        <div className="flex justify-between items-start mb-6">
                            <div className="flex items-center space-x-4">
                                <div className="p-3 bg-ssamz-bg text-ssamz-blue rounded-xl font-black text-xs uppercase shadow-sm">{log.subject}</div>
                                <div>
                                    <p className="text-sm font-black text-ssamz-text">{log.teacher} Teacher</p>
                                    <p className="text-[10px] font-black text-slate-300 uppercase tracking-widest">{log.date}</p>
                                </div>
                            </div>
                            <button className="text-slate-200 group-hover:text-ssamz-blue transition-colors text-xl">📌</button>
                        </div>
                        <p className="text-slate-600 font-medium leading-relaxed bg-ssamz-bg/50 p-6 rounded-2xl border border-ssamz-border/50">
                            {log.content}
                        </p>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default StudentNotes;
