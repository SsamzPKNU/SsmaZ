import { useState } from 'react';

/**
 * Refined Admin Academy Settings Page
 */
function AdminSettings() {
    const [settings] = useState({
        academyName: 'SsamZ 프리미엄 학원',
        owner: '김원장',
        phone: '02-1234-5678',
        email: 'contact@ssamz.com',
        address: '서울특별시 강남구 테헤란로 123',
        businessNumber: '123-45-67890',
        notifications: true,
        autoBackup: true
    });

    return (
        <div className="space-y-12 pb-10">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-black text-ssamz-navy mb-8">Academy Settings</h1>
                <div className="flex space-x-3 mb-8">
                    <button className="px-8 py-3 bg-ssamz-navy text-white font-black rounded-lg shadow-xl hover:shadow-2xl transition-all">Save Changes</button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
                {/* Profile Card - Brand Styled */}
                <div className="lg:col-span-1 space-y-8">
                    <div className="bg-white rounded-[2rem] p-10 text-center flex flex-col items-center border border-ssamz-border shadow-card">
                        <div className="w-32 h-32 bg-ssamz-bg rounded-[3rem] border-4 border-white shadow-xl flex items-center justify-center text-5xl mb-6">
                            🏫
                        </div>
                        <h2 className="text-lg font-black text-ssamz-text">{settings.academyName}</h2>
                        <p className="text-[10px] font-bold text-slate-400 mt-2 uppercase tracking-widest">Premium Member since 2024</p>

                        <div className="w-full h-px bg-ssamz-bg my-8"></div>

                        <div className="w-full space-y-4 text-left">
                            <div className="flex justify-between text-[11px] font-bold">
                                <span className="text-slate-300 uppercase tracking-widest">Plan</span>
                                <span className="text-ssamz-blue">Enterprise</span>
                            </div>
                            <div className="flex justify-between text-[11px] font-bold">
                                <span className="text-slate-300 uppercase tracking-widest">Storage</span>
                                <span className="text-slate-600">84% / 100GB</span>
                            </div>
                        </div>
                    </div>

                    <div className="bg-ssamz-navy rounded-[2rem] p-8 text-white relative overflow-hidden shadow-2xl">
                        <div className="absolute -right-6 -bottom-6 text-white/5 text-9xl font-black rotate-12">Sz</div>
                        <h3 className="text-[10px] font-black mb-2 opacity-40 uppercase tracking-widest relative z-10">Customer Support</h3>
                        <p className="text-sm font-bold mb-8 leading-relaxed relative z-10">전담 매니저가 <br />학원 운영을 도와드립니다.</p>
                        <button className="w-full py-3 bg-white/10 hover:bg-white/20 transition-all rounded-xl font-black text-[10px] ring-1 ring-white/10 uppercase tracking-widest relative z-10">Contact Support</button>
                    </div>
                </div>

                {/* Settings Form - Brand Styled */}
                <div className="lg:col-span-2 space-y-12">
                    <section className="space-y-8">
                        <div className="flex items-center space-x-4">
                            <div className="w-1.5 h-6 bg-ssamz-blue rounded-full"></div>
                            <h3 className="text-lg font-black text-ssamz-navy tracking-tight">Basic Information</h3>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-slate-300 uppercase tracking-widest ml-1">Academy Name</label>
                                <input type="text" defaultValue={settings.academyName} className="w-full px-5 py-3.5 bg-ssamz-bg/50 border border-ssamz-border rounded-xl focus:bg-white focus:ring-4 ring-ssamz-blue/5 outline-none font-bold text-ssamz-text shadow-sm transition-all text-sm" />
                            </div>
                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-slate-300 uppercase tracking-widest ml-1">Owner Name</label>
                                <input type="text" defaultValue={settings.owner} className="w-full px-5 py-3.5 bg-ssamz-bg/50 border border-ssamz-border rounded-xl focus:bg-white focus:ring-4 ring-ssamz-blue/5 outline-none font-bold text-ssamz-text shadow-sm transition-all text-sm" />
                            </div>
                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-slate-300 uppercase tracking-widest ml-1">Phone Number</label>
                                <input type="tel" defaultValue={settings.phone} className="w-full px-5 py-3.5 bg-ssamz-bg/50 border border-ssamz-border rounded-xl focus:bg-white focus:ring-4 ring-ssamz-blue/5 outline-none font-bold text-ssamz-text shadow-sm transition-all text-sm" />
                            </div>
                            <div className="space-y-2">
                                <label className="text-[10px] font-black text-slate-300 uppercase tracking-widest ml-1">Email Address</label>
                                <input type="email" defaultValue={settings.email} className="w-full px-5 py-3.5 bg-ssamz-bg/50 border border-ssamz-border rounded-xl focus:bg-white focus:ring-4 ring-ssamz-blue/5 outline-none font-bold text-ssamz-text shadow-sm transition-all text-sm" />
                            </div>
                        </div>
                        <div className="space-y-2">
                            <label className="text-[10px] font-black text-slate-300 uppercase tracking-widest ml-1">Business Address</label>
                            <input type="text" defaultValue={settings.address} className="w-full px-5 py-3.5 bg-ssamz-bg/50 border border-ssamz-border rounded-xl focus:bg-white focus:ring-4 ring-ssamz-blue/5 outline-none font-bold text-ssamz-text shadow-sm transition-all text-sm" />
                        </div>
                    </section>

                    <section className="space-y-8 pt-10 border-t border-ssamz-bg">
                        <div className="flex items-center space-x-4">
                            <div className="w-1.5 h-6 bg-emerald-400 rounded-full"></div>
                            <h3 className="text-lg font-black text-ssamz-navy tracking-tight">System Preferences</h3>
                        </div>
                        <div className="space-y-4">
                            <div className="flex items-center justify-between p-8 bg-ssamz-bg/30 rounded-3xl border border-ssamz-bg">
                                <div>
                                    <p className="text-[14px] font-black text-ssamz-text">Auto Attendance Push</p>
                                    <p className="text-[11px] text-slate-400 font-bold mt-1">등하원 시 학부모에게 자동으로 푸시 알림을 보냅니다.</p>
                                </div>
                                <div className="w-12 h-6 bg-emerald-500 rounded-full relative shadow-inner">
                                    <div className="w-4 h-4 bg-white rounded-full absolute right-1 top-1 shadow-sm"></div>
                                </div>
                            </div>
                        </div>
                    </section>
                </div>
            </div>
        </div>
    );
}

export default AdminSettings;
