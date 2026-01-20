import { useNavigate, Link } from 'react-router-dom';

/**
 * Premium Landing Page - Navy Theme
 */
function LandingPage() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-slate-50 font-sans text-slate-900 overflow-x-hidden">
            {/* Header / Nav */}
            <nav className="fixed w-full z-50 bg-white/70 backdrop-blur-xl border-b border-ssamz-border px-6 py-4 flex items-center justify-between">
                <div
                    onClick={() => navigate('/')}
                    className="flex items-center space-x-2 cursor-pointer"
                >
                    <div className="text-3xl font-serif italic text-ssamz-navy">Sz</div>
                    <span className="text-xl font-black text-ssamz-navy tracking-tighter uppercase">SAMZ</span>
                </div>
                <div className="hidden md:flex items-center space-x-10 text-sm font-bold text-slate-500">
                    <a href="#features" className="hover:text-ssamz-navy transition-colors">기능소개</a>
                    <a href="#about" className="hover:text-ssamz-navy transition-colors">서비스 안내</a>
                    <a href="#contact" className="hover:text-ssamz-navy transition-colors">문의하기</a>
                    <Link to="/login" className="px-6 py-2.5 bg-ssamz-navy text-white rounded-xl shadow-lg shadow-ssamz-navy/10 hover:bg-ssamz-navy/90 transition-all">시작하기</Link>
                </div>
            </nav>

            {/* Hero Section */}
            <header className="relative pt-48 pb-32 px-6 flex flex-col items-center text-center">
                <div className="absolute top-0 left-0 w-full h-full -z-10 opacity-30">
                    <div className="absolute top-20 left-20 w-96 h-96 bg-blue-100 rounded-full blur-3xl"></div>
                    <div className="absolute bottom-20 right-20 w-96 h-96 bg-ssamz-bg rounded-full blur-3xl"></div>
                </div>

                <div className="animate-fade-in max-w-4xl">
                    <span className="px-4 py-1.5 bg-ssamz-navy/5 text-ssamz-navy text-xs font-black uppercase tracking-[0.2em] rounded-full inline-block mb-6 tracking-widest">Premium Academy Solution</span>
                    <h1 className="text-6xl md:text-8xl font-black text-ssamz-navy tracking-tight leading-[1.1] mb-10">
                        학원 운영의 새로운 기준, <br />
                        <span className="text-ssamz-blue underline decoration-blue-100 underline-offset-8">SsamZ</span>와 함께하세요.
                    </h1>
                    <p className="text-xl text-slate-500 font-medium leading-relaxed max-w-2xl mx-auto mb-12">
                        출결부터 수납, 학습 기록까지 조각난 관리 시스템을 하나로. <br />
                        가장 완벽한 학원 관리 플랫폼을 지금 경험해보세요.
                    </p>
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                        <button onClick={() => navigate('/join')} className="w-full sm:w-auto px-10 py-5 bg-ssamz-navy text-white font-black rounded-2xl shadow-2xl shadow-ssamz-navy/40 hover:scale-105 transition-all text-lg">
                            무료로 시작하기
                        </button>
                        <button onClick={() => navigate('/login')} className="w-full sm:w-auto px-10 py-5 bg-white text-ssamz-navy border-2 border-ssamz-border font-black rounded-2xl hover:bg-ssamz-bg transition-all text-lg">
                            관리자/학생 로그인
                        </button>
                    </div>
                </div>
            </header>

            {/* Feature Cards 섹션 - Brand Styled */}
            <section id="features" className="py-32 bg-white px-6">
                <div className="max-w-[1400px] mx-auto">
                    <div className="text-center mb-24">
                        <h2 className="text-4xl font-black text-ssamz-navy mb-4 tracking-tight">강력한 핵심 기능</h2>
                        <p className="text-lg text-slate-400 font-bold">학부모와 원장님 모두가 만족하는 SsamZ의 솔루션</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                        {[
                            { title: '출결 관리', desc: '등/하원 시 자동 알림 발송으로 부모님의 안심을 더합니다.', icon: '📍', color: 'bg-blue-50 text-ssamz-blue' },
                            { title: '수납/정산', desc: '복잡한 수납 일정과 미납 관리를 클릭 한 번으로 정산하세요.', icon: '💳', color: 'bg-emerald-50 text-emerald-500' },
                            { title: '학습 알림장', desc: '아이의 학습 태도와 과제 현황을 일기처럼 기록하고 공유합니다.', icon: '📝', color: 'bg-blue-50 text-ssamz-blue' },
                            { title: '통계 리포트', desc: '월별 매출과 원생 증가 추이를 비주얼 차트로 확인하세요.', icon: '📊', color: 'bg-ssamz-bg text-ssamz-navy' },
                        ].map((f, i) => (
                            <div key={i} className="bg-white rounded-[2rem] p-10 group cursor-default shadow-card border border-ssamz-border transition-all hover:translate-y-[-4px]">
                                <div className={`w-16 h-16 ${f.color} rounded-2xl flex items-center justify-center text-3xl mb-8 shadow-sm group-hover:scale-110 transition-transform`}>
                                    {f.icon}
                                </div>
                                <h3 className="text-xl font-bold text-ssamz-text mb-4">{f.title}</h3>
                                <p className="text-slate-400 font-bold text-sm leading-relaxed">{f.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* Contact Section - Brand Styled */}
            <section id="contact" className="py-32 bg-ssamz-bg/50 px-6">
                <div className="max-w-4xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="text-4xl font-black text-ssamz-navy mb-4 tracking-tight">문의하기</h2>
                        <p className="text-lg text-slate-400 font-bold">궁금하신 점이 있다면 언제든 문의해 주세요.</p>
                    </div>

                    <div className="bg-white rounded-[2rem] p-10 shadow-card border border-ssamz-border">
                        <form className="space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">학원명</label>
                                    <input type="text" placeholder="SsamZ 학원" className="w-full px-5 py-3.5 bg-ssamz-bg/50 border border-ssamz-border rounded-xl focus:ring-4 ring-ssamz-blue/5 outline-none font-bold text-ssamz-text shadow-sm" />
                                </div>
                                <div className="space-y-2">
                                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">연락처</label>
                                    <input type="tel" placeholder="010-0000-0000" className="w-full px-5 py-3.5 bg-ssamz-bg/50 border border-ssamz-border rounded-xl focus:ring-4 ring-ssamz-blue/5 outline-none font-bold text-ssamz-text shadow-sm" />
                                </div>
                            </div>
                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">문의 내용</label>
                                <textarea rows="4" placeholder="문의하실 내용을 입력하세요" className="w-full px-5 py-3.5 bg-ssamz-bg/50 border border-ssamz-border rounded-xl focus:ring-4 ring-ssamz-blue/5 outline-none font-bold text-ssamz-text shadow-sm resize-none"></textarea>
                            </div>
                            <button type="button" className="w-full py-4 bg-ssamz-navy text-white font-black rounded-xl shadow-2xl shadow-ssamz-navy/20 hover:bg-ssamz-navy/90 transition-all">
                                문의 신청하기
                            </button>
                        </form>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="py-20 px-6 border-t border-slate-100">
                <div className="max-w-[1400px] mx-auto flex flex-col md:flex-row justify-between items-center opacity-40">
                    <div className="flex items-center space-x-2 mb-8 md:mb-0">
                        <span className="text-2xl font-serif italic font-black">Sz</span>
                        <span className="text-sm font-black tracking-widest">SAMZ</span>
                    </div>
                    <p className="text-xs font-bold text-slate-500">© 2026 SsamZ. All rights reserved. </p>
                    <div className="flex space-x-8 mt-8 md:mt-0 text-xs font-bold">
                        <a href="#">Privacy Policy</a>
                        <a href="#">Terms of Service</a>
                        <a href="#">Support</a>
                    </div>
                </div>
            </footer>
        </div>
    );
}

export default LandingPage;
