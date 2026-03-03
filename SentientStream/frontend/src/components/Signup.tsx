import { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
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
      setError(err.response?.data?.detail || 'Signup failed');
    }
  };

  return (
    <div className="flex items-center justify-center h-screen bg-black text-white">
      <form onSubmit={handleSignup} className="w-full max-w-sm p-8 bg-zinc-900 rounded-2xl shadow-xl flex flex-col gap-4">
        <h2 className="text-3xl font-bold text-center mb-6">Join Stream</h2>
        {error && <div className="text-red-500 text-sm text-center">{error}</div>}
        <input 
          type="text" 
          placeholder="New Username" 
          className="p-3 rounded-lg bg-zinc-800 focus:outline-none focus:ring-2 focus:ring-pink-500"
          value={username} onChange={e => setUsername(e.target.value)} required 
        />
        <input 
          type="password" 
          placeholder="New Password" 
          className="p-3 rounded-lg bg-zinc-800 focus:outline-none focus:ring-2 focus:ring-pink-500"
          value={password} onChange={e => setPassword(e.target.value)} required 
        />
        <button type="submit" className="mt-4 p-3 font-semibold text-white bg-gradient-to-r from-pink-600 to-purple-600 rounded-lg hover:opacity-90 transition">Create Account</button>
        <p className="text-center text-sm mt-4 text-zinc-400">
          Already have an account? <Link to="/login" className="text-pink-400 hover:text-pink-300">Login</Link>
        </p>
      </form>
    </div>
  );
}
