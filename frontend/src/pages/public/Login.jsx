import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { login } from '../../services/api';

/**
 * Premium Login Page - Navy Theme
 */
function LoginPage() {
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            await login(username, password);
            // 기본적으로 관리자 대시보드로 이동
            navigate('/a');
        } catch (err) {
            setError('아이디 또는 비밀번호가 올바르지 않습니다.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-ssamz-bg flex items-center justify-center p-6 relative overflow-hidden">
            {/* Background Decoration */}
            <div className="absolute top-0 left-0 w-full h-full -z-10 opacity-20">
                <div className="absolute -top-40 -left-40 w-[600px] h-[600px] bg-ssamz-navy/5 rounded-full blur-[100px]"></div>
                <div className="absolute -bottom-40 -right-40 w-[600px] h-[600px] bg-ssamz-blue/5 rounded-full blur-[100px]"></div>
            </div>

            <div className="max-w-md w-full animate-fade-in">
                {/* Logo Section */}
                <div className="flex flex-col items-center mb-10">
                    <div className="text-5xl font-serif italic text-ssamz-navy mb-2">Sz</div>
                    <div className="text-sm font-black text-ssamz-navy tracking-[0.2em] uppercase">SAMZ</div>
                </div>

                {/* Login Card - Brand Styled */}
                <div className="bg-white rounded-[2rem] p-10 shadow-card border border-ssamz-border">
                    <h2 className="text-2xl font-black text-ssamz-navy mb-8 text-center uppercase tracking-tight">Sign In</h2>

                    {error && (
                        <div className="mb-6 p-4 bg-red-50 text-red-500 text-xs font-bold rounded-xl border border-red-100 animate-fade-in">
                            ⚠️ {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Username</label>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="w-full px-5 py-3.5 bg-ssamz-bg border border-ssamz-border rounded-xl focus:ring-4 focus:ring-ssamz-blue/5 focus:border-ssamz-blue focus:bg-white outline-none transition-all font-bold text-ssamz-text"
                                placeholder="아이디를 입력하세요"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2 ml-1">Password</label>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full px-5 py-3.5 bg-ssamz-bg border border-ssamz-border rounded-xl focus:ring-4 focus:ring-ssamz-blue/5 focus:border-ssamz-blue focus:bg-white outline-none transition-all font-bold text-ssamz-text"
                                placeholder="비밀번호를 입력하세요"
                                required
                            />
                        </div>

                        <div className="flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-slate-400 px-1">
                            <label className="flex items-center space-x-2 cursor-pointer hover:text-ssamz-navy transition-colors">
                                <input type="checkbox" className="rounded border-slate-200 text-ssamz-navy focus:ring-ssamz-navy" />
                                <span>Remember me</span>
                            </label>
                            <a href="#" className="hover:text-ssamz-navy transition-colors text-[10px]">Forgot Password?</a>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-4 bg-ssamz-navy text-white font-black rounded-xl shadow-2xl shadow-ssamz-navy/20 hover:bg-ssamz-navy/90 transition-all scale-100 active:scale-95 disabled:opacity-50"
                        >
                            {loading ? '로그인 중...' : 'SIGN IN'}
                        </button>
                    </form>

                    <div className="mt-8 pt-8 border-t border-ssamz-bg text-center">
                        <p className="text-xs font-bold text-slate-400">
                            처음이신가요?{' '}
                            <Link to="/join" className="text-ssamz-blue hover:underline ml-1">계정 만들기</Link>
                        </p>
                    </div>
                </div>

                {/* Footer Copy */}
                <p className="mt-10 text-center text-[10px] font-black text-slate-300 uppercase tracking-[0.2em]">
                    © 2026 SSAMZ ACADEMY SOLUTION
                </p>
            </div>
        </div>
    );
}

export default LoginPage;
