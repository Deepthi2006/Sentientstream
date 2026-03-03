// src/components/Home.tsx
import { useState, useContext, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Sparkles, Navigation, UserCircle2, Activity, BarChart3, CalendarDays, Home as HomeIcon } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';
import api from '../api';

const MOODS = [
  { id: 'happy', label: 'Happy', emoji: '😊' },
  { id: 'sad', label: 'Sad/Melancholy', emoji: '🌧️' },
  { id: 'energetic', label: 'Energetic', emoji: '⚡' },
  { id: 'calm', label: 'Calm/Peaceful', emoji: '🌊' },
  { id: 'romantic', label: 'Romantic', emoji: '❤️' },
  { id: 'dark', label: 'Dark/Mysterious', emoji: '🌑' },
  { id: 'inspirational', label: 'Inspirational', emoji: '✨' },
  { id: 'funny', label: 'Funny', emoji: '😂' },
];

export default function Home() {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useContext(AuthContext);
  const [currentMood, setCurrentMood] = useState<string | null>(null);

  useEffect(() => {
    // Fetch the user's mathematically dominant mood from recent watch history
    api.get('/user/profile')
      .then(res => {
        if (res.data && res.data.dominant_mood) {
          setCurrentMood(res.data.dominant_mood);
        }
      })
      .catch(err => console.error("Could not fetch user profile", err));
  }, []);

  const goToFeed = (moodId?: string) => {
    navigate(moodId ? `/feed?mood=${moodId}` : '/feed?mode=auto');
  };

  const activeMoodData = MOODS.find(m => m.id === currentMood);

  return (
    <div className="flex flex-col items-center justify-center bg-black text-zinc-100 p-6 relative pb-32">
      <button
        onClick={logout}
        className="absolute top-6 right-6 p-2 bg-zinc-900 border border-zinc-800 rounded-full hover:bg-zinc-800 transition"
      >
        <UserCircle2 size={24} className="text-zinc-400" />
      </button>

      <div className="max-w-md w-full text-center space-y-8">

        {/* Header */}
        <div className="space-y-3">
          <h1 className="text-4xl font-extrabold flex justify-center items-center gap-3">
            <Sparkles className="text-pink-500" size={32} />
            <span>Sentient<span className="text-zinc-500 font-light">Stream</span></span>
          </h1>
          <p className="text-zinc-400 text-lg">Discover videos tuned to your frequency</p>
        </div>

        {/* Dynamic Vibe Indicator */}
        <div className="flex flex-col items-center justify-center gap-2 pt-2">
          <div className="flex items-center gap-2 text-zinc-500 text-xs font-bold uppercase tracking-widest">
            <Activity size={14} className="animate-pulse text-pink-500" />
            Your Detected Vibe
          </div>
          {activeMoodData ? (
            <div className="px-5 py-2.5 bg-[#0a0a0a] border border-zinc-800 rounded-full shadow-lg shadow-pink-500/5 flex items-center gap-3">
              <span className="text-2xl">{activeMoodData.emoji}</span>
              <span className="font-semibold text-zinc-200">{activeMoodData.label}</span>
            </div>
          ) : (
            <div className="px-5 py-2.5 bg-[#0a0a0a] border border-zinc-800 rounded-full text-zinc-500 text-sm font-medium">
              Analyzing watch history...
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <button
          onClick={() => goToFeed()}
          className="w-full flex items-center justify-center gap-3 bg-zinc-100 hover:bg-white text-black transition-all active:scale-[0.98] p-4 rounded-xl text-lg font-bold"
        >
          <Navigation size={20} className="fill-current" />
          Surprise Me (Auto Mood)
        </button>

        <div className="flex items-center gap-4 text-zinc-600 my-6">
          <div className="h-px bg-zinc-800 flex-1"></div>
          <span className="text-xs font-semibold tracking-widest uppercase">Or force a mood</span>
          <div className="h-px bg-zinc-800 flex-1"></div>
        </div>

        {/* Mood Grid */}
        <div className="grid grid-cols-2 gap-3">
          {MOODS.map(mood => (
            <button
              key={mood.id}
              onClick={() => goToFeed(mood.id)}
              className="flex flex-col items-center justify-center gap-2 bg-[#0a0a0a] border border-zinc-800 hover:border-zinc-500 active:scale-95 p-4 rounded-xl transition-all group"
            >
              <span className="text-3xl group-hover:scale-110 transition-transform">{mood.emoji}</span>
              <span className="text-sm font-medium text-zinc-400 group-hover:text-zinc-200">{mood.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 w-full max-w-md bg-black/90 backdrop-blur-lg border-t border-zinc-800 pb-safe pt-3 px-6 flex justify-around items-center z-50">
        <button
          onClick={() => navigate('/home')}
          className={`flex flex-col items-center gap-1 p-2 transition-colors ${location.pathname === '/home' ? 'text-white' : 'text-zinc-500 hover:text-zinc-300'}`}
        >
          <HomeIcon size={24} />
          <span className="text-[10px] uppercase font-bold tracking-wider">Home</span>
        </button>
        <button
          onClick={() => navigate('/insights')}
          className={`flex flex-col items-center gap-1 p-2 transition-colors ${location.pathname === '/insights' ? 'text-pink-500' : 'text-zinc-500 hover:text-zinc-300'}`}
        >
          <BarChart3 size={24} />
          <span className="text-[10px] uppercase font-bold tracking-wider">Insights</span>
        </button>
        <button
          onClick={() => navigate('/weekly-summary')}
          className={`flex flex-col items-center gap-1 p-2 transition-colors ${location.pathname === '/weekly-summary' ? 'text-purple-400' : 'text-zinc-500 hover:text-zinc-300'}`}
        >
          <CalendarDays size={24} />
          <span className="text-[10px] uppercase font-bold tracking-wider">Summary</span>
        </button>
      </nav>
    </div>
  );
}
