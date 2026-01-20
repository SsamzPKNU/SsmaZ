function PublicLayout({ children }) {
    return (
        <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
            {children}
        </div>
    );
}

export default PublicLayout;
