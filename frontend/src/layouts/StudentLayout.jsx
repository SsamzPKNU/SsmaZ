import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';

const studentMenus = [
    { path: '/s', label: 'Dashboard', icon: '🏠' },
    { path: '/s/attendance', label: 'Attendance', icon: '📅' },
    { path: '/s/payments', label: 'Payments', icon: '💳' },
    { path: '/s/notes', label: 'Learning Logs', icon: '📢' },
];

function StudentLayout({ children }) {
    return (
        <div className="flex h-screen bg-ssamz-bg font-sans text-ssamz-text">
            <Sidebar menus={studentMenus} />
            <main className="flex-1 flex flex-col overflow-hidden">
                <Topbar userRole="Student" />
                <div className="flex-1 overflow-y-auto bg-ssamz-bg/50">
                    <div className="p-10">
                        <div className="max-w-[1400px] mx-auto animate-fade-in">
                            {children}
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default StudentLayout;
