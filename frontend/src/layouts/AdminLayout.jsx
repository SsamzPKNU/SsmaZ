import Sidebar from '../components/Sidebar';
import Topbar from '../components/Topbar';

const adminMenus = [
    { path: '/a', label: 'Dashboard', icon: '🏠' },
    { path: '/a/students', label: 'Student List', icon: '👥' },
    { path: '/a/classes', label: 'Classes', icon: '🏫' },
    { path: '/a/attendance', label: 'Attendance', icon: '✅' },
    { path: '/a/payments', label: 'Payments', icon: '💳' },
    { path: '/a/settings', label: 'Settings', icon: '⚙️' },
];

function AdminLayout({ children }) {
    return (
        <div className="flex h-screen bg-ssamz-bg font-sans text-ssamz-text">
            <Sidebar menus={adminMenus} />
            <main className="flex-1 flex flex-col overflow-hidden">
                <Topbar userRole="Admin" />
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

export default AdminLayout;
