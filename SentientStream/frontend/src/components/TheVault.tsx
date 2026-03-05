import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, Database, Sparkles, Film, PlayCircle } from 'lucide-react';
import api from '../api';
import BottomNav from './BottomNav';

interface Memory {
    mood: string;
    title: string;
    summary: string;
    intensity: number;
    video_ids: string[];
}

export default function TheVault() {
    const navigate = useNavigate();
    const [memories, setMemories] = useState<Memory[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get('/user/vault')
            .then(res => {
                const data = res.data.memories || [];
                if (data.length === 0) {
                    // Provide high-quality mocks if backend is empty
                    setMemories([
                        {
                            mood: 'calm',
                            title: 'The Serenity Protocol',
                            summary: 'A deep-state neural reconstruction of your peaceful frequencies. The echoes of silence remain within the matrix.',
                            intensity: 85,
                            video_ids: ['dfb7dd7b-be4c-4e8c-859a-df5fb9bf7a5f', '4ef270a6-16e6-4de3-4965-a2e3-1963da1c1490']
                        },
                        {
                            mood: 'energetic',
                            title: 'Kinetic Surge Arc',
                            summary: 'High-frequency synchronization detected. Re-trace the path of peak emotional momentum through the neural void.',
                            intensity: 92,
                            video_ids: ['096bcfea-2299-4438-90fe-8a1a36731506', '0b561295-af62-4b30-90a2-094e9f78326e']
                        },
                        {
                            mood: 'dark',
                            title: 'Noir Frequency Archive',
                            summary: 'Exploring the shadows of the subconscious. A cinematic rewind into the elitist obsidian matrix of the mind.',
                            intensity: 64,
                            video_ids: ['6731506', 'pexels-2026'] // Pexels style IDs or UUIDs
                        }
                    ]);
                } else {
                    setMemories(data);
                }
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
                <div className="flex items-center gap-4 mb-10 pt-4">
                    <button onClick={() => navigate('/home')} className="p-2 bg-zinc-900 rounded-full hover:bg-zinc-800 transition">
                        <ChevronLeft size={24} />
                    </button>
                    <h1 className="text-2xl font-bold flex items-center gap-2">
                        <Database className="text-zinc-500" />
                        The Vault
                    </h1>
                </div>

                {loading ? (
                    <div className="flex justify-center items-center h-64 text-zinc-500 animate-pulse font-mono tracking-widest text-xs">
                        DECRYPTING NEURAL ARCHIVES...
                    </div>
                ) : (
                    <div className="space-y-6">
                        <p className="text-xs text-zinc-500 uppercase font-black tracking-[0.2em] mb-4">Historical Reconstruction</p>

                        {memories.length > 0 ? (
                            memories.map((mem, idx) => (
                                <div key={idx} className="bg-[#050505] border border-zinc-800 rounded-2xl p-6 flex flex-col gap-4 relative overflow-hidden group">
                                    <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-30 transition-opacity">
                                        <Film size={60} />
                                    </div>

                                    <div className="flex items-center gap-3">
                                        <div className="w-2 h-2 rounded-full bg-pink-500 animate-pulse" />
                                        <h2 className="text-lg font-bold tracking-tight">{mem.title}</h2>
                                    </div>

                                    <p className="text-sm text-zinc-400 leading-relaxed italic">
                                        "{mem.summary}"
                                    </p>

                                    <div className="flex items-center justify-between mt-2">
                                        <div className="flex flex-col">
                                            <span className="text-[10px] text-zinc-600 uppercase font-bold tracking-widest">Memory Gain</span>
                                            <div className="w-32 h-1 bg-zinc-900 rounded-full mt-1 overflow-hidden">
                                                <div className="h-full bg-pink-500" style={{ width: `${mem.intensity}%` }} />
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => navigate(`/vault/player?ids=${mem.video_ids.join(',')}&mood=${mem.mood}`)}
                                            className="flex items-center gap-2 text-xs font-bold text-zinc-200 bg-zinc-800 px-4 py-2 rounded-lg hover:bg-zinc-700 transition"
                                        >
                                            <PlayCircle size={14} />
                                            Restore
                                        </button>
                                    </div>
                                </div>
                            ))
                        ) : (
                            <div className="text-center p-12 bg-zinc-900/30 rounded-3xl border border-dashed border-zinc-800">
                                <Sparkles className="mx-auto text-zinc-700 mb-4" size={32} />
                                <p className="text-zinc-500 text-sm">No neural clusters detected for archive reconstruction.</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
            <BottomNav />
        </div>
    );
}
