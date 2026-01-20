function StatCard({ label, value, icon, active, color }) {
    // Determine styles based on active state or color prop
    const borderClass = active ? 'border-ssamz-blue shadow-card' : 'border-slate-100 shadow-sm';
    const iconBgClass = active ? 'bg-blue-50 text-ssamz-blue' : 'bg-slate-50 text-slate-300';

    // If specific color overrides are needed, they can be handled here or passed via props

    return (
        <div className={`p-8 bg-white rounded-2xl flex items-center space-x-6 border ${borderClass}`}>
            <div className={`w-14 h-14 rounded-full flex items-center justify-center text-2xl ${iconBgClass}`}>
                {icon}
            </div>
            <div>
                <p className="text-[11px] font-bold text-slate-400 mb-1">{label}</p>
                <p className="text-xl font-bold text-ssamz-text tracking-tight">{value}</p>
            </div>
        </div>
    );
}

export default StatCard;
