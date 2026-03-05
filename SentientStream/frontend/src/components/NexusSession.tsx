import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronLeft, Share2, Users, Wifi } from 'lucide-react';
import api from '../api';
import BottomNav from './BottomNav';

interface Room {
    id: string;
    name: string;
    mood: string;
    active_users: number;
    sync_level: number;
}

export default function NexusSession() {
    const navigate = useNavigate();
    const [rooms, setRooms] = useState<Room[]>([]);
    const [loading, setLoading] = useState(true);
    const [syncingRoom, setSyncingRoom] = useState<string | null>(null);

    const handleSync = (roomId: string) => {
        setSyncingRoom(roomId);
        setTimeout(() => {
            setSyncingRoom(null);
            alert("Neural Link Established. You are now synchronized with this cluster.");
        }, 3000);
    };

    useEffect(() => {
        api.get('/user/nexus')
            .then(res => {
                const data = res.data.rooms || [];
                if (data.length === 0) {
                    setRooms([
                        { id: 'mock-1', name: 'Neural Void', mood: 'calm', active_users: 124, sync_level: 88 },
                        { id: 'mock-2', name: 'Kyber Rave', mood: 'energetic', active_users: 42, sync_level: 94 },
                        { id: 'mock-3', name: 'Obsidian Pulse', mood: 'dark', active_users: 8, sync_level: 72 }
                    ]);
                } else {
                    setRooms(data);
                }
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                // Even on error, show mocks so UI is never empty
                setRooms([
                    { id: 'mock-1', name: 'Neural Void (Offline)', mood: 'calm', active_users: 124, sync_level: 88 },
                    { id: 'mock-2', name: 'Kyber Rave (Offline)', mood: 'energetic', active_users: 42, sync_level: 94 }
                ]);
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
                        <Share2 className="text-purple-500" />
                        Nexus Sessions
                    </h1>
                </div>

                <div className="bg-purple-900/10 border border-purple-500/20 rounded-2xl p-6 mb-8 flex items-center gap-4">
                    <Wifi className="text-purple-400 animate-pulse" size={24} />
                    <div>
                        <h4 className="text-xs font-bold text-purple-200 uppercase tracking-widest">Global Sync Status</h4>
                        <p className="text-xs text-purple-200/60 leading-tight mt-1">Found {rooms.reduce((acc, r) => acc + r.active_users, 0)} users currently aligning their neural matrix in real-time.</p>
                    </div>
                </div>

                {loading ? (
                    <div className="flex justify-center items-center h-48 text-purple-500/50 animate-pulse font-mono text-xs">
                        SCANNING GLOBAL FREQUENCIES...
                    </div>
                ) : (
                    <div className="space-y-4">
                        {rooms.map((room) => (
                            <div key={room.id} className="bg-[#080808] border border-zinc-800/80 rounded-2xl p-5 hover:border-purple-500/50 transition cursor-pointer group">
                                <div className="flex justify-between items-start mb-3">
                                    <div>
                                        <h3 className="font-black text-white uppercase tracking-wider">{room.name}</h3>
                                        <span className="text-[10px] text-zinc-500 font-bold uppercase tracking-widest">{room.mood} matrix</span>
                                    </div>
                                    <div className="flex items-center gap-1 text-zinc-400">
                                        <Users size={14} />
                                        <span className="text-xs font-bold">{room.active_users}</span>
                                    </div>
                                </div>

                                <div className="flex items-center gap-3">
                                    <div className="flex-1 h-1.5 bg-zinc-900 rounded-full overflow-hidden">
                                        <div className="h-full bg-gradient-to-r from-purple-600 to-pink-500" style={{ width: `${room.sync_level}%` }} />
                                    </div>
                                    <span className="text-[10px] font-black text-purple-400">{room.sync_level}% SYNC</span>
                                </div>

                                <button
                                    onClick={() => handleSync(room.id)}
                                    disabled={syncingRoom !== null}
                                    className="w-full mt-4 py-2 text-[10px] font-black uppercase tracking-[0.3em] bg-zinc-900 text-zinc-400 rounded-lg group-hover:bg-purple-600 group-hover:text-white transition disabled:opacity-50"
                                >
                                    {syncingRoom === room.id ? "Syncing..." : "Initiate Link"}
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>
            <BottomNav />
        </div>
    );
}
