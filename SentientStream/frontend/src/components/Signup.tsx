import { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Sparkles, User, Lock } from 'lucide-react';
import { AuthContext } from '../context/AuthContext';
import api from '../api';

export default function Signup() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/auth/signup', { username, password });
      const res = await api.post('/auth/login', { username, password });
      login(res.data.access_token);
      navigate('/home');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Sign up failed. Username might be taken.');
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-black text-zinc-100 p-6">

      {/* Formal Header */}
      <div className="mb-10 text-center space-y-3">
        <h1 className="text-4xl font-extrabold flex justify-center items-center gap-3">
          <Sparkles className="text-pink-500" size={32} />
          <span>Sentient<span className="text-zinc-500 font-light">Stream</span></span>
        </h1>
        <p className="text-zinc-400 text-lg">Create a new account</p>
      </div>

      <form
        onSubmit={handleSignup}
        className="w-full max-w-sm p-10 bg-[#0a0a0a] border border-zinc-800 rounded-2xl shadow-2xl flex flex-col gap-5"
      >
        {error && (
          <div className="p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-sm text-center font-medium">
            {error}
          </div>
        )}

        <div className="space-y-1">
          <label className="text-xs font-semibold text-zinc-400 uppercase tracking-widest pl-1">Choose Username</label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
            <input
              type="text"
              placeholder="e.g. john_doe"
              className="w-full pl-10 p-3 rounded-xl bg-zinc-900 border border-zinc-800 focus:border-zinc-600 focus:outline-none focus:ring-1 focus:ring-zinc-600 transition-all font-medium placeholder:text-zinc-600"
              value={username} onChange={e => setUsername(e.target.value)} required
            />
          </div>
        </div>

        <div className="space-y-1">
          <label className="text-xs font-semibold text-zinc-400 uppercase tracking-widest pl-1">Secure Password</label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" size={18} />
            <input
              type="password"
              placeholder="Create a password"
              className="w-full pl-10 p-3 rounded-xl bg-zinc-900 border border-zinc-800 focus:border-zinc-600 focus:outline-none focus:ring-1 focus:ring-zinc-600 transition-all font-medium placeholder:text-zinc-600"
              value={password} onChange={e => setPassword(e.target.value)} required
            />
          </div>
        </div>

        <button
          type="submit"
          className="mt-6 w-full py-3.5 px-4 font-bold text-black bg-zinc-100 rounded-xl hover:bg-white active:scale-[0.98] transition-all"
        >
          Create Account
        </button>

        <p className="text-center text-sm mt-4 text-zinc-500">
          Already have an account?{" "}
          <Link to="/login" className="text-zinc-300 font-semibold hover:text-white transition-colors">
            Sign In
          </Link>
        </p>
      </form>
    </div>
  );
}
