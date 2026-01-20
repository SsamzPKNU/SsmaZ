import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { signup } from '../../services/api';

/**
 * Premium Join Page - Navy Theme
 */
function JoinPage() {
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
                const detail = err.response.data.detail;
                // FastAPI/Pydantic 유효성 검사 에러는 배열로 옴
                if (Array.isArray(detail)) {
                    // 첫 번째 에러 메시지만 표시하거나, 필요한 경우 가공
                    // 예: { loc: ['body', 'username'], msg: 'Field required', ... }
                    setError(detail[0].msg || '입력값을 확인해주세요.');
                }
                // 일반적인 에러 메시지가 문자열로 오는 경우
                else if (typeof detail === 'string') {
                    setError(detail);
                }
                // 그 외 알 수 없는 객체인 경우
                else {
                    setError('회원가입 처리에 실패했습니다. (' + JSON.stringify(detail) + ')');
                }
            } else {
                setError('서버와 연결할 수 없습니다');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-ssamz-bg flex items-center justify-center p-6 relative overflow-hidden">
            {/* Background Decoration */}
            <div className="absolute top-0 left-0 w-full h-full -z-10 opacity-20">
                <div className="absolute -top-40 -right-40 w-[600px] h-[600px] bg-ssamz-navy/5 rounded-full blur-[100px]"></div>
                <div className="absolute -bottom-40 -left-40 w-[600px] h-[600px] bg-ssamz-blue/5 rounded-full blur-[100px]"></div>
            </div>

            <div className="max-w-xl w-full animate-fade-in">
                {/* Logo Section */}
                <div className="flex flex-col items-center mb-10">
                    <div className="text-5xl font-serif italic text-ssamz-navy mb-2">Sz</div>
                    <div className="text-sm font-black text-ssamz-navy tracking-[0.2em] uppercase">SAMZ</div>
                </div>

                {/* Join Card - Brand Styled */}
                <div className="bg-white rounded-[2rem] p-10 shadow-card border border-ssamz-border">
                    <h2 className="text-2xl font-black text-ssamz-navy mb-8 text-center uppercase tracking-tight">Create Account</h2>

                    {/* 성공 메시지 */}
                    {success && (
                        <div className="bg-emerald-50 border border-emerald-100 text-emerald-600 text-xs font-bold p-4 rounded-xl mb-6">
                            회원가입이 완료되었습니다! 로그인 페이지로 이동합니다...
                        </div>
                    )}

                    {/* 에러 메시지 */}
                    {error && (
                        <div className="bg-red-50 border border-red-100 text-red-500 text-xs font-bold p-4 rounded-xl mb-6">
                            ⚠️ {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        {/* 아이디 입력 */}
                        <div>
                            <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Username <span className="text-red-500">*</span></label>
                            <input
                                type="text"
                                name="username"
                                value={formData.username}
                                onChange={handleChange}
                                required
                                className="w-full px-5 py-3.5 bg-ssamz-bg border border-ssamz-border rounded-xl focus:ring-4 focus:ring-ssamz-blue/5 focus:border-ssamz-blue focus:bg-white outline-none transition-all font-bold text-ssamz-text"
                                placeholder="사용할 아이디"
                            />
                        </div>

                        {/* 비밀번호 입력 */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Password <span className="text-red-500">*</span></label>
                                <input
                                    type="password"
                                    name="password"
                                    value={formData.password}
                                    onChange={handleChange}
                                    required
                                    className="w-full px-5 py-3.5 bg-ssamz-bg border border-ssamz-border rounded-xl focus:ring-4 focus:ring-ssamz-blue/5 focus:border-ssamz-blue focus:bg-white outline-none transition-all font-bold text-ssamz-text"
                                    placeholder="6자 이상"
                                />
                            </div>
                            <div>
                                <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Confirm <span className="text-red-500">*</span></label>
                                <input
                                    type="password"
                                    name="passwordConfirm"
                                    value={formData.passwordConfirm}
                                    onChange={handleChange}
                                    required
                                    className="w-full px-5 py-3.5 bg-ssamz-bg border border-ssamz-border rounded-xl focus:ring-4 focus:ring-ssamz-blue/5 focus:border-ssamz-blue focus:bg-white outline-none transition-all font-bold text-ssamz-text"
                                    placeholder="비밀번호 재입력"
                                />
                            </div>
                        </div>

                        {/* 학원 ID 및 역할 */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Academy ID <span className="text-red-500">*</span></label>
                                <input
                                    type="number"
                                    name="academy_id"
                                    value={formData.academy_id}
                                    onChange={handleChange}
                                    required
                                    className="w-full px-5 py-3.5 bg-ssamz-bg border border-ssamz-border rounded-xl focus:ring-4 focus:ring-ssamz-blue/5 focus:border-ssamz-blue focus:bg-white outline-none transition-all font-bold text-ssamz-text"
                                    placeholder="학원 번호"
                                />
                            </div>
                            <div>
                                <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Role <span className="text-red-500">*</span></label>
                                <select
                                    name="user_role"
                                    value={formData.user_role}
                                    onChange={handleChange}
                                    className="w-full px-5 py-3.5 bg-ssamz-bg border border-ssamz-border rounded-xl focus:ring-4 focus:ring-ssamz-blue/5 focus:border-ssamz-blue focus:bg-white outline-none transition-all font-bold text-ssamz-text"
                                >
                                    <option value="ADMIN">ADMIN</option>
                                    <option value="TEACHER">TEACHER</option>
                                    <option value="STUDENT">STUDENT</option>
                                </select>
                            </div>
                        </div>

                        {/* 이름 및 전화번호 */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Name</label>
                                <input
                                    type="text"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    className="w-full px-5 py-3.5 bg-ssamz-bg border border-ssamz-border rounded-xl focus:ring-4 focus:ring-ssamz-blue/5 focus:border-ssamz-blue focus:bg-white outline-none transition-all font-bold text-ssamz-text"
                                    placeholder="실명"
                                />
                            </div>
                            <div>
                                <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Phone</label>
                                <input
                                    type="tel"
                                    name="phone"
                                    value={formData.phone}
                                    onChange={handleChange}
                                    className="w-full px-5 py-3.5 bg-ssamz-bg border border-ssamz-border rounded-xl focus:ring-4 focus:ring-ssamz-blue/5 focus:border-ssamz-blue focus:bg-white outline-none transition-all font-bold text-ssamz-text"
                                    placeholder="010-0000-0000"
                                />
                            </div>
                        </div>

                        {/* 버튼 */}
                        <button
                            type="submit"
                            disabled={loading || success}
                            className="w-full py-4 bg-ssamz-navy text-white font-black rounded-xl shadow-2xl shadow-ssamz-navy/20 hover:bg-ssamz-navy/90 transition-all scale-100 active:scale-95 disabled:opacity-50 mt-4"
                        >
                            {loading ? '가입 처리 중...' : 'CREATE ACCOUNT'}
                        </button>
                    </form>

                    <div className="mt-8 pt-8 border-t border-ssamz-bg text-center">
                        <p className="text-xs font-bold text-slate-400">
                            이미 계정이 있으신가요?{' '}
                            <Link to="/login" className="text-ssamz-blue hover:underline ml-1">로그인하기</Link>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default JoinPage;
