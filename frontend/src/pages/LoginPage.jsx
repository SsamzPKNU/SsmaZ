/**
 * 📄 파일명: LoginPage.jsx
 * 📝 설명: 로그인 페이지 - 사용자 인증을 처리합니다
 * 🔗 API: POST /auth/login
 * ✏️ 수정 시 주의: formData의 필드명은 백엔드 API와 일치해야 합니다
 */

import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { login } from '../services/api';

function LoginPage() {
    const navigate = useNavigate();

    // 폼 상태 관리
    const [formData, setFormData] = useState({
        username: '',
        password: '',
    });

    // 로딩 및 에러 상태
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    /**
     * 입력 필드 변경 핸들러
     */
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        // 입력 시 에러 메시지 초기화
        setError('');
    };

    /**
     * 폼 제출 핸들러
     */
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            // 로그인 API 호출
            const response = await login(formData);

            console.log('로그인 성공:', response);

            // 메인 페이지로 이동
            navigate('/');

        } catch (err) {
            console.error('로그인 실패:', err);

            // 에러 메시지 설정
            if (err.response) {
                setError(err.response.data.detail || '로그인에 실패했습니다');
            } else {
                setError('서버와 연결할 수 없습니다');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="page-wrapper">
            <div className="max-w-md w-full">
                {/* 로고 및 제목 */}
                <div className="text-center mb-3">
                    <h1 className="logo">SsmaZ</h1>
                    <p className="text-gray">학원 관리 서비스</p>
                </div>

                {/* 로그인 폼 */}
                <div className="card-lg">
                    <h2 className="text-2xl font-bold text-gray-dark mb-3">로그인</h2>

                    {/* 에러 메시지 */}
                    {error && (
                        <div className="alert alert-error">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit}>
                        {/* 아이디 입력 */}
                        <div className="form-group">
                            <label htmlFor="username" className="form-label">
                                아이디
                            </label>
                            <input
                                type="text"
                                id="username"
                                name="username"
                                value={formData.username}
                                onChange={handleChange}
                                required
                                className="input"
                                placeholder="아이디를 입력하세요"
                            />
                        </div>

                        {/* 비밀번호 입력 */}
                        <div className="form-group">
                            <label htmlFor="password" className="form-label">
                                비밀번호
                            </label>
                            <input
                                type="password"
                                id="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                required
                                className="input"
                                placeholder="비밀번호를 입력하세요"
                            />
                        </div>

                        {/* 로그인 버튼 */}
                        <button
                            type="submit"
                            disabled={loading}
                            className="btn btn-primary btn-lg mt-2"
                        >
                            {loading ? '로그인 중...' : '로그인'}
                        </button>
                    </form>

                    {/* 회원가입 링크 */}
                    <div className="mt-3 text-center">
                        <p className="text-gray">
                            계정이 없으신가요?{' '}
                            <Link to="/signup" className="link">
                                회원가입
                            </Link>
                        </p>
                    </div>
                </div>

                {/* 푸터 */}
                <p className="text-center text-gray text-sm mt-3">
                    © 2026 SsmaZ. All rights reserved.
                </p>
            </div>
        </div>
    );
}

export default LoginPage;
