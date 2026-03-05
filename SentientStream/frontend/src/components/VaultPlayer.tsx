import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { ChevronLeft, Film, Sparkles } from 'lucide-react';
import api from '../api';

interface Video {
    video_id: string;
    stream_url: string;
    title: string;
    primary_mood: string;
}

export default function VaultPlayer() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const vidIds = searchParams.get('ids')?.split(',') || [];
    const mood = searchParams.get('mood') || 'Archive';

    const [videos, setVideos] = useState<Video[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (vidIds.length === 0) {
            navigate('/vault');
            return;
        }

        // Fetch details for each video in the archive
        const fetchVids = async () => {
            try {
                const results = await Promise.all(
                    vidIds.map(id => api.get(`/videos/${id}`))
                );
                setVideos(results.map(r => r.data));
            } catch (err) {
                console.error("Vault retrieval failed", err);
            } finally {
                setLoading(false);
            }
        };

        fetchVids();
    }, []);

    if (loading) return (
        <div className="h-screen bg-black flex flex-col items-center justify-center text-zinc-500 font-mono text-xs tracking-[0.3em]">
            <Film className="animate-spin mb-4 text-zinc-800" size={40} />
            RECONSTRUCTING NEURAL ARC...
        </div>
    );

    return (
        <div className="h-screen w-full bg-black flex flex-col overflow-hidden">
            {/* Header */}
            <div className="p-6 flex items-center gap-4 bg-black/80 backdrop-blur-xl border-b border-zinc-900 z-50">
                <button onClick={() => navigate('/vault')} className="p-2 bg-zinc-900 rounded-full">
                    <ChevronLeft size={20} />
                </button>
                <div>
                    <h1 className="text-sm font-black uppercase tracking-widest text-zinc-400">Cinematic Rewind</h1>
                    <p className="text-xs text-zinc-600 flex items-center gap-1">
                        <Sparkles size={10} /> {mood} Matrix
                    </p>
                </div>
            </div>

            {/* Scrollable Gallery */}
            <div className="flex-1 overflow-y-auto snap-y snap-mandatory scrollbar-hide">
                {videos.map((vid, idx) => (
                    <div key={idx} className="h-full w-full snap-start relative bg-zinc-950 flex flex-col justify-center">
                        <video
                            src={vid.stream_url}
                            className="w-full aspect-video object-cover"
                            controls
                            autoPlay={idx === 0}
                            loop
                        />
                        <div className="p-6 bg-gradient-to-t from-black to-transparent">
                            <h2 className="text-xl font-bold text-white">{vid.title}</h2>
                            <p className="text-zinc-500 text-sm mt-1 uppercase tracking-tighter">Frequency: {vid.primary_mood}</p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Cinematic Overlay */}
            <div className="fixed inset-0 pointer-events-none border-[40px] border-black/20 mix-blend-overlay opacity-30" />
        </div>
    );
}
