<<<<<<< Updated upstream
/**
 * 메인 App 컴포넌트
 * 라우팅 및 전역 설정
 */

=======
>>>>>>> Stashed changes
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { isAuthenticated } from './services/api';
import LoginPage from './pages/public/Login';
import JoinPage from './pages/public/Join';
import LandingPage from './pages/public/Home';
// 2. 관리자 영역 (/a)
import AdminDashboard from './pages/admin/Dashboard';
import AdminStudents from './pages/admin/Students';
import AdminClasses from './pages/admin/Classes';
import AdminAttendance from './pages/admin/Attendance';
import AdminPayments from './pages/admin/Payments';
import AdminLogs from './pages/admin/Logs';
import AdminSettings from './pages/admin/Settings';

// 3. 학생/학부모 영역 (/s)
import StudentDashboard from './pages/student/Dashboard';
import StudentAttendance from './pages/student/Attendance';
import StudentPayments from './pages/student/Payments';
import StudentNotes from './pages/student/Notes';
import Layout from './components/Layout';

// 임시 Placeholder 컴포넌트들
const Placeholder = ({ title }) => (
    <div className="p-10 bg-white rounded-3xl border border-dashed border-slate-300 text-center">
        <h2 className="text-2xl font-black text-slate-300">{title} 준비 중</h2>
        <p className="text-slate-400 mt-2">곧 출시될 예정입니다.</p>
    </div>
);

function ProtectedRoute({ children }) {
    return isAuthenticated() ? children : <Navigate to="/login" replace />;
}

function PublicRoute({ children }) {
    return !isAuthenticated() ? children : <Navigate to="/a" replace />;
}

function App() {
    return (
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
            <Routes>
<<<<<<< Updated upstream
                {/* 공개 라우트 */}
                <Route
                    path="/login"
                    element={
                        <PublicRoute>
                            <LoginPage />
                        </PublicRoute>
                    }
                />
                <Route
                    path="/signup"
                    element={
                        <PublicRoute>
                            <SignupPage />
                        </PublicRoute>
                    }
                />

                {/* 보호된 라우트 */}
                <Route
                    path="/"
                    element={
                        <ProtectedRoute>
                            <HomePage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/attendance"
                    element={
                        <ProtectedRoute>
                            <AttendanceDashboard />
                        </ProtectedRoute>
                    }
                />

                {/* 404 처리 */}
                <Route
                    path="*"
                    element={<Navigate to="/" replace />}
                />
=======
                {/* 1. 공개 페이지 */}
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
                <Route path="/join" element={<PublicRoute><JoinPage /></PublicRoute>} />

                {/* 2. 관리자 영역 (/a) */}
                <Route path="/a" element={<ProtectedRoute><Layout><AdminDashboard /></Layout></ProtectedRoute>} />
                <Route path="/a/students" element={<ProtectedRoute><Layout><AdminStudents /></Layout></ProtectedRoute>} />
                <Route path="/a/classes" element={<ProtectedRoute><Layout><AdminClasses /></Layout></ProtectedRoute>} />
                <Route path="/a/attendance" element={<ProtectedRoute><Layout><AdminAttendance /></Layout></ProtectedRoute>} />
                <Route path="/a/payments" element={<ProtectedRoute><Layout><AdminPayments /></Layout></ProtectedRoute>} />
                <Route path="/a/logs" element={<ProtectedRoute><Layout><AdminLogs /></Layout></ProtectedRoute>} />
                <Route path="/a/settings" element={<ProtectedRoute><Layout><AdminSettings /></Layout></ProtectedRoute>} />

                {/* 3. 학생/학부모 영역 (/s) */}
                <Route path="/s" element={<ProtectedRoute><Layout><StudentDashboard /></Layout></ProtectedRoute>} />
                <Route path="/s/attendance" element={<ProtectedRoute><Layout><StudentAttendance /></Layout></ProtectedRoute>} />
                <Route path="/s/payments" element={<ProtectedRoute><Layout><StudentPayments /></Layout></ProtectedRoute>} />
                <Route path="/s/notes" element={<ProtectedRoute><Layout><StudentNotes /></Layout></ProtectedRoute>} />

                {/* 404 처리 */}
                <Route path="*" element={<Navigate to="/" replace />} />
>>>>>>> Stashed changes
            </Routes>
        </Router>
    );
}

export default App;
