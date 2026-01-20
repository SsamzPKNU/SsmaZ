function Table({ headers, data, renderRow }) {
    return (
        <div className="overflow-x-auto">
            <table className="w-full">
                <thead>
                    <tr className="border-b border-ssamz-border">
                        {headers.map((header, index) => (
                            <th key={index} className="px-6 py-4 text-left text-[10px] font-black text-slate-400 uppercase tracking-widest">
                                {header}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                    {data.map((item, index) => renderRow(item, index))}
                </tbody>
            </table>
        </div>
    );
}

export default Table;
