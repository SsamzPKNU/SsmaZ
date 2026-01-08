/**
 * 회원가입 페이지
 * 새로운 사용자 등록을 처리합니다
 */

import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { signup } from '../services/api';

function SignupPage() {
    const navigate = useNavigate();

    // 폼 상태 관리
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        passwordConfirm: '',
        academy_id: '',
        user_role: 'TEACHER',
        name: '',
        phone: '',
    });

    // 로딩 및 에러 상태
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);

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

        // 비밀번호 확인
        if (formData.password !== formData.passwordConfirm) {
            setError('비밀번호가 일치하지 않습니다');
            setLoading(false);
            return;
        }

        // 비밀번호 길이 확인
        if (formData.password.length < 6) {
            setError('비밀번호는 최소 6자 이상이어야 합니다');
            setLoading(false);
            return;
        }

        try {
            // API 요청용 데이터 (passwordConfirm 제외)
            const { passwordConfirm, ...signupData } = formData;

            // academy_id를 숫자로 변환
            signupData.academy_id = parseInt(signupData.academy_id);

            // 회원가입 API 호출
            const response = await signup(signupData);

            console.log('회원가입 성공:', response);

            // 성공 메시지 표시
            setSuccess(true);

            // 2초 후 로그인 페이지로 이동
            setTimeout(() => {
                navigate('/login');
            }, 2000);

        } catch (err) {
            console.error('회원가입 실패:', err);

            // 에러 메시지 설정
            if (err.response) {
                setError(err.response.data.detail || '회원가입에 실패했습니다');
            } else {
                setError('서버와 연결할 수 없습니다');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
            <div className="max-w-2xl w-full">
                {/* 로고 및 제목 */}
                <div className="text-center mb-8">
                    <h1 className="text-4xl font-bold text-primary-700 mb-2">SsmaZ</h1>
                    <p className="text-gray-600">학원 관리 서비스</p>
                </div>

                {/* 회원가입 폼 */}
                <div className="bg-white rounded-2xl shadow-xl p-8">
                    <h2 className="text-2xl font-bold text-gray-800 mb-6">회원가입</h2>

                    {/* 성공 메시지 */}
                    {success && (
                        <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-4">
                            회원가입이 완료되었습니다! 로그인 페이지로 이동합니다...
                        </div>
                    )}

                    {/* 에러 메시지 */}
                    {error && (
                        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        {/* 아이디 입력 */}
                        <div>
                            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                                아이디 <span className="text-red-500">*</span>
                            </label>
                            <input
                                type="text"
                                id="username"
                                name="username"
                                value={formData.username}
                                onChange={handleChange}
                                required
                                minLength={3}
                                maxLength={50}
                                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
                                placeholder="영문, 숫자, 언더스코어 사용 가능"
                            />
                            <p className="text-xs text-gray-500 mt-1">3-50자, 영문/숫자/언더스코어만 사용</p>
                        </div>

                        {/* 비밀번호 입력 */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                                    비밀번호 <span className="text-red-500">*</span>
                                </label>
                                <input
                                    type="password"
                                    id="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    required
                                    minLength={6}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
                                    placeholder="최소 6자 이상"
                                />
                            </div>

                            <div>
                                <label htmlFor="passwordConfirm" className="block text-sm font-medium text-gray-700 mb-2">
                                    비밀번호 확인 <span className="text-red-500">*</span>
                                </label>
                                <input
                                    type="password"
                                    id="passwordConfirm"
                                    name="passwordConfirm"
                                    value={formData.passwordConfirm}
                                    onChange={handleChange}
                                    required
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
                                    placeholder="비밀번호 재입력"
                                />
                            </div>
                        </div>

                        {/* 학원 ID 및 역할 */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label htmlFor="academy_id" className="block text-sm font-medium text-gray-700 mb-2">
                                    학원 ID <span className="text-red-500">*</span>
                                </label>
                                <input
                                    type="number"
                                    id="academy_id"
                                    name="academy_id"
                                    value={formData.academy_id}
                                    onChange={handleChange}
                                    required
                                    min={1}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
                                    placeholder="소속 학원 ID"
                                />
                            </div>

                            <div>
                                <label htmlFor="user_role" className="block text-sm font-medium text-gray-700 mb-2">
                                    역할 <span className="text-red-500">*</span>
                                </label>
                                <select
                                    id="user_role"
                                    name="user_role"
                                    value={formData.user_role}
                                    onChange={handleChange}
                                    required
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
                                >
                                    <option value="TEACHER">선생님</option>
                                    <option value="STUDENT">학생</option>
                                    <option value="ADMIN">관리자</option>
                                </select>
                            </div>
                        </div>

                        {/* 이름 및 전화번호 (선택) */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                                    이름
                                </label>
                                <input
                                    type="text"
                                    id="name"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    maxLength={50}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
                                    placeholder="실명 (선택)"
                                />
                            </div>

                            <div>
                                <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                                    전화번호
                                </label>
                                <input
                                    type="tel"
                                    id="phone"
                                    name="phone"
                                    value={formData.phone}
                                    onChange={handleChange}
                                    maxLength={20}
                                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent transition"
                                    placeholder="010-1234-5678 (선택)"
                                />
                            </div>
                        </div>

                        {/* 회원가입 버튼 */}
                        <button
                            type="submit"
                            disabled={loading || success}
                            className="w-full bg-primary-600 hover:bg-primary-700 text-white font-semibold py-3 px-4 rounded-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed mt-6"
                        >
                            {loading ? '가입 중...' : success ? '가입 완료!' : '회원가입'}
                        </button>
                    </form>

                    {/* 로그인 링크 */}
                    <div className="mt-6 text-center">
                        <p className="text-gray-600">
                            이미 계정이 있으신가요?{' '}
                            <Link to="/login" className="text-primary-600 hover:text-primary-700 font-semibold">
                                로그인
                            </Link>
                        </p>
                    </div>
                </div>

                {/* 푸터 */}
                <p className="text-center text-gray-500 text-sm mt-8">
                    © 2026 SsmaZ. All rights reserved.
                </p>
            </div>
        </div>
    );
}

export default SignupPage;
