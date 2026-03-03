import { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import api from '../api';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post('/auth/login', { username, password });
      login(res.data.access_token);
      navigate('/home');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <div className="flex items-center justify-center h-screen bg-black text-white">
      <form onSubmit={handleLogin} className="w-full max-w-sm p-8 bg-zinc-900 rounded-2xl shadow-xl flex flex-col gap-4">
        <h2 className="text-3xl font-bold text-center mb-6">SentientStream</h2>
        {error && <div className="text-red-500 text-sm text-center">{error}</div>}
        <input 
          type="text" 
          placeholder="Username" 
          className="p-3 rounded-lg bg-zinc-800 focus:outline-none focus:ring-2 focus:ring-purple-500"
          value={username} onChange={e => setUsername(e.target.value)} required 
        />
        <input 
          type="password" 
          placeholder="Password" 
          className="p-3 rounded-lg bg-zinc-800 focus:outline-none focus:ring-2 focus:ring-purple-500"
          value={password} onChange={e => setPassword(e.target.value)} required 
        />
        <button type="submit" className="mt-4 p-3 font-semibold text-white bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg hover:opacity-90 transition">Login</button>
        <p className="text-center text-sm mt-4 text-zinc-400">
          Don't have an account? <Link to="/signup" className="text-purple-400 hover:text-purple-300">Sign Up</Link>
        </p>
      </form>
    </div>
  );
}
