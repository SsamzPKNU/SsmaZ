/**
 * 📄 파일명: App.jsx
 * 📝 설명: 메인 App 컴포넌트 - 라우팅 및 접근 제어를 담당합니다
 * 🔗 API: 없음 (라우팅만 처리)
 * ✏️ 수정 시 주의: 새 페이지 추가 시 여기에 Route를 추가해야 합니다
 */

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { isAuthenticated } from './services/api';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import HomePage from './pages/HomePage';
import AttendanceDashboard from './pages/AttendanceDashboard';

/**
 * 보호된 라우트 컴포넌트
 * 로그인하지 않은 사용자는 로그인 페이지로 리다이렉트
 */
function ProtectedRoute({ children }) {
    return isAuthenticated() ? children : <Navigate to="/login" replace />;
}

/**
 * 공개 라우트 컴포넌트
 * 이미 로그인한 사용자는 홈으로 리다이렉트
 */
function PublicRoute({ children }) {
    return !isAuthenticated() ? children : <Navigate to="/" replace />;
}

function App() {
    return (
        <Router>
            <Routes>
                {/* 공개 라우트 - 로그인하지 않은 사용자만 접근 가능 */}
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

                {/* 보호된 라우트 - 로그인한 사용자만 접근 가능 */}
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

                {/* 404 처리 - 존재하지 않는 경로는 홈으로 */}
                <Route
                    path="*"
                    element={<Navigate to="/" replace />}
                />
            </Routes>
        </Router>
    );
}

export default App;
