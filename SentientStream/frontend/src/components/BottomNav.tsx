import { useNavigate, useLocation } from 'react-router-dom';
import { Home as HomeIcon, BarChart3, CalendarDays, BrainCircuit, Database, Share2, PlusSquare } from 'lucide-react';

export default function BottomNav() {
    const navigate = useNavigate();
    const location = useLocation();

    return (
        <nav className="fixed bottom-0 w-full max-w-md bg-black/90 backdrop-blur-lg border-t border-zinc-800 pb-safe pt-2 px-4 flex justify-around items-center z-50 left-1/2 -translate-x-1/2">
            <button
                onClick={() => navigate('/home')}
                className={`flex flex-col items-center gap-1 p-2 transition-colors ${location.pathname === '/home' ? 'text-white' : 'text-zinc-500 hover:text-zinc-300'}`}
            >
                <HomeIcon size={18} />
                <span className="text-[7px] uppercase font-bold tracking-wider">Home</span>
            </button>
            <button
                onClick={() => navigate('/upload')}
                className={`flex flex-col items-center gap-1 p-2 transition-colors ${location.pathname === '/upload' ? 'text-green-500' : 'text-zinc-500 hover:text-zinc-300'}`}
            >
                <PlusSquare size={18} />
                <span className="text-[7px] uppercase font-bold tracking-wider">Upload</span>
            </button>
            <button
                onClick={() => navigate('/insights')}
                className={`flex flex-col items-center gap-1 p-2 transition-colors ${location.pathname === '/insights' ? 'text-pink-500' : 'text-zinc-500 hover:text-zinc-300'}`}
            >
                <BarChart3 size={18} />
                <span className="text-[8px] uppercase font-bold tracking-wider">Insights</span>
            </button>
            <button
                onClick={() => navigate('/weekly-summary')}
                className={`flex flex-col items-center gap-1 p-2 transition-colors ${location.pathname === '/weekly-summary' ? 'text-purple-400' : 'text-zinc-500 hover:text-zinc-300'}`}
            >
                <CalendarDays size={18} />
                <span className="text-[8px] uppercase font-bold tracking-wider">Summary</span>
            </button>
            <button
                onClick={() => navigate('/ai-coach')}
                className={`flex flex-col items-center gap-1 p-2 transition-colors ${location.pathname === '/ai-coach' ? 'text-cyan-400' : 'text-zinc-500 hover:text-zinc-300'}`}
            >
                <BrainCircuit size={18} />
                <span className="text-[8px] uppercase font-bold tracking-wider">Coach</span>
            </button>
            <button
                onClick={() => navigate('/vault')}
                className={`flex flex-col items-center gap-1 p-2 transition-colors ${location.pathname === '/vault' ? 'text-pink-500' : 'text-zinc-500 hover:text-zinc-300'}`}
            >
                <Database size={18} />
                <span className="text-[8px] uppercase font-bold tracking-wider">Vault</span>
            </button>
            <button
                onClick={() => navigate('/nexus')}
                className={`flex flex-col items-center gap-1 p-2 transition-colors ${location.pathname === '/nexus' ? 'text-purple-500' : 'text-zinc-500 hover:text-zinc-300'}`}
            >
                <Share2 size={18} />
                <span className="text-[8px] uppercase font-bold tracking-wider">Nexus</span>
            </button>
        </nav>
    );
}
