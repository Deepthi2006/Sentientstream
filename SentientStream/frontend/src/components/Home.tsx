// src/components/Home.tsx
import { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Navigation, ListFilter, UserCircle2 } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';

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
  const { logout } = useContext(AuthContext);

  const goToFeed = (moodId?: string) => {
    navigate(moodId ? `/feed?mood=${moodId}` : '/feed?mode=auto');
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-black text-white p-6 relative">
      <button
        onClick={logout}
        className="absolute top-6 right-6 p-2 bg-zinc-800 rounded-full hover:bg-zinc-700 transition"
      >
        <UserCircle2 size={24} />
      </button>

      <div className="max-w-md w-full text-center space-y-8">
        <div className="space-y-2">
          <h1 className="text-4xl font-extrabold bg-gradient-to-r from-purple-400 to-pink-600 bg-clip-text text-transparent flex justify-center items-center gap-2">
            <Sparkles className="text-pink-500" />
            SentientStream
          </h1>
          <p className="text-zinc-400">Discover videos tuned to your emotional frequency</p>
        </div>

        <button
          onClick={() => goToFeed()}
          className="w-full flex items-center justify-center gap-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:opacity-90 transition p-4 rounded-xl text-lg font-bold shadow-lg shadow-indigo-500/30"
        >
          <Navigation size={20} />
          Surprise Me (Auto Mood)
        </button>

        <div className="flex items-center gap-4 text-zinc-500 my-6">
          <div className="h-px bg-zinc-800 flex-1"></div>
          <span className="text-sm">OR CHOOSE A MOOD</span>
          <div className="h-px bg-zinc-800 flex-1"></div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          {MOODS.map(mood => (
            <button
              key={mood.id}
              onClick={() => goToFeed(mood.id)}
              className="flex flex-col items-center justify-center gap-2 bg-zinc-900 border border-zinc-800 hover:border-zinc-600 hover:bg-zinc-800 p-4 rounded-xl transition group"
            >
              <span className="text-3xl group-hover:scale-110 transition-transform">{mood.emoji}</span>
              <span className="text-sm font-medium text-zinc-300 group-hover:text-white">{mood.label}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
