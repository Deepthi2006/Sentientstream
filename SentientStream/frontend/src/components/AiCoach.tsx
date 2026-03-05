import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, BrainCircuit, Activity, Crosshair, Zap } from 'lucide-react';
import api from '../api';
import BottomNav from './BottomNav';

interface CoachData {
    title: string;
    content: string;
    action: string;
    intensity: number;
}

export default function AiCoach() {
    const navigate = useNavigate();
    const [data, setData] = useState<CoachData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get('/user/ai-coach')
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
        <div className="flex flex-col items-center min-h-screen bg-black text-zinc-100 relative pb-24">
            <div className="w-full max-w-md p-6">
                {/* Header */}
                <div className="flex items-center gap-4 mb-10 pt-4">
                    <button onClick={() => navigate('/home')} className="p-2 bg-zinc-900 rounded-full hover:bg-zinc-800 transition">
                        <ChevronLeft size={24} />
                    </button>
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                        <BrainCircuit className="text-cyan-400" />
                        AI Coach
                    </h1>
                </div>

                {loading ? (
                    <div className="flex justify-center items-center h-64 text-cyan-500/50 animate-pulse font-mono text-sm tracking-widest">
                        INITIALIZING NEURAL LINK...
                    </div>
                ) : (
                    <div className="space-y-8">
                        {/* Main Cybernetic Card */}
                        <div className="bg-[#050505] border border-zinc-800 p-8 rounded-3xl shadow-2xl relative overflow-hidden group">
                            {/* Dynamic Glow */}
                            <div
                                className="absolute inset-0 opacity-20 transition-opacity duration-1000"
                                style={{
                                    background: `radial-gradient(circle at center, rgb(34 211 238 / ${data?.intensity || 50}%), transparent 70%)`
                                }}
                            />

                            <div className="relative z-10 flex flex-col gap-6">
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="p-3 bg-cyan-500/10 text-cyan-400 rounded-xl border border-cyan-500/20">
                                            <Crosshair size={24} />
                                        </div>
                                        <div>
                                            <h2 className="text-[10px] font-bold text-cyan-500/70 uppercase tracking-[0.2em] leading-tight">Current Objective</h2>
                                            <h3 className="text-lg font-black text-white tracking-widest uppercase">{data?.title}</h3>
                                        </div>
                                    </div>

                                    {/* Intensity Meter */}
                                    <div className="flex flex-col items-end gap-1">
                                        <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Vector Drive</span>
                                        <div className="text-xl font-black text-cyan-400">
                                            {data?.intensity}%
                                        </div>
                                    </div>
                                </div>

                                <div className="w-full h-px bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent"></div>

                                <p className="text-zinc-300 font-medium leading-relaxed text-sm md:text-base tracking-wide">
                                    "{data?.content}"
                                </p>

                                <div className="mt-4 bg-cyan-950/30 rounded-xl p-4 border border-cyan-500/20 flex gap-4 items-center">
                                    <Zap className="text-cyan-400 shrink-0 animate-pulse" size={20} />
                                    <p className="text-xs text-cyan-100 font-bold uppercase tracking-wider">
                                        {data?.action}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Sub-components / Lore */}
                        <div className="bg-[#0a0a0a] border border-zinc-800/60 p-6 rounded-2xl flex flex-col gap-3">
                            <div className="flex items-center gap-3">
                                <Activity className="text-pink-500 shrink-0" size={18} />
                                <h4 className="font-bold text-xs tracking-widest text-zinc-400 uppercase">Coach Dynamics</h4>
                            </div>
                            <p className="text-xs text-zinc-500 leading-relaxed pl-7 lg:pl-0">
                                This AI strictly analyzes your deep emotional patterns mathematically. It does not judge, it optimizes. Trust the vectors, follow the action plan, and elevate your frequency.
                            </p>
                        </div>
                    </div>
                )}
            </div>

            <BottomNav />
        </div>
    );
}
