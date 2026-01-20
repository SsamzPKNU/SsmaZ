import { createBrowserRouter, Navigate } from 'react-router-dom';
import { isAuthenticated } from '../services/api';

// Layouts
import AdminLayout from '../layouts/AdminLayout';
import StudentLayout from '../layouts/StudentLayout';
import PublicLayout from '../layouts/PublicLayout';

// Public Pages
import LoginPage from '../pages/public/Login';
import JoinPage from '../pages/public/Join';
import LandingPage from '../pages/public/Home';

// Admin Pages
import AdminDashboard from '../pages/admin/Dashboard';
import AdminStudents from '../pages/admin/Students';
import AdminClasses from '../pages/admin/Classes';
import AdminAttendance from '../pages/admin/Attendance';
import AdminPayments from '../pages/admin/Payments';
import AdminLogs from '../pages/admin/Logs';
import AdminSettings from '../pages/admin/Settings';

// Student Pages
import StudentDashboard from '../pages/student/Dashboard';
import StudentAttendance from '../pages/student/Attendance';
import StudentPayments from '../pages/student/Payments';
import StudentNotes from '../pages/student/Notes';

// Route Guards
function ProtectedRoute({ children }) {
    return isAuthenticated() ? children : <Navigate to="/login" replace />;
}

function PublicRoute({ children }) {
    return !isAuthenticated() ? children : <Navigate to="/a" replace />;
}

export const router = createBrowserRouter([
    {
        path: "/",
        element: <PublicLayout><LandingPage /></PublicLayout>,
    },
    {
        path: "/login",
        element: <PublicRoute><PublicLayout><LoginPage /></PublicLayout></PublicRoute>,
    },
    {
        path: "/join",
        element: <PublicRoute><PublicLayout><JoinPage /></PublicLayout></PublicRoute>,
    },
    {
        path: "/a",
        element: <ProtectedRoute><AdminLayout><AdminDashboard /></AdminLayout></ProtectedRoute>,
    },
    {
        path: "/a/students",
        element: <ProtectedRoute><AdminLayout><AdminStudents /></AdminLayout></ProtectedRoute>,
    },
    {
        path: "/a/classes",
        element: <ProtectedRoute><AdminLayout><AdminClasses /></AdminLayout></ProtectedRoute>,
    },
    {
        path: "/a/attendance",
        element: <ProtectedRoute><AdminLayout><AdminAttendance /></AdminLayout></ProtectedRoute>,
    },
    {
        path: "/a/payments",
        element: <ProtectedRoute><AdminLayout><AdminPayments /></AdminLayout></ProtectedRoute>,
    },
    {
        path: "/a/logs",
        element: <ProtectedRoute><AdminLayout><AdminLogs /></AdminLayout></ProtectedRoute>,
    },
    {
        path: "/a/settings",
        element: <ProtectedRoute><AdminLayout><AdminSettings /></AdminLayout></ProtectedRoute>,
    },
    {
        path: "/s",
        element: <ProtectedRoute><StudentLayout><StudentDashboard /></StudentLayout></ProtectedRoute>,
    },
    {
        path: "/s/attendance",
        element: <ProtectedRoute><StudentLayout><StudentAttendance /></StudentLayout></ProtectedRoute>,
    },
    {
        path: "/s/payments",
        element: <ProtectedRoute><StudentLayout><StudentPayments /></StudentLayout></ProtectedRoute>,
    },
    {
        path: "/s/notes",
        element: <ProtectedRoute><StudentLayout><StudentNotes /></StudentLayout></ProtectedRoute>,
    },
    {
        path: "*",
        element: <Navigate to="/" replace />,
    }
], {
    future: {
        v7_startTransition: true,
        v7_relativeSplatPath: true,
        v7_fetcherPersist: true,
        v7_normalizeFormMethod: true,
        v7_partialHydration: true,
        v7_skipActionErrorRevalidation: true,
    }
});
