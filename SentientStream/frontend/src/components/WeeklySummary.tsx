import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, CalendarDays, Sparkles, Zap, Brain } from 'lucide-react';
import api from '../api';
import BottomNav from './BottomNav';

interface SummaryData {
    title: string;
    content: string;
    dominant_mood: string;
    suggestion: string;
}

export default function WeeklySummary() {
    const navigate = useNavigate();
    const [data, setData] = useState<SummaryData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get('/user/weekly-summary')
            .then(res => {
                setData(res.data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    return (
        <div className="min-h-screen bg-black text-zinc-100 p-6 relative pb-24">
            {/* Header */}
            <div className="flex items-center gap-4 mb-10 pt-4">
                <button onClick={() => navigate('/home')} className="p-2 bg-zinc-900 rounded-full hover:bg-zinc-800 transition">
                    <ChevronLeft size={24} />
                </button>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                    <CalendarDays className="text-pink-500" />
                    Weekly Recap
                </h1>
            </div>

            {loading ? (
                <div className="flex justify-center items-center h-64 text-zinc-500 animate-pulse">
                    Synthesizing historical patterns...
                </div>
            ) : (
                <div className="space-y-8 max-w-md mx-auto">
                    {/* Main Card */}
                    <div className="bg-gradient-to-br from-zinc-900 to-[#0a0a0a] border border-zinc-800 p-8 rounded-3xl shadow-2xl relative overflow-hidden">

                        <div className="absolute -top-10 -right-10 w-32 h-32 bg-pink-500/10 rounded-full blur-3xl p-5"></div>
                        <div className="absolute -bottom-10 -left-10 w-32 h-32 bg-purple-500/10 rounded-full blur-3xl p-5"></div>

                        <div className="relative z-10 flex flex-col gap-6">
                            <div className="flex items-center gap-3">
                                <div className="p-3 bg-pink-500/20 text-pink-500 rounded-xl">
                                    <Brain size={28} />
                                </div>
                                <div>
                                    <h2 className="text-xs font-bold text-zinc-500 uppercase tracking-widest leading-tight">Algorithm Verdict</h2>
                                    <h3 className="text-xl font-bold text-white capitalize">{data?.title}</h3>
                                </div>
                            </div>

                            <div className="w-full h-px bg-zinc-800"></div>

                            <p className="text-zinc-300 leading-relaxed text-sm md:text-base">
                                {data?.content}
                            </p>

                            <div className="mt-2 bg-zinc-950/50 rounded-xl p-4 border border-zinc-800/50 flex gap-3 items-start">
                                <Sparkles className="text-purple-400 shrink-0 mt-0.5" size={18} />
                                <p className="text-xs text-zinc-400 italic">
                                    {data?.suggestion}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-[#0a0a0a] border border-zinc-800 p-6 rounded-2xl flex items-center gap-4">
                        <Zap className="text-yellow-500 shrink-0" size={24} />
                        <div>
                            <h4 className="font-bold text-sm tracking-widest uppercase mb-1">Matrix Calibration</h4>
                            <p className="text-xs text-zinc-500 leading-relaxed">Your neural fingerprint mathematically readjusts every time you like, skip, or replay a video sequence. Your dominant mood vectors are permanently adapting to your behavior.</p>
                        </div>
                    </div>
                </div>
            )}

            <BottomNav />
        </div>
    );
}
