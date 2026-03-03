import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, BarChart3, TrendingUp, Clock, PlayCircle, Heart } from 'lucide-react';
import api from '../api';

interface InsightsData {
    mood_distribution: { mood: string; watch_time: number }[];
    engagement: {
        total_plays: number;
        total_likes: number;
        total_replays: number;
    };
}

export default function Insights() {
    const navigate = useNavigate();
    const [data, setData] = useState<InsightsData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get('/user/insights')
            .then(res => {
                setData(res.data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    const totalWatchTime = data?.mood_distribution.reduce((acc, curr) => acc + curr.watch_time, 0) || 0;

    return (
        <div className="min-h-screen bg-black text-zinc-100 p-6 relative pb-24">
            {/* Header */}
            <div className="flex items-center gap-4 mb-8 pt-4">
                <button onClick={() => navigate('/home')} className="p-2 bg-zinc-900 rounded-full hover:bg-zinc-800 transition">
                    <ChevronLeft size={24} />
                </button>
                <h1 className="text-2xl font-bold flex items-center gap-2">
                    <BarChart3 className="text-pink-500" />
                    Neural Insights
                </h1>
            </div>

            {loading ? (
                <div className="flex justify-center items-center h-64 text-zinc-500 animate-pulse">
                    Calculating matrices...
                </div>
            ) : (
                <div className="space-y-6 max-w-md mx-auto">
                    {/* Top Level Stats */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-[#0a0a0a] border border-zinc-800 p-4 rounded-2xl flex flex-col gap-2">
                            <Clock className="text-blue-400" size={20} />
                            <p className="text-xs text-zinc-500 font-bold uppercase tracking-wider">Total Matrix Time</p>
                            <p className="text-2xl font-bold">
                                {totalWatchTime < 60 ? Math.round(totalWatchTime) : Math.round(totalWatchTime / 60)}
                                <span className="text-sm text-zinc-400 font-normal ml-1">
                                    {totalWatchTime < 60 ? 'sec' : 'min'}
                                </span>
                            </p>
                        </div>
                        <div className="bg-[#0a0a0a] border border-zinc-800 p-4 rounded-2xl flex flex-col gap-2">
                            <TrendingUp className="text-green-400" size={20} />
                            <p className="text-xs text-zinc-500 font-bold uppercase tracking-wider">Network Growth</p>
                            <p className="text-2xl font-bold">{data?.engagement.total_plays || 0} <span className="text-sm text-zinc-400 font-normal">videos</span></p>
                        </div>
                        <div className="bg-[#0a0a0a] border border-zinc-800 p-4 rounded-2xl flex flex-col gap-2">
                            <Heart className="text-pink-500" size={20} />
                            <p className="text-xs text-zinc-500 font-bold uppercase tracking-wider">Liked Inputs</p>
                            <p className="text-2xl font-bold">{data?.engagement.total_likes || 0}</p>
                        </div>
                        <div className="bg-[#0a0a0a] border border-zinc-800 p-4 rounded-2xl flex flex-col gap-2">
                            <PlayCircle className="text-purple-400" size={20} />
                            <p className="text-xs text-zinc-500 font-bold uppercase tracking-wider">Loop Analytics</p>
                            <p className="text-2xl font-bold">{data?.engagement.total_replays || 0} <span className="text-sm text-zinc-400 font-normal">replays</span></p>
                        </div>
                    </div>

                    {/* Detailed Mood Distribution */}
                    <div className="bg-[#0a0a0a] border border-zinc-800 p-6 rounded-2xl space-y-5">
                        <h2 className="text-sm font-bold text-zinc-400 uppercase tracking-widest">Vector Distribution</h2>

                        <div className="space-y-4">
                            {data?.mood_distribution.map((item, i) => {
                                const percentage = totalWatchTime > 0 ? (item.watch_time / totalWatchTime) * 100 : 0;
                                return (
                                    <div key={i} className="space-y-1">
                                        <div className="flex justify-between text-sm font-medium">
                                            <span className="capitalize">{item.mood}</span>
                                            <span className="text-zinc-500">{percentage.toFixed(1)}%</span>
                                        </div>
                                        <div className="w-full h-2 bg-zinc-900 rounded-full overflow-hidden">
                                            <div
                                                className="h-full bg-gradient-to-r from-pink-500 to-purple-500 rounded-full transition-all duration-1000 ease-out"
                                                style={{ width: `${percentage}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                );
                            })}
                            {data?.mood_distribution.length === 0 && (
                                <p className="text-zinc-500 text-sm text-center">No structural data recorded yet.</p>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
