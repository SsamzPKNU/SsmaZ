/**
 * 메인 App 컴포넌트
 * 라우팅 및 전역 설정
 */

import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { isAuthenticated } from './services/api';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import HomePage from './pages/HomePage';

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

                {/* 404 처리 */}
                <Route
                    path="*"
                    element={<Navigate to="/" replace />}
                />
            </Routes>
        </Router>
    );
}

export default App;
